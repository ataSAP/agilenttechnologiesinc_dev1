def get_bearer():
    ## Make sure to leverage CredMgmt and new Urls
    token = AuthorizedRestClient.GetPasswordGrantOAuthToken("bearer_cred", "{}/basic/api/token".format(baseUrl), True)
    bearer_header = {"Authorization": "Bearer {}".format(token.access_token)}
    return bearer_header

def loop_table(lower, upper, table_name):
    ## Loop through States list
    res = SqlHelper.GetList("SELECT * FROM {} WHERE (cpqtableentryid > {} AND cpqtableentryid <= {}) AND notes != 'skip'".format(table_name, lower, upper))
    header = get_bearer()
    for rec in res:
        countryCode = rec.Country ## 2-char code
        countryDesc = rec.CountryDescription
        stateCode = rec.State
        stateDesc = rec.StateDescription

        ## Check if country exists by 3-char code, create if it doesn't
        country_res = RestClient.Get("{}/api/general/v1/countries?$filter=abrev3 eq '{}'".format(baseUrl, rec.country3), header)
        if country_res.totalNumberOfRecords == 0:
            Trace.Write("Attempting to create country: {}".format(countryDesc))
            create_country_body = {
                "name":countryDesc,
                "abrev3":rec.country3,
                "abrev2":countryCode
            }
            RestClient.Post("{}/api/general/v1/countries".format(baseUrl), create_country_body, header)
            Trace.Write("Country {} created".format(countryDesc))
        else:
            if country_res.pagedRecords[0].name != countryDesc or country_res.pagedRecords[0].abrev3 != rec.country3 or country_res.pagedRecords[0].abrev2 != countryCode:
                Trace.Write("Attempting to update country: {}".format(countryDesc))
                update_country_body = {
                    "id": country_res.pagedRecords[0].id,
                    "name": countryDesc,
                    "abrev3": rec.country3,
                    "abrev2": countryCode
                }
                RestClient.Put("{}/api/general/v1/countries/{}".format(baseUrl, country_res.pagedRecords[0].id), update_country_body, header)
                Trace.Write("Country {} updated".format(countryDesc))
        ## Create or update State
        state_str = "{}/api/general/v1/states?$filter=abbreviation eq '{}' and countryName eq '{}'".format(baseUrl, stateCode, countryDesc)
        state_res = RestClient.Get(state_str, header)
        if state_res.totalNumberOfRecords == 0:
            Trace.Write("ATTEMPTING to create State: {} | country: {} | {}".format(stateDesc, rec.country3, state_str))
            create_state_body = {
                "name":stateDesc,
                "abbreviation":stateCode,
                "countryId":rec.country3
            }
            RestClient.Post("{}/api/general/v1/states".format(baseUrl), create_state_body, header)
            Trace.Write("State {} created".format(stateDesc))
        ## Update the name if it does not match
        else:
            if state_res.pagedRecords[0].name != countryDesc or state_res.pagedRecords[0].countryId != rec.country3 or state_res.pagedRecords[0].abbreviation != stateCode:
                Trace.Write("ATTEMPTING to update State({}): {} | country: {}".format(state_res.pagedRecords[0].id, stateDesc, rec.country3))
                update_state_body = {
                    "id": state_res.pagedRecords[0].id,
                    "name": stateDesc,
                    "abbreviation": stateCode,
                    "countryId": rec.country3
                }
                RestClient.Put("{}/api/general/v1/states/{}".format(baseUrl, state_res.pagedRecords[0].id), update_state_body, header)
                Trace.Write("State {} updated".format(stateDesc))

## Inital Variables
baseUrl = "https://{}".format(RequestContext.Url.Host)
table = "temp_statedata"

## Calculate the number of iterations
rec_count = SqlHelper.GetFirst("SELECT TOP 1 cpqtableentryid FROM {} ORDER BY cpqtableentryid DESC".format(table))
total = rec_count.cpqtableentryid
num_iterations = total // 1000
if total % 1000 != 0: num_iterations += 1

## Loop through iterations to hit all rows
for i in range(num_iterations):
    loop_table(i*1000, (i+1)*1000, table)