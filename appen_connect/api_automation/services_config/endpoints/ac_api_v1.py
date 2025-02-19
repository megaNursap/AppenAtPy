EMAIL = "/api/email/projectLandingPageUrls"

PROJECT = "/api/projects/{id}"

PROJECT_IAS = "/api/projects/{id}/ias"

GUIDELINES = "/api/guidelines"

PROJECT_GUIDELINES = "/api/guidelines/project/{projectId}"

USER_GUIDELINES = "/api/guidelines/user/{userId}"

GUIDLINE_DOCUMENT = "/api/guidelines/user/{userId}/document/{documentId}"

FIGURE_EIGHT_API_START = "/f8partner_api/start"

FIGURE_EIGHT_API_FINISH = "/f8partner_api/finish"

GET_INVOICE = "/api/invoices/{id}"

CREATE_INVOICE ="/api/invoices/createInvoice"
CREATE_INVOICES = "/api/invoices/createInvoices"

FIND_INVOICE = "/api/invoices/findInvoice"
FIND_INVOICES = "/api/invoices/findInvoices"


OPT_IN_ACKNOWLEDGE = "/api/optin/acknowledge"


PARTNER_DATA_API = "/api/partnerData"

CUSTOMER = "/api/customers/{id}/ias"

USERS = "/api/users"

USER = "/api/users/{id}"

CHECK_PASSWORD = "/api/users/checkPassword"

USERS_PROJECT = "/api/users/project/{projectId}"

FACE_ID = "/api/users/setUserFaceId/{userId}"

INTELLIGENT_ATTRIBUTE = "/api/ias"

TICKETS_PREPARE_RESPONSE = "/api/tickets/prepare_response"

SMART_TICKET_ANSWERING = "/api/tickets/smartTicketAnswering"

SMART_TICKET_ANSWERING_BY_ID = "/api/tickets/smartTicketAnsweringById"

SWS_USER_TOKEN_VALIDATION_API = "/api/users/validateUserSession"

GET_PAYRATE="/api/payrates/{businessUnit}"

GET_APPROVE_USER="/api/payments/payoneer/approveUser"
GET_CANCEL_PAYMENT="/api/payments/payoneer/cancelPayment"
GET_DECLINE_USER="/api/payments/payoneer/declineUser"
GET_PAYONEER_REGISTRATION="/api/payments/payoneer/registration"


def URL(env):
    return {
        'qa': 'https://connect-qa.sandbox.cf3.us/qrp',
        'stage': 'https://connect-stage.integration.cf3.us/qrp',
        'integration': 'https://connect.integration.cf3.us/qrp'
    }.get(env)


