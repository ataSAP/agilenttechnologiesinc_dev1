from CPQ_SF_IntegrationSettings import CL_SalesforceAccountObjects
from CPQ_SF_FunctionModules import strip_html_tags, get_country_code_from_abrev3


###############################################################################################
# Class CL_InboundBusinessPartnerMapping:
#       Class to store Business Partner mapping for Salesforce -> CPQ (Quote Creation/Update from CRM)
###############################################################################################
class CL_InboundBusinessPartnerMapping:

    inboundPartnerMappings = list()

    mapping = dict()
    mapping["CpqPartnerFunction"] = "SP"
    mapping["SalesforceAccount"] = CL_SalesforceAccountObjects.OpportunitySP
    inboundPartnerMappings.append(mapping)

    mapping = dict()
    mapping["CpqPartnerFunction"] = "SH"
    mapping["SalesforceAccount"] = CL_SalesforceAccountObjects.OpportunitySH
    inboundPartnerMappings.append(mapping)

    mapping = dict()
    mapping["CpqPartnerFunction"] = "UEU"
    mapping["SalesforceAccount"] = CL_SalesforceAccountObjects.OpportunityUEU
    inboundPartnerMappings.append(mapping)

    mapping = dict()
    mapping["CpqPartnerFunction"] = "PRO"
    mapping["SalesforceAccount"] = CL_SalesforceAccountObjects.OpportunityPRO
    inboundPartnerMappings.append(mapping)

    mapping = dict()
    mapping["CpqPartnerFunction"] = "RE"
    mapping["SalesforceAccount"] = CL_SalesforceAccountObjects.OpportunityRE
    inboundPartnerMappings.append(mapping)

    # mapping = dict()
    # mapping["CpqPartnerFunction"] = "BP"
    # mapping["SalesforceAccount"] = CL_SalesforceAccountObjects.SF_OPPORTUNITY_PARTNER_ACC_BILL_TO
    # inboundPartnerMappings.append(mapping)

###############################################################################################
# Function for Business Partner mappings on Quote Create (Salesforce -> CPQ)
###############################################################################################
    def on_quote_create_mapping(self, cpqPartnerFunction, cpqBusinessPartner, salesforceCustomer):
        return cpqBusinessPartner

###############################################################################################
# Function for Business Partner mappings on Quote Update (Salesforce -> CPQ)
###############################################################################################
    def on_quote_update_mapping(self, cpqPartnerFunction, cpqBusinessPartner, salesforceCustomer):
        return cpqBusinessPartner

###############################################################################################
# Function for Business Partner mappings on Quote Create & Update (Salesforce -> CPQ)
###############################################################################################
    def on_quote_createupdate_mapping(self, cpqPartnerFunction, cpqBusinessPartner, salesforceCustomer):

        # if cpqPartnerFunction == "SP" or cpqPartnerFunction == "BP" or cpqPartnerFunction == "SH":
        #     cpqBusinessPartner.Name = str(salesforceCustomer["Name"])
        #     cpqBusinessPartner.CityName = str(salesforceCustomer["BillingCity"])
        #     if str(salesforceCustomer["BillingStreet"]) != "None":
        #         cpqBusinessPartner.AddressName = str(salesforceCustomer["BillingStreet"])
        #     else:
        #         cpqBusinessPartner.AddressName = str()
        #     # Set country using get_country_code_from_abrev3()
        #     cpqBusinessPartner.Country = get_country_code_from_abrev3(str(salesforceCustomer["BillingCountry"]))
        #     cpqBusinessPartner.PostalCode = str(salesforceCustomer["BillingPostalCode"])
        return cpqBusinessPartner


###############################################################################################
# Class CL_OutboundBusinessPartnerMapping:
#       Class to store Business partner mapping for CPQ -> Salesforce (Opportunity Creation/Update from CRM)
###############################################################################################
class CL_OutboundBusinessPartnerMapping:

    outboundPartnerMappings = list()

    # mapping = dict()
    # mapping["CpqPartnerFunction"] = "SP"
    # mapping["SalesforceAccount"] = CL_SalesforceAccountObjects.SF_OPPORTUNITY_ACC
    # outboundPartnerMappings.append(mapping)
    
    # mapping = dict()
    # mapping["CpqPartnerFunction"] = "BP"
    # mapping["SalesforceAccount"] = CL_SalesforceAccountObjects.SF_OPPORTUNITY_PARTNER_ACC_BILL_TO
    # outboundPartnerMappings.append(mapping)
    
    # mapping = dict()
    # mapping["CpqPartnerFunction"] = "SH"
    # mapping["SalesforceAccount"] = CL_SalesforceAccountObjects.SF_OPPORTUNITY_PARTNER_ACC_SHIP_TO
    # outboundPartnerMappings.append(mapping)

###############################################################################################
# Function for Business Partner mappings on Quote Create (CPQ -> Salesforce)
###############################################################################################
    def on_opportunity_create_mapping(self, cpqPartnerFunction, Quote, cpqBusinessPartner):
        salesforceCustomer = dict()

        return salesforceCustomer

###############################################################################################
# Function for Business Partner mappings on Quote Update (CPQ -> Salesforce)
###############################################################################################
    def on_opportunity_update_mapping(self, cpqPartnerFunction, Quote, cpqBusinessPartner):
        salesforceCustomer = dict()

        return salesforceCustomer

###############################################################################################
# Function for Business Partner mappings on Quote Create & Update (CPQ -> Salesforce)
###############################################################################################
    def on_opportunity_createupdate_mapping(self, cpqPartnerFunction, Quote, cpqBusinessPartner):
        salesforceCustomer = dict()

        # if cpqPartnerFunction == "SP" or cpqPartnerFunction == "BP" or cpqPartnerFunction == "SH":
        #     salesforceCustomer["Name"] = cpqBusinessPartner.Name
        #     salesforceCustomer["BillingStreet"] = cpqBusinessPartner.AddressName
        #     salesforceCustomer["CurrencyIsoCode"] = Quote.SelectedMarket.CurrencyCode

        return salesforceCustomer
