Trace.Write("CONTEXT IS" + str(dir(context)))
for item in context.AffectedItems:
    Trace.Write("Quantities are : " + str(item.Quantity) + " : " + str(item["ZPR_OriginalQuantity"]))
    item["ZPR_OriginalQuantity"] = item.Quantity
    Trace.Write("RECONFIGURING")
    Trace.Write(item.PartNumber)
    main = item.AsMainItem
    prod = main.Edit()
    Trace.Write(str(dir(prod)))
    prod.ApplyRules()
    #main.Reconfigure()
    prod.UpdateQuote()
    Trace.Write("Reconfiguring2")
Trace.Write("Reconfiguring")
#product = Item.Edit
#product.ExecuteRulesOnce
#product.UpdateQuote