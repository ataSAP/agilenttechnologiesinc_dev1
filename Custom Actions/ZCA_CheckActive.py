## Initial Variables
baseUrl = "https://{}".format(RequestContext.Url.Host)
if context.WorkflowContext.NewCartId: quote = QuoteHelper.Get(context.WorkflowContext.NewCartId)
else: quote = context.Quote
domain = ""
sqlQry = """SELECT end_point FROM ZCA_INTEGRATIONINFO
    WHERE cpq_url = '{}' AND end_point_key = 'CPQ Domain'
    """.format(RequestContext.Url.Host)
domain = SqlHelper.GetFirst(sqlQry).end_point

## Payload to get JWT
payload = {
    "username": User.UserName,
    "domain": domain
}
## Generate JWT via credMgmt SharedSecret
tokenParams = JwtTokenProvider.CreateParameters(payload, "SharedSecret", 300)
token = JwtTokenProvider.Generate(tokenParams)
headers = {"Authorization": "Bearer {}".format(token)}

## Call revisions API
url = "{}/api/v1/quotes/{}/revisions".format(baseUrl, quote.Id)
res = RestClient.Get(url, headers)

## Set Active CF for all quotes
for rec in res:
    quote2 = QuoteHelper.Get(rec.QuoteId)
    quote2.GetCustomField('ZQT_RevisionDescription').Value = rec.Name
    if int(rec.QuoteId) == quote.Id: quote2.GetCustomField('ZQT_RevisionDescription').Value = rec.Name
    else: quote2.GetCustomField('ZQT_IsActive').Value = ""
    quote2.Save()