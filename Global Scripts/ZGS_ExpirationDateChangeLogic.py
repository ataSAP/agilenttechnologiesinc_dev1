from Scripting.Quote import MessageLevel

def convertToDate(stringDate):
    return UserPersonalizationHelper.CovertToDate(stringDate)


def getCF(cfName):
    return context.Quote.GetCustomField(cfName)


def getCFValue(cfName):
    return getCF(cfName).Value


def setCFValue(cfName, valueParam):
    getCF(cfName).Value = valueParam


def addErrorMessage(stringParam):
    context.Quote.AddMessage(stringParam, MessageLevel.Error, True)



newValue = getCFValue("Quote Expiration Date")
defaultValue = getCFValue("ZQT_ExpirationDate_Default")
fieldName = context.FieldName

if fieldName == "Quote Expiration Date":
    oldValue = context.PreviousValue
else:
    oldValue = defaultValue

dateCreated = context.Quote.DateCreated
oldExpDate = convertToDate(oldValue)
newExpDate = convertToDate(newValue)
defaultExpDate = convertToDate(defaultValue)
quoteType = getCFValue("ZQT_QuoteType")


if newExpDate < dateCreated:
    messageStr = "Quote Expiration Date cannot be before Create Date. Date reverted."
    addErrorMessage(messageStr)
    setCFValue("Quote Expiration Date", oldExpDate)
elif quoteType.lower() == "mlu" and newExpDate.Year > dateCreated.Year:
    messageStr = "Select an Expiration Date within the calendar year."
    addErrorMessage(messageStr)
    setCFValue("Quote Expiration Date", oldExpDate)
else:
    expirationDateIsLate = newExpDate > dateCreated.AddDays(180)
    isLateStr = "{}".format(expirationDateIsLate)
    setCFValue("ZQT_LateExpirationDate_Flag", isLateStr)