from CPQ_SF_CpqHelper import CL_CpqHelper
from CPQ_SF_FunctionModules import strip_html_tags


###############################################################################################
# Class CL_CustomObjectMapping:
#       Class to store Custom Object Mappings
###############################################################################################
class CL_CustomObjectMapping(CL_CpqHelper):

    ###############################################################################################
    # Function to to store custom object mappings
    ###############################################################################################
    def custom_object_mappings(self):
        mappings = list()

        # mapping = dict()
        # mapping["Name"] = "Opportunity_Decision_Maker"
        # mapping["Type"] = "Contact"
        # # SELECT ContactId FROM OpportunityContactRole WHERE OpportunityId = '<*CTX(SFDC.Opportunity.Id)*>' AND Role = 'Decision Maker'
        # mapping["Query"] = self.build_soql_query(selectedFields="ContactId",
        #                                          table="OpportunityContactRole",
        #                                          condition="OpportunityId='"+self.Quote.GetCustomField("Opportunity_ID").Value+"'AND Role = 'Decision Maker'")
        # mapping["Linked_To_Quote"] = False
        # mapping["Inbound"] = True
        # mapping["Outbound"] = True
        # mapping["Create"] = False
        # mappings.append(mapping)

        return mappings

    #############################
    # INBOUND Salesforce -> CPQ #
    ###############################################################################################
    # Function for Custom Object mappings on Quote Create (Salesforce -> CPQ)
    ###############################################################################################
    def on_quote_create_custom_object_mapping(self, Quote, customObject, customObjectName):
        # if customObjectName == "Opportunity_Decision_Maker":
        #     # Set customObject data => Quote
        #     pass
        pass

    ###############################################################################################
    # Function for Custom Object mappings on Quote Update (Salesforce -> CPQ)
    ###############################################################################################
    def on_quote_update_custom_object_mapping(self, Quote, customObject, customObjectName):
        # if customObjectName == "Opportunity_Decision_Maker":
        #     # Set customObject data => Quote
        #     pass
        pass

    ###############################################################################################
    # Function for Custom Object mappings on Quote Create/Update (Salesforce -> CPQ)
    ###############################################################################################
    def on_quote_createupdate_custom_object_mapping(self, Quote, customObject, customObjectName):
        # if customObjectName == "Opportunity_Decision_Maker":
        #     # Set customObject data => Quote
        #     pass
        pass

    ##############################
    # OUTBOUND CPQ -> Salesforce #
    ###############################################################################################
    # Function for Custom Object mappings on Quote Create (CPQ -> Salesforce)
    ###############################################################################################
    def on_opp_create_custom_object_mapping(self, Quote, customObjectName):
        customObject = dict()
        # if customObjectName == "Opportunity_Decision_Maker":
        #     pass
        return customObject

    ###############################################################################################
    # Function for Custom Object mappings on Quote Update (CPQ -> Salesforce)
    ###############################################################################################
    def on_opp_update_custom_object_mapping(self, Quote, customObjectName):
        customObject = dict()
        # if customObjectName == "Opportunity_Decision_Maker":
        #     pass
        return customObject

    ###############################################################################################
    # Function for Custom Object mappings on Quote Create/Update (CPQ -> Salesforce)
    ###############################################################################################
    def on_opp_createupdate_custom_object_mapping(self, Quote, customObjectName):
        customObject = dict()
        # if customObjectName == "Opportunity_Decision_Maker":
        #     pass
        return customObject