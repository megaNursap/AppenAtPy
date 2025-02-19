JOB = '/jobs.json'
JOB_V2 = '/jobs'
UPLOAD_JSON = '/jobs/upload.json?key=%s'
UPLOAD_FILE_TO_JOB = '/jobs/%s/upload.json?key=%s'
DELETE = '/jobs/%s.json?key=%s'
UPDATE = '/jobs/%s.json?key=%s'
COPY = '/jobs/%s/copy?key=%s'
COPY_TEMPLATE = '/jobs/%s/copy.json?key=%s'
ROW_COUNT = '/jobs/%s/units/ping.json?key=%s'
ROWS = '/jobs/%s/units.json?key=%s&page=1'
UNIT = '/jobs/%s/units/%s.json?key=%s'
SPLIT_UNITS = '/jobs/%s/units/split?key=%s&on=%s&with=%s'
ADD_ROW = '/jobs/%s/units.json'
JSON_JOB_STATUS = '/jobs/%s.json?key=%s'
JOB_STATUS = '/jobs/%s/ping.json?key=%s'
CONVERT_UPLOADED_TQ = '/jobs/%s/gold.json?key=%s'
SET_TASK_PAYMENT = '/jobs/%s.json?key=%s'
LAUNCH_JOB = '/jobs/%s/orders.json?key=%s'
PAUSE_JOB = '/jobs/%s/pause.json?key=%s'
RESUME_JOB = '/jobs/%s/resume.json?key=%s'
CANCEL_JOB = '/jobs/%s/cancel.json?key=%s'
CANCEL_UNIT = '/jobs/%s/units/%s/cancel.json?key=%s'
CHANNELS = '/jobs/%s/channels?key=%s'
DISABLE_CHANNEL = '/jobs/%s/disable_channel?key=%s'
DELETE_UNIT = '/jobs/%s/units/%s?key=%s'
UPDATE_UNIT = '/jobs/%s/units/%s.json'
JOB_TAGS = '/jobs/%s/tags?key=%s'
NOTIFY_CONTRIBUTOR = '/jobs/%s/workers/%s/notify?key=%s'
PAY_CONTRIBUTOR_BONUS = '/jobs/%s/workers/%s/bonus.json?key=%s'
REJECT_CONTRIBUTOR = '/jobs/%s/workers/%s/reject?key=%s'
FLAG_CONTRIBUTOR = '/jobs/%s/workers/%s.json?key=%s'
TEAMS = '/users/teams?key=%s'
SWITCH_API_TEAM = '/users/switch_api_team/%s?key=%s'
LEGEND = '/jobs/%s/legend.json?key=%s'
MAX_CROWD_PAY = '/jobs/%s/max_pay_for_crowd?key=%s'
GET_BALANCE = '/account.json?key=%s'


URL = "https://api.{}.cf3.us/v1"
URL_V2 = "https://api-beta.{}.cf3.us/v2"
PROD = "https://api.figure-eight.com/v1"
FED = "https://app.{}.secure.cf3.us/builder/v1"
FED_CUSTOMIZE = "https://{}/builder/v1"
HIPAA = "https://api.nxxgpxhq0rum22cd.staging.cf3.us/v1"
STAGING = "https://api.whatsappenin.com/v1"
INTEGRATION = "https://api.integration.cf3.us/v1"

