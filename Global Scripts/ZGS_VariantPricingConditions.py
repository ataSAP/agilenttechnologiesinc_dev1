## Loops through newly modified items to pull out ZBCT condition types into a QT
## These are then used on the CFDs
## Event: afterProduct Add/Update/Copy/Delete
def getFloat(val):
    try: x = float(val)
    except: x = 0.00
    return x
## Add new rows to the QuoteTable Add or Copy Action
## This procedure adds the cart item itself to the QuoteTable
def addItemRow(item,parentval):
    newRow = qt.AddNewRow()
    #Check for language based fields in custom table
    #Trace.Write("Looking up long desc for " + str(item.PartNumber) + " with language " + str(qt_language))
    lang_desc = SqlHelper.GetFirst("SELECT TOP 1 MaterialDescription,LongDescription FROM ZMA_MaterialLanguage WHERE MaterialNumber = '{0}' and Language = '{1}'".format(item.PartNumber,qt_language))
    if lang_desc:
        newRow['LongDescription'] = lang_desc.LongDescription
        newRow['ProductName'] = lang_desc.MaterialDescription
    else:
        newRow['ProductName'] = item.ProductName
    #if we have an alternative description manually entered, add it to the quote table
    if item['ZPR_AlternateMaterialDescription'] != "":
        newRow['AlternateMaterialDescription'] = item['ZPR_AlternateMaterialDescription']
    #if we have an item subtitle manually entered, add it to the quote table
    if item['ZMA_ItemSubtitle'] != "":
        newRow['ItemSubtitle'] = item['ZMA_ItemSubtitle']
    newRow['ItemId'] = item.Id
    if parentval == 0:
        newRow['ParentItemId'] = str(parentval)
    newRow['RolledUpQuoteItem'] = item.RolledUpQuoteItem
    newRow['PartNumber'] = item.PartNumber
    newRow['Quantity'] = item.Quantity
    #Add info for if this is a simple or a configurable product
    if item.AsMainItem.GetChildItems().Count > 0:
        newRow['ProductDisplayType'] = "Configurable"
    else:
        newRow['ProductDisplayType'] = "Simple"
    ##This is the check for bundled intallation services -  we do not want to show the price in the CFD, so if it stars with an H and ends with an H or an S, we want to show 0.00
    if item.PartNumber[:1] == "H" and (item.PartNumber[-1] == "H" or item.PartNumber[-1] == "S"):
        #Loop back and add the bundled installation services to the parent item amounts
        parent_line_num = str(item.RolledUpQuoteItem).split('.')
        for row in qt.Rows:
            if row['RolledUpQuoteItem'] == parent_line_num[0]:
                row['ListPrice'] += item.ListPrice
                row['ExtendedAmount'] += item.ExtendedAmount
                row['DiscountAmount'] += item.DiscountAmount * -1
                break
        #Delete the parent installation line, so we only have the one
        #qt.DeleteRow(newRow.Id)
    else:
        newRow['DiscountAmount'] = item.DiscountAmount * -1
        newRow['DiscountPercent'] = item.DiscountPercent * -1
        newRow['ListPrice'] = item.ListPrice
        newRow['ExtendedAmount'] = item.ExtendedAmount
        newRow['GetUnitOfMeasure'] = item.GetUnitOfMeasure('ListPrice')
        newRow['RolledUpDiscountAmount'] = item['ZPR_RolledUpDiscountAmount'] * -1
        newRow['RolledUpListPrice'] = item['ZPR_RolledUpListPrice']
        newRow['RolledUpExtendedAmount'] = item['ZPR_RolledUpExtendedAmount']

## Add new rows to the QuoteTable Add or Copy Action
## This procedure loops through the attributes on the item and pulls the value for the ones that are found in the ZQT_PrintFlags table (Non-Priced Options) to add to the QuoteTable
def addPrintFlagRows(item):
    for attr in item.SelectedAttributes:
        attr_res = SqlHelper.GetFirst("SELECT system_id FROM attribute_defn WHERE standard_attribute_code = {0}".format(attr.StandardAttributeCode))
        flag = SqlHelper.GetFirst("SELECT CharacteristicName FROM ZQT_PrintFlags WHERE CharacteristicName = '{0}'".format(attr_res.system_id))
        if flag and flag.CharacteristicName:
            newRow = qt.AddNewRow()
            newRow['ItemId'] = item.Id
            newRow['RolledUpQuoteItem'] = item.RolledUpQuoteItem
            newRow['PartNumber'] = attr_res.system_id
            newRow['ProductName'] = "Print Flag"
            newRow['ConditionTypeDescription'] = attr.Name
            attr_values = attr.Values
            val_list = []
            for val in attr_values: val_list.append(val.Display)
            newRow['ConditionValue'] = ",".join(val_list)

