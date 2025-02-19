""" Create QA Performance Test Workflow """

from adap.e2e_automation.services_config.workflow_api_support import api_create_wf_from_config
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user
from adap.perf_platform.test_data.data_generator import generate_csv_data_what_is_greater
from adap.perf_platform.utils.results_handler import add_task_info
from adap.settings import Config
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.test_scripts.common import create_jobs

log = get_logger(__name__)

env = Config.ENV
if env == 'integration':
    user = get_user('perf_platform2')
else:
    user = get_user('perf_platform')

api_key = user['api_key']
template_job_id = user['template_job_id']


filter_payload1 = {
  "filter_rule": {
      "comparison_field": "what_is_greater",
      "comparison_operation": "==",
      "comparison_value": "col1",
      "rule_connector": "and"}
}

filter_payload2 = {
  "filter_rule": {
      "comparison_field": "what_is_greater",
      "comparison_operation": "==",
      "comparison_value": "col2",
      "rule_connector": "and"}
}


wf_config = {
    "env": Config.ENV,
    "user": {
        "api_key": api_key
    },
    "workflow": {
        "payload": {
            "name": f"QA Performance Test {Config.SESSION_ID}.{Config.TASK_ID}",
            "description": "Sample WF with 3 Jobs",
            "kafka": "true"
        }
    },
    "routes": {
        "1": {"connect": (1, 2), "filter": filter_payload1},
        "2": {"connect": (1, 3), "filter": filter_payload2}
    },
    "data_upload": [generate_csv_data_what_is_greater(Config.NUM_UNITS, filename='/tmp/units.csv')],
    "launch": True,
    "row_order": Config.LAUNCH_NUM_UNITS
}

payload = {'job': {'title': f"QA Performance Test (WF) {Config.SESSION_ID}.{Config.TASK_ID}"}}


def main():
    b = Builder(api_key, env=Config.ENV)
    job_ids = create_jobs(3, launch=False)
    for job_id in job_ids:
        b.update_job(job_id, payload)

    wf_config['job_ids'] = job_ids
    wf_info = api_create_wf_from_config(wf_config)

    log.debug("Add workflow job_ids to `tasks` table in Results DB")
    info = {'workflow_job_ids': job_ids}
    add_task_info(info)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.error(e.__repr__())
        raise
