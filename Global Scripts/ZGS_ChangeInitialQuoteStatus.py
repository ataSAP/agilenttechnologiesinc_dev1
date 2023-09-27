quote = context.Quote

############################
##  On quote creation via CRM, all CPQ CFs that are being populated from CRM must be Editable in order for the values to be saved.
##  Some of these fields need to be presented to the CPQ User as read-only
##  We control most editability of the CPQ CFs using the OOB features that rely on Quote Status
############################

if quote.StatusName == "aOpen":
    ## We need to use QuoteHelper here because having multiple onEdit scripts conflicts and causes QuoteAlreadyModified error
    quote2 = QuoteHelper.Get(quote.Id)
    quote2.ChangeStatus("Preparing")
    quote2.Save()
    #quote.GetCustomField("ZQT_QuoteType_Default").Value = quote.GetCustomField("ZQT_QuoteType").Value
    ScriptExecutor.Execute("ZGS_CallUpdateOpportunity")