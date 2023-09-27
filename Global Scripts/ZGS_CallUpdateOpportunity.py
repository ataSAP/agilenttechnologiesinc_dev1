from Scripting.Quote import MessageLevel

quote = context.Quote
if quote.StatusName != "aOpen":
    baseUrl = "https://{}".format(RequestContext.Url.Host)
    domain = ""
    sqlQry = """SELECT end_point FROM ZCA_INTEGRATIONINFO
        WHERE cpq_url = '{}' AND end_point_key = 'CPQ Domain'
        """.format(RequestContext.Url.Host)
    domain = SqlHelper.GetFirst(sqlQry).end_point
    action_id = 0

    ## Payload to get JWT
    payload = {
        "username": User.UserName,
        "domain": domain
    }

    ## Generate JWT via credMgmt SharedSecret
    tokenParams = JwtTokenProvider.CreateParameters(payload, "SharedSecret", 300)
    token = JwtTokenProvider.Generate(tokenParams)
    headers = {"Authorization": "Bearer {}".format(token)}

    ## Get available Quote Actions
    action_url = "{}/api/v1/quotes/{}/actions".format(baseUrl, quote.Id)
    action_res = RestClient.Get(action_url, headers)
    for each in action_res:
        if each.SystemId == "updateOpportunity_cpq":
            action_id = each.Id
            break

    if action_id:
        ## Call InvokeAction API
        url = "{}/api/v1/quotes/{}/actions/{}/invoke".format(baseUrl, quote.Id, action_id)
        res = RestClient.Post(url, "", headers)
    else:
        context.Quote.AddMessage("Update Opportunity: Failed, no action found", MessageLevel.Warning, True)