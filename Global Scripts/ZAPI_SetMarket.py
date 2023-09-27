## Set up initial variables
apiResp = 'Success'
respDetail = ''
response = {}
apiQuoteNumber = Param.quote
market = Param.market
currency = Param.currency
dChannel = Param.distributionchannel

## Getting quote object inline
quote = QuoteHelper.Get(apiQuoteNumber)
## Error handling for incorrect quote numbers
if not quote:
    apiResp = 'Failure'
    respDetail = 'Quote number not found.'
else:
    if market and currency:
        mrkRes = SqlHelper.GetFirst("SELECT * FROM market_defn WHERE market_code = '{}' AND currency_sign = '{}'".format(market, currency))
        if mrkRes and dChannel:
            mrkId = mrkRes.market_id
            pbRes = SqlHelper.GetFirst("SELECT * FROM pricebooktabledefn WHERE marketid = {} AND distributionchannel = '{}'".format(mrkId, dChannel))
            pbId = pbRes.Id
        else:
            apiResp = 'Failure'
            respDetail = 'No market or distribution channel found'
    else:
        mrkId = quote.SelectedMarket.Id
        pbId = quote.PricebookId
    if mrkId and pbId and dChannel:
        quote.SetMarket(mrkId, pbId)
    else:
        apiResp = 'Failure'
        respDetail = 'Market, Currency, and DistributionChannel combination not found'

## Send back a response
response['message'] = apiResp
if respDetail: response['error'] = respDetail
ApiResponse = ApiResponseFactory.JsonResponse(response)