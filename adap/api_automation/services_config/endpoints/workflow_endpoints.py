CREATE_WF = '/workflows'
WF_INFO = '/workflows/%s'
WF_OWNER = '/workflows/%s/compact'
UPLOAD_DATA = '/workflows/%s/upload'
UPLOAD_DATA_INFO = '/workflows/%s/data_uploads/%s'
LIST_DATA_INFO = '/workflows/%s/data_uploads'
STEPS = '/workflows/%s/steps'
STEP = '/workflows/%s/steps/%s'
ROUTES = '/workflows/%s/steps/%s/routes'
ROUTE = '/workflows/%s/steps/%s/routes/%s'
FILTER_RULES = '/workflows/%s/steps/%s/routes/%s/rules'
FILTER_RULE = '/workflows/%s/steps/%s/routes/%s/rules/%s'
LAUNCH = "/workflows/%s/launch?rows=%s"
PAUSE = "/workflows/%s/pause"
RESUME = "/workflows/%s/resume"
REGENERATE_WF_REPORT = "/workflows/{wf_id}/report/regenerate?type={report_type}"
DOWNLOAD_WF_REPORT = "/workflows/{wf_id}/report/download?type={report_type}"
STATISTICS = "/workflows/%s/statistics"
COUNT_WFS = "/workflows/counts"
COPY_WF = "/workflows/{wf_id}/copy"

API_GATEWAY = 'https://api-beta.{}.cf3.us/v2'
API_GATEWAY_STAGING = 'https://api-beta.staging.cf3.us/v2'
LIVE = 'https://api-beta.appen.com/v2'
FED = 'https://api-beta.{}.secure.cf3.us/v2'
