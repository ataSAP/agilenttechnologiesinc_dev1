from CPQ_SF_CpqHelper import CL_CpqHelper

###############################################################################################
# Class CL_MessageHandler:
#       Class to handle messages
###############################################################################################
class CL_MessageHandler(CL_CpqHelper):

    def __init__(self, Quote, Session):
        self.Quote = Quote
        self.Session = Session

###############################################################################################
# Function to add messages (Temporary Message)
###############################################################################################
    def add_message(self, msg, msgLevel):
        # Truncate to 1000 Characters (CPQ Limit for Quote Messages)
        msg = msg[:1000]
        self.Quote.AddMessage(msg, msgLevel, True)

###############################################################################################
# Class CL_IntegrationMessages:
#       Class to store messages
###############################################################################################
class CL_IntegrationMessages:

    ONLY_ONE_QUOTE_E_MSG = "Only one quote can be linked to an opportunity. Please contact your CPQ Admin."
    NO_OPPORTUNITY_NAME = "Opportunity name is missing. To Create/Update an Opportunity please add the Opportunity Name."
    NO_PRICE_BOOK_MAPPING = "Integration failed: Market Mapping does not exist. Please change Market or create new mapping."
    NO_STATUS_MAPPING = "Status Mapping does not exist. Please create new mapping."
    CANNOT_ATTACH_QUOTE = "Quote is already attached to an Opportunity. Please detach Quote from Opportunity before reattaching with another Opportunity."
    CANNOT_DETACH_QUOTE = "Quote cannot be detached as it is not linked to any Opportunity."
    NO_OPPORTUNITY_ATTACHED = "Quote is not attached to any Opportunity."