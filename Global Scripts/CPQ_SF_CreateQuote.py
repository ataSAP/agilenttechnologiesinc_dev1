from CPQ_SF_Configuration import CL_CPQSettings
from CPQ_SF_CustomObjectModules import CL_CustomObjectModules
from CPQ_SF_IntegrationModules import CL_SalesforceIntegrationModules
from CPQ_SF_IntegrationSettings import CL_SalesforceIntegrationParams, CL_GeneralIntegrationSettings, CL_SalesforceQuoteParams
from CPQ_SF_FunctionModules import set_quote_opportunity_id
from CPQ_SF_CpqHelper import EVENT_CREATE
from CPQ_SF_IntegrationReferences import CL_CompositeRequestReferences as REF, CL_SalesforceApis as API, CL_IntegrationReferences as INT_REF
import CPQ_SF_OpportunityMapping as OpportunityMapping
from CPQ_SF_PriceBookMapping import CL_PriceBookMapping
from CPQ_SF_BusinessPartnerModules import CL_BusinessPartnerModules
from CPQ_SF_ContactModules import CL_ContactIntegrationModules
from CPQ_SF_IntegrationMessages import CL_MessageHandler, CL_IntegrationMessages
from Scripting.Quote import MessageLevel


def main(Param, quote):
    editQuoteURl = "/cart/edit?ownerId={ownerId}&quoteId={quoteId}"
    redirectionUrl = str()
    externalParameters = Param.externalParameters
    # Get Opportunity Id
    opportunityId = externalParameters["opportunityid"]
    if opportunityId:
        # Create New Quote
        if Param.createQuote:
            Quote = QuoteHelper.CreateNewQuote()
        # Get current Quote
        else:
            Quote = quote
        if Quote:
            # Set redirection URL
            redirectionUrl = CL_CPQSettings.CPQ_URL + editQuoteURl.format(ownerId=str(Quote.OwnerId), quoteId=str(Quote.Id))
            class_sf_integration_modules = CL_SalesforceIntegrationModules(Quote, Session)
            class_bp_modules = CL_BusinessPartnerModules(Quote, Session, BusinessPartnerRepository)
            class_contact_modules = CL_ContactIntegrationModules(Quote, Session, BusinessPartnerRepository)
            class_custom_object_modules = CL_CustomObjectModules(Quote, Session)
            class_msg_handler = CL_MessageHandler(Quote, Session)
            #############################################
            # 1. AUTHORIZATION
            #############################################
            bearerToken = class_sf_integration_modules.get_auth2_token()
            # GET other quotes linked to opportunity
            compositePayload = list()
            compositeRequest = class_sf_integration_modules.build_cr_get_opp_quotes(opportunityId)
            compositePayload.append(compositeRequest)
            # Call REST API
            response = class_sf_integration_modules.post_composite_request(bearerToken, compositePayload, INT_REF.REF_GET_QUOTES_LINKED_TO_OPPORTUNITY)
            linkedQuotesResp = next((resp for resp in response["compositeResponse"] if resp["referenceId"] == REF.GET_OPP_QUOTES_REFID), None)
            # Only one quote can be linked to SF opportunity
            if CL_GeneralIntegrationSettings.ONLY_ONE_QUOTE_LINKED_TO_OPPORTUNITY and CL_GeneralIntegrationSettings.ATTACH_TO_OPP_IMMEDIATELY_ON_QUOTE_CREATED:
                if linkedQuotesResp:
                    if linkedQuotesResp["body"]["totalSize"] > 0:
                        # STOP PROCESSING
                        class_msg_handler.add_message(CL_IntegrationMessages.ONLY_ONE_QUOTE_E_MSG, MessageLevel.Error)
                        return redirectionUrl
            ##############################################################
            # 2. COLLECT OPPORTUNITY INFORMATION & CREATE QUOTE & PRIMARY
            ##############################################################
            # Attach Opportunity Id to Quote
            set_quote_opportunity_id(Quote, opportunityId)

            compositePayload = list()
            # Opportunity
            compositeRequest = class_sf_integration_modules.build_cr_sobject_get_opportunity(opportunityId)
            compositePayload.append(compositeRequest)

            # Make Quote Primary - Set other Quotes Primary Flag to False
            if CL_GeneralIntegrationSettings.ATTACH_TO_OPP_IMMEDIATELY_ON_QUOTE_CREATED:
                if linkedQuotesResp is not None:
                    if linkedQuotesResp["body"]["totalSize"] > 0:
                        records = list()
                        for linkedQuote in linkedQuotesResp["body"]["records"]:
                            record = dict()
                            record[CL_SalesforceQuoteParams.SF_PRIMARY_QUOTE_FIELD] = False
                            record["Id"] = str(linkedQuote["Id"])
                            record["attributes"] = {"type": CL_SalesforceQuoteParams.SF_QUOTE_OBJECT}
                            records.append(record)
                        if records:
                            compositeRequest = class_sf_integration_modules.get_cr_sobjectcollection_payload_header(API.PATCH, REF.UPDATE_PRIMARY_REFID, None)
                            compositeRequest["body"] = {"records": records}
                            compositePayload.append(compositeRequest)

            # Opportunity Partners
            compositeRequest = class_sf_integration_modules.build_cr_sobject_get_opportunity_partners(opportunityId)
            compositePayload.append(compositeRequest)

            # Attach quote to opportunity immediately upon quote is created
            if CL_GeneralIntegrationSettings.ATTACH_TO_OPP_IMMEDIATELY_ON_QUOTE_CREATED:
                # Quote
                records = list()
                record = class_sf_integration_modules.build_cr_record_create_quote(opportunityId)
                records.append(record)
                compositeRequest = class_sf_integration_modules.get_cr_sobjectcollection_payload_header(API.POST, CL_SalesforceQuoteParams.SF_QUOTE_OBJECT, None)
                compositeRequest["body"] = {"records": records}
                compositePayload.append(compositeRequest)

            if compositePayload:
                response = class_sf_integration_modules.post_composite_request(bearerToken, compositePayload, INT_REF.REF_UPDATE_OPP_MAKE_PRIMARY)

            if response:
                # Set header fields in Quote
                # Get Opportunity info
                opportunityResponse = next((resp for resp in response["compositeResponse"] if str(resp["referenceId"]) == CL_SalesforceIntegrationParams.SF_OPPORTUNITY_OBJECT), None)
                if opportunityResponse:
                    OpportunityMapping.on_quote_create_inbound_opportunity_integration_mapping(Quote, opportunityResponse["body"])
                    OpportunityMapping.on_quote_createupdate_inbound_opportunity_integration_mapping(Quote, opportunityResponse["body"])

                # Get Opportunity Partners info
                opportunityPartnersResp = next((resp for resp in response["compositeResponse"] if str(resp["referenceId"]) == REF.GET_OPP_PARTNERS_REFID), None)
                
                if opportunityResponse:
                    # Set Market on quote
                    priceBookMappings = CL_PriceBookMapping().priceBookMapping
                    priceBookMapping = next((mapping for mapping in priceBookMappings if mapping["SF_PRICEBOOK_ID"] == str(opportunityResponse["body"]["Pricebook2Id"])), None)
                    if priceBookMapping:
                        # Get CPQ Market Code
                        Quote.SetMarket(priceBookMapping["CPQ_MARKET_ID"])
                    ######################################################
                    # 3. COLLECT ADDITIONAL INFORMATION
                    ######################################################
                    response = class_bp_modules.get_customer_details(bearerToken, class_contact_modules, opportunityId, opportunityResponse, opportunityPartnersResp)
                    if response:
                        # Process Customers and Contacts
                        class_bp_modules.process_customers_contacts(response, EVENT_CREATE)
            #############################################
            # 4. CUSTOM OBJECTS
            #############################################
            class_custom_object_modules.process_inbound_custom_object_mappings(bearerToken, EVENT_CREATE) 
            if Param.createQuote: Quote.Save()
        return redirectionUrl

# Execute Main and return redirect URL
if Param is not None:
    quote = None
    if "context" in globals():
        quote = context.Quote
    Result = main(Param, quote)