###############################################################################################
# Class CL_CPQSettings:
#       Class to store general CPQ properties (TENANT SPECIFIC)
###############################################################################################
class CL_CPQSettings:
    # https://xxx.webcomcpq.com
    CPQ_URL = "https://agilenttechnologiesinc-dev1.cpq.cloud.sap"


###############################################################################################
# Class CL_SalesforceSettings:
#       Class to store general Salesforce properties (TENANT SPECIFIC)
###############################################################################################
class CL_SalesforceSettings:

    SALESFORCE_VERSION = "55.0"
    # https://xxx.my.salesforce.com
    SALESFORCE_URL = "https://agilent--dev1.sandbox.my.salesforce.com"
    # whats the difference between these two URLS, vf.force vc my.salesforce

    # Credential Management Keys for Integration User
    SALESFORCE_PWD = "CPQ_SFDC_PWD"
    #"ZHzA1Ila6M"
    SALESFORCE_SECRET = "CPQ_SFDC_SECRET"
    #"nggneLuKUQaLt8rEEsbhwaFSp"