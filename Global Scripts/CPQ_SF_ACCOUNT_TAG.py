from CPQ_SF_IntegrationModules import CL_SalesforceIntegrationModules
from CPQ_SF_FunctionModules import get_quote_opportunity_id
from CPQ_SF_IntegrationSettings import CL_SalesforceIntegrationParams
from CPQ_SF_IntegrationReferences import CL_CompositeRequestReferences as REF, CL_IntegrationReferences as INT_REF
from CPQ_SF_BusinessPartnerModules import CL_BusinessPartnerModules


def execute():
    #########################################
    # 1. INIT
    #########################################
    result = str()
    Quote = context.Quote
    key = Param.PROPERTY
    session_key = 'account_' + key
    class_sf_integration_modules = CL_SalesforceIntegrationModules(Quote, Session)
    class_bp_modules = CL_BusinessPartnerModules(Quote, Session)
    opportunityId = get_quote_opportunity_id(Quote)
    # Get from Session if empty on Quote
    if not opportunityId:
        opportunityId = Session["OpportunityId"]
    compositePayload = list()
    #########################################
    # 2. SESSION CHECK
    #########################################
    session_opp = Session[opportunityId]
    if str(session_opp) != 'None':
        if session_key in session_opp.keys():
            return session_opp[session_key]
    else:
        Session[opportunityId] = {}
    #########################################
    # 3. AUTHORIZATION
    #########################################
    bearerToken = class_sf_integration_modules.get_auth2_token()
    #########################################
    # 4. RETURN SELECTED PROPERTY TO TAG
    #########################################
    oppRequest = class_sf_integration_modules.build_cr_sobject_get_opportunity(opportunityId)
    compositePayload.append(oppRequest)
    oppAccountRequest = class_bp_modules.build_cr_sobject_get_account("@{"+CL_SalesforceIntegrationParams.SF_OPPORTUNITY_OBJECT+".AccountId}", REF.GET_OPP_ACC)
    compositePayload.append(oppAccountRequest)
    response = class_sf_integration_modules.post_composite_request(bearerToken, compositePayload, INT_REF.REF_GET_ACC)
    for resp in response['compositeResponse']:
        if resp:
            if str(resp['body']['attributes']['type']) == CL_SalesforceIntegrationParams.SF_ACCOUNT_OBJECT:
                result = getattr(resp['body'], key)
                Session[opportunityId][session_key] = result
                return result


Result = ''
Result = str(execute())