def getCFValue(quote, cfNameStr):
    return quote.GetCustomField(cfNameStr).Value


def setCFValue(quote, cfNameStr, value):
    quote.GetCustomField(cfNameStr).Value = value


def getMostSpecificRow(sqlRowsList):
    orderedListOfRows = []
    for row in sqlResults:
        numberOfAny = 0
        if row.Customer_Group.lower() == "any":
            numberOfAny += 1
        if row.Sales_Org.lower() == "any":
            numberOfAny += 1
        if row.Currency.lower() == "any":
            numberOfAny += 1
        orderedListOfRows.append((numberOfAny, row))
    orderedListOfRows.sort()
    return orderedListOfRows[0][1]


def getDaysUntilExpiration(quote):
    currency = getCFValue(quote, "ZQT_Currency")
    salesOrg = quote.SelectedMarket.Code
    custGroup = getCFValue(quote, "ZQT_CustomerGroup")

    sqlCall = ("SELECT DISTINCT Customer_Group, Sales_Org, Currency, Days_Until_Expiration"
               + " FROM ZMA_ExpirationDate"
               + " WHERE Customer_Group IN ('{}', 'Any')".format(custGroup)
               + " AND Sales_Org IN ('{}', 'Any')".format(salesOrg)
               + " AND Currency IN ('{}', 'Any')".format(currency)
               )
    sqlResults = SqlHelper.GetList(sqlCall)

    daysUntilExpiration = 90 # Default amount if not found in table
    count = sqlResults.Count
    if count == 1:
        daysUntilExpiration = sqlResults[0].Days_Until_Expiration
    elif count > 1:
        specificRow = getMostSpecificRow(sqlResults)
        daysUntilExpiration = specificRow.Days_Until_Expiration
    return daysUntilExpiration


def setExpirationDate(quote):
    numDatesTilExp = getDaysUntilExpiration(quote)
    expirationDate = quote.DateCreated.AddDays(numDatesTilExp)
    setCFValue(quote, "Quote Expiration Date", expirationDate)
    setCFValue(quote, "ZQT_ExpirationDate_Default", expirationDate)