import time

import allure

import pytest
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user_api_key
from adap.api_automation.utils.helpers import retry

pytestmark = [pytest.mark.regression_core, pytest.mark.new_auth, pytest.mark.adap_api_uat]

users = pytest.data.users
delay_status = 10

def get_job_with_status_from_cash(status=None):
    if cash_jobs.get(status) is None:
        cash_jobs[status] = []
        return None
    elif len(cash_jobs[status]) == 0:
        return None
    return cash_jobs[status][0]


def update_job_cash(status, job_id):
    if cash_jobs.get(status) is None:
        _jobs = [job_id]
        cash_jobs[status] = _jobs

    _jobs = cash_jobs[status]
    _jobs.append(job_id)
    cash_jobs[status] = list(set(_jobs))

    # delete job with previous status
    for k in cash_jobs:
        if k != status:
            if job_id in cash_jobs[k]:
                _jobs = cash_jobs[k]
                _jobs.remove(job_id)
                cash_jobs[k] = _jobs

    return cash_jobs


def find_all_jobs_with_status_for_user(api_key):
    job = Builder(api_key)

    page = 1
    jobs = job.get_jobs_for_user()
    count_job = len(jobs.json_response)

    _jobs = {}

    while count_job > 0:
        for current_job in jobs.json_response:
            job.job_id = current_job['id']
            res = job.get_json_job_status()
            if res.status_code == 200:
                if _jobs.get(res.json_response['state']) is not None:
                    jobs_with_status = _jobs[res.json_response['state']]
                    jobs_with_status.append(job.job_id)
                    _jobs[res.json_response['state']] = jobs_with_status
                else:
                    _jobs[res.json_response['state']] = [job.job_id]

        page += 1
        jobs = job.get_jobs_for_user(page=page)
        count_job = len(jobs.json_response)

    return _jobs


api_key = get_user_api_key('test_account')
cash_jobs = {}


@pytest.fixture(scope="module")
def find_all_jobs():
    global cash_jobs
    # cash_jobs = find_all_jobs_with_status_for_user(api_key)


@allure.severity(allure.severity_level.BLOCKER)
@allure.parent_suite('/jobs/{job_id}/orders:post')
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.flaky(reruns=1)
@pytest.mark.skipif(pytest.flaky == "false", reason="Flaky test")
def test_launch_simple_job(find_all_jobs):
    api_key = get_user_api_key('test_account')

    # create job with title, instructions, data and test questions
    job = Builder(api_key)
    job.create_simple_job_with_test_questions()

    res = job.launch_job()
    res.assert_response_status(200)
    time.sleep(delay_status)

    res = job.get_json_job_status()
    res.assert_response_status(200)

    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    update_job_cash("running", job.job_id)


@allure.severity(allure.severity_level.CRITICAL)
@allure.parent_suite('/jobs/{job_id}/pause:get')
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.skipif(pytest.flaky == "false", reason="Flaky test")
def test_pause_simple_job(find_all_jobs):
    api_key = get_user_api_key('test_account')

    job = Builder(api_key)

    reuse_job = get_job_with_status_from_cash('running')

    if reuse_job is not None:
        job.job_id = reuse_job
    else:
        job.create_simple_job_with_test_questions()
        job.launch_job()

    time.sleep(delay_status)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    job.pause_job()
    time.sleep(delay_status)

    res = job.get_json_job_status()
    res.assert_response_status(200)

    assert 'paused' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "paused")

    update_job_cash("paused", job.job_id)


@allure.severity(allure.severity_level.CRITICAL)
@allure.parent_suite('/jobs/{job_id}/resume:get')
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.skipif(pytest.flaky == "false", reason="Flaky test")
def test_resume_simple_job(find_all_jobs):
    api_key = get_user_api_key('test_account')
    job = Builder(api_key)

    reuse_job = get_job_with_status_from_cash('paused')

    if reuse_job is not None:
        job.job_id = reuse_job
    else:
        job.create_simple_job_with_test_questions()
        job.launch_job()
        job.pause_job()

    time.sleep(delay_status)
    res = job.get_json_job_status()
    assert 'paused' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "paused")

    update_job_cash("paused", job.job_id)

    job.resume_job()
    time.sleep(delay_status)

    res = job.get_json_job_status()
    res.assert_response_status(200)

    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    update_job_cash("running", job.job_id)


@allure.severity(allure.severity_level.CRITICAL)
@allure.parent_suite('/jobs/{job_id}/cancel:get')
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.skipif(pytest.flaky == "false", reason="Flaky test")
def test_cancel_running_simple_job(find_all_jobs):
    api_key = get_user_api_key('test_account')
    job = Builder(api_key)

    reuse_job = get_job_with_status_from_cash('running')

    if reuse_job is not None:
        job.job_id = reuse_job
    else:
        job.create_simple_job_with_test_questions()
        job.launch_job()

    job.cancel_job()
    time.sleep(delay_status)

    res = job.get_json_job_status()
    res.assert_response_status(200)

    assert 'canceled' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "canceled")

    update_job_cash("canceled", job.job_id)


@allure.severity(allure.severity_level.NORMAL)
@allure.parent_suite('/jobs/{job_id}/cancel:get')
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.skipif(pytest.flaky == "false", reason="Flaky test")
def test_cancel_paused_simple_job(find_all_jobs):
    api_key = get_user_api_key('test_account')
    job = Builder(api_key)

    reuse_job = get_job_with_status_from_cash('paused')

    if reuse_job is not None:
        job.job_id = reuse_job
    else:
        reuse_job = get_job_with_status_from_cash('running')
        job.job_id = reuse_job

    if reuse_job is not None:
        job.pause_job()
    else:
        job.create_simple_job_with_test_questions()
        job.launch_job()

        job.pause_job()

    def check_job_status():
        res = job.get_json_job_status()
        res.assert_response_status(200)
        assert 'paused' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
            res.json_response['state'], "paused")

    retry(check_job_status, max_retries=60)

    update_job_cash("paused", job.job_id)

    job.cancel_job()
    time.sleep(delay_status)
    res = job.get_json_job_status()
    res.assert_response_status(200)

    assert 'canceled' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "canceled")

    update_job_cash("canceled", job.job_id)


@allure.severity(allure.severity_level.CRITICAL)
@allure.parent_suite('/jobs/{job_id}/channels:post')
@pytest.mark.regression
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
def test_auto_launch_job(find_all_jobs):
    """
        A job has to have at least 4 rows uploaded in order to be auto launched
    """
    api_key = get_user_api_key('test_account')
    updated_payload = {
        'job': {
            'auto_order': "true",
        }
    }

    job = Builder(api_key)
    resp = job.create_simple_job_no_data()
    assert resp is True

    updated_job = Builder(api_key=api_key, payload=updated_payload)
    res = updated_job.update_job(job.job_id)
    res.assert_response_status(200)

    for i in range(5):
        data = {"name": "row %s" % i, "url": "example.com/new_row%s" % i}
        job.add_new_row(job_id=job.job_id, data=data)

    for i in range(50):
        try:
            res = job.get_json_job_status()
            assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
                res.json_response['state'], "running")
            if res.json_response['state'] == 'running':
                print("Job has been auto launched!")
                break
            else:
                print("Job has not been auto launched!")
        except Exception:
            print("not working")
