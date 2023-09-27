from CPQ_SF_Configuration import CL_CPQSettings
from CPQ_SF_IntegrationModules import CL_SalesforceIntegrationModules
from CPQ_SF_IntegrationSettings import CL_SalesforceIntegrationParams
from CPQ_SF_FunctionModules import set_quote_opportunity_id, get_market_code
from CPQ_SF_CpqHelper import EVENT_UPDATE
from CPQ_SF_IntegrationReferences import CL_CompositeRequestReferences as REF, CL_IntegrationReferences as INT_REF
import CPQ_SF_OpportunityMapping as OpportunityMapping
from CPQ_SF_PriceBookMapping import CL_PriceBookMapping
from CPQ_SF_BusinessPartnerModules import CL_BusinessPartnerModules
from CPQ_SF_ContactModules import CL_ContactIntegrationModules
from CPQ_SF_CustomObjectModules import CL_CustomObjectModules

if Param is not None:
    editQuoteURl = "/cart/edit?ownerId={ownerId}&quoteId={quoteId}"
    externalParameters = Param.externalParameters
    redirectionUrl = CL_CPQSettings.CPQ_URL
    # Get Opportunity Id
    opportunityId = externalParameters["opportunityid"]
    quoteId = externalParameters["quoteId"]
    if opportunityId and quoteId:
        Quote = QuoteHelper.Get(float(quoteId))
        if Quote:
            # Attach Opportunity Id to Quote
            set_quote_opportunity_id(Quote, opportunityId)
            class_sf_integration_modules = CL_SalesforceIntegrationModules(Quote, Session)
            class_bp_modules = CL_BusinessPartnerModules(Quote, Session, BusinessPartnerRepository)
            class_contact_modules = CL_ContactIntegrationModules(Quote, Session, BusinessPartnerRepository)
            class_custom_object_modules = CL_CustomObjectModules(Quote, Session)
            #############################################
            # 1. AUTHORIZATION
            #############################################
            bearerToken = class_sf_integration_modules.get_auth2_token()
            ######################################################
            # 2. COLLECT OPPORTUNITY INFORMATION & CREATE QUOTE
            ######################################################
            compositePayload = list()
            # Opportunity
            compositeRequest = dict()
            compositeRequest = class_sf_integration_modules.build_cr_sobject_get_opportunity(opportunityId)
            compositePayload.append(compositeRequest)

            # Opportunity Partners
            compositeRequest = dict()
            compositeRequest = class_sf_integration_modules.build_cr_sobject_get_opportunity_partners(opportunityId)
            compositePayload.append(compositeRequest)

            # Call API
            response = class_sf_integration_modules.post_composite_request(bearerToken, compositePayload, INT_REF.REF_GET_OPP)
            if response:
                # Set opportunity fields in Quote
                # Get Opportunity info
                opportunityResponse = next((resp for resp in response["compositeResponse"] if str(resp["referenceId"]) == CL_SalesforceIntegrationParams.SF_OPPORTUNITY_OBJECT), None)
                if opportunityResponse:
                    OpportunityMapping.on_quote_update_inbound_opportunity_integration_mapping(Quote, opportunityResponse["body"])
                    OpportunityMapping.on_quote_createupdate_inbound_opportunity_integration_mapping(Quote, opportunityResponse["body"])

                # Get Opportunity Partners info
                opportunityPartnersResp = next((resp for resp in response["compositeResponse"] if str(resp["referenceId"]) == REF.GET_OPP_PARTNERS_REFID), None)

                if opportunityResponse:
                    # Set Market on quote
                    priceBookMappings = CL_PriceBookMapping().priceBookMapping
                    priceBookMapping = next((mapping for mapping in priceBookMappings if mapping["SF_PRICEBOOK_ID"] == str(opportunityResponse["body"]["Pricebook2Id"])), None)
                    if priceBookMapping:
                        # Get CPQ Market Code
                        marketCode = get_market_code(priceBookMapping["CPQ_MARKET_ID"])
                        if marketCode:
                            Quote.SetMarket(marketCode)
                    ######################################################
                    # 3. COLLECT ADDITIONAL INFORMATION
                    ######################################################
                    response = class_bp_modules.get_customer_details(bearerToken, class_contact_modules, opportunityId, opportunityResponse, opportunityPartnersResp)
                    if response:
                        # Process Customers and Contacts
                        class_bp_modules.process_customers_contacts(response, EVENT_UPDATE)
            #############################################
            # 4. CUSTOM OBJECTS
            #############################################
            class_custom_object_modules.process_inbound_custom_object_mappings(bearerToken, EVENT_UPDATE)
        Quote.Save()
    # Return redirect URL
    redirectionUrl = CL_CPQSettings.CPQ_URL + editQuoteURl.format(ownerId=str(Quote.OwnerId), quoteId=str(Quote.Id))
    Result = str(redirectionUrl)