import time

import allure
import pytest
import random
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_data_file, get_user_api_key, count_row_in_file, get_user_team_id

users = pytest.data.users
pytestmark = [pytest.mark.regression_core, pytest.mark.new_auth, pytest.mark.adap_api_uat, pytest.mark.rerun_test]


@allure.parent_suite('/jobs:post')
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.builder
@pytest.mark.wip_portal
@pytest.mark.flaky(reruns=3)
@pytest.mark.devspace
def test_create_blank_job():
    api_key = get_user_api_key('test_account')
    resp = Builder(api_key).create_job()
    resp.assert_response_status(200)


@allure.parent_suite('/jobs:post')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.cross_team
@pytest.mark.skip_hipaa
@pytest.mark.flaky(reruns=3)
def test_create_blank_job_team_id():
    api_key = get_user_api_key('multi_team_user')
    teams = get_user_team_id('multi_team_user', 1)

    job = Builder(api_key)
    resp = job.create_job(teams)
    resp.assert_response_status(200)
    job_team = resp.json_response.get('team_id')
    assert job_team == teams, "team id doesn't match!"


@allure.parent_suite('/jobs:post')
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
# @pytest.mark.fed_api
@pytest.mark.wip
@pytest.mark.flaky(reruns=3)
#  fed has bug for case 2 and 3, it returns 404 instead of 401, skip until bug fixed
@pytest.mark.parametrize('api_key_type, api_key, expected_status',
                         [("valid_key", get_user_api_key('test_account'), 200),
                          ("empty_key", "", 401),
                          ("invalid_key", "12345678qwerty", 401)])
@pytest.mark.devspace
def test_create_job_with_api_key(api_key_type, api_key, expected_status):
    resp = Builder(api_key).create_job()
    resp.assert_response_status(expected_status)


@allure.parent_suite('/jobs:post')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.flaky(reruns=3)
@pytest.mark.devspace
def test_create_job_with_title_and_instructions():
    api_key = get_user_api_key('test_account')
    payload = {
        'job': {
            'title': "Test API",
            'instructions': "Test job Instructions"
        }
    }
    job = Builder(api_key, payload=payload)
    resp = job.create_job()
    resp.assert_response_status(200)
    resp.assert_job_title('Test Api')
    assert resp.json_response['instructions'] == payload['job']['instructions'], "Expected title: %s \n Actual status: " \
                                                                                 "%s" % (payload['job']['instructions'],
                                                                                        resp.json_response['title'])


@allure.parent_suite('/jobs:post')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.skip_hipaa
@pytest.mark.flaky(reruns=3)
@pytest.mark.devspace
def test_create_job_with_title_and_instructions_team_id():
    api_key = get_user_api_key('multi_team_user')
    teams = get_user_team_id('multi_team_user', 1)

    payload = {
        'job': {
            'title': "Test Api with team id",
            'instructions': "Test job Instructions",
            'team_id': teams}
    }
    job = Builder(api_key, payload=payload)
    resp = job.create_job()
    resp.assert_response_status(200)
    resp.assert_job_title('Test Api With Team Id')
    assert resp.json_response['instructions'] == payload['job']['instructions'], "Expected title: %s \n Actual status: " \
                                                                                 "%s" % (payload['job']['instructions'],
                                                                                         resp.json_response['title'])
    job_team = resp.json_response.get('team_id')
    assert job_team == teams, "team id doesn't match!"


@allure.parent_suite('/jobs/upload:post')
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.jenkins
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.builder
@pytest.mark.wip_portal
@pytest.mark.flaky(reruns=3)
@pytest.mark.devspace
def test_create_job_with_json_data():
    api_key = get_user_api_key('test_account')
    sample_file = get_data_file('/sample_data.json')

    rows_in_json = count_row_in_file(sample_file)

    job = Builder(api_key)
    resp =job.create_job_with_json(sample_file)
    resp.assert_response_status(200)

    job_status = job.get_job_status(job.job_id)
    assert rows_in_json == job_status.json_response['all_units']


@allure.parent_suite('/jobs/upload:post')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.skip_hipaa
@pytest.mark.cross_team
@pytest.mark.flaky(reruns=3)
def test_create_job_with_json_data_team_id():
    """
    This test checks for the optional team id when creating a job and invoking the upload method
    """
    api_key = get_user_api_key('multi_team_user')
    sample_file = get_data_file('/sample_data.json')

    rows_in_json = count_row_in_file(sample_file)

    job = Builder(api_key)
    i = random.randint(1, 2)
    payload = {
         "team_id": get_user_team_id('multi_team_user', i)
    }
    resp = job.create_job_with_json(sample_file, payload)
    resp.assert_response_status(200)

    job_status = job.get_job_status(job.job_id)
    assert rows_in_json == job_status.json_response['all_units']

    job_team = resp.json_response['team_id']
    assert job_team == get_user_team_id('multi_team_user', i), "team id doesn't match!"


@allure.parent_suite('/jobs/upload:post')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.jenkins
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.flaky(reruns=3)
@pytest.mark.devspace
def test_create_job_with_empty_json_data():
    api_key = get_user_api_key('test_account')
    sample_file = get_data_file('/empty_json.json')

    job = Builder(api_key)
    resp = job.create_job_with_json(sample_file)
    resp.assert_response_status(200)

    job_status = job.get_job_status(job.job_id)
    assert 0 == job_status.json_response['all_units']


@allure.parent_suite('/jobs/upload:post,/jobs/{job_id}/units/ping:get')
@allure.severity(allure.severity_level.BLOCKER)
# @allure.issue("https://crowdflower.atlassian.net/browse/EE-1149")
@pytest.mark.jenkins
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.builder
@pytest.mark.flaky(reruns=3)
@pytest.mark.skipif(pytest.flaky == "false", reason="Flaky test")
def test_create_job_with_csv_data():
    api_key = get_user_api_key('test_account')
    sample_file = get_data_file("/dod_data.csv")
    job = Builder(api_key)
    resp = job.create_job_with_csv(sample_file)
    num_rows = count_row_in_file(sample_file)
    resp.assert_response_status(200)
    count_res = job.count_rows()
    assert num_rows == count_res.json_response['count'], "Expected number of rows: 5 \n Actual number: %s" % count_res.json_response['count']


@allure.parent_suite('/jobs/upload:post,/jobs/{job_id}/units/ping:get')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.cross_team
@pytest.mark.flaky(reruns=3)
def test_create_job_with_csv_data_team_id():
    api_key = get_user_api_key('multi_team_user')
    sample_file = get_data_file("/dod_data.csv")
    job = Builder(api_key)

    payload = {
        "team_id": get_user_team_id('multi_team_user', 2)
    }
    resp = job.create_job_with_csv(sample_file, payload)
    num_rows = count_row_in_file(sample_file)
    resp.assert_response_status(200)
    count_res = job.count_rows()
    assert num_rows == count_res.json_response['count'], "Expected number of rows: 5 \n Actual number: %s" % count_res.json_response['count']


@allure.parent_suite('/jobs:post')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.flaky(reruns=3)
@pytest.mark.devspace
def test_create_cml_group_aggregation_job():
    api_key = get_user_api_key('test_account')
    job = Builder(api_key)
    resp = job.create_simple_job(aggregation=True)
    assert resp is True, "Aggregation job was not created"
