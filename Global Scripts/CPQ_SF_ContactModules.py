## CPQ_SF_ContactModules

from CPQ_SF_IntegrationModules import CL_SalesforceIntegrationModules
from CPQ_SF_ContactMapping import CL_OutboundContactMapping
from CPQ_SF_IntegrationReferences import CL_SalesforceApis as API, CL_CompositeRequestReferences as REF, CL_SalesforceCustomerRoles as SFROLES, CL_IntegrationReferences as INT_REF
from CPQ_SF_IntegrationSettings import CL_SalesforceContactObjects, CL_SalesforceIntegrationParams
from CPQ_SF_CpqHelper import EVENT_CREATE, EVENT_UPDATE
from CPQ_SF_FunctionModules import get_quote_business_partner


###############################################################################################
# Class CL_ContactIntegrationModules:
#       Class to store integration functions related to contacts
###############################################################################################
class CL_ContactIntegrationModules(CL_SalesforceIntegrationModules):
    ###############################################################################################
    # Function to get the compositeRequest of a GET Contact request
    ###############################################################################################
    def build_cr_sobject_get_contact(self, contactId, cpqRoleContact):
        url = API.CR_GET_CONTACT_API.format(contactId=str(contactId))
        compositeRequest = self.build_cr_sobject_request(url, API.GET, None, cpqRoleContact)
        return compositeRequest

    ###############################################################################################
    # Function to get the compositeRequest of a PATCH Contact request
    ###############################################################################################
    def build_cr_sobject_patch_contact(self, contactId, cpqRoleContact, record):
        url = API.CR_GET_CONTACT_API.format(contactId=str(contactId))
        compositeRequest = self.build_cr_sobject_request(url, API.PATCH, record, cpqRoleContact)
        return compositeRequest

    ###############################################################################################
    # Function to get the compositeRequest to GET Opportunity Contacts
    ###############################################################################################
    def build_cr_sobject_get_opportunity_contacts(self, opportunityId):
        url = API.CR_GET_OPP_CONTACTS_API.format(opportunityId=str(opportunityId))
        compositeRequest = self.build_cr_sobject_request(url, API.GET, None, REF.GET_OPP_CONTACTS_REFID)
        return compositeRequest

    ###############################################################################################
    # Function to build Create Contact sObject POST API body
    ###############################################################################################
    def build_contact_sobject_create_record(self, partnerFunction, event):
        body = dict()
        # Build records with values to send to Salesforce
        businessPartner = get_quote_business_partner(self.Quote, partnerFunction)
        if businessPartner:
            if event == EVENT_CREATE:
                body = CL_OutboundContactMapping().on_opportunity_create_contact_mapping(self.Quote, businessPartner)
            elif event == EVENT_UPDATE:
                body = CL_OutboundContactMapping().on_opportunity_update_contact_mapping(self.Quote, businessPartner)
            body.update(CL_OutboundContactMapping().on_opportunity_createupdate_contact_mapping(self.Quote, businessPartner))
        return body

    ###############################################################################################
    # Function to get create/update Contact Composite Payload
    ###############################################################################################
    def get_create_update_contact_composite_payload(self, event):
        compositePayload = list()
        contactMappings = CL_OutboundContactMapping().outboundContactMappings
        for contactMapping in contactMappings:
            if contactMapping["SalesforceContact"]:
                businessPartner = get_quote_business_partner(self.Quote, contactMapping["CpqPartnerFunction"])
                if businessPartner:
                    # Get Business Partner Look up id
                    bpLookUpId = self.get_business_partner_id(contactMapping["CpqPartnerFunction"], businessPartner)
                    # Create contact
                    if not bpLookUpId:
                        customerRecord = self.build_contact_sobject_create_record(contactMapping["CpqPartnerFunction"], event)
                        compositeRequest = self.get_sobject_post_payload_header(CL_SalesforceIntegrationParams.SF_CONTACT_OBJECT, REF.CREATE_BP_CONTACT.format(partnerFunction=str(contactMapping["CpqPartnerFunction"])))
                        compositeRequest["body"] = customerRecord
                        compositePayload.append(compositeRequest)
                    # Update contact
                    elif bpLookUpId:
                        customerRecord = self.build_contact_sobject_create_record(contactMapping["CpqPartnerFunction"], event)
                        compositeRequest = self.build_cr_sobject_patch_contact(bpLookUpId, REF.UPDATE_BP_CONTACT.format(partnerFunction=str(contactMapping["CpqPartnerFunction"])), customerRecord)
                        compositePayload.append(compositeRequest)

        return compositePayload

    ###############################################################################################
    # Function to get Contact Composite Payload
    ###############################################################################################
    def get_contact_composite_payload(self, compositePayload, contactType, opportunityId, opportunityResponse, referenceId):
        # OpportunityAccountFirstContact
        if contactType == CL_SalesforceContactObjects.SF_OPPORTUNITY_ACC_FIRST_CONTACT:
            if str(opportunityResponse["body"]["AccountId"]):
                condition = "AccountId='{oppAccountId}'".format(oppAccountId=str(str(opportunityResponse["body"]["AccountId"])))
                soql = self.build_soql_query("Id", "Contact", condition)
                compositeRequest = self.build_soql_query_composite_payload(soql, referenceId)
                compositePayload.append(compositeRequest)
        # OpportunityFirstRole
        elif contactType == CL_SalesforceContactObjects.SF_OPPORTUNITY_FIRST_ROLE:
            condition = "OpportunityId='{opportunityId}'".format(opportunityId=str(opportunityId))
            soql = self.build_soql_query("ContactId", "OpportunityContactRole", condition)
            compositeRequest = self.build_soql_query_composite_payload(soql, referenceId)
            compositePayload.append(compositeRequest)
        # OpportunityBillToRole
        elif contactType == CL_SalesforceContactObjects.SF_OPPORTUNITY_BILL_TO_ROLE:
            condition = "OpportunityId='{opportunityId}' AND Role='Bill To'".format(opportunityId=str(opportunityId))
            soql = self.build_soql_query("ContactId", "OpportunityContactRole", condition)
            compositeRequest = self.build_soql_query_composite_payload(soql, referenceId)
            compositePayload.append(compositeRequest)
        # OpportunityShipToRole
        elif contactType == CL_SalesforceContactObjects.SF_OPPORTUNITY_SHIP_TO_ROLE:
            condition = "OpportunityId='{opportunityId}' AND Role = 'Ship To'".format(opportunityId=str(opportunityId))
            soql = self.build_soql_query("ContactId", "OpportunityContactRole", condition)
            compositeRequest = self.build_soql_query_composite_payload(soql, referenceId)
            compositePayload.append(compositeRequest)
        # OpportunityPrimaryRole
        elif contactType == CL_SalesforceContactObjects.SF_OPPORTUNITY_PRIMARY_ROLE:
            condition = "OpportunityId='{opportunityId}' AND IsPrimary=true".format(opportunityId=str(opportunityId))
            soql = self.build_soql_query("ContactId", "OpportunityContactRole", condition)
            compositeRequest = self.build_soql_query_composite_payload(soql, referenceId)
            compositePayload.append(compositeRequest)
        # OpportunityAccountBillToRole
        elif contactType == CL_SalesforceContactObjects.SF_OPPORTUNIY_ACC_BILL_TO_ROLE:
            if str(opportunityResponse["body"]["AccountId"]) != "":
                condition = "AccountId='{oppAccountId}' AND Role='Bill To'".format(oppAccountId=str(str(opportunityResponse["body"]["AccountId"])))
                soql = self.build_soql_query("ContactId", "AccountContactRole", condition)
                compositeRequest = self.build_soql_query_composite_payload(soql, referenceId)
                compositePayload.append(compositeRequest)
        # OpportunityAccountShipToRole
        elif contactType == CL_SalesforceContactObjects.SF_OPPORTUNITY_ACC_SHIP_TO_ROLE:
            if str(opportunityResponse["body"]["AccountId"]) != "":
                condition = "AccountId='{oppAccountId}' AND Role='Ship To'".format(oppAccountId=str(str(opportunityResponse["body"]["AccountId"])))
                soql = self.build_soql_query("ContactId", "AccountContactRole", condition)
                compositeRequest = self.build_soql_query_composite_payload(soql, referenceId)
                compositePayload.append(compositeRequest)
        # OpportunityAccountPrimaryContact
        elif contactType == CL_SalesforceContactObjects.SF_OPPORTUNIY_ACC_PRIMARY_CONTACT:
            if str(opportunityResponse["body"]["AccountId"]) != "":
                condition = "AccountId='{oppAccountId}' AND IsPrimary=true'".format(oppAccountId=str(str(opportunityResponse["body"]["AccountId"])))
                soql = self.build_soql_query("ContactId", "AccountContactRole", condition)
                compositeRequest = self.build_soql_query_composite_payload(soql, referenceId)
                compositePayload.append(compositeRequest)
        # OpportunityPartnerAccountFirstContact
        elif contactType == CL_SalesforceContactObjects.SF_OPPORTUNITY_PARTNER_ACC_FIRST_CONTACT:
            if str(opportunityResponse["body"]["AccountId"]) != "":
                # Get Opportunity Partner Account
                condition = "OpportunityId='{opportunityId}' AND AccountToId !='{oppAccountId}'".format(opportunityId=str(opportunityId), oppAccountId=str(str(opportunityResponse["body"]["AccountId"])))
                soql = self.build_soql_query("AccountToId", "Partner", condition)
                compositeRequest = self.build_soql_query_composite_payload(soql, REF.GET_OPP_PARTNER_ACC)
                compositePayload.append(compositeRequest)
                # Get Contact
                condition = "AccountId='@{"+REF.GET_OPP_PARTNER_ACC+".records[0].AccountToId}'"
                soql = self.build_soql_query("Id", "Contact", condition)
                compositeRequest = self.build_soql_query_composite_payload(soql, referenceId)
                compositePayload.append(compositeRequest)
        # OpportunityPartnerRoleAccountPrimaryContact
        elif contactType == CL_SalesforceContactObjects.SF_OPPORTUNITY_PARTNER_ROLE_ACC_PRIMARY_CONTACT:
            if str(opportunityResponse["body"]["AccountId"]) != "":
                # Get Opportunity Partner Account
                condition = "OpportunityId='{opportunityId}' AND AccountToId !='{oppAccountId}'".format(opportunityId=str(opportunityId), oppAccountId=str(str(opportunityResponse["body"]["AccountId"])))
                soql = self.build_soql_query("AccountToId", "Partner", condition)
                compositeRequest = self.build_soql_query_composite_payload(soql, REF.GET_OPP_PARTNER_ACC)
                compositePayload.append(compositeRequest)
                # Get Contact
                condition = "AccountId='@{"+REF.GET_OPP_PARTNER_ACC+".records[0].AccountToId}' AND IsPrimary=true"
                soql = self.build_soql_query("Id", "Contact", condition)
                compositeRequest = self.build_soql_query_composite_payload(soql, referenceId)
                compositePayload.append(compositeRequest)
        ## Start of SAP listed contacts
        ## OpportunityPrimaryContact
        elif contactType == CL_SalesforceContactObjects.OpportunityPrimaryContact:
            condition = "opportunityid='{opportunityId}' AND role = 'Primary Contact'".format(opportunityId=opportunityId)
            soql = self.build_soql_query("ContactId", "OpportunityContactRole", condition)
            compositeRequest = self.build_soql_query_composite_payload(soql, referenceId)
            compositePayload.append(compositeRequest)
        ## OpportunitySWC
        elif contactType == CL_SalesforceContactObjects.OpportunitySWC:
            condition = "opportunityid='{opportunityId}' AND role = 'SW Install'".format(opportunityId=opportunityId)
            soql = self.build_soql_query("ContactId", "OpportunityContactRole", condition)
            compositeRequest = self.build_soql_query_composite_payload(soql, referenceId)
            compositePayload.append(compositeRequest)
        ## OpportunityIC
        elif contactType == CL_SalesforceContactObjects.OpportunityIC:
            condition = "opportunityid='{opportunityId}' AND role = 'Install Contact'".format(opportunityId=opportunityId)
            soql = self.build_soql_query("ContactId", "OpportunityContactRole", condition)
            compositeRequest = self.build_soql_query_composite_payload(soql, referenceId)
            compositePayload.append(compositeRequest)
        ## OpportunityRC
        elif contactType == CL_SalesforceContactObjects.OpportunityRC:
            condition = "opportunityid='{opportunityId}' AND role = 'Reseller Contact'".format(opportunityId=opportunityId)
            soql = self.build_soql_query("ContactId", "OpportunityContactRole", condition)
            compositeRequest = self.build_soql_query_composite_payload(soql, referenceId)
            compositePayload.append(compositeRequest)
        return compositePayload

    ###############################################################################################
    # Functions to build composite payload to assign contacts
    ###############################################################################################
    def build_composite_payload_assign_contacts(self, opportunityId, recordType, partnerFunction, compositePayload, businessPartnerId):
        # Get reference
        referenceId = REF.ASSIGN_BP_CONTACT_REFID.format(partnerFunction=str(partnerFunction))
        # Build payload
        if businessPartnerId:
            # Get Opportunity to get AccountId
            if (recordType == CL_SalesforceContactObjects.SF_OPPORTUNITY_ACC_FIRST_CONTACT
                or recordType == CL_SalesforceContactObjects.SF_OPPORTUNIY_ACC_BILL_TO_ROLE
                or recordType == CL_SalesforceContactObjects.SF_OPPORTUNITY_ACC_SHIP_TO_ROLE
                or recordType == CL_SalesforceContactObjects.SF_OPPORTUNIY_ACC_PRIMARY_CONTACT):
                if next((req for req in compositePayload if req["referenceId"] == CL_SalesforceIntegrationParams.SF_OPPORTUNITY_OBJECT), None) is None:
                    compositeRequest = self.build_cr_sobject_get_opportunity(opportunityId)
                    compositePayload.append(compositeRequest)
            # AccountId field variable
            refAccIdField = ".AccountId}"
            # OpportunityAccountFirstContact
            if recordType == CL_SalesforceContactObjects.SF_OPPORTUNITY_ACC_FIRST_CONTACT:
                # Update Contact assignment
                url = API.CR_GET_CONTACT_API.format(contactId=str(businessPartnerId))
                record = dict()
                record["AccountId"] = "@{"+CL_SalesforceIntegrationParams.SF_OPPORTUNITY_OBJECT + refAccIdField
                compositeRequest = self.build_cr_sobject_request(url, API.PATCH, record, referenceId)
                compositePayload.append(compositeRequest)
            # OpportunityFirstRole
            elif recordType == CL_SalesforceContactObjects.SF_OPPORTUNITY_FIRST_ROLE:
                # Update Contact assignment
                record = dict()
                record["OpportunityId"] = opportunityId
                record["ContactId"] = businessPartnerId
                compositeRequest = self.get_sobject_post_payload_header(CL_SalesforceIntegrationParams.SF_OPPORTUNITY_CONTACT_OBJECT, referenceId)
                compositeRequest["body"] = record
                compositePayload.append(compositeRequest)
            # OpportunityBillToRole
            elif recordType == CL_SalesforceContactObjects.SF_OPPORTUNITY_BILL_TO_ROLE:
                # Update Contact assignment
                record = dict()
                record["OpportunityId"] = opportunityId
                record["Role"] = SFROLES.SF_BILL_TO
                record["ContactId"] = businessPartnerId
                compositeRequest = self.get_sobject_post_payload_header(CL_SalesforceIntegrationParams.SF_OPPORTUNITY_CONTACT_OBJECT, referenceId)
                compositeRequest["body"] = record
                compositePayload.append(compositeRequest)
            # OpportunityShipToRole
            elif recordType == CL_SalesforceContactObjects.SF_OPPORTUNITY_SHIP_TO_ROLE:
                # Update Contact assignment
                record = dict()
                record["OpportunityId"] = opportunityId
                record["Role"] = SFROLES.SF_SHIP_TO
                record["ContactId"] = businessPartnerId
                compositeRequest = self.get_sobject_post_payload_header(CL_SalesforceIntegrationParams.SF_OPPORTUNITY_CONTACT_OBJECT, referenceId)
                compositeRequest["body"] = record
                compositePayload.append(compositeRequest)
            # OpportunityPrimaryRole
            elif recordType == CL_SalesforceContactObjects.SF_OPPORTUNITY_PRIMARY_ROLE:
                # Update Contact assignment
                record = dict()
                record["OpportunityId"] = opportunityId
                record["ContactId"] = businessPartnerId
                record["IsPrimary"] = True
                compositeRequest = self.get_sobject_post_payload_header(CL_SalesforceIntegrationParams.SF_OPPORTUNITY_CONTACT_OBJECT, referenceId)
                compositeRequest["body"] = record
                compositePayload.append(compositeRequest)
            # OpportunityAccountBillToRole & OpportunityAccountShipToRole
            elif recordType == CL_SalesforceContactObjects.SF_OPPORTUNIY_ACC_BILL_TO_ROLE or recordType == CL_SalesforceContactObjects.SF_OPPORTUNITY_ACC_SHIP_TO_ROLE:
                record = dict()
                # OpportunityAccountBillToRole
                if recordType == CL_SalesforceContactObjects.SF_OPPORTUNIY_ACC_BILL_TO_ROLE:
                    # Update Contact assignment
                    record["Role"] = SFROLES.SF_BILL_TO
                # OpportunityAccountShipToRole
                elif recordType == CL_SalesforceContactObjects.SF_OPPORTUNITY_ACC_SHIP_TO_ROLE:
                    # Update Contact assignment
                    record["Role"] = SFROLES.SF_SHIP_TO
                # Update Contact assignment
                record["AccountId"] = "@{"+CL_SalesforceIntegrationParams.SF_OPPORTUNITY_OBJECT + refAccIdField
                record["ContactId"] = businessPartnerId
                compositeRequest = self.get_sobject_post_payload_header(CL_SalesforceIntegrationParams.SF_ACCOUNT_CONTACT_ROLE, referenceId)
                compositeRequest["body"] = record
                compositePayload.append(compositeRequest)
            # OpportunityAccountPrimaryContact
            elif recordType == CL_SalesforceContactObjects.SF_OPPORTUNIY_ACC_PRIMARY_CONTACT:
                # Update Contact assignment
                record = dict()
                record["AccountId"] = "@{"+CL_SalesforceIntegrationParams.SF_OPPORTUNITY_OBJECT + refAccIdField
                record["ContactId"] = businessPartnerId
                record["IsPrimary"] = True
                compositeRequest = self.get_sobject_post_payload_header(CL_SalesforceIntegrationParams.SF_ACCOUNT_CONTACT_ROLE, referenceId)
                compositeRequest["body"] = record
                compositePayload.append(compositeRequest)
            # OpportunityPartnerAccountFirstContact
            elif recordType == CL_SalesforceContactObjects.SF_OPPORTUNITY_PARTNER_ACC_FIRST_CONTACT:
                # Get Opportunity Partner Account
                compositeRequest = self.build_cr_sobject_get_opportunity_partners(opportunityId)
                compositePayload.append(compositeRequest)
                # Update Contact assignment
                record = dict()
                record["AccountId"] = "@{"+REF.GET_OPP_PARTNERS_REFID+".records[0].AccountToId}"
                url = API.CR_GET_CONTACT_API.format(contactId=str(businessPartnerId))
                compositeRequest = self.build_cr_sobject_request(url, API.PATCH, record, REF.UPDATE_CONTACT)
                compositePayload.append(compositeRequest)
            # OpportunityPartnerRoleAccountPrimaryContact
            elif recordType == CL_SalesforceContactObjects.SF_OPPORTUNITY_PARTNER_ROLE_ACC_PRIMARY_CONTACT:
                # Get Opportunity Partner Account
                compositeRequest = self.build_cr_sobject_get_opportunity_partners(opportunityId)
                compositePayload.append(compositeRequest)
                # Update Contact assignment
                record = dict()
                record["AccountId"] = "@{"+REF.GET_OPP_PARTNERS_REFID+".records[0].AccountToId}"
                record["ContactId"] = businessPartnerId
                record["IsPrimary"] = True
                compositeRequest = self.get_sobject_post_payload_header(CL_SalesforceIntegrationParams.SF_ACCOUNT_CONTACT_ROLE, referenceId)
                compositeRequest["body"] = record
                compositePayload.append(compositeRequest)
            ## Start of SAP listed contacts
            elif recordType in [CL_SalesforceContactObjects.OpportunityPrimaryContact,
                                CL_SalesforceContactObjects.OpportunitySWC,
                                CL_SalesforceContactObjects.OpportunityIC,
                                CL_SalesforceContactObjects.OpportunityRC
                                ]:
                # Update Contact assignment
                record = dict()
                record["OpportunityId"] = opportunityId
                record["ContactId"] = businessPartnerId
                compositeRequest = self.get_sobject_post_payload_header(CL_SalesforceIntegrationParams.SF_OPPORTUNITY_CONTACT_OBJECT, referenceId)
                compositeRequest["body"] = record
                compositePayload.append(compositeRequest)
        return compositePayload
    ###############################################################################################
    # Function to get contact ids from Contacts response
    ###############################################################################################
    def get_contact_ids_from_response(self, contactsResponse, partnerFunction):
        contactIds = list()
        # Get reference
        referenceId = REF.BP_CONTACT_ID_REFID.format(partnerFunction=str(partnerFunction))
        # Get contact Id
        contactsResponse = next((resp["body"]["records"] for resp in contactsResponse["compositeResponse"] if resp["referenceId"]==referenceId and resp["body"]["totalSize"]>0), None)
        if contactsResponse:
            for contact in contactsResponse:
                contactId = None
                for attr in contact:
                    if attr.Name != "attributes":
                        contactId = str(getattr(contact, attr.Name))
                        if contactId:
                            contactIds.append(contactId)
                        break
        return contactIds
    ###############################################################################################
    # Functions to assign Contacts
    ###############################################################################################
    def assign_contacts(self, bearerToken, opportunityId, opportunityResponse):
        response = None
        if opportunityResponse:
            # Check if contacts need to be assigned
            compositePayload = list()
            contactMappings = CL_OutboundContactMapping().outboundContactMappings
            for contactMapping in contactMappings:
                if contactMapping["SalesforceContact"]:
                    referenceId = REF.BP_CONTACT_ID_REFID.format(partnerFunction=str(contactMapping["CpqPartnerFunction"]))
                    # Get Contact Id
                    compositePayload = self.get_contact_composite_payload(compositePayload, contactMapping["SalesforceContact"], opportunityId, opportunityResponse, referenceId)
            
            if compositePayload:
                contactsResponse = self.post_composite_request(bearerToken, compositePayload, INT_REF.REF_GET_CONTACTS)
                if contactsResponse:
                    # Assign Contacts
                    compositePayload = list()
                    for contactMapping in contactMappings:
                        if contactMapping["SalesforceContact"]:
                            businessPartnerId = self.get_business_partner_id(contactMapping["CpqPartnerFunction"])
                            if businessPartnerId:
                                # Get contact Ids
                                contactIds = self.get_contact_ids_from_response(contactsResponse, contactMapping["CpqPartnerFunction"])
                                # Assign Contact if it is different
                                if businessPartnerId not in contactIds:
                                    compositePayload = self.build_composite_payload_assign_contacts(opportunityId, contactMapping["SalesforceContact"], contactMapping["CpqPartnerFunction"], compositePayload, businessPartnerId)
                    # Call API to Assign Contacts
                    if compositePayload:
                        response = self.post_composite_request(bearerToken, compositePayload, INT_REF.REF_ASSIGN_CONTACTS)
        return response

    ###############################################################################################
    # Functions to assign Contacts
    ###############################################################################################
    def create_update_contacts(self, bearerToken):
        compositePayload = self.get_create_update_contact_composite_payload(EVENT_UPDATE)
        if compositePayload:
            # Call REST API
            createdAccountsContacts = self.post_composite_request(bearerToken, compositePayload, INT_REF.REF_CREATE_CONTACTS)
            contactMappings = CL_OutboundContactMapping().outboundContactMappings
            for mapping in contactMappings:
                contactResp = next((resp for resp in createdAccountsContacts["compositeResponse"] if float(resp["httpStatusCode"]) in [200,201] and resp["referenceId"] == REF.CREATE_BP_CONTACT.format(partnerFunction=str(mapping["CpqPartnerFunction"]))), None)
                if contactResp:
                    self.set_business_partner_id(mapping["CpqPartnerFunction"], str(contactResp["body"]["id"]))
