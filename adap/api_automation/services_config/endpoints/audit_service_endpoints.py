JOB_STATUS = '/jobs/{job_id}/status'
GENERATE_AGGREGATIONS = '/jobs/{job_id}/generate_aggregations'
GET_AGGREGATIONS_DISTRIBUTION = '/jobs/{job_id}/aggregations_distribution'
JOB_ACCURACY = '/jobs/{job_id}/accuracy'
AUDIT_UNIT = '/jobs/{job_id}/units/{unit_id}/audit'
SEARCH_UNIT = '/jobs/{job_id}/search'
REPORT = '/jobs/{job_id}/reports'
REPORT_VERSION = '/jobs/{job_id}/reports/{report_version}'
ALL_JUDGMENTS = '/jobs/{job_id}/units/{unit_id}/all_judgments'
CANCEL_AGGREGATIONS = '/jobs/{job_id}/cancel_aggregations'
CONTRIBUTORS = '/jobs/{job_id}/contributors?question={question_name}'


URL = 'https://audit.internal.{}.cf3.us/v1'
