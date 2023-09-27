from CPQ_SF_FunctionModules import get_quote_opportunity_id
from CPQ_SF_IntegrationMessages import CL_IntegrationMessages
from Scripting.Quote import MessageLevel

Quote = context.Quote
if get_quote_opportunity_id(Quote) == "":
    # Build Params
    externalParameters = dict()
    # Get Opportunity Id from Session
    if Session["OpportunityId"] != "":
        externalParameters["opportunityid"] = Session["OpportunityId"]
        # Trigger Create Quote Flow
        ScriptExecutor.Execute("CPQ_SF_CreateQuote", {"externalParameters": externalParameters, "createQuote": False})
else:
    Quote.AddMessage(CL_IntegrationMessages.CANNOT_ATTACH_QUOTE, MessageLevel.Warning, True)
