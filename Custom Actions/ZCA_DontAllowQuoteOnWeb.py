#context.Quote.GetCustomField("ZQT_NoDisplayWeb").Value = "No"
plDict = {}
pl_res = SqlHelper.GetList("""SELECT pl FROM zma_productlineexclusions
  WHERE dontallowquoteonweb = 1 AND country != '{}'
  """.format(context.Quote.GetCustomField("ZQT_SoldToPartyCountry").Value))
if pl_res:
    for rec in pl_res:
        if rec.pl not in plDict: plDict[rec.pl] = ""

    Trace.Write("Checking Don't Allow Quote on Web PLs")
    for item in context.Quote.GetAllItems():
        if item["ZPR_Division"] in plDict:
            context.Quote.GetCustomField("ZQT_NoDisplayWeb").Value = "Yes"
            break