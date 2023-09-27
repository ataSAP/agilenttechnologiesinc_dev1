import datetime

def createTable(context,approvalTable,approvalData):
    #Takes the list of approver roles found and removes duplicate roles.
    #In addition finds the named user either in truvis, or in role to user mapping table.
    #Then builds the approval tables on approvals tab
    
    #truvis Data
    territory = context.Quote.GetCustomField("ZQT_TerritoryID").Value
    if territory == "" or RequestContext.Url.Host == "agilenttechnologiesinc-dev1.cpq.cloud.sap":
        territory = "44UHDE"
    truvisData = SqlHelper.GetFirst("SELECT * FROM ZQT_Truvis WHERE TerritoryId = '{0}'".format(territory))
    
    #Concatenate data
    concatApprovalData = []
    roleList = []
    for approver in approvalData:
        if approver.role not in roleList:
            roleList.append(approver.role)
            concatApprovalData.append(approver)
        else:
            for concatApprover in concatApprovalData:
                if concatApprover.role == approver.role:
                    concatApprover.type += ', ' + approver.type
    
    #Write to table
    approvalTable.Rows.Clear()
    for approver in concatApprovalData:
        newRow = approvalTable.AddNewRow()
        newRow["Type"] = approver.type
        newRow["Role"] = approver.role
        newRow["Status"] = "Pending"
        if approver.role in ["L10","L20","L30","L40"]:
            newRow["Approver"] = getattr(truvisData,approver.role)
        else:
            region = context.Quote.GetCustomField("ZQT_Region").Value
            Trace.Write(region)
            role2user = SqlHelper.GetFirst("SELECT Email from ZQT_RoleToUser WHERE Role = '{0}' AND Region = '{1}'".format(approver.role,region))
            Trace.Write("SELECT Email from ZQT_RoleToUser WHERE Role = '{0}' AND Region = '{1}'".format(approver.role,region))
            Trace.Write(role2user.Email)
            newRow["Approver"] = role2user.Email

def sales(context,approvalTable):
    #define default values
    multiUse = "No"
    brilliance = "No"
    health = 5
    YMAX = "No"
    GSA = "No"
    
    #rules
    businessUnit = context.Quote.GetCustomField("ZQT_BusinessUnit").AttributeValue[0:3]
    if context.Quote.GetCustomField("ZQT_QuoteType").AttributeValueCode == "MLU":
        multiUse = "Yes"
    health = int(context.Quote.QuoteTables["ZQT_DealMargin"].Rows[0].GetColumnValue("Deal_Score"))
    Trace.Write("SCORE IS " + str(health))
    YMAX = context.Quote.GetCustomField("ZQT_YMAXExceeded").AttributeValueCode
    brilliance = context.Quote.GetCustomField("ZQT_OverrideShipping").AttributeValueCode
    customerType = context.Quote.GetCustomField("ZQT_CustomerType").AttributeValueCode
    for party in context.Quote.GetInvolvedParties():
        if party.PartnerFunctionKey == "SP":
            spCountry = party.Country
    foundPA = False
    exceedYA9 = False
    foundPL = False
    for item in context.Quote.GetAllItems():
        if item["ZPR_Division"] in ["AZ","BZ","29","89","MA","AJ","9F","LI"]:
            foundPL = True
        if item["ZPR_Division"] == "74":
            if item.PartNumber[-1:] == "A":
                foundPL = True
        if item["ZPR_PA"] > 0:
            foundPA = True
        if item["ZPR_Division"] in ["AZ","BZ","29","89","MA","AJ","9F","LI"] and item["ZPR_YA9"] > 37:
            exceedYA9 = True
        elif item["ZPR_Division"] in ["58","AA","JW","BC","9P"] and item["ZPR_YA9"] > 36:
            exceedYA9 = True
        elif item["ZPR_Division"] in ["74"] and item["ZPR_YA9"] > 27 and item.PartNumber[-1:] == "A":
            exceedYA9 = True
    if spCountry == "US" and foundPA and customerType not in ["NPG","NPU","NPH","FPA","FPO"] and context.Quote.Totals.NetPrice < 250000 and exceedYA9 and foundPL:
        GSA = "Yes"
    
    #build where clauses
    multiUseWhere = "(type = 'Multi Use Quote' AND Value = '{0}')".format(multiUse)
    healthWhere = "OR (type = 'Discount Approval' AND ValueNum >= {0})".format(health)
    if context.Quote.GetCustomField("ZQT_SelfAttest").Value == "Yes":
        healthWhere = ""
    YMAXWhere = "(type = 'Ymax Exceeded' AND Value = '{0}')".format(YMAX)
    brillianceWhere = "(type = 'S&H Override (Brilliance)' AND Business = '{0}' AND Value = '{1}')".format(businessUnit,brilliance)
    gsaWhere = "(type = 'GSA Discount' AND Value = '{0}')".format(GSA)
    

    #get approver data
    approvalData = SqlHelper.GetList("SELECT TOP 100 type,aRank.role as role, rank from ZQT_ApprovalRules aRule JOIN ZQT_ApprovalRanking aRank ON aRULE.role = aRank.role WHERE {0} {1} OR {2} OR {3} OR {4}".format(multiUseWhere,healthWhere,YMAXWhere,brillianceWhere,gsaWhere))
    for a in approvalData:
        Trace.Write(a.type + " : " + a.role)
    
    createTable(context,approvalTable,approvalData)

