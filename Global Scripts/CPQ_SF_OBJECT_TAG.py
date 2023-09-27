from CPQ_SF_IntegrationModules import CL_SalesforceIntegrationModules
from CPQ_SF_FunctionModules import get_quote_opportunity_id
from CPQ_SF_CustomObjectMapping import CL_CustomObjectMapping

Quote = context.Quote

def obj_session(opportunityId, obj_name):
    if str(Session[opportunityId]) == "None":
        Session[opportunityId] = {}
    if "Objects" not in Session[opportunityId].keys():
        mapping = CL_CustomObjectMapping(Quote, Session).custom_object_mappings()
        Session[opportunityId]["Objects"] = dict((x["Name"], x) for x in mapping)
    if obj_name in Session[opportunityId]["Objects"].keys():
        return Session[opportunityId]["Objects"][obj_name]
    # Trace.Write("[obj_session]")
    return ""


def id_from_query(headers, query, class_sf_integration_modules):
    response = class_sf_integration_modules.call_soql_api(headers, query)
    for record in response.records:
        for attr in record:
            if attr.Name != 'attributes':
                obj_id = getattr(record, attr.Name)
                return obj_id
    # Trace.Write("[id_from_query] - {} =\n=> {}".format(query, str(response)))
    return ""


def id_from_qt(obj_name):
    table = Quote.QuoteTables['CPQ_SF_QUOTE_CUSTOM_OBJECTS']
    for obj in table.Rows:
        if obj.GetColumnValue("CUSTOM_OBJECT_NAME") == obj_name:
            return str(obj.GetColumnValue("CUSTOM_OBJECT_ID"))
    # Trace.Write("[id_from_qt]")
    return ""


def execute():
    #########################################
    # 1. INIT
    #########################################
    result = str()
    obj_name = Param.OBJECT_NAME
    key = Param.PROPERTY
    opportunityId = get_quote_opportunity_id(Quote)
    # Get from Session if empty on Quote
    if not opportunityId:
        opportunityId = Session["OpportunityId"]
    obj = obj_session(opportunityId, obj_name)
    if not obj:
        return ""
    session_key = "{}_{}".format(obj_name, key)

    class_sf_integration_modules = CL_SalesforceIntegrationModules(Quote, Session)

    #########################################
    # 2. SESSION CHECK
    #########################################
    session_opp = Session[opportunityId]
    if str(session_opp) != 'None':
        if session_key in session_opp.keys():
            return session_opp[session_key]
    #########################################
    # 3. AUTHORIZATION
    #########################################
    bearerToken = class_sf_integration_modules.get_auth2_token()
    headers = class_sf_integration_modules.get_authorization_header(bearerToken)
    #########################################
    # 4. RETURN SELECTED PROPERTY TO TAG
    #########################################
    if obj['Linked_To_Quote']:
        obj_id = id_from_qt(obj_name)
    else:
        obj_id = id_from_query(headers, obj['Query'], class_sf_integration_modules)

    if not obj_id:
        # Trace.Write("[execute]")
        return ""

    response = class_sf_integration_modules.get_sobject(bearerToken, obj['Type'], obj_id)

    result = str(getattr(response, key))
    Session[opportunityId][session_key] = result
    return result


Result = ''
Result = str(execute())