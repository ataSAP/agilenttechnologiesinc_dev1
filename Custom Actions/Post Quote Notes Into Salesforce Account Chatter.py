from CPQ_SF_IntegrationMessages import CL_IntegrationMessages, CL_MessageHandler
from CPQ_SF_IntegrationModules import CL_SalesforceIntegrationModules
from CPQ_SF_IntegrationSettings import CL_SalesforceIntegrationParams
from CPQ_SF_FunctionModules import get_quote_opportunity_id
from Scripting.Quote import MessageLevel

Quote = context.Quote
opportunityId = get_quote_opportunity_id(Quote)
class_msg_handler = CL_MessageHandler(Quote, Session)
if opportunityId:
    if Quote.Comment:
        postComment = False
        if Session["accountComment"]:
            if Session["accountComment"]["QuoteId"] != Quote.Id or Session["accountComment"]["UserId"] != Quote.OwnerId or Session["accountComment"]["Comment"] != Quote.Comment:
                postComment = True
        else:
            postComment = True
        if postComment:
            class_sf_integration_modules = CL_SalesforceIntegrationModules(Quote, Session)
            bearerToken = class_sf_integration_modules.get_auth2_token()
            # Get Opportunity
            response = class_sf_integration_modules.get_sobject(bearerToken, CL_SalesforceIntegrationParams.SF_OPPORTUNITY_OBJECT, opportunityId)
            if response:
                # Get Opportunity Account Id
                accountId = str(response["AccountId"])
                if accountId:
                    text = "QuoteId #{quoteNumber}: {text}".format(quoteNumber=str(Quote.QuoteNumber), text=unicode(Quote.Comment))
                    response = class_sf_integration_modules.post_notes_into_chatter(bearerToken, accountId, text)
                    Session["accountComment"] = {"QuoteId": Quote.Id, "UserId": Quote.OwnerId, "Comment": Quote.Comment}
else:
    class_msg_handler.add_message(CL_IntegrationMessages.NO_OPPORTUNITY_ATTACHED, MessageLevel.Error)