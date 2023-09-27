from ZQS_ExpirationDate_Module import setExpirationDate

if getCFValue("Quote Expiration Date") == "" or context.PartnerFunctionKey in ["SP"]:
    setExpirationDate(context.Quote)