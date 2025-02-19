#GET_PRESIGNED_URL = "preSignedUrl/0/PRODUCTIVITY_DATA/%s"
FILE_STATUS = "/uploadFile/%s/status"
PROJECT_METRICS = ""
GET_PRE_SIGNED_URL_BY_UPLOAD_TYPE = "/uploadDataFile/preSignedUrl/{clientId}/{dataUploadType}/{fileName}"
UPLOAD_DATA_FILE = "/uploadDataFile"
GET_PRE_SIGNED_URL_BY_FILE_ID = "/uploadDataFile/preSignedUrl/preview/{fileId}"
GET_UPLOADED_FILE_BY_ID = "/uploadDataFile/{fileId}"
UPDATE_UPLOADED_FILE_BY_ID = "/uploadDataFile/{fileId}"
GET_PARTNER_DATA_COLUMN_MAPPING = "/partnerDataColumnMapping/client/{clientId}"
GET_PARTNER_DATA_COLUMN_MAPPING_BY_COLUMN_MAPPING_ID = "/partnerDataColumnMapping/{columnMappingId}/columns"
GET_PARTNER_DATA_COLUMN_MAPPING_HEADERS = "/uploadDataFile/{fileId}/headers"
GET_PARTNER_DATA_COLUMN_TYPES_DICTIONARY = "/dictionaries/columnTypes"
UPDATE_COLUMN_MAPPING_BY_ID = "/partnerDataColumnMapping/{{columnMappingId}}"
CHECK_TEMPLATE_EXISTS = "/partnerDataColumnMapping/checkName/{template_name}"
PARTNER_DATA_COLUMN_MAPPING ="/partnerDataColumnMapping"
PROJECT_MAPPING ="/uploadDataFile/{fileId}/projectUserSet?step=PROJECT_MAPPING"
UPDATE_PARTNER_DATA_FILE_WITH_MAPPING ="/uploadDataFile/{fileId}"
USER_MAPPING="/uploadDataFile/{fileId}/projectUserSet?step=USER_MAPPING"
GET_PROJECT_MAPPING_ROWS_COUNT ="/dataMapping/projects/{fileId}/count"
GET_USER_MAPPING_ROWS_COUNT = "/dataMapping/users/{fileId}/count"
GET_CURRENT_INVOICE_PERIOD = "/invoicePeriods/currentInvoicePeriod"
UPDATE_SUBMIT_FOR_PRECHECK ="/uploadDataFile/2965/submitForPrecheck"
GET_PROJECT_MAPPING_DOWNLOAD= "/dataMapping/projects/{fileId}/download"
GET_USERS_MAPPING_DOWNLOAD= "/dataMapping/users/{fileId}/download"
GET_UPLOADED_FILE_STATUS = "/uploadDataFile/{fileId}/status"

def URL(env):
    return {
        'qa': 'https://connect-qa.sandbox.cf3.us/qrp/v2/services/svc/',
        'stage': 'https://connect-stage.integration.cf3.us/qrp/v2/services/svc',
        'integration': 'https://connect.integration.cf3.us/qrp/v2/services/svc'
    }.get(env)