## Add new rows to the QuoteTable Add or Copy Action
## This procedure loops through the Pricing Conditions on the item and pulls the value for the ones that are ZBCT (Priced Options) to add to the QuoteTable
def addConditionRows(item):
    Trace.Write("Checking ZBCT records for " + item.ProductName)
    zbct_list = 0.00
    zbct_amount = 0.00
    zbct_disount = 0.00
    for each in item.PricingConditions:
        if each.ConditionType == "ZBCT":
            newRow = qt.AddNewRow()
            newRow['ItemId'] = item.Id
            newRow['RolledUpQuoteItem'] = item.RolledUpQuoteItem
            newRow['Quantity'] = each.ConditionUnitQuantity
            newRow['ProductName'] = each.ConditionTypeDescription
            newRow['PartNumber'] = each.ConditionType
            newRow['ListPrice'] = each.ConditionValue
            newRow['DiscountAmount'] = (each.ConditionValue * item.DiscountPercent/100) * -1
            newRow['DiscountPercent'] = item.DiscountPercent * -1
            #Apply discount to the ZBCT items
            newRow['ExtendedAmount'] = each.ConditionValue + (each.ConditionValue * item.DiscountPercent/100)
            #Sum the ZBCT amounts and discounts
            zbct_list += each.ConditionValue
            zbct_amount += each.ConditionValue + (each.ConditionValue * item.DiscountPercent/100)
            zbct_disount += (each.ConditionValue * item.DiscountPercent/100) * -1
    #Loop back and subtract the ZBCT amount and discount from the parent row
    for row in qt.Rows:
        if row['RolledUpQuoteItem'] == str(item.RolledUpQuoteItem):
            row['ListPrice'] = row['ListPrice'] - round(zbct_list,2)
            row['ExtendedAmount'] = row['ExtendedAmount'] - round(zbct_amount,2)
            row['DiscountAmount'] = row['DiscountAmount'] - round(zbct_disount,2)
            break

## Check for discount values in the cart columns that contain the various discounts and display a line for each in the QuoteTable for the CFD
def getGSAInfo(item):
    if item["ZPR_GSA"] > 0 and ((custGroup == "09" and priceListType == "03") or (custGroup == "01" and priceListType == "03")):
        gsa_amt = getFloat(round((item["ZPR_RolledUpExtendedAmount"] * (item["ZPR_GSA"]/100)),2))
        discountRow = qt.AddNewRow()
        discountRow['ItemId'] = item.Id
        discountRow['RolledUpQuoteItem'] = item.RolledUpQuoteItem
        discountRow['ConditionTypeDescription'] = "Discount Text"
        if item["ZPR_GSA_NA"] != "":
            discountRow['ConditionValue'] = "GSA (" + item["ZPR_GSA_NA"] + ") Discount of {} {} applied.".format(gsa_amt, currencyCode)
        else:
            discountRow['ConditionValue'] = "GSA Discount of {} {} applied.".format(gsa_amt, currencyCode)

## Check for discount values in the cart columns that contain the various discounts and display a line for each in the QuoteTable for the CFD
def getDiscounts(item):
    discount_dict = {
        "ZPR_PA" : ["Purchase Agreement ("+ PAnum +")","%", ""],
        "ZPR_Edu" : ["Educational Agreement ("+ PAnum +")" ,"%", ""],
        "ZPR_DR" : ["Designated Reseller", "%", ""],
        "ZPR_YA9" : ["Special","%", ""],
        "ZPR_Demo" : ["Demo","%", ""],
        "ZPR_PromoAmt" : ["Promotional", "" , currencyCode],
        "ZPR_Promo" : ["Promotional", "%", ""],
        "ZPR_Y07R" : ["Promotional" ,"%", ""],
        "ZPR_AutoPromo" : ["Multi-Year Services Promotional","%", ""]
    }
    for key in discount_dict:
        if item[key] > 0:
            discountRow = qt.AddNewRow()
            discountRow['ItemId'] = item.Id
            discountRow['RolledUpQuoteItem'] = item.RolledUpQuoteItem
            discountRow['ConditionTypeDescription'] = "Discount Text"
            discountRow['ConditionValue'] = "{} Discount of {}{}{} applied.".format(discount_dict[key][0], str(round(item[key],2)), discount_dict[key][1], discount_dict[key][2])
            if key == "ZPR_Demo":
                discountRow = qt.AddNewRow()
                discountRow['ItemId'] = item.Id
                discountRow['RolledUpQuoteItem'] = item.RolledUpQuoteItem
                discountRow['ConditionTypeDescription'] = "Discount Text"
                discountRow['ConditionValue'] = "Product availability is subject to prior sales and delivery times may vary."

