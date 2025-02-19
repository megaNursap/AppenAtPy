"""
https://api-kepler.integration.cf3.us/work/swagger-ui/index.html#/job-controller-2
"""

import time

import allure
import pytest
from faker import Faker
import datetime

from adap.api_automation.services_config.quality_flow import QualityFlowApiWork, QualityFlowApiProject
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id, find_dict_in_array_by_value

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_api,
              pytest.mark.regression_qf,
              mark_env]

faker = Faker()

_today = datetime.datetime.now().strftime("%Y_%m_%d")


@pytest.fixture(scope="module")
def setup():
    # User Credentials
    username = get_test_data('qf_user_dc', 'email')
    password = get_test_data('qf_user_dc', 'password')
    team_id = get_test_data('qf_user_dc', 'teams')[0]['id']

    api = QualityFlowApiWork()
    api.get_valid_sid(username, password)

    # create project
    api_project = QualityFlowApiProject()
    api_project.get_valid_sid(username, password)
    project_name = f"automation project {_today} {faker.zipcode()}: work controller "
    payload_project = {"name": project_name,
                       "description": project_name,
                       "unitSegmentType": "UNIT_ONLY"}

    res = api_project.post_create_project(team_id=team_id, payload=payload_project)
    assert res.status_code == 200
    response = res.json_response
    project_data = response.get('data')
    project_id = project_data['id']

    # create Data Collection job
    dc_job_payload = {"title": "New DC WORK job - api",
                      "teamId": team_id,
                      "projectId": project_id,
                      "type": "DATA_COLLECTION"}

    res = api.post_create_dc_job_v2(team_id=team_id, payload=dc_job_payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    job_data = res.json_response.get('data')
    assert job_data.get('type') == 'DATA_COLLECTION'
    dc_job_id = job_data['id']

    return {
        "username": username,
        "password": password,
        "team_id": team_id,
        "api": api,
        "project_id": project_id,
        "dc_job_id": dc_job_id
    }


# get /work/v2/job/dc/setting
def test_get_dc_job_settings_valid(setup):
    api = setup['api']

    res = api.get_dc_job_settings(team_id=setup['team_id'], job_id=setup['dc_job_id'])
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response['data']
    assert data['jobId'] == setup['dc_job_id']
    assert data['launchPlatform'] == []
    assert data['enableBlueTooth'] is False
    assert data['latestAppVersion'] is False
    assert data['reusablePrompt'] is False
    assert data['reusablePin'] is False
    assert data['maxJudgmentPerContributor'] == 0


def test_get_dc_job_settings_invalid_cookies(setup):
    api = QualityFlowApiWork()

    res = api.get_dc_job_settings(team_id=setup['team_id'], job_id=setup['dc_job_id'])
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'

@pytest.mark.skip(reason="Test scripts not valid because there is no checking mechanism for team_id on the BackEnd code")
@allure.link("Bug DC-987", "https://appen.atlassian.net/browse/DC-987")
@pytest.mark.parametrize('name, team_id, status_code, message', [
    ('empty', '', 400, 'Job not found'),
    ('not exist', 'fkreek0mvml', 203, 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 203, 'Access Denied')
])
def test_get_dc_job_settings_invalid_team_id(setup, name, team_id, status_code, message):
    api = setup['api']

    res = api.get_dc_job_settings(team_id=team_id, job_id=setup['dc_job_id'])
    assert res.status_code == status_code
    assert res.json_response['message'] == message


def test_get_dc_job_settings_empty_job_id(setup):
    api = setup['api']

    res = api.get_dc_job_settings(team_id=setup['team_id'], job_id="")
    assert res.status_code == 400
    assert res.json_response['message'] in 'Job not found. Please check again.'


# post /work/v2/job/dc/setting
def test_post_dc_job_settings_valid(setup):
    api = setup['api']

    payload = {
        "jobId": setup['dc_job_id'],
        "launchPlatform": [
            "Android", "IOS"
        ],
        "enableBlueTooth": "true",
        "latestAppVersion": "true",
        "reusablePrompt": "true",
        "reusablePin": "true",
        "maxJudgmentPerContributor": 2
    }

    res = api.post_dc_job_settings(team_id=setup['team_id'], payload=payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response['data']
    assert data['jobId'] == setup['dc_job_id']
    assert data['launchPlatform'] == ["Android", "IOS"]
    assert data['enableBlueTooth'] is True
    assert data['latestAppVersion'] is True
    assert data['reusablePrompt'] is True
    assert data['reusablePin'] is True
    assert data['maxJudgmentPerContributor'] == 2

    res_get_settings = api.get_dc_job_settings(team_id=setup['team_id'], job_id=setup['dc_job_id'])
    assert res_get_settings.status_code == 200
    assert res_get_settings.json_response['message'] == 'success'

    data_get_settings = res_get_settings.json_response['data']
    assert data_get_settings['jobId'] == setup['dc_job_id']
    assert data_get_settings['launchPlatform'] == ["Android", "IOS"]
    assert data_get_settings['enableBlueTooth'] is True
    assert data_get_settings['latestAppVersion'] is True
    assert data_get_settings['reusablePrompt'] is True
    assert data_get_settings['reusablePin'] is True
    assert data_get_settings['maxJudgmentPerContributor'] == 2


def test_post_dc_job_settings_invalid_cookies(setup):
    api = QualityFlowApiWork()

    payload = {
        "jobId": setup['dc_job_id'],
        "launchPlatform": [
            "Android", "IOS"
        ],
        "enableBlueTooth": "true",
        "latestAppVersion": "true",
        "reusablePrompt": "true",
        "reusablePin": "true",
        "maxJudgmentPerContributor": 2
    }

    res = api.post_dc_job_settings(team_id=setup['team_id'], payload=payload)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'

@pytest.mark.skip(reason="Test scripts not valid because there is no checking mechanism for team_id on the BackEnd code")
@allure.link("Bug DC-987", "https://appen.atlassian.net/browse/DC-987")
@pytest.mark.parametrize('name, team_id, status_code, message', [
    ('empty', '', 200, 'Job not found'),
    ('not exist', 'fkreek0mvml', 203, 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 203, 'Access Denied')
])
def test_post_dc_job_settings_invalid_team_id(setup, name, team_id, status_code, message):
    api = setup['api']

    payload = {
        "jobId": setup['dc_job_id'],
        "launchPlatform": [
            "Android", "IOS"
        ],
        "enableBlueTooth": "true",
        "latestAppVersion": "true",
        "reusablePrompt": "true",
        "reusablePin": "true",
        "maxJudgmentPerContributor": 2
    }

    res = api.post_dc_job_settings(team_id=team_id, payload=payload)
    assert res.status_code == status_code
    assert res.json_response['message'] == message


def test_post_dc_job_settings_empty_payload(setup):
    api = setup['api']

    res = api.post_dc_job_settings(team_id=setup['team_id'], payload="")
    assert res.status_code == 400


@pytest.mark.parametrize('name, job_id, status_code, message', [
    ('empty', '', 400, 'Job not found. Please check again.'),
    ('not exist', 'fkreek0mvml', 400, 'Job not found. Please check again.'),
    ('other user', 'cf098de7-deca-4f18-976e-9f9e9f55ca2d', 400, 'Update job config denied')
])
def test_post_dc_job_settings_invalid_job_id(setup, name, job_id, status_code, message):
    api = setup['api']

    payload = {
        "jobId": job_id,
        "launchPlatform": [
            "Android", "IOS"
        ],
        "enableBlueTooth": "true",
        "latestAppVersion": "true",
        "reusablePrompt": "true",
        "reusablePin": "true",
        "maxJudgmentPerContributor": 2
    }
    res = api.post_dc_job_settings(team_id=setup['team_id'], payload=payload)
    assert res.status_code == 400
    assert res.json_response['message'] in message


# post /v2/job/update-title-instruction
@allure.link("Bug DC-988", "https://appen.atlassian.net/browse/DC-988")
def test_post_dc_job_title_instruction_valid(setup):
    api = setup['api']

    payload = {
        "id": setup['dc_job_id'],
        "version":1,
        "projectId": setup['project_id'],
        "title": "Updated DC WORK job - api",
        "instruction": "<p>Some test instructions</p>",
        "teamId": setup['team_id'],
        "type": "DATA_COLLECTION"
    }

    res = api.post_dc_job_title_instruction(team_id=setup['team_id'], payload=payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    res2 = api.post_dc_job_title_instruction(team_id=setup['team_id'], payload=payload)
    assert res2.status_code == 200
    assert res2.json_response['message'] == 'success'

    job_by_id_payload = {"queryContents": ["jobFilter"]}

    job_by_id_res = api.post_job_by_id_v2(team_id=setup['team_id'], job_id=setup['dc_job_id'], payload=job_by_id_payload)
    assert job_by_id_res.status_code == 200
    assert job_by_id_res.json_response['message'] == 'success'

    data = job_by_id_res.json_response['data']
    assert data['id'] == setup['dc_job_id']
    assert data['instruction'] == "<p>Some test instructions</p>"
    assert data['title'] == "Updated DC WORK job - api"


def test_post_dc_job_title_instruction_invalid_cookies(setup):
    api = QualityFlowApiWork()

    payload = {
        "id": setup['dc_job_id'],
        "projectId": setup['project_id'],
        "title": "Updated DC WORK job - api",
        "instruction": "<p>Some test instructions</p>",
        "teamId": setup['team_id'],
        "type": "DATA_COLLECTION"
    }

    res = api.post_dc_job_title_instruction(team_id=setup['team_id'], payload=payload)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.skip(reason="Test scripts not valid because there is no checking mechanism for team_id on the BackEnd code")
@pytest.mark.parametrize('name, team_id, status_code, message', [
    ('not exist', 'fkreek0mvml', 203, 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 203, 'Access Denied')
])
def test_post_dc_job_title_instruction_invalid_team_id(setup, name, team_id, status_code, message):
    api = setup['api']

    payload = {
        "id": setup['dc_job_id'],
        "projectId": setup['project_id'],
        "title": "Updated DC WORK job - api",
        "instruction": "<p>Some test instructions</p>",
        "teamId": team_id,
        "type": "DATA_COLLECTION"
    }

    res = api.post_dc_job_title_instruction(team_id=team_id, payload=payload)
    assert res.status_code == status_code
    assert res.json_response['message'] == message

