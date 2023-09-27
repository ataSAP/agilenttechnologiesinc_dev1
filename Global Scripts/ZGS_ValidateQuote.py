def addErrorWarningRow(table,name,message,level,itemid,rolledupid,partnum):
    error_warning_row = table.AddNewRow()
    error_warning_row["ErrorText"] = "'" + str(name) + "' " + message
    error_warning_row["Level"] = level
    error_warning_row['ItemId'] = itemid
    error_warning_row['RolledUpQuoteItem'] = rolledupid
    error_warning_row['PartNumber'] = partnum

context.Quote.GetCustomField("ZQT_ECDFlag").Value = "No"
error_table = context.Quote.QuoteTables["ZQT_QuoteErrors"]
error_table.Rows.Clear()
warning_table = context.Quote.QuoteTables["ZQT_QuoteWarnings"]
warning_table.Rows.Clear()
material_error_codes = {
        "B0": "Design; Engineering",
        "J1": "Pre-rel;ReadyPricing",
        "R1": "Qt/Ord Block-Factory",
        "S1": "Discon;Delivery Only",
        "S4": "ReferCust.to Supelco",
        "S5": "Discon;No QT;OrdOnly",
        "Y0": "Discon/ObsoleteFully",
        "Z0": "Invalid-this country",
        "ZZ": "DO NOT ship Internat"
    }
material_warning_codes = {
        "J0": "Pre-rel;Test'gDesign",
        "S0": "Discon/Recent;Warn'g",
        "S2": "Discon; Demo"
    }

for item in context.Quote.GetAllItems():
    #Check for incomplete items
    if not item.AsMainItem.HasCompleteConfiguration:
        addErrorWarningRow(error_table,item.ProductName,"has an incomplete configuration. Please correct this item to proceed with your quote.","Error",item.Id,item.RolledUpQuoteItem,item.PartNumber)
    #Add error if there is no Item Category for a parent item - this item cannot be sold as a main item
    if item.ParentItemId == 0:
        #Check if we have an Inconsistent message resulting from a VC Conflict
        extConfig = JsonHelper.Deserialize(item.ExternalConfiguration)
        if extConfig['consistent'] == False:
            addErrorWarningRow(error_table,item.ProductName,"has an inconsistent/invalid configuration. Please correct this item to proceed with your quote.","Error",item.Id,item.RolledUpQuoteItem,item.PartNumber)
        #Check for ECD Flag
        ecd_flag = SqlHelper.GetFirst("SELECT MaterialNumber,ECDOption FROM ZMA_ECDMaterials WHERE MaterialNumber = '{0}'".format(item.PartNumber))
        if ecd_flag and ecd_flag.MaterialNumber:
            #Trace.Write("Found ECD flag for " + str(ecd_flag.MaterialNumber))
            #if we find a record in the table with no value for ECDOption, then the entire parent part number is flagged as ECD
            if ecd_flag.ECDOption == "":
                item["ZMA_ECDFlag"] = "X"
                context.Quote.GetCustomField("ZQT_ECDFlag").Value = "Yes"
            #if we find a record in the table that does have a value for ECDOption, we need to loop through all the attributes on the parent and see if we have the selected characteristic value
            else:
                for attr in item.SelectedAttributes:
                    attr_values = attr.Values
                    for val in attr_values:
                        if val.ValueCode in ecd_flag.ECDOption.split(","):
                            #Trace.Write("Found ECD option for " + str(attr.Name) + ": " + str(val.ValueCode))
                            item["ZMA_ECDFlag"] = "X"
                            context.Quote.GetCustomField("ZQT_ECDFlag").Value = "Yes"
                            break
        if item["ZPR_ItemCategory"] == "" or item["ZPR_ItemCategory"] is None:
            addErrorWarningRow(error_table,item.ProductName,"cannot be sold as a stand-alone item. Please remove this item to proceed with your quote.","Error",item.Id,item.RolledUpQuoteItem,item.PartNumber)
        else:
            #Check for material status errors and warnings if the main item is valide
            if item["ZPR_MaterialStatus"] in material_error_codes:
                addErrorWarningRow(error_table,item.ProductName,"cannot be used on the quote due to the material status of '" + material_error_codes[item["ZPR_MaterialStatus"]] + "'.","Error",item.Id,item.RolledUpQuoteItem,item.PartNumber)
            if item["ZPR_MaterialStatus"] in material_warning_codes:
                addErrorWarningRow(warning_table,item.ProductName,"has a material status of '" + material_warning_codes[item["ZPR_MaterialStatus"]] + "'.","Warning",item.Id,item.RolledUpQuoteItem,item.PartNumber)
    else:
        #Check for material status errors and warnings for non-main items
        if item["ZPR_MaterialStatus"] in material_error_codes:
            addErrorWarningRow(error_table,item.ProductName,"cannot be used on the quote due to the material status of '" + material_error_codes[item["ZPR_MaterialStatus"]] + "'.","Error",item.Id,item.RolledUpQuoteItem,item.PartNumber)
        if item["ZPR_MaterialStatus"] in material_warning_codes:
            addErrorWarningRow(warning_table,item.ProductName,"has a material status of '" + material_warning_codes[item["ZPR_MaterialStatus"]] + "'.","Warning",item.Id,item.RolledUpQuoteItem,item.PartNumber)

#set quote level custom field to indicate quote has errors if the errors quote table has rows
if error_table.Rows.Count > 0:
    context.Quote.GetCustomField("ZQT_HasErrors").Value = "Yes"
else:
    context.Quote.GetCustomField("ZQT_HasErrors").Value = "No"
