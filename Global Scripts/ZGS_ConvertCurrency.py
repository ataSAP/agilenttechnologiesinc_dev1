def getFloat(val):
    try: x = float(val)
    except: x = 0.00
    return x

def convert_currency(val,from_currency,to_currency):
    #Trace.Write("Converting Cost to " + to_currency)
    converted_amount = getFloat(val)
    rate_data = SqlHelper.GetFirst("SELECT TOP 1 ExchangeRate, RatioFrom, RatioTo FROM ZPR_ExchangeRates WHERE FromCurrency = '{0}' AND ToCurrency = '{1}' AND ValidFrom <= GETDATE() ORDER BY ValidFrom DESC".format(from_currency,to_currency))
    if rate_data:
        try:
            converted_amount = (val/rate_data.RatioFrom)*(rate_data.ExchangeRate/rate_data.RatioTo)
        except:
            Trace.Write("Error converting Cost to " + to_currency)
    return converted_amount