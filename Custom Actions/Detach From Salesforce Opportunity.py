from CPQ_SF_FunctionModules import get_quote_opportunity_id, set_quote_opportunity_id, set_quote_opportunity_name
from CPQ_SF_IntegrationMessages import CL_IntegrationMessages
from CPQ_SF_IntegrationModules import CL_SalesforceIntegrationModules
from CPQ_SF_Configuration import CL_SalesforceSettings
from CPQ_SF_IntegrationReferences import CL_IntegrationReferences as INT_REF
from Scripting.Quote import MessageLevel

Quote = context.Quote
# Check if Quote is attached to an Opportunity
opportunityId = get_quote_opportunity_id(Quote)
if opportunityId:
    # Delete Quote from Salesforce
    class_sf_integration_modules = CL_SalesforceIntegrationModules(Quote, Session)
    bearerToken = class_sf_integration_modules.get_auth2_token()
    # Get All Quote versions from Salesforce
    response = class_sf_integration_modules.get_quote_by_number(bearerToken, opportunityId, INT_REF.REF_GET_SF_QUOTE)
    if response:
        if response["totalSize"] > 0:
            # Collect Quote Id records
            quoteIdRecords = [str(record["Id"]) for record in response["records"]]
            url = CL_SalesforceSettings.SALESFORCE_URL + class_sf_integration_modules.build_delete_sobj_collection_url(quoteIdRecords)
            # Call REST API
            response = class_sf_integration_modules.call_sobject_delete_api(bearerToken, url, INT_REF.REF_DETACH_QUOTE)
            # Clear Opportunity Id
            set_quote_opportunity_id(Quote, str())
            # Clear Opportunity Name
            set_quote_opportunity_name(Quote, str())
else:
    Quote.AddMessage(CL_IntegrationMessages.CANNOT_DETACH_QUOTE, MessageLevel.Warning, True)
