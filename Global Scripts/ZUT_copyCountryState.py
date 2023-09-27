########
## Utility script to be leveraged to map a Source environment's countries+states into a Destination environment
########

def get_bearer(url):
    ## Make sure to leverage CredMgmt and new Urls
    token = AuthorizedRestClient.GetPasswordGrantOAuthToken("bearer_cred", "{}/basic/api/token".format(url), True)
    bearer_header = {"Authorization": "Bearer {}".format(token.access_token)}
    return bearer_header

def get_count(api_name, url, header):
    count = RestClient.Get("{}/api/general/v1/{}?$top=1".format(url, api_name), header)
    return count.totalNumberOfRecords

## Inital Variables
def grab_state(idCheck):
    stateId_sql = SqlHelper.GetList("SELECT top 1000 state_id AS id FROM v_usa_code WHERE state_id > {} ORDER BY state_id ASC".format(idCheck))
    return stateId_sql
countryId_sql = SqlHelper.GetList("SELECT top 1000 country_id AS id FROM v_country ORDER BY country_id ASC")
sourceUrl = "https://{}".format(RequestContext.Url.Host) ## Source environment
destinUrl = "https://{}".format("agilenttechnologiesinc-sit.cpq.cloud.sap") ##Destination environment

## Countries logic
destinHeader = get_bearer(destinUrl)
sourceHeader = get_bearer(sourceUrl)
for rec in countryId_sql:
    ## Update Country record
    try:
        sourceCountry = RestClient.Get("{}/api/general/v1/countries/{}".format(sourceUrl, rec.id), sourceHeader)
        destinCountry = RestClient.Get("{}/api/general/v1/countries/{}".format(destinUrl, rec.id), destinHeader)
        ## Push to destination environment if different
        if destinCountry.name != sourceCountry.name or destinCountry.abrev3 != sourceCountry.abrev3 or destinCountry.abrev2 != sourceCountry.abrev2:
            update_country_body = {
                "id": rec.id,
                "name": sourceCountry.name,
                "abrev3": sourceCountry.abrev3,
                "abrev2": sourceCountry.abrev2
            }
            Trace.Write("Attempting to update country: {}".format(destinCountry.name))
            RestClient.Put("{}/api/general/v1/countries/{}".format(destinUrl, rec.id), update_country_body, destinHeader)
            Trace.Write("Country {} updated".format(destinCountry.name))
    except Exception, e:
        ## Create Country record when 404 on GET
        if "404" in str(e):
            create_country_body = {
                "name": sourceCountry.name,
                "abrev3": sourceCountry.abrev3,
                "abrev2": sourceCountry.abrev2
            }
            Trace.Write("Attempting to create country: {} | record was not originally found".format(sourceCountry.name))
            RestClient.Post("{}/api/general/v1/countries".format(destinUrl), create_country_body, destinHeader)
            Trace.Write("Country {} created".format(sourceCountry.name))
        ## Log errors if it is not a 404
        else:
            Log.Error(str(e))

## States Logic
idCheck = 0
while idCheck < 3000:
    destinHeader = get_bearer(destinUrl)
    sourceHeader = get_bearer(sourceUrl)
    stateId_sql = grab_state(idCheck)
    for rec in stateId_sql:
        ## Update State record
        try:
            sourceState = RestClient.Get("{}/api/general/v1/states/{}".format(sourceUrl, rec.id), sourceHeader)
            destinState = RestClient.Get("{}/api/general/v1/states/{}".format(destinUrl, rec.id), destinHeader)
            ## Push to destination environment if different
            if destinState.name != sourceState.name or destinState.abbreviation != sourceState.abbreviation or destinState.countryId != sourceState.countryId:
                update_state_body = {
                    "id": rec.id,
                    "name": sourceState.name,
                    "abbreviation": sourceState.abbreviation,
                    "countryId": sourceState.countryId
                }
                Trace.Write("Attempting to update state: {}".format(destinState.name))
                RestClient.Put("{}/api/general/v1/states/{}".format(destinUrl, rec.id), update_state_body, destinHeader)
                Trace.Write("State {} updated".format(destinState.name))
        except Exception, e:
            ## Create State record when 404 on GET
            if "404" in str(e) or "state doesn't exist" in str(e):
                create_state_body = {
                    "name": sourceState.name,
                    "abbreviation": sourceState.abbreviation,
                    "countryId": sourceState.countryId
                }
                Trace.Write("Attempting to create state: {}".format(sourceState.name))
                RestClient.Post("{}/api/general/v1/states".format(destinUrl), create_state_body, destinHeader)
                Trace.Write("State {} created".format(sourceState.name))
            ## Log errors if it is not a 404
            else:
                Log.Error(str(e))
    idCheck += 1000