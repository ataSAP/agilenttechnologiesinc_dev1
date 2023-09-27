from CPQ_SF_Configuration import CL_SalesforceSettings
from CPQ_SF_IntegrationModules import CL_SalesforceIntegrationModules
from CPQ_SF_IntegrationReferences import CL_SalesforceApiLimits as API_LIMIT, CL_SalesforceApis as API, CL_CompositeRequestReferences as REF, CL_IntegrationReferences as INT_REF
from CPQ_SF_IntegrationSettings import CL_GeneralIntegrationSettings, CL_SalesforceIntegrationParams
from CPQ_SF_OpportunityLineItemMapping import product_integration_mapping, opplineitem_integration_mapping


###############################################################################################
# Class CL_LineItemIntegrationModules:
#       Class to store integration functions related to line items
###############################################################################################
class CL_LineItemIntegrationModules(CL_SalesforceIntegrationModules):
    ###############################################################################################
    # Function to get Salesforce Line item records from OpportunityLineItem object
    ###############################################################################################
    def get_sf_opp_line_items(self, bearerToken, opportunityId, integrationReference):
        response = None
        condition = """OpportunityId='{opportunityId}'""".format(opportunityId=str(opportunityId))
        soql = self.build_soql_query(selectedFields="Id",
                                     table=CL_SalesforceIntegrationParams.SF_OPPORTUNITY_LINE_ITEM_OBJECT,
                                     condition=condition)
        if soql:
            headers = self.get_authorization_header(bearerToken)
            response = self.call_soql_api(headers, soql, integrationReference)
        return response

    ###############################################################################################
    # Function to delete Opportunity Line Items
    ###############################################################################################
    def delete_opp_line_items(self, bearerToken, opportunityId):
        responses = list()
        # Get all OpportunityLineItem records to delete
        lineItems = self.get_sf_opp_line_items(bearerToken, opportunityId, INT_REF.REF_GET_OPP_LINE_ITEMS)
        if lineItems["totalSize"] > 0:
            lineItemrecords = [str(record["Id"]) for record in lineItems["records"]]
            # Delete in batches of API_LIMIT.DELETE_API_RECORD_LIMIT (Currently 200)
            for batch in range(0, len(lineItemrecords), API_LIMIT.DELETE_API_RECORD_LIMIT):
                url = CL_SalesforceSettings.SALESFORCE_URL + self.build_delete_sobj_collection_url(lineItemrecords[batch:batch+API_LIMIT.DELETE_API_RECORD_LIMIT])
                response = self.call_sobject_delete_api(bearerToken, url, INT_REF.REF_DEL_OPP_LINE_ITEMS)
                responses.append(response)
        return responses

    ###############################################################################################
    # Function to get Salesforce Internal Product Ids
    ###############################################################################################
    def get_sf_internal_product_ids(self, bearerToken, listOfLookUps):
        responses = list()
        if listOfLookUps:
            headers = self.get_authorization_header(bearerToken)
            # Remove Duplicates
            revListOfLookUps = []
            for lookUpList in listOfLookUps:
                if lookUpList not in revListOfLookUps:
                    revListOfLookUps.append(lookUpList)
            # Get Salesforce LookUp Fields
            lookUpFields = str([key["SalesforceField"] for key in listOfLookUps[0]])[1:-1].replace("'", "").replace(" ", "")
            # Get ids in batches of API_LIMIT.GET_INTERNAL_PRODUCT_SOQL_LIMIT (Currently 7000 different items)
            for batch in range(0, len(revListOfLookUps), API_LIMIT.GET_INTERNAL_PRODUCT_SOQL_LIMIT):
                batchListOfLookUps = (revListOfLookUps[batch:batch+API_LIMIT.GET_INTERNAL_PRODUCT_SOQL_LIMIT])
                # Build Condition
                condition = str()
                for mainIndx, lookUpList in enumerate(batchListOfLookUps):
                    condition += "("
                    for indx, lookUp in enumerate(lookUpList):
                        condition += "{lookUpField}='{lookUpValue}'".format(lookUpField=str(lookUp["SalesforceField"]), lookUpValue=str(lookUp["CpqLookUpValue"]))
                        if indx+1 != len(lookUpList):
                            condition += " AND "
                    condition += ")"
                    if mainIndx+1 != len(batchListOfLookUps):
                        condition += " OR "
                # Build soql to find Salesforce Internal Product Ids
                soql = self.build_soql_query(selectedFields="Id,"+lookUpFields,
                                             table=CL_SalesforceIntegrationParams.SF_PRODUCT_OBJECT,
                                             condition=condition)
                # Call API
                response = self.call_soql_api(headers, soql, INT_REF.REF_GET_OPP_LINE_ITEMS)
                responses.append(response)
        return responses

    ###############################################################################################
    # Function to get Salesforce Products by their IDs. To retrieve LookupValues.
    ###############################################################################################
    def get_sf_product_by_ids(self, bearerToken, sfIds, listOfLookUps):
        responses = list()
        headers = self.get_authorization_header(bearerToken)
        # Remove Duplicates
        sfIds = list(set(sfIds))
        if sfIds:
            # Get Salesforce LookUp Fields
            lookUpFields = str([key["SalesforceField"] for key in listOfLookUps[0]])[1:-1].replace("'", "").replace(" ", "")
            # Get ids in batches of API_LIMIT.GET_INTERNAL_PRODUCT_SOQL_LIMIT (Currently 7000 different items)
            for batch in range(0, len(sfIds), API_LIMIT.GET_INTERNAL_PRODUCT_SOQL_LIMIT):
                sfIds = str((sfIds[batch:batch+API_LIMIT.GET_INTERNAL_PRODUCT_SOQL_LIMIT]))[1:-1]
                # Build soql to find Salesforce Internal Product Ids
                soql = """?q=Select+id+,+{lookUpField}+FROM+Product2+WHERE+id+IN+({sfIds})""".format(lookUpField=str(lookUpFields), sfIds=str(sfIds))
                # Call API
                response = self.call_soql_api(headers, soql, INT_REF.REF_GET_OPP_LINE_ITEMS)
                responses.append(response)
        return responses

    ###############################################################################################
    # Function to collect internal Salesforce product ids in quoteItems list
    ###############################################################################################
    def collect_sf_internal_product_ids(self, quoteItems, response):
        if response["totalSize"] > 0:
            for item in quoteItems:
                condition = str()
                for indx, lookUp in enumerate(item["lookUps"]):
                    condition += "record['{lookUpField}'] == '{lookUpValue}'".format(lookUpField=str(lookUp["SalesforceField"]), lookUpValue=str(lookUp["CpqLookUpValue"]))
                    if indx+1 != len(item["lookUps"]):
                        condition += " and "
                if condition:
                    sfId = next((str(record["Id"]) for record in response["records"] 
                                 if eval(condition)), None)
                    if sfId:
                        item["sfId"] = sfId
        return quoteItems

    ###############################################################################################
    # Function to collect pricebook entries in quoteItems list
    ###############################################################################################
    def collect_sf_pricebook_ids(self, quoteItems, response, sfStandardPriceBookId):
        if response["totalSize"] > 0:
            for item in filter(lambda x: x["sfId"] != "", quoteItems):
                for entry in filter(lambda x: str(x["Product2Id"]) == item["sfId"], response["records"]):
                    if str(entry["Pricebook2Id"]) == sfStandardPriceBookId:
                        item["sfStandardPriceBookEntryId"] = str(entry["Id"])
                    else:
                        item["sfCustomPriceBookEntryId"] = str(entry["Id"])
        return quoteItems

    ###############################################################################################
    # Function to collect pricebook entries
    ###############################################################################################
    def process_collection_pricebook_ids(self, bearerToken, quoteItems, sfPriceBook, sfStandardPriceBookId):
        # Call API to get existing Price Book Entries
        responses = self.get_existing_price_book_entries(bearerToken, quoteItems, sfPriceBook, sfStandardPriceBookId)
        for response in responses:
            quoteItems = self.collect_sf_pricebook_ids(quoteItems, response, sfStandardPriceBookId)
        return quoteItems

    ###############################################################################################
    # Function to create/update Salesforce product master
    ###############################################################################################
    def create_update_sf_product_master(self, bearerToken, quoteItems, updateProducts):
        response = None
        compositePayload = list()
        # Collect line items without corresponding Salesforce products
        productsToCreate = filter(lambda x: x["sfId"] == "", quoteItems)
        # POST: Create new product records
        if productsToCreate:
            records = list()
            for item in productsToCreate:
                record = product_integration_mapping(self.Quote, item["item"])
                # Fill Look Up Fields
                for lookUp in item["lookUps"]:
                    record[lookUp["SalesforceField"]] = lookUp["CpqLookUpValue"]
                record["IsActive"] = True
                record["attributes"] = {"type": CL_SalesforceIntegrationParams.SF_PRODUCT_OBJECT}
                records.append(record)
            compositeRequest = self.get_cr_sobjectcollection_payload_header(API.POST, REF.CREATE_PRODUCTS_REFID, None)
            compositeRequest["body"] = {"records": records}
            compositePayload.append(compositeRequest)

        if updateProducts:
            # Collect line items that should be updated
            productsToUpdate = filter(lambda x: x["sfId"] != "", quoteItems)
            # PATCH: Update existing product records
            if productsToUpdate:
                records = list()
                for item in productsToUpdate:
                    record = product_integration_mapping(self.Quote, item["item"])
                    record["Id"] = item["sfId"]
                    # Fill Look Up Fields
                    for lookUp in item["lookUps"]:
                        record[lookUp["SalesforceField"]] = lookUp["CpqLookUpValue"]
                    record["attributes"] = {"type": CL_SalesforceIntegrationParams.SF_PRODUCT_OBJECT}
                    records.append(record)
                compositeRequest = self.get_cr_sobjectcollection_payload_header(API.PATCH, REF.UPDATE_PRODUCTS_REFID, None)
                compositeRequest["body"] = {"records": records}
                compositePayload.append(compositeRequest)

        if compositePayload:
            # Call REST API
            response = self.post_composite_request(bearerToken, compositePayload, INT_REF.REF_CR_UP_PRODUCT_MASTER)
        return response

    ###############################################################################################
    # Function to get existing Salesforce Price Book entries
    ###############################################################################################
    def get_existing_price_book_entries(self, bearerToken, quoteItems, sfPriceBook, sfStandardPriceBookId):
        responses = list()
        currencyCode = self.Quote.SelectedMarket.CurrencyCode
        sfProductIds = [item["sfId"] for item in quoteItems if item["sfId"] != ""]
        if sfProductIds:
            # Remove Duplicates
            sfProductIds = list(set(sfProductIds))
            headers = self.get_authorization_header(bearerToken)
            # Get ids in batches of API_LIMIT.GET_PRICEBOOK_ENTRIES_SOQL_LIMIT (Currently 5000 different items)
            for batch in range(0, len(sfProductIds), API_LIMIT.GET_PRICEBOOK_ENTRIES_SOQL_LIMIT):
                sfProductIds = sfProductIds[batch:batch+API_LIMIT.GET_PRICEBOOK_ENTRIES_SOQL_LIMIT]
                if sfPriceBook:
                    if CL_GeneralIntegrationSettings.SF_MCE:
                        soql = """?q=SELECT+Id,+Pricebook2Id,+Product2Id,+UnitPrice,+CurrencyIsoCode+FROM+PricebookEntry+WHERE+Pricebook2Id+IN+('{sfStandardPriceBookId}','{sfPriceBookId}')+AND+Product2Id+IN+({sfProductIds})+AND+CurrencyIsoCode+=+'{currencyCode}'+AND+IsActive+=True""".format(sfStandardPriceBookId=str(sfStandardPriceBookId), sfPriceBookId=str(sfPriceBook["SF_PRICEBOOK_ID"]), sfProductIds=str(sfProductIds)[1:-1], currencyCode=str(currencyCode))
                    else:
                        soql = """?q=SELECT+Id,+Pricebook2Id,+Product2Id,+UnitPrice+FROM+PricebookEntry+WHERE+Pricebook2Id+IN+('{sfStandardPriceBookId}','{sfPriceBookId}')+AND+Product2Id+IN+({sfProductIds})+AND+IsActive+=True""".format(sfStandardPriceBookId=str(sfStandardPriceBookId), sfPriceBookId=str(sfPriceBook["SF_PRICEBOOK_ID"]), sfProductIds=str(sfProductIds)[1:-1])
                else:
                    if CL_GeneralIntegrationSettings.SF_MCE:
                        soql = """?q=SELECT+Id,+Pricebook2Id,+Product2Id,+UnitPrice,+CurrencyIsoCode+FROM+PricebookEntry+WHERE+Pricebook2Id+IN+('{sfStandardPriceBookId}')+AND+Product2Id+IN+({sfProductIds})+AND+CurrencyIsoCode+=+'{currencyCode}'+AND+IsActive+=True""".format(sfStandardPriceBookId=str(sfStandardPriceBookId), sfProductIds=str(sfProductIds)[1:-1], currencyCode=str(currencyCode))
                    else:
                        soql = """?q=SELECT+Id,+Pricebook2Id,+Product2Id,+UnitPrice+FROM+PricebookEntry+WHERE+Pricebook2Id+IN+('{sfStandardPriceBookId}')+AND+Product2Id+IN+({sfProductIds})+AND+IsActive+=True""".format(sfStandardPriceBookId=str(sfStandardPriceBookId), sfProductIds=str(sfProductIds)[1:-1])
                # Call API to get existing Price Book Entries
                priceBookEntries = self.call_soql_api(headers, soql, INT_REF.REF_GET_PRICE_BOOK)
                responses.append(priceBookEntries)
        return responses

    ###############################################################################################
    # Function to create/update Salesforce Price Book entries
    ###############################################################################################
    def create_update_price_book_entries(self, bearerToken, quoteItems, sfPriceBook, sfStandardPriceBookId):
        response = None
        compositePayload = list()
        currencyCode = self.Quote.SelectedMarket.CurrencyCode
        # Update Price Book Entries (Standard & Custom)
        quoteItemsPriceToUpdate = filter(lambda item: item["sfId"] != "" and (item["sfStandardPriceBookEntryId"] != "" or item["sfCustomPriceBookEntryId"] != ""), quoteItems)
        if quoteItemsPriceToUpdate:
            records = list()
            for item in quoteItemsPriceToUpdate:
                if item["sfStandardPriceBookEntryId"] != "":
                    record = dict()
                    record["Id"] = item["sfStandardPriceBookEntryId"]
                    record["UnitPrice"] = float(item["item"].ListPrice)
                    record["attributes"] = {"type": CL_SalesforceIntegrationParams.SF_PRICEBOOK_ENTRY_OBJECT}
                    records.append(record)
                if item["sfCustomPriceBookEntryId"] != "":
                    record = dict()
                    record["Id"] = item["sfCustomPriceBookEntryId"]
                    record["UnitPrice"] = float(item["item"].ListPrice)
                    record["attributes"] = {"type": CL_SalesforceIntegrationParams.SF_PRICEBOOK_ENTRY_OBJECT}
                    records.append(record)
            compositeRequest = self.get_cr_sobjectcollection_payload_header(API.PATCH, REF.UPDATE_PRICEBOOK_ENTRIES_REFID, None)
            compositeRequest["body"] = {"records": records}
            compositePayload.append(compositeRequest)

        # Create Price Book Entries (Standard & Custom)
        quoteItemsPriceToCreate = filter(lambda item: item["sfId"] != "" and (item["sfStandardPriceBookEntryId"] == "" or item["sfCustomPriceBookEntryId"] == ""), quoteItems)
        if quoteItemsPriceToCreate:
            records = list()
            for item in quoteItemsPriceToCreate:
                if item["sfStandardPriceBookEntryId"] == "":
                    record = dict()
                    record["Pricebook2Id"] = sfStandardPriceBookId
                    record["Product2Id"] = item["sfId"]
                    record["UnitPrice"] = float(item["item"].ListPrice)
                    if CL_GeneralIntegrationSettings.SF_MCE:
                        record["CurrencyIsoCode"] = currencyCode
                    record["attributes"] = {"type": CL_SalesforceIntegrationParams.SF_PRICEBOOK_ENTRY_OBJECT}
                    record["IsActive"] = True
                    records.append(record)
                if item["sfCustomPriceBookEntryId"] == "" and sfPriceBook:
                    record = dict()
                    record["Pricebook2Id"] = sfPriceBook["SF_PRICEBOOK_ID"]
                    record["Product2Id"] = item["sfId"]
                    record["UnitPrice"] = float(item["item"].ListPrice)
                    if CL_GeneralIntegrationSettings.SF_MCE:
                        record["CurrencyIsoCode"] = currencyCode
                    record["attributes"] = {"type": CL_SalesforceIntegrationParams.SF_PRICEBOOK_ENTRY_OBJECT}
                    record["IsActive"] = True
                    records.append(record)
            compositeRequest = self.get_cr_sobjectcollection_payload_header(API.POST, REF.CREATE_PRICEBOOK_ENTRIES_REFID, None)
            compositeRequest["body"] = {"records": records}
            compositePayload.append(compositeRequest)

        if compositePayload:
            # Call REST API
            response = self.post_composite_request(bearerToken, compositePayload, INT_REF.REF_CR_UP_PRICE_BOOK)
        return response

    ###############################################################################################
    # Function to Create Opportunity Line Items
    ###############################################################################################
    def create_line_items(self, bearerToken, opportunityId, quoteItems, sfPriceBook):
        responses = list()
        quoteLineItemsToCreate = filter(lambda item: item["sfId"] != "", quoteItems)
        if quoteLineItemsToCreate:
            # Create in batches of API_LIMIT.CREATE_API_RECORD_LIMIT (Currently 200)
            for batch in range(0, len(quoteLineItemsToCreate), API_LIMIT.CREATE_API_RECORD_LIMIT):
                records = list()
                for item in quoteLineItemsToCreate[batch:batch+API_LIMIT.CREATE_API_RECORD_LIMIT]:
                    record = opplineitem_integration_mapping(self.Quote, item["item"])
                    record["OpportunityId"] = opportunityId
                    record["Product2Id"] = item["sfId"]
                    if sfPriceBook:
                        record["PriceBookEntryId"] = item["sfCustomPriceBookEntryId"]
                    else:
                        record["PriceBookEntryId"] = item["sfStandardPriceBookEntryId"]
                    record["attributes"] = {"type": CL_SalesforceIntegrationParams.SF_OPPORTUNITY_LINE_ITEM_OBJECT}
                    records.append(record)
                if records:
                    body = dict()
                    body["records"] = records
                    headers = self.get_authorization_header(bearerToken)
                    response = self.post_sobjectcollection_request(headers, body, INT_REF.REF_CREATE_OPP_LINE_ITEMS)
                    responses.append(response)
        return responses