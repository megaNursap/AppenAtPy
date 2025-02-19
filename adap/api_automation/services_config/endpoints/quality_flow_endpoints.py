# --- Project Controller ---------
PROJECTS_LIST = "/project/list"
PROJECT_DETAILS = "/project/detail"
PROJECT_DATA_SUMMARY = "/project/data-summary"
PROJECT_CREATE = "/project/create"
PROJECT_DELETE = "/project/delete"
PROJECT_UPDATE = "/project/update"

# ---- Project File Controller ----
FILE_NOTIFY = "/project/file/notify"
FILE_DOWNLOAD = "/project/file/download"
FILES = "/project/files"
FILE_UPLOAD_URL = "/project/file/upload-url"
FILE_DOWNLOAD_LIST = "/project/file/download/list"  # Deprecated
FILE = "/project/file"
FILE_LINK = "/project/file/link"
FILE_DATASET = "/project/file/upload-dataset"


# ---- Project Unit Controller ----
UNITS = "/project/units"
UNITS_SEND_TO_JOB = "/project/send-to-job"
UNITS_SEND_TO_GROUP = "/project/send-to-group"
UNITS_SEND_TO_CONTRIBUTOR = "/project/send-to-contributor"
UNITS_REMOVE_FROM_JOB = "/project/remove-from-job"
UNITS_REMOVE_FROM_GROUP = "/project/remove-from-group"
UNITS_REMOVE_FROM_CONTRIBUTOR = "/project/remove-from-contributor"
UNITS_RECOVER = "/project/recover-units"
UNITS_INACTIVE = "/project/inactive-units"
FIELD_VALUES = "/project/field-values"
UNITS_DELETE = "/project/delete-units"
UNITS_DATA_GROUP_LIST = "/project/data-group-list"
UNITS_HEADER = "/project/units-header"
UNIT = "/project/unit"
UNIT_COMMIT_HISTORY = "/project/unit-commit-history"
UNIT_DATA_GROUP = "/project/data-group"
SEGMENT_GROUP_LIST = "/project/unit/segment-group-list"

# ---- Project Feedback Controller ----
FEEDBACK_LIST = "/project/feedback/list"
FEEDBACK_STATISTICS = "/project/feedback/statistics"
FEEDBACK_COLUMNS = "/project/feedback/columns"

# ---- Project Internal Controller ----
PROJECT_INTERNAL_UNITS = "/project/internal/units"

# -----  Invoice Controller  ----
INVOICE_LIST='/project/invoice/list'
INVOICE_RETRY='/project/invoice/retry'

# -----  Batch job Controller  ----
BATCH_JOB_TRIGGER='/batchjob/trigger'
BATCH_PROGRESS_LIST='/batchjob/progress/list'
BATCH_PROGRESS_HISTORY='/batchjob/progress/history'

# ---- Curated Crowd sync-setting-manage-controller-impl ----
CONTRIBUTOR_SYNC_SETTING_UPDATE = "/contributor/setting/update"
CONTRIBUTOR_SYNC_SETTING_EFFECT = "/contributor/setting/effect"
CONTRIBUTOR_SYNC_SETTING_REFRESH = "/contributor/setting/refresh"
CONTRIBUTOR_SYNC_SETTING_CREATE = "/contributor/setting/create"
CONTRIBUTOR_SYNC_SETTING_UPDATE_EXTERNAL_PROJECT = "/contributor/setting/update-external-project"
CONTRIBUTOR_SYNC_SETTING_JOB_LINK = "/contributor/setting/job-link"
CONTRIBUTOR_SYNC_SETTING_CREATE_EFFECT = "/contributor/setting/create-effect"
CONTRIBUTOR_SYNC_SETTING_EXTERNAL_PROJECT_CHECK = "/contributor/setting/external-project-check"
CONTRIBUTOR_SYNC_SETTING_LIST = "/contributor/setting/list"
CONTRIBUTOR_SYNC_SETTING_DETAIL_BY_JOB = "/contributor/setting/detail-by-job"

# ---- Curated Crowd sync-setting-biz-controller-impl ----
CONTRIBUTOR_SYNC_SETTING_UPDATE_EFFECT = "/contributor/setting/update-effect"

# ---- Curated Crowd sync-setting-query-controller-impl ----
CONTRIBUTOR_SYNC_SETTING_EXTERNAL_USER_GROUP = "/contributor/setting/external-user-group"
CONTRIBUTOR_SYNC_SETTING_EXTERNAL_LOCALE = "/contributor/setting/external-locale"
CONTRIBUTOR_SYNC_SETTING_DETAIL = "/contributor/setting/detail"
CONTRIBUTOR_SYNC_SETTING_PAY_RATE_LIST = "/contributor/setting/pay-rate-list"

