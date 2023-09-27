from CPQ_SF_IntegrationSettings import CL_CpqIntegrationParams
from CPQ_SF_OpportunityStatusMapping import opportunity_status_mapping


###############################################################################################
# Function to retrieve CPQ Business Partner on Quote
###############################################################################################
def get_quote_business_partner(Quote, partnerFuntion):
    businessPartner = next((party for party in Quote.GetInvolvedParties() if party.PartnerFunctionKey == partnerFuntion), None)
    return businessPartner


###############################################################################################
# Function to delete CPQ Business Partner on Quote by Partner Function
###############################################################################################
def del_quote_business_partner_by_function(Quote, partnerFuntion):
    for partner in filter(lambda x: x.PartnerFunctionKey == partnerFuntion,Quote.GetInvolvedParties()):
        Quote.DeleteInvolvedParty(partner.Id)


###############################################################################################
# Function to retrieve Opportunity Id attached to Quote
###############################################################################################
def get_quote_opportunity_id(Quote):
    value = None
    customField = Quote.GetCustomField(CL_CpqIntegrationParams.OPPORTUNITY_ID_FIELD)
    if customField:
        value = customField.Value
    return value


###############################################################################################
# Function to get Opportunity Name
###############################################################################################
def get_quote_opportunity_name(Quote):
    value = str()
    customField = Quote.GetCustomField(CL_CpqIntegrationParams.OPPORTUNITY_NAME_FIELD)
    if customField:
        value = customField.Value
    return value


###############################################################################################
# Function to attach opportunity id to Quote
###############################################################################################
def set_quote_opportunity_id(Quote, opportunityId):
    customField = Quote.GetCustomField(CL_CpqIntegrationParams.OPPORTUNITY_ID_FIELD)
    if customField:
        customField.Value = opportunityId


###############################################################################################
# Function to set Opportunity Name
###############################################################################################
def set_quote_opportunity_name(Quote, opportunityName):
    customField = Quote.GetCustomField(CL_CpqIntegrationParams.OPPORTUNITY_NAME_FIELD)
    if customField:
        customField.Value = opportunityName


###############################################################################################
# Function to get Salesforce Opportunity Status to be mapped
###############################################################################################
def get_opportunity_mapping_status(Quote):
    oppStatus = str()
    cpqStatus = Quote.StatusName
    statusMappings = opportunity_status_mapping()
    mappings = next((x for x in statusMappings if x["CPQ_STATUS"] == cpqStatus), None)
    if mappings:
        oppStatus = mappings["SF_STATUS"]
    return oppStatus


###############################################################################################
# Function to get Market Code based on Market Id
###############################################################################################
def get_market_code(marketId):
    marketCode = None
    sql = """SELECT market_code FROM market_defn
    WHERE market_id = '{marketId}'""".format(marketId=str(marketId))
    sqlRecord = SqlHelper.GetFirst(sql)
    if sqlRecord:
        marketCode = sqlRecord.market_code
    return marketCode


###############################################################################################
# Function to get Country abrev2 by Country abrev3 (BP country can only be set by abrev2 else error)
###############################################################################################
def get_country_code_from_abrev3(abrev3):
    countryCode = str()
    sql = """SELECT *
    FROM V_COUNTRY
    WHERE COUNTRY_ABREV3 = '{abrev3}'""".format(abrev3=str(abrev3))
    record = SqlHelper.GetFirst(sql)
    if record:
        countryCode = record.COUNTRY_ABREV2
    return countryCode
###############################################################################################
# Function to strip HTML Tags
###############################################################################################
def strip_html_tags(text):
    tag = False
    quote = False
    out = ""
    for letter in text:
        if letter == '<' and not quote:
            tag = True
        elif letter == '>' and not quote:
            tag = False
        elif (letter == '"' or letter == "'") and tag:
            quote = not quote
        elif not tag:
            out = out + letter
    return out


###############################################################################################
# Function to get number of users types which have workflow permission on an action
###############################################################################################
def get_usergroup_count(User, actionId):
    user_type_code = SqlHelper.GetFirst("""
    SELECT COUNT(1) AS count
    FROM actions_usergroups
    WHERE action_id = {actionId}
    AND user_type_code={userTypeCode}
    """.format(actionId=actionId, userTypeCode=User.UserType.Id))

    return user_type_code.count


###############################################################################################
# Function block to get tab id
# The Tab Id value e.g. 1 for My Quotes, 2 for Waiting For Approval and 3 for Other Quotes.
###############################################################################################
def get_tabid(User, ownerId):
    # My Quotes
    if User.UserType.Id == ownerId: tabId = 1
    # Other Quotes
    else: tabId = 3

    return tabId


###############################################################################################
# Function to get number of actions which have been assigned to workflow
###############################################################################################
def get_actionid_count(tabId, Quote, actionId):
    action_id = SqlHelper.GetFirst("""
        SELECT COUNT(1) AS count
        FROM actions AS actions
        JOIN actions_status AS actions_status
        ON actions.action_id = actions_status.action_id
        WHERE actions.action_id = {actionId}
        AND actions_status.start_order_status_id={statusId}
        AND actions_status.tab_id={tabId}
    """.format(actionId=actionId, statusId=Quote.StatusId, tabId=tabId))

    return action_id.count


###############################################################################################
# Function to check if user is allowed to trigger this action
###############################################################################################
def is_action_allowed(QuoteHelper, User, externalParameters, actionId):
    quoteId = externalParameters["quoteId"]
    ownerId = externalParameters["ownerId"]
    Quote = QuoteHelper.Get(float(quoteId))

    # get tab Id, whether user is on My Quote, Other Quotes
    tabId = get_tabid(User, ownerId)
    # action count = 0 when this action is not assigned on worflow
    actionCount = get_actionid_count(tabId, Quote, actionId)
    # user type count = 0 when user type does not have permission on this action
    userTypeCount = get_usergroup_count(User, actionId)

    if actionCount > 0 and userTypeCount > 0:  return True
    else: return False