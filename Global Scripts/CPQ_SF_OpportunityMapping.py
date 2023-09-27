from CPQ_SF_FunctionModules import strip_html_tags


###############################################################################################
# OUTBOUND (CPQ -> Salesforce)
###############################################################################################
###############################################################################################
# Function for Opportunity integration mapping
###############################################################################################
def on_opp_create_outbound_opportunity_integration_mapping(Quote):
    opportunity = dict()

    return opportunity


###############################################################################################
# Function for Opportunity integration mapping
###############################################################################################
def on_opp_update_outbound_opportunity_integration_mapping(Quote):
    opportunity = dict()

    # opportunity["Quote_Type__c"] = Quote.GetCustomField("ZQT_QuoteType").Value

    return opportunity


###############################################################################################
# Function for Opportunity integration mapping
###############################################################################################
def on_opp_createupdate_outbound_opportunity_integration_mapping(Quote):
    opportunity = dict()

    return opportunity

###############################################################################################
# INBOUND (Salesforce -> CPQ)
###############################################################################################
###############################################################################################
# Function for Opportunity integration mapping
###############################################################################################
def on_quote_create_inbound_opportunity_integration_mapping(Quote, opportunity):

    Quote.GetCustomField("CPQ_SF_OPPORTUNITY_NAME").Value = str(opportunity["Name"])
    Quote.GetCustomField("ZQT_OpportunityID").Value = str(opportunity["Id"])
    Quote.GetCustomField("ZQT_OpportunityName").Value = str(opportunity["Name"])
    Quote.GetCustomField("ZQT_Currency").Value = str(opportunity["CurrencyISOCode"])
    Quote.GetCustomField("ZQT_CRM_Type").Value = "SFDC"
    # pass

###############################################################################################
# Function for Opportunity integration mapping
###############################################################################################
def on_quote_update_inbound_opportunity_integration_mapping(Quote, opportunity):

    pass


###############################################################################################
# Function for Opportunity integration mapping
###############################################################################################
def on_quote_createupdate_inbound_opportunity_integration_mapping(Quote, opportunity):

    Quote.GetCustomField("ZQT_OpportunityStatus").Value = str(opportunity["Stage"])
    Quote.GetCustomField("ZQT_MarketCode").Value = str(opportunity["BT_Market_Code__c"])
    Quote.GetCustomField("ZQT_BusinessUnit").Value = str(opportunity["Business_Unit__c"])
    Quote.GetCustomField("ZQT_TerritoryID").Value = str(opportunity["Territory_Name__c"])
    Quote.GetCustomField("ZQT_TerritoryName").Value = str(opportunity["Territory_Name__c"])
    Quote.GetCustomField("ZQT_DistributionChannel").Value = str(opportunity["Distribution_Channel__c"])
    Quote.GetCustomField("ZQT_Division").Value = str(opportunity["Division__c"])
    Quote.GetCustomField("ZQT_QuoteType").Value = str(opportunity["Quote_Type__c"])