def finance(context,approvalTable):
    
    #define default values
    paymentTerms = "No"
    quoteExtension = "None"
    thirdParty = "No"
    
    #rules
    allowedTerms = ["SP00","SP01","FLSP","ZCR"]
    businessUnit = context.Quote.GetCustomField("ZQT_BusinessUnit").AttributeValue[0:3]
    thirdPartyVal = context.Quote.GetCustomField("ZQT_PersonalElectronicDevices").AttributeValueCode
    defaultTerms = context.Quote.GetCustomField("ZQT_PaymentTerms_Default").AttributeValueCode
    selectedTerms = context.Quote.GetCustomField("ZQT_PaymentTerms").AttributeValueCode
    defaultExpDate = UserPersonalizationHelper.CovertToDate(context.Quote.GetCustomField("ZQT_ExpirationDate_Default").Value)
    expDate = UserPersonalizationHelper.CovertToDate(context.Quote.GetCustomField("Quote Expiration Date").Value)
    Trace.Write(expDate)
    Trace.Write(str(dir(datetime)))
    #date1 = datetime.datetime.strptime(expDate,"%d/%m/%y")
    #date2 = datetime.datetime.strptime(defaultExpDate,"%d/%m/%y")
    #datediff = (date1-date2).days
    datediff = (expDate-defaultExpDate).Days
    Trace.Write("DATEDIFF IS" + str(datediff))
    quoteTotal = context.Quote.Totals.Amount
    remarket = context.Quote.GetCustomField("ZQT_GreaterThanRapid").AttributeValueCode
    Trace.Write("Remarket is " + remarket)

    if thirdPartyVal == "Yes":
        thirdParty = "Yes"
        
    if defaultTerms != selectedTerms and selectedTerms not in allowedTerms:
        Trace.Write("diff terms")
        paymentTerms = "Yes"
        
    if (quoteTotal > 1000000 and datediff > 0) or datediff > 180:
        quoteExtension = "high"
    elif datediff > 0:
        quoteExtension = "low"

    #build where clauses
    Trace.Write("THIRD PARTY VAL IS: " + thirdPartyVal + " " + thirdParty)
    extWhere = "(type = 'Non-Standard Quote Extension' AND (Business = '{0}' or Business = '') AND Value = '{1}')".format(businessUnit, quoteExtension)
    termsWhere = "(type = 'Non-Standard Payment Terms' AND Value = '{0}')".format(paymentTerms)
    thirdPartyWhere = "(type = '3PP Electronic Device' AND Business = '{0}' AND Value = '{1}')".format(businessUnit, thirdParty)
    remarketWhere = "(type = 'Remarket Approval' AND Business = '{0}' AND Value = '{1}')".format(businessUnit, remarket)
    
    #get approver data
    approvalData = SqlHelper.GetList("SELECT TOP 100 type,aRank.role as role, rank from ZQT_ApprovalRules aRule JOIN ZQT_ApprovalRanking aRank ON aRULE.role = aRank.role WHERE {0} OR {1} OR {2} OR {3}".format(extWhere,termsWhere,thirdPartyWhere,remarketWhere))
    for a in approvalData:
        Trace.Write(a.type + " : " + a.role)
    createTable(context,approvalTable,approvalData)




def buildApproval(context):
    approvalTypes = ["Sales","Finance"]
    for approvalType in approvalTypes:
        approvalData = []
        approvalTable = context.Quote.QuoteTables["ZQT_{0}_Approvals".format(approvalType)]
        if approvalType == "Sales":
            approvalData = sales(context,approvalTable)
            Trace.Write("DONE WITH SALES")
        elif approvalType == "Finance":
            approvalData = finance(context,approvalTable)