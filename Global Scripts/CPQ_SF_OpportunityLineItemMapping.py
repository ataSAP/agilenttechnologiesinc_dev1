from CPQ_SF_FunctionModules import strip_html_tags


###############################################################################################
# Function for Oppportunity Line Item Mapping
###############################################################################################
def opplineitem_integration_mapping(Quote, cpqItem):
    salesforceLineItem = dict()

    salesforceLineItem["Description"] = cpqItem.Description
    salesforceLineItem["Quantity"] = cpqItem.Quantity
    salesforceLineItem["UnitPrice"] = cpqItem.ListPrice

    return salesforceLineItem


###############################################################################################
# Function for Product Master Mapping
###############################################################################################
def product_integration_mapping(Quote, cpqItem):
    salesforceLineItem = dict()

    salesforceLineItem["Name"] = cpqItem.PartNumber
    #salesforceLineItem["CurrencyIsoCode"] = Quote.SelectedMarket.CurrencyCode

    return salesforceLineItem

###############################################################################################
# Function for Product lookup Salesforce
###############################################################################################
def get_product_lookups(Quote, cpqItem):
    productlookUps = list()

    lookUp = dict()
    lookUp["SalesforceField"] = "Name"
    lookUp["CpqLookUpValue"] = cpqItem.PartNumber
    productlookUps.append(lookUp)

    return productlookUps