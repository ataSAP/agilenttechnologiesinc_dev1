from CPQ_SF_Configuration import CL_CPQSettings

if Param is not None:
    # Get parameters from Salesforce generated URL
    externalParameters = Param.externalParameters
    # Set default URL for view action
    redirectionUrl = CL_CPQSettings.CPQ_URL
    quoteId = externalParameters["quoteId"]
    ownerId = externalParameters["ownerId"]
    if quoteId and ownerId:
        viewQuoteURl = "/cart/view?ownerId={ownerId}&quoteId={quoteId}".format(ownerId=str(ownerId), quoteId=str(quoteId))
        # Return redirect URL
        redirectionUrl = CL_CPQSettings.CPQ_URL + viewQuoteURl
    Result = str(redirectionUrl)