# ---- Curated Crowd contributor-manage-controller-impl ----
CONTRIBUTOR_CROWD_UN_ASSIGN_JOB = "/contributor/crowd/un-assign-job"
CONTRIBUTOR_CROWD_CLONE = "/contributor/crowd/clone"
CONTRIBUTOR_CROWD_ASSIGN_JOB = "/contributor/crowd/assign-job"

# ---- Curated Crowd contributor-query-controller-impl ----
CONTRIBUTOR_CROWD_LIST_BY_CRITERIA_SEARCH = "/contributor/crowd/list-by-criteria-search"
CONTRIBUTOR_CROWD_CRITERIA_SEARCH = "/contributor/crowd/criteria-search"
CONTRIBUTOR_CROWD_BATCH_DETAIL = "/contributor/crowd/batch-detail"
CONTRIBUTOR_CROWD_LIST_BY_GROUP = "/contributor/crowd/list-by-group"

# ---- Curated Crowd crowd-group-manage-controller-iml ----
CONTRIBUTOR_CROWD_GROUP_UPDATE = "/contributor/group/update"
CONTRIBUTOR_CROWD_GROUP_UNLINK_JOB = "/contributor/group/unlink-job"
CONTRIBUTOR_CROWD_GROUP_REMOVE_CROWD = "/contributor/group/remove-crowd"
CONTRIBUTOR_CROWD_GROUP_LINK_JOB = "/contributor/group/link-job"
CONTRIBUTOR_CROWD_GROUP_CREATE = "/contributor/group/create"
CONTRIBUTOR_CROWD_GROUP_CREATE_WITH_CROWD = "/contributor/group/create-with-crowd"
CONTRIBUTOR_CROWD_GROUP_CREATE_WITH_CRITERIA = "/contributor/group/create-with-criteria"
CONTRIBUTOR_CROWD_GROUP_ADD_CROWD = "/contributor/group/add-crowd"
CONTRIBUTOR_CROWD_GROUP_DELETE = "/contributor/group/delete"

# ---- Curated Crowd crowd-group-query-controller-impl ----
CONTRIBUTOR_CROWD_GROUP_DETAIL_LIST = "/contributor/group/detail-list"
CONTRIBUTOR_CROWD_GROUP_BRIEF_LIST = "/contributor/group/brief-list"

# ---- Curated Crowd crowd-group-biz-controller-impl ----
CONTRIBUTOR_CROWD_GROUP_CREATE_WITH_CONDITION = "/contributor/group/create-with-condition"

CONTRIBUTOR_TEST_CREATE_CONTRIBUTOR = '/contributor/internal/test/create-contributor'

# ---- Internal Crowd crud impl ----
CONTRIBUTOR_INTERNAL_ADD_CONTRIBUTOR = "/contributor/internalcontributor/add-contributor"
CONTRIBUTOR_INTERNAL_DELETE_CONTRIBUTOR = "/contributor/internalcontributor/delete-contributor"
CONTRIBUTOR_INTERNAL_LIST_CONTRIBUTOR = "/contributor/internalcontributor/list"

# ---- Internal Crowd Group crud impl ----
CONTRIBUTOR_INTERNAL_ADD_GROUP = "/contributor/internalcontributor/add-contributor-group"
CONTRIBUTOR_INTERNAL_ADD_CONTRIBUTOR_TO_NEW_GROUP = "/contributor/internalcontributor/add-contributors-to-new-group"
CONTRIBUTOR_INTERNAL_ASSIGN_GROUP_TO_JOB = "/contributor/internalcontributor/assign-group-to-job"
CONTRIBUTOR_INTERNAL_ASSIGN_CONTRIBUTOR_TO_JOB = "/contributor/internalcontributor/assign-job"


# ---- Work Controller ----
# -------------------------

# ---- job-controller ----
JOB = "/work/v2/job"
JOB_LAUNCH = "/work/job/launch"
JOB_LAUNCH_CONFIG = "/work/job/launch-config"
JOB_CLONE = "/work/v2/job/clone"
JOB_SUMMARY = "/work/job/summary"
JOB_LIST_AS_FLOW = "/work/job/list-as-flow"
JOB_WITH_CML = "/work/job/job-with-cml"
JOB_BY = "/work/job/by"
JOB_COLLECTION = "/work/job/appendable-as-collection"
JOB_ALL = "/work/job/all"
JOB_ALL_COLLECTION = "/work/job/all-as-collection"

