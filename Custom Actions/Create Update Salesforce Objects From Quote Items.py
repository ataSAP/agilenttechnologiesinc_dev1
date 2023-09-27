from CPQ_SF_IntegrationModules import CL_SalesforceIntegrationModules
from CPQ_SF_CustomObjectLineItemModules import CL_CustomObjectLineItemModules

Quote = context.Quote
class_sf_integration_modules = CL_SalesforceIntegrationModules(Quote, Session)
class_cust_obj_item_modules = CL_CustomObjectLineItemModules(Quote, Session)
#############################################
# 1. AUTHORIZATION
#############################################
bearerToken = class_sf_integration_modules.get_auth2_token()
#############################################
# 2. ITEM INTEGRATION
#############################################
if Quote.GetAllItems():
    # Send Quote Items to Custom Objects
    class_cust_obj_item_modules.process_custom_object_line_item_mappings(bearerToken)
