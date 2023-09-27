from CPQ_SF_CpqHelper import CL_CpqHelper
from CPQ_SF_FunctionModules import strip_html_tags

###############################################################################################
# Class CL_CustomObjectLineItemMapping:
#       Class to store Quote Items to Custom Object Mappings
###############################################################################################
class CL_CustomObjectLineItemMapping(CL_CpqHelper):
    mappings = list()
    # mapping = dict()
    # mapping["ObjectType"] = "Asset"
    # mapping["Rank"] = 1
    # mappings.append(mapping)

    ###############################################################################################
    # Function that stores condition on whether line item should be created/updated
    ###############################################################################################
    def custom_object_item_condition(self, Quote, cpqItem, customObjectName):
        condition = False
        # An If condition for each object
        # if customObjectName == "Asset":
        #     # Condition
        #     if cpqItem.ProductTypeName == "Service":
        #         condition = True
        return condition

    ###############################################################################################
    # Function that stores the Look up mapping of the custom objects
    ###############################################################################################
    def custom_object_item_lookups(self, Quote, customObjectName):
        customlookUps = list()

        # if customObjectName == "Asset":
        #     lookUp = dict()
        #     lookUp["SalesforceField"] = "Quote_ID__c"
        #     lookUp["CpqLookUpValue"] = Quote.Id
        #     lookUp["FieldType"] = self.TYPE_FLOAT
        #     customlookUps.append(lookUp)

        #     lookUp = dict()
        #     lookUp["SalesforceField"] = "Owner_ID__c"
        #     lookUp["CpqLookUpValue"] = Quote.OwnerId
        #     lookUp["FieldType"] = self.TYPE_FLOAT
        #     customlookUps.append(lookUp)

        return customlookUps

    ###############################################################################################
    # Function that stores the line item mappings per object
    ###############################################################################################
    def custom_object_item_mapping(self, Quote, cpqItem, customObjectName):
        customObjectLineItem = dict()

        # An If condition for each object
        # if customObjectName == "Asset":
        #     customObjectLineItem["CurrencyIsoCode"] = Quote.SelectedMarket.CurrencyCode

        return customObjectLineItem