# ---- job-controller v2 ----
JOB_V2 = "/work/v2/job"
JOB_LAUNCH_V2 = "/work/v2/job/launch"
JOBS_BY_LIST_V2 = "/work/v2/job/jobs-by-list"
JOBS_BY_LIST_TREE_NODE_V2 = "/work/v2/job/tree-nodes"
JOB_BY_ID_V2 = "/work/v2/job/job-by-id"
JOB_CLONE_V2 = "/work/v2/job/clone"
JOB_PREVIEW_V2 = "/work/v2/job/preview"
JOB_RESUME_V2 = "/work/v2/job/resume"
JOB_PAUSE_V2 = "/work/v2/job/pause"
JOB_DELETE_V2 = "/work/v2/job/delete"

# ---- job-cml-controller ----
CML = "/work/cml"
CML_CLONE = "/work/cml/clone"

# -------  job-resource-controller -----
RESOURCE = "/work/resource"
RESOURCE_DATA = "/work/resource/data"

# -------  job-filter-controller -----
JOB_FILTER = "/work/job/filter"
JOB_FILTER_CLONE = "/work/job/filter/clone"

# -------  job-internal-controller -----
WORK_INTERNAL_SESSION_UNITS_V2 = "/work/internal/v2/session/units"

# ------- metrics-work-job-controller -----
METRICS_PRODUCTIVITY_JOB_THROUGHPUT = "/metrics/productivity/job-throughput"
METRICS_QUALITY_PROJECT_QUALITY = "/metrics/quality/project-quality"
METRICS_QUALITY_LEADING_JOB_STATISTIC = "/metrics/quality/leading-job-statistic"
METRICS_QUALITY_REVIEW_JOB_STATISTIC = "/metrics/quality/review-job-statistic"
METRICS_CONTRIBUTOR_QACHECKER_PERFORMANCE = "/metrics/contributor/qachecker-performance"
METRICS_CONTRIBUTOR_PERFORMANCE = "/metrics/contributor/performance"
METRICS_PROJECT_JOB_STATISTIC_PROGRESS = "/project/job-statistic/progress"
METRICS_PROJECT_JOB_STATISTIC_BREAKDOWN_WORD_ERROR_RATE = "/project/job-statistic/breakdown/word/error-rate"
METRICS_PROJECT_JOB_STATISTIC_BREAKDOWN_WORD_DETAIL = "/project/job-statistic/breakdown/word/detail"
METRICS_PROJECT_JOB_STATISTIC_BREAKDOWN_TAG_SUMMARY = "/project/job-statistic/breakdown/tag/summary"
METRICS_PROJECT_JOB_STATISTIC_BREAKDOWN_TAG_ERROR_RATE = "/project/job-statistic/breakdown/tag/error-rate"
METRICS_PROJECT_JOB_STATISTIC_BREAKDOWN_TAG_DETAIL = "/project/job-statistic/breakdown/tag/detail"
METRICS_PROJECT_JOB_STATISTIC_BREAKDOWN_LABEL_ERROR_RATE = "/project/job-statistic/breakdown/label/error-rate"
METRICS_PROJECT_JOB_STATISTIC_BREAKDOWN_LABEL_DETAIL = "/project/job-statistic/breakdown/label/detail"
METRICS_PROJECT_FEEDBACK_STATISTICS = "/project/feedback/statistics"
METRICS_PROJECT_FEEDBACK_COLUMNS = "/project/feedback/columns"
METRICS_PROJECT_FEEDBACK_LIST = "/project/feedback/list"
METRICS_PROJECT_JOB_STATISTIC_REVIEW_BREAKDOWN_WORD_ERROR_RATE = "/project/job-statistic/review/breakdown/word/error-rate"
METRICS_PROJECT_JOB_STATISTIC_REVIEW_BREAKDOWN_WORD_DETAIL = "/project/job-statistic/review/breakdown/word/detail"
METRICS_PROJECT_JOB_STATISTIC_REVIEW_BREAKDOWN_TAG_SUMMARY = "/project/job-statistic/review/breakdown/tag/summary"
METRICS_PROJECT_JOB_STATISTIC_REVIEW_BREAKDOWN_TAG_ERROR_RATE = "/project/job-statistic/review/breakdown/tag/error-rate"
METRICS_PROJECT_JOB_STATISTIC_REVIEW_BREAKDOWN_TAG_DETAIL = "/project/job-statistic/review/breakdown/tag/detail"
METRICS_PROJECT_JOB_STATISTIC_REVIEW_BREAKDOWN_LABEL_ERROR_RATE = "/project/job-statistic/review/breakdown/label/error-rate"
METRICS_PROJECT_JOB_STATISTIC_REVIEW_BREAKDOWN_LABEL_DETAIL = "/project/job-statistic/review/breakdown/label/detail"

