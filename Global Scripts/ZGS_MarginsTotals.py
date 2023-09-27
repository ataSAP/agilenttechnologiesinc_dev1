import ZGS_ConvertCurrency as ZGS_ConvertCurrency

def getFloat(val):
    try: return float(val)
    except: return 0.00

def getDealScore(margin,deal_zero_margin,deal_10_margin,deal_20_margin,deal_30_margin):
    # Calculate Deal score and color
    if margin > deal_zero_margin:
        dealScore = 5
        color = "green"
    elif margin > deal_10_margin:
        dealScore = 4
        color = "yellow"
    elif margin > deal_20_margin:
        dealScore = 3
        color = "orange"
    elif margin > deal_30_margin:
        dealScore = 2
        color = "red"
    else:
        dealScore = 1
        color = "red"
    return dealScore,color

def buildMargins(context):
    excludedParts = ["NON AGILENT PROD","NONAGILENTPROD","NON-AGILENT-OT","NON-AGILENT-14686","NON-AGILENT-04686","NON AGILENT DROP"]
    ## Get user territory for margin 0/00
    #Uncomment this line and the next to pull the actual territory id from the quote
    #territory_id = context.Quote.GetCustomField("ZQT_TerritoryID").Value
    #Comment out the next line to remove hard coded territory id
    quote_currency = context.Quote.SelectedMarket.CurrencyCode
    territory_id = "44UHDE"
    zero_margin_setting = "00"
    territory_role = SqlHelper.GetFirst("SELECT TOP 1 TerritoryRole FROM ZQT_Truvis WHERE TerritoryId = '{0}'".format(territory_id))
    if territory_role:
        if territory_role.TerritoryRole == "MR":
            zero_margin_setting = "0"
    zero_margin_level = "ZPR_Level" + zero_margin_setting + "Margin"
    ## Reset CFD PL logic
    context.Quote.GetCustomField("ZQT_CFDContainsNonAgilent").Value = "Hide"
    context.Quote.GetCustomField("ZQT_CFDContainsPLRB").Value = "Hide"
    parent_item = None
    ## Calculate rolled up amounts/items
    ymaxExceeded = 0
    marginData = []
    marginDict = {}
    for item in context.Quote.GetAllItems():
        Trace.Write(item.PartNumber)
        #Cost calc
        if item["ZPR_Cost"] == 0:
            if item["ZPR_Division"] == "74":
                item["ZPR_Cost"] = item.ListPrice * .355
                #Trace.Write("TESTINGCOST PL 74 for item {0} using basis {1} calculated cost is {2}".format(item.PartNumber,item.ListPrice,item["ZPR_Cost"]))
                #Trace.Write("TESTINGCOST RETURNS: LIST {0}, NET {1}".format(item.ListPrice,item.NetPrice))
                #Trace.Write("TESTINGCOST {0}".format(str(item)))
            elif item["ZPR_Division"] == "LI":
                item["ZPR_Cost"] = 1
            elif item["ZPR_Division"] == "FS":
                item["ZPR_Cost"] = item.Quantity * .365
                #Trace.Write("PL FS for item {0} using basis {1} calculated cost is {2}".format(item.PartNumber,item.ListPrice,item["ZPR_Cost"]))
            #Convert cost if not USD
            if quote_currency != "USD":
                usd_value = item["ZPR_Cost"]
                item["ZPR_Cost"] = ZGS_ConvertCurrency.convert_currency(usd_value,"USD",quote_currency)
        #Ymax calc
        for condition in item.PricingConditions:
            if condition.ConditionType == "YMAX" and condition.InactiveFlag == " ":
                if item["ZPR_YA9"] > item["ZPR_YMAX"]:
                    ymaxExceeded = 1
        item["ZPR_RolledUpCost"] = 0.00
        item["ZPR_RolledUpListPrice"] = 0.00        
        item["ZPR_RolledUpDiscountAmount"] = 0.00
        item["ZPR_RolledUpExtendedAmount"] = 0.00
        marginRolledUpCost = 0.00
        marginRolledUpExtended = 0.00
        ## Calcluate Discount Percent, as it is not returned from CPS
        if item.ExtendedListPrice > 0:
            item.DiscountPercent = (item.DiscountAmount / item.ExtendedListPrice) * 100
        ## Calculate rolled up fields
        if item.ParentItemId == 0:
            if marginDict != {}:
                marginData.append(marginDict)
            marginDict = {"Id":item.Id,"Amount":0.00,"Cost":0.00}
            if item.PartNumber not in excludedParts:
                Trace.Write("Adding Part {0} to margin".format(item.PartNumber))
                #Trace.Write(str(marginDict))
                marginDict["Amount"] += getFloat(item.ExtendedAmount)
                marginDict["Cost"] += getFloat(item["ZPR_Cost"])
            #Trace.Write("MarginDict is {0}".format(str(marginDict)))
            parent_item = context.Quote.GetItemByItemId(item.Id)
            item["ZPR_RolledUpListPrice"] = getFloat(item.ListPrice)
            item["ZPR_RolledUpDiscountAmount"] = getFloat(item.DiscountAmount)
            item["ZPR_RolledUpExtendedAmount"] = getFloat(item.ExtendedAmount)
            item["ZPR_RolledUpCost"] = getFloat(item["ZPR_Cost"])            
        else:
            #Trace.Write("SubItem")
            parent_item["ZPR_RolledUpListPrice"] += getFloat(item.ListPrice)
            parent_item["ZPR_RolledUpDiscountAmount"] += getFloat(item.DiscountAmount)
            parent_item["ZPR_RolledUpExtendedAmount"] += getFloat(item.ExtendedAmount)
            parent_item["ZPR_RolledUpCost"] += getFloat(item["ZPR_Cost"])
            #Trace.Write("Checking item " + item.PartNumber)
            if item.PartNumber not in excludedParts:
                Trace.Write("Adding Part {0} to margin".format(item.PartNumber))
                #Trace.Write(str(marginDict))
                marginDict["Amount"] += getFloat(item.ExtendedAmount)
                marginDict["Cost"] += getFloat(item["ZPR_Cost"])
                Trace.Write(marginDict["Amount"])
            else:
                Trace.Write("Excluding Part {0}".format(item.PartNumber))
                #pass
        Trace.Write(marginDict["Amount"])
        # Check for Non-Agilent and RB products
        if item["ZPR_Division"] == "6G":
            parent_item["ZPR_NonAgilent"] = "X"
            context.Quote.GetCustomField("ZQT_CFDContainsNonAgilent").Value = "Show"
        elif item["ZPR_Division"] == "RB":
            parent_item["ZPR_PLRB"] = "X"
            context.Quote.GetCustomField("ZQT_CFDContainsPLRB").Value = "Show"
        #Trace.Write("ScriptTesting Rolled Up Item" + str(item.RolledUpQuoteItem))
    if marginDict != {}:
        marginData.append(marginDict)
        Trace.Write("MarginData {0}".format(str(marginData)))
    ## Do calculations
    totalMarginCost = totalMarginAmount = totalExtendedAmount = totalCost = deal_0_00_margin = deal_10_margin = deal_20_margin = deal_30_margin = item_margin = 0.00
    if ymaxExceeded == 1:
        context.Quote.GetCustomField("ZQT_YMAXExceeded").Value = "Yes"
    else:
        context.Quote.GetCustomField("ZQT_YMAXExceeded").Value = "No"
    for item in context.Quote.GetAllItems():
        if item.ParentItemId == 0:
            #Calculate line item margin and deal health
            #item_margin = item["ZPR_RolledUpExtendedAmount"] - (item["ZPR_RolledUpCost"]*item.Quantity)
            for marginItem in marginData:
                if marginItem["Id"] == item.Id:
                    item_margin = marginItem["Amount"] - (marginItem["Cost"] * item.Quantity)
                    item["ZPR_ItemMargin"] = item_margin
                    item_deal_0_00_margin = ((marginItem["Cost"] * item.Quantity) / (1 - float(item[zero_margin_level])) - (marginItem["Cost"] * item.Quantity))
                    item_deal_10_margin = ((marginItem["Cost"] * item.Quantity) / (1 - float(item["ZPR_Level10Margin"])) - (marginItem["Cost"] * item.Quantity))
                    item_deal_20_margin = ((marginItem["Cost"] * item.Quantity) / (1 - float(item["ZPR_Level20Margin"])) - (marginItem["Cost"] * item.Quantity))
                    item_deal_30_margin = ((marginItem["Cost"] * item.Quantity) / (1 - float(item["ZPR_Level30Margin"])) - (marginItem["Cost"] * item.Quantity))
                    item_score,item_color = getDealScore(item_margin,item_deal_0_00_margin,item_deal_10_margin,item_deal_20_margin,item_deal_30_margin)
                    item["ZPR_ItemDealHealth"] = item_color
                    #Total up margin information for the total Quote
                    deal_0_00_margin += item_deal_0_00_margin
                    deal_10_margin += item_deal_10_margin
                    deal_20_margin += item_deal_20_margin
                    deal_30_margin += item_deal_30_margin
                    ## calculate totals
                    totalCost += (item["ZPR_RolledUpCost"]*item.Quantity)
                    totalExtendedAmount += item["ZPR_RolledUpExtendedAmount"]
                    totalMarginCost += marginItem["Cost"]
                    totalMarginAmount += marginItem["Amount"]
    context.Quote.Totals.Amount = totalExtendedAmount
    #totalMargin = totalExtendedAmount - totalCost
    totalMargin = totalMarginAmount - totalMarginCost
    Trace.Write("Amount = {0}, Cost = {1}".format(totalMarginAmount,totalMarginCost))
    marginPercent = 0.00
    if totalExtendedAmount:
        #marginPercent = totalMargin / totalExtendedAmount * 100
        marginPercent = totalMargin / totalMarginAmount * 100

    # Calculate Deal score and color
    dealScore,color = getDealScore(totalMargin,deal_0_00_margin,deal_10_margin,deal_20_margin,deal_30_margin)
    context.Quote.GetCustomField("ZQT_MarginHealth").Value = dealScore

    # Build table
    table = context.Quote.QuoteTables["ZQT_DealMargin"]
    table.Rows.Clear()
    amountRow = table.AddNewRow()
    percentageRow = table.AddNewRow()

    amountRow["Type"] = "Deal Margin $"
    percentageRow["Type"] = "Deal Margin %"

    amountRow["Color"] = color
    percentageRow["Color"] = color

    amountRow["Deal_Score"] = dealScore
    percentageRow["Deal_Score"] = dealScore

    amountRow["Deal_Standard_Margin"] = totalMargin
    percentageRow["Deal_Standard_Margin"] = marginPercent

    amountRow["Deal_Level_00_Margin"] = deal_0_00_margin
    percentageRow["Deal_Level_00_Margin"] = (deal_0_00_margin) / (deal_0_00_margin + totalMarginCost) * 100

    amountRow["Deal_Level_10_Margin"] = deal_10_margin
    percentageRow["Deal_Level_10_Margin"] = (deal_10_margin) / (deal_10_margin + totalMarginCost) * 100

    amountRow["Deal_Level_20_Margin"] = deal_20_margin
    percentageRow["Deal_Level_20_Margin"] = (deal_20_margin) / (deal_20_margin + totalMarginCost) * 100

    amountRow["Deal_Level_30_Margin"] = deal_30_margin
    percentageRow["Deal_Level_30_Margin"] = (deal_30_margin) / (deal_30_margin + totalMarginCost) * 100