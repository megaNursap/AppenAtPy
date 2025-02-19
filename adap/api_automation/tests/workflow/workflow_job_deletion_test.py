"""
    API tests for deleting job which is part of workflow
"""
import time

from adap.api_automation.services_config.workflow import Workflow
from adap.api_automation.services_config.builder import Builder

from adap.api_automation.utils.data_util import *
from adap.perf_platform.test_data.jobs_data import jobs_data
from adap.e2e_automation.services_config.job_api_support import create_job_from_config_api

pytestmark = [pytest.mark.regression_wf]

username = get_test_data('test_account', 'email')
password = get_test_data('test_account', 'password')
api_key = get_test_data('test_account', 'api_key')
job_data = jobs_data.get('what_is_greater')
data_generator = job_data['data_generator']


def create_job():
    """
    Create a job for WF (no units, no launch)
    """
    config = {
        "job": {
            "title": "QA Test - WF",
            "instructions": "<h1>Overview</h1>",
            "cml": job_data['cml'],
            "units_per_assignment": 5,
            "gold_per_assignment": 0,
            "judgments_per_unit": 1,
            "project_number": "PN000112"
        },
        "launch": False,
        "external_crowd": False,
        "user_email": username,
        "user_password": password
    }
    job_id = create_job_from_config_api(config, pytest.env, api_key)
    return job_id


def create_workflow():
    wf = Workflow(api_key)
    payload = {'name': 'WF Test Job Deletion', 'description': 'WF Test Job Deletion'}
    wf.create_wf(payload=payload)
    return wf.wf_id


@pytest.mark.workflow
def test_unable_delete_job():
    job1 = create_job()
    wf_id = create_workflow()
    wf_service = Workflow(api_key)
    wf_service.create_job_step([job1], wf_id)
    time.sleep(2)

    resp = Builder(api_key, api_version='v2').delete_job(job1)
    resp.assert_response_status(422)
    assert resp.json_response == {"data":None,"errors":["Workflow jobs hard deletion not supported currently"]}
    # resp.assert_error_message_v2('You cannot delete a job that is associated with a workflow.')


@pytest.mark.workflow
def test_delete_workflow_and_job():
    job1 = create_job()
    wf_id = create_workflow()
    wf_service = Workflow(api_key)
    wf_service.create_job_step([job1], wf_id)

    wf_resp = wf_service.delete_wf(wf_id)
    wf_resp.assert_response_status(200)
    time.sleep(5)
    job_resp = Builder(api_key, api_version='v2').delete_job(job1)
    job_resp.assert_response_status(200)


@pytest.mark.workflow
def test_able_delete_job():
    job1 = create_job()
    wf_id = create_workflow()
    wf_service = Workflow(api_key)
    step1 = wf_service.create_job_step([job1], wf_id)

    wf_service.delete_step(step1[0]['step_id'], wf_id)
    time.sleep(2)
    resp = Builder(api_key, api_version='v2').delete_job(job1)
    resp.assert_response_status(200)
