from CPQ_SF_Configuration import CL_SalesforceSettings
from CPQ_SF_IntegrationModules import CL_SalesforceIntegrationModules
from CPQ_SF_IntegrationReferences import CL_IntegrationReferences as INT_REF, CL_SalesforceApiLimits as API_LIMIT
from CPQ_SF_CustomObjectLineItemMapping import CL_CustomObjectLineItemMapping


###############################################################################################
# Class CL_CustomObjectLineItemModules:
#       Class to store integration functions related to quote items to custom objects
###############################################################################################
class CL_CustomObjectLineItemModules(CL_SalesforceIntegrationModules, CL_CustomObjectLineItemMapping):

    ###############################################################################################
    # Function process quote items to custom objects mappings (CPQ -> Salesforce)
    ###############################################################################################
    def process_custom_object_line_item_mappings(self, bearerToken):
        # Get Mappings sorted by rank
        mappings = sorted(self.mappings, key=lambda x: x["Rank"])
        headers = self.get_authorization_header(bearerToken)
        # Process for each Custom Object
        for mapping in mappings:
            # Initialize list of quote items to be sent
            quoteItems = [{"item": item, "recordId": ""} for item in self.Quote.GetAllItems()]
            # Remove items that should not be sent depending on condition
            quoteItems = filter(lambda item,mapping=mapping: self.custom_object_item_condition(self.Quote, item["item"], mapping["ObjectType"]), quoteItems)
            if quoteItems:
                # Get lookups
                lookUps = self.custom_object_item_lookups(self.Quote, mapping["ObjectType"])
                # Get existing record ids
                recordIds = self.get_custom_object_item_record_ids(headers, lookUps, mapping["ObjectType"])
                # Create records
                for batch in range(0, len(quoteItems), API_LIMIT.CREATE_API_RECORD_LIMIT):
                    self.recreate_cust_obj_items(bearerToken, lookUps, recordIds, mapping["ObjectType"], quoteItems[batch:batch+API_LIMIT.CREATE_API_RECORD_LIMIT])

    ###############################################################################################
    # Function to delete custom object item records in Salesforce
    ###############################################################################################
    def delete_cust_obj_items(self, bearerToken, recordsToDelete):
        # Delete in batches of API_LIMIT.DELETE_API_RECORD_LIMIT (Currently 200)
        for batch in range(0, len(recordsToDelete), API_LIMIT.DELETE_API_RECORD_LIMIT):
            url = CL_SalesforceSettings.SALESFORCE_URL + self.build_delete_sobj_collection_url(recordsToDelete[batch:batch+API_LIMIT.DELETE_API_RECORD_LIMIT])
            self.call_sobject_delete_api(bearerToken, url, INT_REF.REF_CR_UP_CUST_OBJ_ITEM)

    ###############################################################################################
    # Function to recreate quote items to custom objects mapping
    ###############################################################################################
    def recreate_cust_obj_items(self, bearerToken, lookUps, recordIds, customObjectName, quoteItems):
        if recordIds:
            if recordIds["totalSize"] > 0:
                # Delete all Salesforce records id
                recordsToDelete = [str(record["Id"]) for record in recordIds["records"]]
                self.delete_cust_obj_items(bearerToken, recordsToDelete)

        # Create in batches of API_LIMIT.CREATE_API_RECORD_LIMIT (Currently 200)
        for batch in range(0, len(quoteItems), API_LIMIT.CREATE_API_RECORD_LIMIT):
            records = list()
            for item in quoteItems[batch:batch+API_LIMIT.CREATE_API_RECORD_LIMIT]:
                record = self.custom_object_item_mapping(self.Quote, item["item"], customObjectName)
                record = self.fill_cust_obj_lookup_record(lookUps, record)
                record["attributes"] = {"type": customObjectName}
                records.append(record)
            if records:
                body = dict()
                body["records"] = records
                headers = self.get_authorization_header(bearerToken)
                self.post_sobjectcollection_request(headers, body, INT_REF.REF_CR_UP_CUST_OBJ_ITEM)

    ###############################################################################################
    # Function to get record ids of the custom objects on Salesforce
    ###############################################################################################
    def get_custom_object_item_record_ids(self, headers, lookUps, customObjectName):
        response = None
        if lookUps:
            # Get Salesforce LookUp Fields
            lookUpFields = str([key["SalesforceField"] for key in lookUps])[1:-1].replace("'", "").replace(" ", "")
            # Build Condition
            condition = str()
            for indx, lookUp in enumerate(lookUps):
                lookUpValue = str()
                if lookUp["FieldType"] == self.TYPE_STRING:
                    lookUpValue = "'{lookUpValue}'".format(lookUpValue=str(lookUp["CpqLookUpValue"]))
                elif lookUp["FieldType"] == self.TYPE_FLOAT:
                    lookUpValue = "{lookUpValue}".format(lookUpValue=str(lookUp["CpqLookUpValue"]))
                condition += "{lookUpField}={lookUpValue}".format(lookUpField=str(lookUp["SalesforceField"]), lookUpValue=str(lookUpValue))
                if indx+1 != len(lookUps):
                    condition += " AND "
            soql = self.build_soql_query(selectedFields="Id,"+lookUpFields,
                                        table= customObjectName,
                                        condition=condition)
            # Call API
            response = self.call_soql_api(headers, soql, INT_REF.REF_GET_CUST_ITEM_IDS)
        return response

    ###############################################################################################
    # Function to fill Custom Object look up fields in a record payload (Composite Request)
    ###############################################################################################
    def fill_cust_obj_lookup_record(self, lookUps, record):
        for lookUp in lookUps:
            record[lookUp["SalesforceField"]] = lookUp["CpqLookUpValue"]
        return record