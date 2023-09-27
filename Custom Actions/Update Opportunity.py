import sys
import datetime
from Scripting.Quote import MessageLevel

#CRM Methods

## Recursive Method
def get_val(rec, counter, nested_obj):
    counter -= 1
    if rec.seq_name and counter > 0:
        parent_obj = SqlHelper.GetFirst("""SELECT * FROM zqt_crmfieldmapping
        WHERE seq_name = '{}' AND seq_level = {}
        """.format(rec.seq_name, counter))
        val = get_val(rec, counter, getattr(nested_obj, parent_obj.field_name))
    else:
        val = getattr(nested_obj, rec.field_name)
        if rec.field_type == "float": val = round(val, 2)
    return val

## Update to date from datetime (YYYY-MM-DD)
def convert_date(date_value):
    return str(datetime.datetime(date_value).date())

## Convert to date from string (YYYY-MM-DD)
def convert_string(string_value):
    try:
        userDateTime = UserPersonalizationHelper.CovertToDate(string_value)
        return userDateTime.ToString("yyyy-MM-dd")
    except:
        return ""

def updateCRM(context):
    ## Initial Variables
    if context.WorkflowContext.NewCartId: quote = QuoteHelper.Get(context.WorkflowContext.NewCartId)
    else: quote = context.Quote
    cpiDict = {}
    sqlQry = """SELECT end_point_key, end_point FROM ZCA_INTEGRATIONINFO
        WHERE cpq_url = '{}' AND end_point_key LIKE 'CPI%'
        """.format(RequestContext.Url.Host)
    for row in SqlHelper.GetList(sqlQry):
        cpiDict[row.end_point_key] = row.end_point
    cpiUrl = cpiDict['CPI Update Opp']
    tokenUrl = cpiDict['CPI Token']
    result = AuthorizedRestClient.GetClientCredentialsGrantOAuthToken('CPQCPI_NP_OAUTH', tokenUrl, True)
    update_dict = {}

    ## Error handling fields
    missingFields = []
    post_error = ""
    ## Get fields/data list
    field_res = SqlHelper.GetList("SELECT * FROM zqt_crmfieldmapping WHERE end_sys != 'None'")

    for rec in field_res:
        if rec.field_level == "QP":
            update_dict[rec.end_field_name] = get_val(rec, rec.seq_level, quote)
            if rec.field_type == "date":
                update_dict[rec.end_field_name] = convert_date(update_dict[rec.end_field_name])
        elif rec.field_level == "CF":
            if quote.GetCustomField(rec.field_name): ## catching if CF exists, skips if it doesn't
                update_dict[rec.end_field_name] = quote.GetCustomField(rec.field_name).Value
                if rec.field_type == "date":
                    update_dict[rec.end_field_name] = convert_string(update_dict[rec.end_field_name])
            else:
                missingFields.append(rec.field_name)
        else:
            pass
        if rec.char_limit > 0: update_dict[rec.end_field_name] = update_dict[rec.end_field_name][0:rec.char_limit]

    ## POST to CPI
    update_json = RestClient.SerializeToJson(update_dict)
    header = {"Authorization":"Bearer {}".format(result.access_token)}
    try:
        x = RestClient.Post(cpiUrl, update_json, header)
        Log.Write("CRM Opportunity Updated with: {}".format(update_json))
    except Exception, e:
        post_error = "ZCA_updateOpportunity: {} | Line#: {}".format(e, sys.exc_traceback.tb_lineno)
        Log.Error(post_error)
        Trace.Write(post_error)

    ## Display Error Messages
    if post_error:
        quote.AddMessage("Update Opportunity Failed. Error: {}".format(e), MessageLevel.Error, True)
    if missingFields:
        if len(missingFields) > 1:
            plural = "s"
            verb = "are"
        else:
            verb = "is"
        quote.AddMessage("Update Opportunity Custom Action: The following field{} {} missing {}".format(plural, verb, missingFields), MessageLevel.Error, True)
    if not missingFields and not post_error:
        quote.AddMessage("Update Opportunity Custom Action: Success!", MessageLevel.Success, True)

##SFDC Methods
def updateSFDC(context):
    ScriptExecutor.Execute("CPQ_SF_CreateUpdateOpportunity")

## Decide which CRM system to update
CRMEnv = context.Quote.GetCustomField("ZQT_CRM_Type").Value

if CRMEnv == "SFDC":
    updateSFDC(context)
else:
    updateCRM(context)