import sys
from Scripting.Quote import MessageLevel

## Set float
def getFloat(val):
    try: return float(val)
    except: return 0.00

## Initial Variables
quote = context.Quote
if quote.GetCustomField('ZQT_QuoteType').Value != "BUD":
    excludedList = [] #excludedList = ["G_REF_VBAP_KWMENG"]
    eccCounter = taxAmt = foundError = 0
    post_error = ""
    integrationDict = {}
    prcDict = {}
    qicfDict = {}
    dateDict = {}
    textDict = {}
    intgQry = """SELECT end_point_key, end_point
        FROM ZCA_INTEGRATIONINFO
        WHERE cpq_url = '{}'
        """.format(RequestContext.Url.Host)
    for row in SqlHelper.GetList(intgQry): integrationDict[row.end_point_key] = row.end_point
    baseUrl = "https://{}".format(RequestContext.Url.Host)
    cpiUrl = integrationDict['CPI ECC Quote']
    tokenUrl = integrationDict['CPI Token']
    qicfRes = SqlHelper.GetList("""SELECT cpq_name, field_type, ecc_field_name FROM zqt_eccfieldmapping WHERE field_level = 'item'""")
    if qicfRes:
        qicfDict["date"] = []
        qicfDict["text"] = []
        for qicf in qicfRes:
            if qicf.field_type == "date": dateDict[qicf.cpq_name] = qicf.ecc_field_name
            else: textDict[qicf.cpq_name] = qicf.ecc_field_name
        qicfDict["date"].append(dateDict)
        qicfDict["text"].append(textDict)
    pricingRes = SqlHelper.GetList("""SELECT cpq_name, ecc_field_name FROM zqt_eccfieldmapping WHERE field_level = 'pricingFields'""")
    for prc in pricingRes: prcDict[prc.cpq_name] = prc.ecc_field_name
    user_res = SqlHelper.GetFirst("SELECT username FROM users WHERE id = '{}'".format(quote.OwnerId))
    if user_res: username = user_res.username
    else: username = User.UserName

    ## Generate CPI OAuth
    credResult = AuthorizedRestClient.GetClientCredentialsGrantOAuthToken('CPQCPI_NP_OAUTH', tokenUrl, True)
    cpiHeader = {"Authorization":"Bearer {}".format(credResult.access_token)}

    ## Payload to get JWT
    payload = {
        "username": username,
        "domain": integrationDict['CPQ Domain']
    }

    ## Generate JWT via credMgmt SharedSecret
    tokenParams = JwtTokenProvider.CreateParameters(payload, "SharedSecret", 300)
    token = JwtTokenProvider.Generate(tokenParams)
    cpqHeader = {"Authorization": "Bearer {}".format(token)}

    ## GET standard Quotes API
    url = "{}/api/v1/quotes/{}".format(baseUrl, quote.Id)
    res = RestClient.Get(url, cpqHeader)

    ## Generate QuoteItems
    itemsDict = {}
    for item in quote.GetAllItems():
        if item.ParentItemId == 0 and item.AsMainItem.HasCompleteConfiguration:
            if item.QuoteItem == 1:
                ## Store configurable products (name is set because of CPI)
                itemsDict["QuoteItems"] = {}
                itemsDict["QuoteItems"]["row"] = []
                ## Store simple products (name is set because of CPI)
                itemsDict["SimpleProducts"] = {}
                itemsDict["SimpleProducts"]["row"] = []
            itemDict = {}
            itemDict["ItemId"] = item.Id
            itemDict["ItemNumber"] = item.QuoteItem
            itemDict["ExternalConfigurationItemId"] = item.QuoteItem
            itemDict["ParentItemId"] = item.ParentItemId
            itemDict["ParentItemNumber"] = item.ParentItemId
            itemDict["RolledUpItemNumber"] = item.RolledUpQuoteItem
            itemDict["IsMainItem"] = not item.IsLineItem
            itemDict["Quantity"] = int(item.Quantity)
            itemDict["UnitOfMeasure"] = item.GetUnitOfMeasure("ListPrice")
            itemDict["PartNumber"] = item.PartNumber
            itemDict["ProductSystemId"] = item.ProductSystemId
            itemDict["ProductId"] = item.ProductId

            ## Technically a QICF but CPI wants it as an item node
            for qicf in qicfDict:
                if qicf == "date":
                    for date in qicfDict["date"][0]:
                        if item[date]: itemDict[qicfDict["date"][0][date]] = item[date].ToString("yyyy-MM-dd")
                        else: itemDict[date] = ""
                else:
                    for text in qicfDict["text"][0]:
                        if item[text]: itemDict[qicfDict["text"][0][text]] = item[text]

            ## Separate out the pricing QICFs
            pricingFields = []
            for prc in prcDict:
                if getFloat(item[prc]) > 0:
                    pricingFields.append({"Name": prcDict[prc],"Content":getFloat(item[prc]), "RolledUpItemNumber":item.RolledUpQuoteItem})
            if len(pricingFields) > 0: itemDict["CustomFields"] = pricingFields

            ## Loop through SelectedAttributes and adds them to a list
            characteristicsList = []
            extConfig = JsonHelper.Deserialize(item.ExternalConfiguration)
            if extConfig != None:
                for attr in extConfig['rootItem']['characteristics']:
                    attrDict = {}
                    attrDict["SystemId"] = attr['id']
                    attrDict["ValueDataType"] = attr['type']
                    attrDict["Values"] = []
                    for val in attr['values']:
                        valDict = { "Value":val["value"], "Author":val["author"] }
                        attrDict["Values"].append(valDict)
                    if attr['id'] not in excludedList: characteristicsList.append(attrDict)
            isConfigurable = len(characteristicsList) > 0
            if isConfigurable: itemDict["SelectedAttributes"] = characteristicsList
            itemDict["Configurable"] = isConfigurable
            ## Append Item Info
            if isConfigurable: itemsDict["QuoteItems"]["row"].append(itemDict)
            else: itemsDict["SimpleProducts"]["row"].append(itemDict)

    ## Merge GET Quotes result with itemsDict
    post_dict = {"ns0:Message1": {"Quotes": res}}
    if "QuoteItems" in itemsDict:
        post_dict["ns0:Message2"] = {"QuoteItems": itemsDict["QuoteItems"]}
    if "SimpleProducts" in itemsDict:
        post_dict["ns0:Message3"] = {"SimpleProducts": itemsDict["SimpleProducts"]}

    def setErrors(line_rec):
        global foundError
        global eccTable
        if foundError == 0:
            foundError = 1
            if context.Quote.StatusName == "Preparing": quote.AddMessage("S&H Calculation Failed", MessageLevel.Error, True)
            else: context.Quote.ChangeStatus("ECC Failed")
        newRow = eccTable.AddNewRow()
        newRow["ZMessage_Type"] = line_rec.TYPE
        newRow["ZMessage"] = line_rec.MESSAGE
        newRow["ZMessage_V1"] = line_rec.MESSAGE_V1
        newRow["ZMessage_V2"] = line_rec.MESSAGE_V2
        newRow["ZMessage_V3"] = line_rec.MESSAGE_V3
        newRow["ZMes_Parameter"] = line_rec.PARAMETER
        newRow["ZMessage_Date"] = DateTime.Now

    ## Function to set QICFs from ECC
    def setTax(lineItem, tax_rec):
        lineItem["ZPR_TAX_AMT_1"] = getFloat(tax_rec.TAX_AMT_1)
        lineItem["ZPR_TAX_AMT_2"] = getFloat(tax_rec.TAX_AMT_2)
        lineItem["ZPR_TAX_AMT_3"] = getFloat(tax_rec.TAX_AMT_3)
        lineItem["ZPR_TAX_PCT_1"] = getFloat(tax_rec.TAX_PCT_1)
        lineItem["ZPR_TAX_PCT_2"] = getFloat(tax_rec.TAX_PCT_2)
        lineItem["ZPR_TAX_PCT_3"] = getFloat(tax_rec.TAX_PCT_3)
        return getFloat(tax_rec.TAX_AMT_1) + getFloat(tax_rec.TAX_AMT_2) + getFloat(tax_rec.TAX_AMT_3)

    ## Function to set ECC response
    def setLineEcc(item_rec):
        global taxAmt
        global eccCounter
        itemNum = int(item_rec.ITM_NUMBER)
        if itemNum % 1000 == 0:
            eccCounter += 1
            item = quote.GetItemByItemNumber(eccCounter)
            taxAmt += setTax(item, item_rec)
            for child in item.AsMainItem.GetChildItems():
                eccCounter += 1
                for each2 in ecc_res.Response.Quote_Item.Item:
                    childNum = int(each2.ITM_NUMBER) - itemNum
                    if (0 < childNum < 1000) and (child.PartNumber == str(each2.MATERIAL)):
                        taxAmt += setTax(child, each2)
                        break

    ## POST to CPI
    try: ecc_res = RestClient.Post(cpiUrl, post_dict, cpiHeader)
    except Exception as e: post_error = "ZCA_SendQuote: {} | Line#: {}".format(e, sys.exc_traceback.tb_lineno)

    ## If no issues posting to CPI then run ECC return logic
    if not post_error:
        eccTable = context.Quote.QuoteTables["ECC_Messages"]
        eccTable.Rows.Clear()
        if hasattr(ecc_res.Response, "log") and hasattr(ecc_res.Response.log, "line"):
            if "{}".format(type(ecc_res.Response.log.line)) != "<type 'JObject'>":
                ## Error handling from ECC response
                for each in ecc_res.Response.log.line:
                    if each.MESSAGE != "" and each.TYPE != "I":
                        setErrors(each)
            else:
                setErrors(ecc_res.Response.log.line)
        if foundError == 0:
            if context.Quote.StatusName == "Preparing":
                quote.AddMessage("S&H Calculated", MessageLevel.Success, True)
            else:
                quote.AddMessage("Send Quote Action: Success!", MessageLevel.Success, True)
            #else:
                #quote.AddMessage("ECC Success", MessageLevel.Success, True)
                #context.Quote.ChangeStatus("ECC Success")
            ## If no errors from ECC, write values to CPQ
            quote.GetCustomField("ZQT_PA_Number").Value = ecc_res.Response.Quote_Header.PA_NUMBER
            quote.GetCustomField("ZQT_EccQuoteNumber").Value = ecc_res.Response.Quote_Header.QUOTE_NUM
            quote.GetCustomField("ZQT_EccQuoteCreationDate").Value = DateTime.Now
            quote.GetCustomField("ZQT_DeliveryTimeLOV").Value = ecc_res.Response.Quote_Header.DelivTime
            quote.GetCustomField("ZQT_EccTotalValue").Value = "{:.2f}".format(float(ecc_res.Response.Quote_Header.TOTAL_VALUE))
            quote.GetCustomField("ZQT_ShippingHandlingAmt").Value = "{:.2f}".format(float(ecc_res.Response.Quote_Header.SHIPPING_HANDLING_AMT))
            if "{}".format(type(ecc_res.Response.Quote_Item.Item)) == "<type 'JArray'>":
                for each in ecc_res.Response.Quote_Item.Item:
                    setLineEcc(each)
            elif ecc_res.Response.Quote_Item == "":
                pass
            else:
                setLineEcc(ecc_res.Response.Quote_Item.Item)
            quote.GetCustomField('ZQT_EstimatedTaxesAmt').Value = taxAmt
            ScriptExecutor.Execute("ZGS_CallRebuildProductsQuoteTable")

    ## Display POST Errors
    if post_error:
        quote.AddMessage("Send Quote Failed because of POST Error: {}".format(e), MessageLevel.Error, True)
        Log.Error(post_error)