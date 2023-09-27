CPQ_BP_STANDARD_FIELD = "BpStandardField"
CPQ_BP_CUSTOM_FIELD = "BpCustomField"
OUTBOUND = "OUTBOUND"
INBOUND = "INBOUND"
EVENT_CREATE = "Create"
EVENT_UPDATE = "Update"
###############################################################################################
# Class CL_CpqHelper:
#       Class to instantiate CPQ Quote
###############################################################################################
class CL_CpqHelper:

    TYPE_STRING = "String"
    TYPE_FLOAT = "Float"

    def __init__(self, Quote, Session, BusinessPartnerRepository=None):
        self.Quote = Quote
        self.Session = Session
        self.BusinessPartnerRepository = BusinessPartnerRepository

    ###############################################################################################
    # Function to build SOQL query to be used in API Calls
    ###############################################################################################
    def build_soql_query(self, selectedFields, table, condition):
        soql = None
        if selectedFields != "" and table != "":
            if condition == "":
                soql = "?q=SELECT {selectedFields} FROM {table}".format(selectedFields=str(selectedFields), table=str(table))
            else:
                soql = "?q=SELECT {selectedFields} FROM {table} WHERE {condition}".format(selectedFields=str(selectedFields), table=str(table), condition=str(condition))
        if soql is not None:
            soql = soql.replace(" ", "+")
        return soql