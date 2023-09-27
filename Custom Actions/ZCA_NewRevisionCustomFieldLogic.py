from ZGS_ExpirationDate_Module import setExpirationDate

# Tuples of fields and the values to set. Date fields require None or DateTime
fieldsAndValues = [("ZQT_EccTotalValue", ""),
                   ("ZQT_EccQuoteNumber", ""),
                   ("ZQT_EccQuoteCreationDate", None),
                   ("ZQT_PA_Number", ""),
                   ("ZQT_PricingDate", DateTime.Now)
                   ]


def setCFValue(quote, cfName, valueParam):
    quote.GetCustomField(cfName).Value = valueParam


newQuoteId = context.WorkflowContext.NewCartId
newQuote = QuoteHelper.Get(newQuoteId)
for (field, value) in fieldsAndValues:
    setCFValue(newQuote, field, value)

setExpirationDate(newQuote)

newQuote.Save()