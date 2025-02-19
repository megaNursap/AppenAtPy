def URL(env):
    return {
        'qa': 'https://connect-qa.sandbox.cf3.us/qrp/api/v2/services/sqlReportSvc',
        'stage': 'https://connect-stage.integration.cf3.us/qrp/api/v2/services/sqlReportSvc',
        'integration': 'https://connect.integration.cf3.us/qrp/api/v2/services/sqlReportSvc'
    }.get(env)


PROD = ""


REPORT_SESSION_BY_ID = '/api/v1/report_sessions/{id}'
REPORT_SESSION = '/api/v1/report_sessions'

REPORT_SESSION_DOWNLOAD = '/api/v1/report_sessions/{id}/download'

REPORT_TEMPLATE_BY_ID = '/api/v1/report_templates/{id}'
REPORT_TEMPLATE = '/api/v1/report_templates'
REPORT_TEMPLATE_CATEGORIES = '/api/v1/report_templates/categories'
