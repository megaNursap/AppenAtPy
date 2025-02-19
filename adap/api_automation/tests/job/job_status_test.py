import allure
import pytest
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user_api_key, get_user_email, sorted_list_of_dict_by_value

users = pytest.data.users

pytestmark = [pytest.mark.regression_core, pytest.mark.new_auth, pytest.mark.adap_api_uat]

API_KEY = get_user_api_key('test_account')


@allure.parent_suite('/jobs/{job_id}/ping:get')
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.builder
@pytest.mark.devspace
# @pytest.mark.skip(reason="https://appen.atlassian.net/browse/CW-8172")
def test_get_status_empty_job():
    api_key = get_user_api_key('test_account')

    # create job
    new_job = Builder(api_key)
    new_job.create_job()

    res = new_job.get_job_status()
    res.assert_response_status(200)

    expected_empty_job_status = {'golden_units': 0,
                                 'all_units': 0,
                                 'ordered_units': 0,
                                 'completed_units_estimate': 0,
                                 'aggregated_units_cached': False,
                                 'needed_judgments': 0,
                                 'all_judgments': 0,
                                 'tainted_judgments': 0,
                                 'completed_gold_estimate': 0,
                                 'completed_non_gold_estimate': 0}

    assert expected_empty_job_status == res.json_response

    json_status = new_job.get_json_job_status()
    json_status.assert_response_status(200)

    # todo json validation
    assert 'unordered' == json_status.json_response['state']
    assert get_user_email('test_account') == json_status.json_response['options']['mail_to']


@allure.parent_suite('/jobs/{job_id}:get')
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.flaky(reruns=1)
@pytest.mark.devspace
def test_get_json_status_for_simple_job():
    api_key = get_user_api_key('test_account')
    job = Builder(api_key)
    job.create_simple_job_with_test_questions()

    job.launch_job()

    json_status = job.get_json_job_status()
    json_status.assert_response_status(200)

    # todo json validation
    assert 'running' == json_status.json_response['state']
    assert get_user_email('test_account') == json_status.json_response['options']['mail_to']
    assert 'Smoke Test Simple' == json_status.json_response['title']


# TODO: QED-1570 should be done for FED support
# https://appen.atlassian.net/browse/QED-1565
# check after https://appen.atlassian.net/browse/DED-1522 is fixed
@allure.parent_suite('/jobs/{job_id}:get')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.fed_api
@pytest.mark.flaky(reruns=1)
def test_launch_job_deduct_from_crowdspend():
    api_key = get_user_api_key('test_account')
    job = Builder(api_key)
    job.create_simple_job_with_test_questions()
    res = job.launch_job(external_crowd=1)
    assert res.status_code == 200


@allure.parent_suite('/jobs:get')
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.devspace
def test_list_of_jobs_for_user():
    api_key = get_user_api_key('test_ui_account')
    user_email = get_user_email('test_ui_account')
    job = Builder(api_key)

    page = 1
    jobs = job.get_jobs_for_user()
    count_job = len(jobs.json_response)
    print("json response is:", jobs.json_response)

    while count_job > 0 and page <= 3:
        for current_job in jobs.json_response:
            assert current_job['support_email'] == user_email, "%s is not the owner of job %s" % (user_email, current_job['id'])
        page += 1
        jobs = job.get_jobs_for_user(page=page)
        count_job = len(jobs.json_response)


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.flaky(reruns=1)
@pytest.mark.devspace(reruns=1)
@pytest.mark.parametrize('scenario, tag_name',
                         [
                             ("single_tag", "tag1"),
                             ("all_caps", "TAG1"),
                             ("camel_case", "tAg1")
                         ])
def test_filter_job_by_tag(scenario, tag_name):
    _job = Builder(API_KEY)
    resp = _job.create_job()
    resp.assert_response_status(200)
    tag = "tag1"
    resp_tag = _job.add_job_tag(tag)
    resp_tag.assert_response_status(200)

    payload = {
        "tags[]": tag_name
    }

    resp_job = _job.filter_jobs(payload)
    resp_job.assert_response_status(200)

    # TODO: Fix assertion
    # assert resp_job.json_response['id'] == _job.job_id


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.devspace
@pytest.mark.parametrize('state',
                         [
                             "finished",
                             "paused",
                             "unordered",
                             "running"
                         ])
def test_filter_job_by_job_state(state):
    _api =  get_user_api_key('test_predefined_jobs')
    _job = Builder(_api)

    payload = {
        "state": state
    }
    payload_upper = {
        "state": state.upper()
    }

    resp_job = _job.filter_jobs(payload)
    resp_job.assert_response_status(200)
    assert resp_job.json_response, f'No jobs returned: {resp_job.json_response}'

    resp_job_upper = _job.filter_jobs(payload_upper)
    resp_job_upper.assert_response_status(200)
    assert resp_job_upper.json_response, f'No jobs returned: {resp_job.json_response}'

    _jobs = [x['id'] for x in resp_job.json_response]
    _jobs_upper = [x['id'] for x in resp_job_upper.json_response]

    assert sorted(_jobs) == sorted(_jobs_upper), "Returned jobs do not match: \n"\
        f"State '{state}' returned: {_jobs}"\
        f"State '{state.upper()}' returned: {_jobs_upper}"


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.devspace
def test_filter_job_by_job_state_invalid():
    _job = Builder(API_KEY)
    resp = _job.create_job()
    resp.assert_response_status(200)

    payload = {
               "state": "invalid"}

    resp = _job.filter_jobs(payload)
    resp.assert_response_status(422)

    resp.assert_error_message("Invalid state param (must be one of - unordered, running, canceled, finished, paused)")


# TODO: Add verification
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.parametrize('date_format, expected_response',
                         [
                             ("2020-03-02", 200),
                             ("02-03-2020", 200),
                             ("03/02/2020", 200),
                             ("30-05-2020", 200),
                             ("04.15.2020", 422),
                             ("invalid", 422)
                         ])
def test_filter_job_by_date(date_format, expected_response):
    _job = Builder(API_KEY)
    resp = _job.create_job()
    resp.assert_response_status(200)

    payload = {
        "created_at_greater_equal": date_format
    }

    payload2 = {
        "created_at_less_equal": date_format
    }

    resp = _job.filter_jobs(payload)
    resp.assert_response_status(expected_response)

    resp = _job.filter_jobs(payload2)
    resp.assert_response_status(expected_response)

    # if expected_response == 422:
    #     resp.assert_error_message("Invalid created_at_greater_equal param (must have date format)")
