import pytest
import allure
import logging
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.jobs_api import JobsApi
from adap.api_automation.utils.data_util import get_user_api_key, get_data_file, count_row_in_file

LOGGER = logging.getLogger(__name__)

pytestmark = [pytest.mark.regression_core, pytest.mark.new_auth, pytest.mark.adap_api_uat]

USERS = pytest.data.users
API_KEY = get_user_api_key('test_account')


@allure.parent_suite('/jobs/{job_id}/archive')
@pytest.mark.uat_api
@pytest.mark.jobs_api
def test_archive_job():
    new_job = Builder(api_key=API_KEY)
    new_job.create_job()
    _job_id = new_job.job_id

    job_to_archive = JobsApi()
    resp = job_to_archive.archive_job(job_id=_job_id)
    resp.assert_response_status(200)
    resp.assert_request_response({'action': 'UPDATED'})

    new_job.wait_until_status2(status='archived', key='archive_state', state_key='state')

    job_resp = new_job.get_json_job_status()
    job_resp.assert_response_status(200)
    assert job_resp.json_response['archive_state']['state'] == 'archived'


@allure.parent_suite('/jobs/{job_id}/restore')
@pytest.mark.uat_api
@pytest.mark.jobs_api
def test_restore_job():
    new_job = Builder(api_key=API_KEY)
    new_job.create_job()
    _job_id = new_job.job_id

    job_to_archive = JobsApi()
    resp = job_to_archive.archive_job(job_id=_job_id)
    resp.assert_response_status(200)
    resp.assert_request_response({'action': 'UPDATED'})

    new_job.wait_until_status2(status='archived', key='archive_state', state_key='state')

    job_resp = new_job.get_json_job_status()
    job_resp.assert_response_status(200)
    new_job.wait_until_status2(status='archived', key='archive_state', state_key='state')

    api = Builder(api_key=API_KEY, api_version='v2')
    restore = api.restore_job(job_id=_job_id)
    restore.assert_response_status(200)
    restore.assert_request_response({'action': 'UPDATED'})

    new_job.wait_until_status2(status='unarchived', key='archive_state', state_key='state')

