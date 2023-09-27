from CPQ_SF_IntegrationModules import CL_SalesforceIntegrationModules
from CPQ_SF_FunctionModules import get_quote_opportunity_id
from CPQ_SF_IntegrationSettings import CL_SalesforceIntegrationParams


def execute():
    #########################################
    # 1. INIT
    #########################################
    result = str()
    Quote = context.Quote
    key = Param.PROPERTY
    class_sf_integration_modules = CL_SalesforceIntegrationModules(Quote, Session)
    opportunityId = get_quote_opportunity_id(Quote)
    # Get from Session if empty on Quote
    if not opportunityId:
        opportunityId = Session["OpportunityId"]
    #########################################
    # 2. SESSION CHECK
    #########################################
    session_opp = Session[opportunityId]
    if str(session_opp) != 'None':
        if key in session_opp.keys():
            return session_opp[key]
    else:
        Session[opportunityId] = {}
    #########################################
    # 3. AUTHORIZATION
    #########################################
    bearerToken = class_sf_integration_modules.get_auth2_token()
    #########################################
    # 4. RETURN SELECTED PROPERTY TO TAG
    #########################################
    response = class_sf_integration_modules.get_sobject(bearerToken, CL_SalesforceIntegrationParams.SF_OPPORTUNITY_OBJECT, opportunityId)
    result = str(getattr(response, key))
    Session[opportunityId][key] = result
    return result


Result = ''
Result = str(execute())