# ------- dc-job-controller-----
DC_JOB_V2 = "/work/v2/job/dc"
DC_JOB_SETTINGS = "/work/v2/job/dc/setting"
DC_JOB_UPDATE_TITLE_INSTRUCTION = "/work/v2/job/update-title-instruction"

# ------- dc-question-controller-----
DC_JOB_QUESTION = "/work/question"
DC_JOB_QUESTION_UPDATE_STATUS = "/work/question/update-status"
DC_JOB_QUESTION_REORDER = "/work/question/reorder"
DC_JOB_QUESTION_DELETE = "/work/question/delete"
DC_JOB_QUESTION_SIMPLE_LIST = "/work/question/simple-list"
DC_JOB_QUESTION_HIDDEN_LIST = "/work/question/hidden-list"
DC_JOB_QUESTION_CUSTOM_LIST = "/work/question/custom-list"

# --------dc-pin-controller-------
DC_PIN_UPDATE_STATUS = "/work/pin/update-status"
DC_PIN_LIST = "/work/pin/list"
DC_PIN_GENERATE = "/work/pin/generate"
DC_PIN_BATCH_UPDATE = "/work/pin/batch-update"
DC_PIN_BATCH_COUNT = "/work/pin/batch-count"
DC_PIN_SESSION_STATUS_LIST = "/work/pin/session-status-list"


# --------dc-prompt-controller-------
DC_PROMPT_SEND_TO_GROUP = "/work/prompt/send-to-group"
DC_PROMPT_OUT_OF_GROUP = "/work/prompt/out-of-group"
DC_PROMPT_GROUP_REORDER = "/work/prompt/group/reorder"
DC_PROMPT_GROUP_RELEASE = "/work/prompt/group/release"
DC_PROMPT_GROUP_PROMPT_SHUFFLE = "/work/prompt/group/prompt-shuffle"
DC_PROMPT_GROUP_ORGANIZE = "/work/prompt/group/organize"
DC_PROMPT_GROUP_EDIT = "/work/prompt/group/edit"
DC_PROMPT_ENABLE = "/work/prompt/enable"
DC_PROMPT_ELEMENT_REORDER = "/work/prompt/element/reorder"
DC_PROMPT_ELEMENT_LIST = "/work/prompt/element/list"
DC_PROMPT_EDIT = "/work/prompt/edit"
DC_PROMPT_DISABLE = "/work/prompt/disable"
DC_PROMPT_DELETE = "/work/prompt/delete"
DC_PROMPT_ADD = "/work/prompt/add"

# --------dc-interlocking-controller-------
DC_INTERLOCKING_UPDATE_STATUS = "/work/interlocking/update-status"
DC_INTERLOCKING_UPDATE_QUOTA = "/work/interlocking/update-quota"
DC_INTERLOCKING_UPDATE_QUOTA_CONFIG = "/work/interlocking/update-quota-config"
DC_INTERLOCKING_LIST = "/work/interlocking/list"
DC_INTERLOCKING_GENERATE_QUOTAS = "/work/interlocking/generate-quotas"
DC_INTERLOCKING_STATISTICS = "/work/interlocking/statistics"
DC_INTERLOCKING_CONFIG_BY_INTERLOCKING_ID = "/work/interlocking/config-by-interlocking-id"



# TODO internal-controller
# ------- distribution-internal-controller -----
DISTRIBUTION_FETCH = '/dist/internal/fetch'
DISTRIBUTION_COMMIT = '/dist/internal/commit'
DISTRIBUTION_REVIEW = '/dist/internal/review'
DISTRIBUTION_SAVE_COMMIT_GROUP = '/dist/internal/saveCommitGroup'
DISTRIBUTION_SAVE_REVIEW_GROUP = '/dist/internal/saveReviewGroup'
DISTRIBUTION_COMMIT_GROUP = '/dist/internal/commitGroup'
DISTRIBUTION_REVIEW_GROUP = '/dist/internal/reviewGroup'


URL = "https://api-kepler.{}.cf3.us"
KEPLER_INTERNAL_API_GATEWAY = 'https://api-kepler.internal.{}.cf3.us'

# ----- external api ---------------
EXTERNAL_API_PROJECT_CREATE = "/v1/project-flow/projects"
EXTERNAL_API_URL = "https://api-beta.{}.cf3.us"
EXTERNAL_API_DATA_UPLOAD = "/v1/project-flow/projects/project/upload"
EXTERNAL_API_DATA_DOWNLOAD = "/v1/project-flow/projects/project/download"
