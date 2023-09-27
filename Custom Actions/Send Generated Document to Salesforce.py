from CPQ_SF_IntegrationModules import CL_SalesforceIntegrationModules
from CPQ_SF_FunctionModules import get_quote_opportunity_id
from CPQ_SF_IntegrationReferences import CL_CompositeRequestReferences as REF, CL_SalesforceApis as API, CL_IntegrationReferences as INT_REF

Quote = context.Quote
opportunityId = get_quote_opportunity_id(Quote)
if opportunityId:
    class_sf_integration_modules = CL_SalesforceIntegrationModules(Quote, Session)
    generatedDocumentName = Quote.GetLatestGeneratedDocumentFileName()
    if generatedDocumentName:
        compositePayload = list()
        #############################################
        # 1. AUTHORIZATION
        #############################################
        bearerToken = class_sf_integration_modules.get_auth2_token()
        #############################################
        # 2. INSERT CONTENT VERSION
        #############################################
        url = API.CR_POST_CONTENT_VERSION_API
        # Build composite request
        record = dict()
        record["Title"] = generatedDocumentName
        record["PathOnClient"] = generatedDocumentName
        record["ContentLocation"] = "S"
        record["VersionData"] = Quote.GetLatestGeneratedDocumentInBytes()
        compositeRequest = dict()
        compositeRequest = class_sf_integration_modules.build_cr_sobject_request(url, API.POST, record, REF.INSERT_CONTENT_VERSION)
        compositePayload.append(compositeRequest)
        #############################################
        # 2. GET CONTENT ID
        #############################################
        # Buil SOQL
        soql = "?q=SELECT+ContentDocumentId+FROM+ContentVersion+WHERE+ID+=+'@{"+REF.INSERT_CONTENT_VERSION+".id}'"
        url = API.CR_GET_SOQL_API.format(soql=str(soql))
        # Build composite request
        compositeRequest = dict()
        compositeRequest = class_sf_integration_modules.build_cr_sobject_request(url, API.GET, None, REF.GET_CONTENT_ID)
        compositePayload.append(compositeRequest)
        #############################################################
        # 3. LINK CONTENT ID TO SALESFORCE OBJECT (QUOTE/OPPORTUNITY)
        #############################################################
        url = API.CR_POST_CONTENT_DOC_LINK_API
        record = dict()
        record["ContentDocumentId"] = "@{"+REF.GET_CONTENT_ID+".records[0].ContentDocumentId}"
        record["LinkedEntityId"] = opportunityId
        record["Visibility"] = "AllUsers"
        compositeRequest = dict()
        compositeRequest = class_sf_integration_modules.build_cr_sobject_request(url, API.POST, record, REF.LINK_CONTENT)
        compositePayload.append(compositeRequest)

        if compositePayload:
            # Call Composite Request API
            response = class_sf_integration_modules.post_composite_request(bearerToken, compositePayload, INT_REF.REF_GEN_DOC)
