ME_RP = '/v1/me'
SWITCH_API_TEAM_RP = '/v1/switch_api_team/%s'
SWITCH_CURRENT_TEAM_RP = '/v1/switch_current_team/%s'
USER_IN_ORG_RP = '/v1/organizations/%s/users'
LEVEL = "/v1/jobs/%s/level"
ONTOLOGY = "/v1/jobs/%s/ontology"
JWT_SESSION = "/v1/session"
UNITS = "/v1/jobs/{job_id}/units"
VIDEO_FRAME = "/contributor_proxy/v1/video/{video_id}/frame/{frame_id}.jpg"
ORDER_TEST_QUESTIONS = "/v1/jobs/{job_id}/order_test_questions"
Get_JUDGMENT_LINK = '/v1/text_annotation/%s/judgment_link?annotationId=%s'
Get_JUDGMENT_LINK_CONTRIBUTOR_PROXY = '/contributor_proxy/v1/text_annotation/%s/judgment_link?annotationId=%s'
POST_GRADE_LINK = '/v1/text_annotation/grade_link'
POST_ACCURACY = '/v1/text_annotation/accuracy'
POST_AGGREGATION = '/v1/text_annotation/aggregation'
POST_PREDICT = '/v1/ml/pretrained-spacy-tokenizer/predict'
POST_CONTRIBUTOR_PROXY_SAVE_ANNOTATION = '/contributor_proxy/v1/text_annotation/save'
REPORT_OPTIONS = '/v1/jobs/{job_id}/reports/options'

# Super Saver endpoints
# POST_REFS_URL = '/v1/jobs/%s/refs/url'
POST_REFS_URL = '/v1/refs/url'
POST_CONTRIBUTOR_PROXY_SUPER_SAVER = '/contributor_proxy/v1/annotation_saver'

# In-Platform Audit endpoints
GENERATE_AGGREGATION_IPA = '/v1/jobs/{job_id}/audit/units/aggregation'
SEARCH_UNITS = '/v1/jobs/{job_id}/audit/units/search'
GET_JOB_AGGREGATIONS_DISTRIBUTION = '/v1/jobs/{job_id}/audit/aggregations_distribution'
GET_UNIT_AUDIT_INFORMATION = '/v1/jobs/{job_id}/audit/units/{unit_id}/audit'
PUT_AUDIT_INFO_TO_UNIT = '/v1/jobs/{job_id}/audit/units/{unit_id}/audit'
AUDIT_AGGREGATION_STATUS = '/v1/jobs/{job_id}/audit/status'
IPA_REPORT = '/v1/jobs/{job_id}/audit/reports'
IPA_REPORT_VERSION = '/v1/jobs/{job_id}/audit/reports/{version}'
ALL_JUDGMENTS = '/v1/jobs/{job_id}/audit/units/{unit_id}/all_judgments'
TAXONOMY_GET_LINK = '/v1/refs/get_link'
TAXONOMY_PUT_LINK = '/v1/refs/put_link'
TAXONOMY_DELETE_LINK = '/v1/refs/delete_link'
TAXONOMY_URL = '/v1/taxonomy/{job_id}/url?'

# admin
TEAM_SETTINGS = '/v1/admin/teams/{team_id}'


URL = "https://requestor-proxy.{}.cf3.us"
PROD = "https://requestor-proxy.appen.com"
STAGING = "https://requestor-proxy.staging.cf3.us"
FED = "https://app.{}.secure.cf3.us/requestor-proxy"
FED_CUSTOMIZE = "https://{}/requestor-proxy"
