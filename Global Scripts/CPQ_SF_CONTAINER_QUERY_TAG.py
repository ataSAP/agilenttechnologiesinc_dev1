from CPQ_SF_IntegrationModules import CL_SalesforceIntegrationModules
import re

def execute():
    #########################################
    # 1. INIT
    #########################################
    Quote = context.Quote
    def update_container_row(row, col_prop_map, prop_values):
        for key, prop in col_prop_map.items():
            for p_key in prop_values.keys():
                if str(p_key).lower() == prop.lower():
                    #Trace.Write(str(prop_values[str(p_key)]))
                    row.SetColumnValue(key, str(prop_values[str(p_key)]))
                    break

    query = "?q=" + re.sub('\++', '+', str(Param.QUERY))
    query = str.replace(query,"[", "(")
    query = str.replace(query,"]", ")")
    #Get id as 1st property in request (after "select")
    query_with_id = query[:9] + "+Id," + query[9:] if not re.search("(?i)(?<![\w\d])id(?![\w\d])", query.lower().split("where")[0]) else query
    container = Product.GetContainerByName(Param.CONTAINER)
    column_proprty_mapping = {}
    #properies in order based on query
    counter = 2 #[0] q, [1] select
    props = re.findall("\w+", query)
    for val in Param.COLUMNS:
        column_proprty_mapping[val.replace("|||", " ")] = props[counter]
        counter = counter + 1
    session_stored = ""
    class_sf_integration_modules = CL_SalesforceIntegrationModules(Quote, Session)
    #########################################
    # 2. SESSION CHECK
    #########################################
    session_query=Session['Query']
    if str(session_query) != 'None':
        if query_with_id in session_query.keys():
           session_stored = session_query[query_with_id]
    else:
        Session['Query'] = {}
    #########################################
    # 3. AUTHORIZATION
    #########################################
    bearerToken = class_sf_integration_modules.get_auth2_token()
    headers = class_sf_integration_modules.get_authorization_header(bearerToken)
    #########################################
    # 4. RESOLVE QUERY
    #########################################
    if not session_stored:
        response = class_sf_integration_modules.call_soql_api(headers, query_with_id, None)
        response_dict = {}
        for record in response.records:
            response_dict[str(record.Id)] = {}
            for attr in record:
               response_dict[str(record.Id)][attr.Name] = getattr(record,attr.Name)

        Session['Query'][query_with_id] = response_dict
        session_stored = response_dict
    #########################################
    # 5. REMOVE EXCESS ROWS
    #########################################
    def crmid_not_in_response(row):
        return row.CrmId not in session_stored.keys()
    def get_row_index(row):
        return row.RowIndex

    #get indexes of rows that need to be removed, sorted to avoid index change of lower rows
    remove_rows_indexes = sorted(map(get_row_index, filter(crmid_not_in_response, container.Rows)), reverse=True)
    for index in remove_rows_indexes:
        container.DeleteRow(index)
    #########################################
    # 6. UPDATE EXISTING ROWS
    #########################################
    for row in container.Rows:
        update_container_row(row, column_proprty_mapping, session_stored[row.CrmId])
    #########################################
    # 7. ADD MISSING ROWS
    #########################################
    rows_to_add = [crmid for crmid in session_stored.keys() if crmid not in [row.CrmId for row in container.Rows]]
    for crmid in rows_to_add:
        row = container.AddNewRow(False)
        row.CrmId = crmid
        update_container_row(row, column_proprty_mapping, session_stored[crmid])
    #########################################
    # 8. CALCULATE CONTAINER
    #########################################
    container.Calculate()

Result = 'NOK'
execute()
Result = 'OK'