from CPQ_SF_Configuration import CL_SalesforceSettings
from CPQ_SF_IntegrationModules import CL_SalesforceIntegrationModules
from CPQ_SF_IntegrationSettings import CL_SalesforceAccountObjects, CL_SalesforceContactObjects, CL_SalesforceIntegrationParams, CL_CrmIdBusinessPartnerMapping
from CPQ_SF_CpqHelper import EVENT_CREATE, EVENT_UPDATE, CPQ_BP_STANDARD_FIELD, CPQ_BP_CUSTOM_FIELD
from CPQ_SF_IntegrationReferences import CL_SalesforceApis as API, CL_CompositeRequestReferences as REF, CL_SalesforceCustomerRoles as SFROLES, CL_IntegrationReferences as INT_REF
from CPQ_SF_BusinessPartnerMapping import CL_OutboundBusinessPartnerMapping, CL_InboundBusinessPartnerMapping
from CPQ_SF_ContactMapping import CL_InboundContactMapping
from CPQ_SF_FunctionModules import del_quote_business_partner_by_function, get_quote_business_partner


###############################################################################################
# Class CL_BusinessPartnerModules:
#       Class to store integration functions related to Business Partners(Accounts)
###############################################################################################
class CL_BusinessPartnerModules(CL_SalesforceIntegrationModules):

    ###############################################################################################
    # Function to get the compositeRequest of a GET Account request
    ###############################################################################################
    def build_cr_sobject_get_account(self, accountId, partnerFunction):
        url = API.CR_GET_ACCOUNT_API.format(version=str(CL_SalesforceSettings.SALESFORCE_VERSION), accountId=str(accountId))
        compositeRequest = self.build_cr_sobject_request(url, API.GET, None, partnerFunction)
        return compositeRequest

    ###############################################################################################
    # Function to get the compositeRequest of a PATCH Account request
    ###############################################################################################
    def build_cr_sobject_patch_account(self, accountId, partnerFunction, record):
        url = API.CR_GET_ACCOUNT_API.format(version=str(CL_SalesforceSettings.SALESFORCE_VERSION), accountId=str(accountId))
        compositeRequest = self.build_cr_sobject_request(url, API.PATCH, record, partnerFunction)
        return compositeRequest

    ###############################################################################################
    # Function to build Customer Role sObject POST API body
    ###############################################################################################
    def build_account_sobject_create_record(self, partnerFunction, businessPartner, event):
        body = dict()
        if event == EVENT_CREATE:
            body = CL_OutboundBusinessPartnerMapping().on_opportunity_create_mapping(partnerFunction, self.Quote, businessPartner)
        elif event == EVENT_UPDATE:
            body = CL_OutboundBusinessPartnerMapping().on_opportunity_update_mapping(partnerFunction, self.Quote, businessPartner)
        body.update(CL_OutboundBusinessPartnerMapping().on_opportunity_createupdate_mapping(partnerFunction, self.Quote, businessPartner))
        return body

    ###############################################################################################
    # Function to get Create/Update Account Composite Payload
    ###############################################################################################
    def get_create_update_account_composite_payload(self, event):
        compositePayload = list()
        businessPartnerMappings = CL_OutboundBusinessPartnerMapping().outboundPartnerMappings
        # Build Create/Update Business Partner composite payload
        for bpMapping in businessPartnerMappings:
            if bpMapping["SalesforceAccount"]:
                businessPartner = get_quote_business_partner(self.Quote, bpMapping["CpqPartnerFunction"])
                if businessPartner:
                    # Get Business Partner Look up id
                    bpLookUpId = self.get_business_partner_id(bpMapping["CpqPartnerFunction"], businessPartner)
                    # Update account
                    if bpLookUpId:
                        customerRecord = self.build_account_sobject_create_record(bpMapping["CpqPartnerFunction"], businessPartner, event)
                        compositeRequest = self.build_cr_sobject_patch_account(bpLookUpId, REF.UPDATE_BP_ACC.format(partnerFunction=str(bpMapping["CpqPartnerFunction"])), customerRecord)
                        compositePayload.append(compositeRequest)
                    # Create account
                    else:
                        customerRecord = self.build_account_sobject_create_record(bpMapping["CpqPartnerFunction"], businessPartner, event)
                        compositeRequest = self.get_sobject_post_payload_header(CL_SalesforceIntegrationParams.SF_ACCOUNT_OBJECT, REF.CREATE_BP_ACC.format(partnerFunction=str(bpMapping["CpqPartnerFunction"])))
                        compositeRequest["body"] = customerRecord
                        compositePayload.append(compositeRequest)
        return compositePayload

    ###############################################################################################
    # Function to get accountId of customers (Accounts & Partners)
    ###############################################################################################
    def get_opportunity_customers_accountid(self, bearerToken, customerType, opportunityResponse, opportunityPartnersResp):
        accountId = None
        # Opportunity Main Account
        oppMainAccount = str(opportunityResponse["body"]["AccountId"])
        if customerType == CL_SalesforceAccountObjects.SF_OPPORTUNITY_ACC:
            accountId = oppMainAccount
        ## SAP added Account look ups
        elif customerType == CL_SalesforceAccountObjects.OpportunitySP:
            accountId = str(opportunityResponse["body"]["Sold_to_Account__c"])
        elif customerType == CL_SalesforceAccountObjects.OpportunitySH:
            accountId = str(opportunityResponse["body"]["Ship_to_Account__c"])
        elif customerType == CL_SalesforceAccountObjects.OpportunityUEU:
            accountId = str(opportunityResponse["body"]["UEU_Account__c"])
        elif customerType == CL_SalesforceAccountObjects.OpportunityPRO:
            accountId = str(opportunityResponse["body"]["Prospect_Account__c"])
        elif customerType == CL_SalesforceAccountObjects.OpportunityRE:
            accountId = str(opportunityResponse["body"]["SubDistributor__c"])
        # OpportunityAccountPartnerRoleAccount
        elif customerType == CL_SalesforceAccountObjects.SF_OPPORTUNITY_ACC_PARTNER_ROLE_ACC:
            compositePayload = list()
            compositeRequest = self.build_cr_get_opp_acc_partner_role(oppMainAccount, REF.GET_OPP_ACC_PARTNER_ROLE_ACC)
            compositePayload.append(compositeRequest)
            if compositePayload:
                response = self.post_composite_request(bearerToken, compositePayload, INT_REF.REF_GET_OPP_ACC_PARTNER_ROLE_ACC)
                if response:
                    partnerResp = next((resp["body"] for resp in response["compositeResponse"] if resp["referenceId"] == REF.GET_OPP_ACC_PARTNER_ROLE_ACC), None)
                    if partnerResp:
                        accountId = next((str(resp["AccountFromId"]) for resp in partnerResp["body"]["records"]), None)
        else:
            # Opportunity Partners
            if opportunityPartnersResp:
                # OpportunityPartnerRoleAccountBillTo
                if customerType == CL_SalesforceAccountObjects.SF_OPPORTUNITY_PARTNER_ACC_BILL_TO:
                    partnerResp = next((resp for resp in opportunityPartnersResp["body"]["records"] if resp["Role"] == SFROLES.SF_BILL_TO and resp["AccountToId"] != oppMainAccount), None)
                    if partnerResp:
                        accountId = str(partnerResp["AccountToId"])
                # OpportunityPartnerRoleAccountShipTo
                elif customerType == CL_SalesforceAccountObjects.SF_OPPORTUNITY_PARTNER_ACC_SHIP_TO:
                    partnerResp = next((resp for resp in opportunityPartnersResp["body"]["records"] if resp["Role"] == SFROLES.SF_SHIP_TO and resp["AccountToId"] != oppMainAccount), None)
                    if partnerResp:
                        accountId = str(partnerResp["AccountToId"])
                # OpportunityPartnerRoleAccountEndUser
                elif customerType == CL_SalesforceAccountObjects.SF_OPPORTUNITY_PARTNER_ACC_END_USER:
                    partnerResp = next((resp for resp in opportunityPartnersResp["body"]["records"] if resp["Role"] == SFROLES.SF_END_USER and resp["AccountToId"] != oppMainAccount), None)
                    if partnerResp:
                        accountId = str(partnerResp["AccountToId"])
                # OpportunityPartnerRoleAccount
                elif customerType == CL_SalesforceAccountObjects.SF_OPPORTUNITY_PARTNER_ROLE_ACC:
                    partnerResp = next((resp for resp in opportunityPartnersResp["body"]["records"] if resp["AccountToId"] != oppMainAccount), None)
                    if partnerResp:
                        accountId = str(partnerResp["AccountToId"])
        return accountId

    ###############################################################################################
    # Function to build create Opportunity Partner compositeRequest
    ###############################################################################################
    def build_opportunitypartners_sobjectcollection_create_record(self, opportunityId, CpqPartnerFunction, partnerRole):
        records = list()
        rec = dict()
        # Check if customer is present on Quote
        businessPartnerId = self.get_business_partner_id(CpqPartnerFunction)
        if businessPartnerId and partnerRole:
            # Opportunity ID
            rec["OpportunityId"] = opportunityId
            # Account ID
            rec["AccountToId"] = businessPartnerId
            # Role
            if partnerRole == CL_SalesforceAccountObjects.SF_OPPORTUNITY_PARTNER_ACC_BILL_TO:
                rec["Role"] = SFROLES.SF_BILL_TO
            elif partnerRole == CL_SalesforceAccountObjects.SF_OPPORTUNITY_PARTNER_ACC_SHIP_TO:
                rec["Role"] = SFROLES.SF_SHIP_TO
            elif partnerRole == CL_SalesforceAccountObjects.SF_OPPORTUNITY_PARTNER_ACC_END_USER:
                rec["Role"] = SFROLES.SF_END_USER
            rec["attributes"] = {"type": CL_SalesforceIntegrationParams.SF_OPPORTUNITY_PARTNER_OBJECT}
            records.append(rec)
        return records

    ###############################################################################################
    # Function to build composite request record to create Opportunity Partners
    ###############################################################################################
    def build_cr_record_create_opp_partners(self, opportunityId, oppPartnerRolesResponse):
        # Build composite request to create opportunity partners
        records = list()
        businessPartnerMappings = CL_OutboundBusinessPartnerMapping().outboundPartnerMappings
        for bpMapping in businessPartnerMappings:
            if bpMapping["SalesforceAccount"] in CL_SalesforceAccountObjects.SF_OPP_PARTNERS:
                if oppPartnerRolesResponse:
                    # Get CPQ Account Id
                    businessPartnerId = self.get_business_partner_id(bpMapping["CpqPartnerFunction"])
                    if businessPartnerId:
                        # Role
                        sfRole = None
                        if bpMapping["SalesforceAccount"] == CL_SalesforceAccountObjects.SF_OPPORTUNITY_PARTNER_ACC_BILL_TO:
                            sfRole = SFROLES.SF_BILL_TO
                        elif bpMapping["SalesforceAccount"] == CL_SalesforceAccountObjects.SF_OPPORTUNITY_PARTNER_ACC_SHIP_TO:
                            sfRole = SFROLES.SF_SHIP_TO
                        elif bpMapping["SalesforceAccount"] == CL_SalesforceAccountObjects.SF_OPPORTUNITY_PARTNER_ACC_END_USER:
                            sfRole = SFROLES.SF_END_USER
                        # Check if partner is already assigned. Create Partner if it is not already assigned
                        if not next((resp for resp in oppPartnerRolesResponse["body"]["records"]if resp["Role"] == sfRole and resp["AccountToId"] == businessPartnerId), None):
                            records += self.build_opportunitypartners_sobjectcollection_create_record(opportunityId, bpMapping["CpqPartnerFunction"], bpMapping["SalesforceAccount"])
                else:
                    records += self.build_opportunitypartners_sobjectcollection_create_record(opportunityId, bpMapping["CpqPartnerFunction"], bpMapping["SalesforceAccount"])
        return records

    ###############################################################################################
    # Function to build composite request to Get Opportunity Account Partner Role
    ###############################################################################################
    def build_cr_get_opp_acc_partner_role(self, opportunityAccountId, referenceId):
        compositeRequest = None
        condition = "AccountToId='{opportunityAccountId}'".format(opportunityAccountId=str(opportunityAccountId))
        soql = self.build_soql_query(selectedFields="AccountFromId",
                                        table="Partner",
                                        condition=condition)
        compositeRequest = self.build_soql_query_composite_payload(soql, referenceId)
        return compositeRequest

    ###############################################################################################
    # Function to build composite payload to create Opportunity Account Partner Role
    ###############################################################################################
    def build_cp_create_update_opp_acc_partner_role(self, bearerToken, opportunityResponse):
        compositePayload = list()
        businessPartnerMappings = CL_OutboundBusinessPartnerMapping().outboundPartnerMappings
        # Get Opportunity Account Id
        opportunityAccountId = str(opportunityResponse["body"]["AccountId"])
        if opportunityAccountId != "":
            for bpMapping in businessPartnerMappings:
                if bpMapping["SalesforceAccount"] == CL_SalesforceAccountObjects.SF_OPPORTUNITY_ACC_PARTNER_ROLE_ACC:
                    referenceId = REF.OPP_PARTNER_ROLE_ACC_REFID.format(partnerFunction=str(bpMapping["CpqPartnerFunction"]))
                    compositeRequest = self.build_cr_get_opp_acc_partner_role(opportunityAccountId, referenceId)
                    compositePayload.append(compositeRequest)
            if compositePayload:
                # Call SOQL
                response = self.post_composite_request(bearerToken, compositePayload, INT_REF.REF_GET_OPP_ACC_PARTNER_ROLE_ACC)
                if response:
                    compositePayload = list()
                    url = API.SOBJECT_API.format(sObject=str(CL_SalesforceIntegrationParams.SF_PARTNER))
                    # Assign Opportunity Account Partner
                    for bpMapping in businessPartnerMappings:
                        referenceId = REF.OPP_PARTNER_ROLE_ACC_REFID.format(partnerFunction=str(bpMapping["CpqPartnerFunction"]))
                        oppAccResponse = next((resp for resp in response["compositeResponse"] if resp["referenceId"] == referenceId), None)
                        if oppAccResponse:
                            # Get Business Partner CRM Id
                            businessPartnerId = self.get_business_partner_id(bpMapping["CpqPartnerFunction"])
                            if businessPartnerId:
                                # Chect if Opportunity Account Partner is already assigned
                                if not next((account for account in oppAccResponse["body"]["records"] if account["AccountFromId"] == businessPartnerId), None):
                                    record = dict()
                                    record["AccountToId"] = opportunityAccountId
                                    record["AccountFromId"] = businessPartnerId
                                    compositeRequest = self.build_cr_sobject_request(url, API.POST, record, referenceId)
                                    compositePayload.append(compositeRequest)
                    if compositePayload:
                        return compositePayload
        return None

    ###############################################################################################
    # Function to get Account and Contact Information from Salesforce
    ###############################################################################################
    def get_customer_details(self, bearerToken, class_contact_modules, opportunityId, opportunityResponse, opportunityPartnersResp):
        response = None
        compositePayload = list()

        # Accounts
        businessPartnerMappings = CL_InboundBusinessPartnerMapping().inboundPartnerMappings
        for bpMapping in businessPartnerMappings:
            if bpMapping["SalesforceAccount"]:
                accountId = self.get_opportunity_customers_accountid(bearerToken, bpMapping["SalesforceAccount"], opportunityResponse, opportunityPartnersResp)
                if accountId:
                    # Account
                    compositeRequest = self.build_cr_sobject_get_account(accountId, bpMapping["CpqPartnerFunction"])
                    compositePayload.append(compositeRequest)

        # Contacts
        contactMappings = CL_InboundContactMapping().inboundContactMappings
        for contactMapping in contactMappings:
            referenceContactId = REF.BP_CONTACT_ID_REFID.format(partnerFunction=str(contactMapping["CpqPartnerFunction"]))
            referenceContact = REF.BP_CONTACT.format(partnerFunction=str(contactMapping["CpqPartnerFunction"]))
            # Get Contact Id
            compositePayload = class_contact_modules.get_contact_composite_payload(compositePayload, contactMapping["SalesforceContact"], opportunityId, opportunityResponse, referenceContactId)
            # Get Contact Details
            ## SAP appending InvolvedParty types at the end of this list()
            if (contactMapping["SalesforceContact"] in [
                    CL_SalesforceContactObjects.SF_OPPORTUNITY_FIRST_ROLE,
                    CL_SalesforceContactObjects.SF_OPPORTUNITY_BILL_TO_ROLE,
                    CL_SalesforceContactObjects.SF_OPPORTUNITY_SHIP_TO_ROLE,
                    CL_SalesforceContactObjects.SF_OPPORTUNITY_PRIMARY_ROLE,
                    CL_SalesforceContactObjects.SF_OPPORTUNIY_ACC_BILL_TO_ROLE,
                    CL_SalesforceContactObjects.SF_OPPORTUNITY_ACC_SHIP_TO_ROLE,
                    CL_SalesforceContactObjects.SF_OPPORTUNIY_ACC_PRIMARY_CONTACT,
                    CL_SalesforceContactObjects.OpportunityPrimaryContact,
                    CL_SalesforceContactObjects.OpportunitySWC,
                    CL_SalesforceContactObjects.OpportunityIC,
                    CL_SalesforceContactObjects.OpportunityRC
                    ]
                    ):
                compositeRequest = class_contact_modules.build_cr_sobject_get_contact("@{"+referenceContactId+".records[0].ContactId}", referenceContact)
            else:
                compositeRequest = class_contact_modules.build_cr_sobject_get_contact("@{"+referenceContactId+".records[0].Id}", referenceContact)
            if compositeRequest:
                compositePayload.append(compositeRequest)
        if compositePayload:
            response = self.post_composite_request(bearerToken, compositePayload, INT_REF.REF_GET_ACC)
        return response

    ###############################################################################################
    # Function to get Business Partner from the CPQ database based on the look up mapping
    ###############################################################################################
    def get_business_partner_by_look_up(self, crmAccountId):
        businessPartner = None
        # Get Look Ups
        crmIdMapping = CL_CrmIdBusinessPartnerMapping().crmIdMapping
        if crmIdMapping:
            # Build look up condition
            condition = "{cpqField}='{salesforceFieldValue}'".format(cpqField=str(crmIdMapping["CpqField"]), salesforceFieldValue=str(crmAccountId))
            sql = """SELECT * 
            FROM sys_BusinessPartners
            WHERE {condition}""".format(condition=str(condition))
            record = SqlHelper.GetFirst(sql)
            if record:
                businessPartner = self.BusinessPartnerRepository.GetById(record.Id)
        return businessPartner

    ###############################################################################################
    # Function to compare Salesforce and Cpq Business Partner
    ###############################################################################################
    def is_sf_cpq_partner_the_same(self, quoteBusinessPartner, crmAccountId):
        same = True
        # Compare look up values between CPQ and Salesforce
        businessPartnerId = self.get_business_partner_id(None, quoteBusinessPartner)
        if businessPartnerId != crmAccountId:
            same = False
        return same

    ###############################################################################################
    # Function to process Accounts and Contacts Information from Salesforce
    ###############################################################################################
    def process_customers_contacts(self, response, event):
        # Process Customers and Contacts
        for mapping in [{"Object": "Account", "Mappings": CL_InboundBusinessPartnerMapping().inboundPartnerMappings, "SalesforceMapping": "SalesforceAccount"},
                        {"Object": "Contact", "Mappings": CL_InboundContactMapping().inboundContactMappings, "SalesforceMapping": "SalesforceContact"}]:
            businessPartnerMappings = mapping["Mappings"]
            salesforceMapping = mapping["SalesforceMapping"]
            for bpMapping in businessPartnerMappings:
                if bpMapping[salesforceMapping]:
                    # Get Reference to retreive Account/Contact Details
                    if mapping["Object"] == "Account":
                        reference = bpMapping["CpqPartnerFunction"]
                    elif mapping["Object"] == "Contact":
                        reference = REF.BP_CONTACT.format(partnerFunction=str(bpMapping["CpqPartnerFunction"]))
                    # Get Account/Contact Details
                    compositeResponse = next((resp for resp in response["compositeResponse"] if str(resp["referenceId"]) == reference and resp["httpStatusCode"] == 200), None)
                    # Check if Partner Function already on Quote
                    quoteBusinessPartner = get_quote_business_partner(self.Quote, bpMapping["CpqPartnerFunction"])
                    if compositeResponse:
                        # Add Business Partner Flag
                        addBusinessPartner = False
                        if quoteBusinessPartner:
                            # Check if BP is the same as the one on Salesforce
                            if not self.is_sf_cpq_partner_the_same(quoteBusinessPartner, str(compositeResponse["body"]["Id"])):
                                # Remove BP from Quote
                                del_quote_business_partner_by_function(self.Quote, bpMapping["CpqPartnerFunction"])
                                addBusinessPartner = True
                        else:
                            addBusinessPartner = True
                        # Add Business Partner
                        if addBusinessPartner:
                            # Check if BP exists in CPQ database
                            #businessPartner = self.get_business_partner_by_look_up(str(compositeResponse["body"]["Id"]))
                            ## SAP updated to pull correct CF for ECC DEBMAS look up
                            businessPartner = self.get_business_partner_by_look_up(str(compositeResponse["body"]["SAP_CustID__c"]))
                            # Assign BP if it exists
                            if businessPartner:
                                # Assign BP to Quote
                                quoteBusinessPartner = self.Quote.AddInvolvedParty(bpMapping["CpqPartnerFunction"], businessPartner.Id)
                            # Create local BP if it doesn't exist
                            else:
                                quoteBusinessPartner = self.Quote.AddInvolvedParty(bpMapping["CpqPartnerFunction"], "temp", str())
                                # Set CRM Guid
                                self.set_business_partner_id(None, str(compositeResponse["body"]["Id"]), quoteBusinessPartner)
                        # Apply mappings
                        if quoteBusinessPartner: 
                            if mapping["Object"] == "Account":
                                if event == EVENT_CREATE:
                                    quoteBusinessPartner = CL_InboundBusinessPartnerMapping().on_quote_create_mapping(bpMapping["CpqPartnerFunction"], quoteBusinessPartner, compositeResponse["body"])
                                elif event == EVENT_UPDATE:
                                    quoteBusinessPartner = CL_InboundBusinessPartnerMapping().on_quote_update_mapping(bpMapping["CpqPartnerFunction"], quoteBusinessPartner, compositeResponse["body"])
                                quoteBusinessPartner = CL_InboundBusinessPartnerMapping().on_quote_createupdate_mapping(bpMapping["CpqPartnerFunction"], quoteBusinessPartner, compositeResponse["body"])
                            elif mapping["Object"] == "Contact":
                                if event == EVENT_CREATE:
                                    quoteBusinessPartner = CL_InboundContactMapping().on_quote_create_contact_mapping(bpMapping["CpqPartnerFunction"], quoteBusinessPartner, compositeResponse["body"])
                                elif event == EVENT_UPDATE:
                                    quoteBusinessPartner = CL_InboundContactMapping().on_quote_update_contact_mapping(bpMapping["CpqPartnerFunction"], quoteBusinessPartner, compositeResponse["body"])
                                quoteBusinessPartner = CL_InboundContactMapping().on_quote_createupdate_contact_mapping(bpMapping["CpqPartnerFunction"], quoteBusinessPartner, compositeResponse["body"])
                    # Remove Business Partner from Quote
                    else:
                        if quoteBusinessPartner:
                            self.Quote.DeleteInvolvedParty(quoteBusinessPartner.Id)


    ###############################################################################################
    # Function to create/update Accounts on Salesforce
    ###############################################################################################   
    def create_update_accounts(self, bearerToken):
        # Create/Update Accounts
        compositePayload = self.get_create_update_account_composite_payload(EVENT_UPDATE)
        if compositePayload:
            # Call REST API
            createdAccounts = self.post_composite_request(bearerToken, compositePayload, INT_REF.REF_CREATE_ACCOUNTS)
            customerMappings = CL_OutboundBusinessPartnerMapping().outboundPartnerMappings
            for mapping in customerMappings:
                custResp = next((resp for resp in createdAccounts["compositeResponse"] if float(resp["httpStatusCode"]) in [200,201] and resp["referenceId"] == REF.CREATE_BP_ACC.format(partnerFunction=str(mapping["CpqPartnerFunction"])) ), None)
                if custResp:
                    self.set_business_partner_id(mapping["CpqPartnerFunction"], str(custResp["body"]["id"]))