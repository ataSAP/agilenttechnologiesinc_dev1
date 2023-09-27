from CPQ_SF_FunctionModules import is_action_allowed

CREATE = "create"
EDIT = "edit"
NEW = "new"
VIEW = "view"
## Get paramters
externalParameters = context.ExternalParameters
action = externalParameters["action"]
Session["apiSessionID"] = externalParameters["apiSessionID"]

## Set Opportunity Id in Session
try: Session["OpportunityId"] = externalParameters["opportunityid"]
except: Session["OpportunityId"] = ""

## Split logic for different actions triggered from SFDC
if action == CREATE:
    redirectionUrl = ScriptExecutor.Execute("CPQ_SF_CreateQuote", {"externalParameters": externalParameters, "createQuote": True})
elif action == EDIT:
    actionId = 13
    if is_action_allowed(QuoteHelper, User, externalParameters, actionId) == True:
        redirectionUrl = ScriptExecutor.Execute("CPQ_SF_EditQuote", {"externalParameters": externalParameters})
    else:
        redirectionUrl = ScriptExecutor.Execute("CPQ_SF_ViewQuote", {"externalParameters": externalParameters})
elif action == NEW:
    redirectionUrl = ScriptExecutor.Execute("CPQ_SF_LandingOnCatalogue")
elif action == VIEW:
    redirectionUrl = ScriptExecutor.Execute("CPQ_SF_ViewQuote", {"externalParameters": externalParameters})
elif action == "quoteslist":
    redirectionUrl = "https://{}/QuoteList".format(RequestContext.Url.Host)
else:
    Log.Error("SFDC Landing: Triggered action not found - {}".format(action))