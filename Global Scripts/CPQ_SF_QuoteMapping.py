from CPQ_SF_FunctionModules import strip_html_tags


###############################################################################################
# Function for Quote integration mapping
###############################################################################################
def quote_integration_mapping(Quote):
    def getCFValue(cfName):
        return Quote.GetCustomField(cfName).Value

    salesforceQuote = dict()

    expirationDateStr = getCFValue("Quote Expiration Date")
    if expirationDateStr:
        expirationDate = UserPersonalizationHelper.CovertToDate(expirationDateStr)
        salesforceQuote["VALID_UNITL__c"] = expirationDate
    salesforceQuote["Quote_Type__c"] = getCFValue("ZQT_QuoteType")
    salesforceQuote["Customer_Quote_No__c"] = getCFValue("ZQT_EccQuoteNumber")
    salesforceQuote["TOTAL_PRICE__c"] = round(Quote.Totals.NetPrice, 2)
    salesforceQuote["QUOTE_STATUS__c"] = Quote.StatusName
    salesforceQuote["Quote_Source_System__c"] = "CPQ 2.0"

    return salesforceQuote
