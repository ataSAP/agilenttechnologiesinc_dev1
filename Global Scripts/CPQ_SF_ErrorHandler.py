###############################################################################################
# Class CL_ErrorHandler:
#       Class to store error handling functions
###############################################################################################
class CL_ErrorHandler():
    ERROR_CODES = ["400","401","403","404","405","409","410","412","414","415","431","500","503"]
###############################################################################################
# Function to handle all responses
###############################################################################################
    def handle_response(self, response, integrationReference):
        errorMessages = list()
        # Composite Request API handling
        if str(type(response)) == "<type 'JObject'>":
            if response["compositeResponse"]:
                errorMessages = self.handle_composite_response(response["compositeResponse"], integrationReference)
        else:
            if str(type(response)) == "<type 'JArray'>":
                errorMessages = self.handle_other_response(response, integrationReference)
        # Regular API call handling
        return errorMessages
###############################################################################################
# Function to handle Composite Request
###############################################################################################
    def handle_composite_response(self, compositeResponse, integrationReference):
        errorMessages = list()

        for bodyPayload in compositeResponse:
            body = bodyPayload["body"]
            #look for httpStatusCode in list, if match then look for errorcodes
            httpHeaders = str(bodyPayload["httpStatusCode"])
            referenceId = str(bodyPayload["referenceId"])
            message = str()
            try:
                for error in body:
                    if httpHeaders in self.ERROR_CODES:
                        errors = error["errorCode"]
                        message = "{integrationReference} ({referenceId}): {message}".format(integrationReference=str(integrationReference), referenceId=str(referenceId), message=str(error["message"]))
                        errorMessages.append(message)
                    else:
                        errors = error["errors"]
                        for msg in errors:
                            message = "{integrationReference} ({referenceId}): {message}".format(integrationReference=str(integrationReference), referenceId=str(referenceId), message=str(msg["message"]))
                            errorMessages.append(message)
            except Exception as e:
                Trace.Write(str(e))
            return errorMessages
###############################################################################################
# Function to handle other API Requests (SObject Collection)
###############################################################################################
    def handle_other_response(self, response, integrationReference):
        errorMessages = list()
        
        for body in response:
            if body["errors"]:
                for msg in body["errors"]:
                    message = "{integrationReference}: {message}".format(integrationReference=str(integrationReference), message=str(msg["message"]))
                    errorMessages.append(message)

        return errorMessages