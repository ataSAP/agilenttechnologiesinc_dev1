from CPQ_SF_IntegrationModules import CL_SalesforceIntegrationModules
from CPQ_SF_IntegrationReferences import CL_IntegrationReferences as INT_REF
import re


def execute():
    #########################################
    # 1. INIT
    #########################################
    result = str()
    Quote = context.Quote
    query = "?q=" + re.sub('\++', '+', str(Param.QUERY))
    query = str.replace(query,"[", "(")
    query = str.replace(query,"]", ")")
    result = str()
    class_sf_integration_modules = CL_SalesforceIntegrationModules(Quote, Session)
    #########################################
    # 2. SESSION CHECK
    #########################################
    session_query = Session['Query']
    if str(session_query) != 'None':
        if query in session_query.keys():
            return session_query[query]
    else:
        Session['Query'] = {}
    #########################################
    # 3. AUTHORIZATION
    #########################################
    bearerToken = class_sf_integration_modules.get_auth2_token()
    headers = class_sf_integration_modules.get_authorization_header(bearerToken)
    #########################################
    # 4. RETURN SELECTED PROPERTY TO TAG
    #########################################
    response = class_sf_integration_modules.call_soql_api(headers, query, INT_REF.REF_QUERY_TAG)
    if response:
        for record in response.records:
            for attr in record:
                if attr.Name != 'attributes':
                    result = getattr(record, attr.Name)
                    break
            break
    Session['Query'][query] = str(result)
    return str(result)


Result = ''
Result = str(execute())