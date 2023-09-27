for item in context.Quote.GetAllItems():
    if item.ParentItemId == 0:
        item["ZPR_YA9"] = context.Quote.GetCustomField("ZQT_BulkYA9").Value