## Delete rows from QuoteTable if Delete Action
def delRows(items):
    for item in items:
        for row in qt.Rows:
            if row['ItemId'] == str(item.Id):
                qt.DeleteRow(row.Id)

## Insert rows for special text
def addSpecialText(item, desc, value):
    newNoteRow = qt.AddNewRow()
    newNoteRow['ItemId'] = item.Id
    newNoteRow['RolledUpQuoteItem'] = item.RolledUpQuoteItem
    newNoteRow['ConditionTypeDescription'] = desc
    newNoteRow['ConditionValue'] = value

## Insert row for subtotal
def addSubtotal(item):
    subRow = qt.AddNewRow()
    subRow['ItemId'] = item.Id
    subRow['RolledUpQuoteItem'] = item.RolledUpQuoteItem
    subRow['ConditionTypeDescription'] = "Item Subtotal"
    subRow['DiscountAmount'] = item["ZPR_RolledUpDiscountAmount"] * -1
    subRow['ExtendedAmount'] = item["ZPR_RolledUpExtendedAmount"]

## Add newRows to QuoteTable
def addRows(items):
    previousItem = None
    for num, item in enumerate(items):
        if item.ParentItemId == 0 or num == len(items):
            if previousItem:
                getGSAInfo(previousItem)
                getDiscounts(previousItem)
                addSubtotal(previousItem)
            previousItem = item
        if item.ParentItemId == 0 or item['ZPR_PricingRel'] == "X":
            addItemRow(item,item.ParentItemId)
            if item.ParentItemId == 0:
                if item.GetCustomField("ZPR_NonAgilent").Value == "X":
                    addSpecialText(item,"Disclaimer","See Non-Agilent product disclaimer.")
                if item.GetCustomField("ZPR_PLRB").Value == "X":
                    addSpecialText(item,"Disclaimer","See Remarket product disclaimer.")
                if item.GetCustomField("ZMA_ECDFlag").Value == "X":
                    addSpecialText(item,"Disclaimer","Please reference the ECD Regulatory Information and General License Registration Form below in this document.")
                if (item.GetCustomField("ZPR_GSA_NA").Value == "") and ((custGroup == "09" and priceListType == "03") or (custGroup == "01" and priceListType == "03")):
                    addSpecialText(item,"Disclaimer","Item not included in Federal Supply Schedule Contract.")
                addPrintFlagRows(item)
                addConditionRows(item)

    if previousItem:
        getGSAInfo(previousItem)
        getDiscounts(previousItem)
        addSubtotal(previousItem)

## Loop through items and only perform actions on ones that are Pricing Relevant
def calculatePricing(context):
    #Trace.Write("Begin line item quote table")
    ## Setting initial variables, we can control which item loop this way
    isCopy = removeItems = False
    if hasattr(context, 'DeletedItems'):
        items = context.DeletedItems
        removeItems = True
    elif hasattr(context, 'CopiedItems'):
        items = context.CopiedItems
        isCopy = True
    else:
        items = context.Quote.GetAllItems()

    global qt
    global qt_language
    global PAnum
    global custGroup
    global priceListType
    global currencyCode
    currencyCode = " " + context.Quote.SelectedMarket.CurrencyCode
    qt = context.Quote.QuoteTables['Products']
    #This needs to pull from wherever we determine language for CFDs
    qt_language = context.Quote.GetCustomField("ZQT_CFDLanguage").Value
    PAnum = context.Quote.GetCustomField("ZQT_PA_Number").Value
    custGroup = context.Quote.GetCustomField("ZQT_CustomerGroup").AttributeValueCode
    priceListType = context.Quote.GetCustomField("ZQT_PriceListType").AttributeValueCode
    if removeItems:
        delRows(items)
    else:
        if isCopy:
            addRows(items)
        else:
            qt.Rows.Clear()
            addRows(items)
    #Trace.Write("End line item quote table")