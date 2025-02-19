"""
This will create a job with:
5 units per page
1 judgment per unit
5 test questions
1 test question per page
20 units are uploaded, 10 launched
5 test questions are uploaded
1 assignment (i.e. 1 page) is complete
At the end, jobs should have:
5 judgments submitted
5 judgable units
5 finalized units
10 new units
"""

from adap.api_automation.utils.data_util import get_user
from adap.e2e_automation.services_config.job_api_support import (
    create_job_from_config_api, generate_job_link
)
from adap.perf_platform.test_data.jobs_data import jobs_data
from adap.api_automation.services_config.judgments import Judgments
from adap.perf_platform.utils.logging import get_logger

log = get_logger(__name__)
job_data = jobs_data.get('what_is_greater')
data_generator = job_data['data_generator']

envs = [
    'sandbox',
    'qa',
    'integration'
]


if __name__ == '__main__':
    for env in envs:
        user = get_user('test_predefined_jobs', env=env)
        email = user.get('email')
        password = user.get('password')
        api_key = user.get('api_key')
        config = {
            "job": {
                "title": "Sample job for copying",
                "instructions": "<h1>Overview</h1>",
                "cml": job_data['cml'],
                "units_per_assignment": 5,
                "gold_per_assignment": 1,
                "judgments_per_unit": 1,
                "project_number": "PN000112"
            },
            "data_upload": [data_generator(20,filename='/tmp/units.csv')],
            "test_questions": [data_generator(
                5,
                gold=True,
                filename='/tmp/tq.csv')],
            "launch": True,
            "rows_to_launch": 10,
            # "level": 'unleveled',
            "user_email": email,
            "user_password": password
        }
        job_id = create_job_from_config_api(config, env, api_key)
        log.info(f"Job created in {env}: {job_id}")
        j = Judgments(
            worker_email=email,
            worker_password=password,
            env=env
        )
        assignment_page_resp = j.sign_in_internal(
            job_id=job_id,
            internal_job_url=generate_job_link(job_id, api_key, env)
        )
        j.contribute(assignment_page_resp, num_assignments=1)
