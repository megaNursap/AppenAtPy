"""
https://api-kepler.integration.cf3.us/work/swagger-ui/index.html#/pin-controller
"""

import time

import pytest
from faker import Faker
import datetime

from adap.api_automation.services_config.quality_flow import QualityFlowApiWork, QualityFlowApiProject
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id, find_dict_in_array_by_value

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_api,
              pytest.mark.regression_qf,
              pytest.mark.qf_dc_api,
              mark_env]

faker = Faker()

_today = datetime.datetime.now().strftime("%Y_%m_%d")


@pytest.fixture(scope="module")
def setup():
    # User Credentials
    username = get_test_data('qf_user_dc', 'email')
    password = get_test_data('qf_user_dc', 'password')
    team_id = get_test_data('qf_user_dc', 'teams')[0]['id']
    default_dc_project = get_test_data('qf_user_dc', 'dc_project')[0]['id']
    default_dc_job = get_test_data('qf_user_dc', 'dc_project')[0]['dc_jobs'][0]

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
    job_title = f"automation job {_today} {faker.zipcode()}"
    dc_job_payload = {"title": job_title,
                      "teamId": team_id,
                      "projectId": project_id,
                      "type": "DATA_COLLECTION"}

    res = api.post_create_dc_job_v2(team_id=team_id, payload=dc_job_payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    job_data = res.json_response.get('data')
    assert job_data.get('type') == 'DATA_COLLECTION'
    job_id = job_data['id']

    return {
        "username": username,
        "password": password,
        "team_id": team_id,
        "api": api,
        "project_id": project_id,
        "job_id": job_id,
        "default_dc_project": default_dc_project,
        "default_dc_job": default_dc_job
    }


@pytest.fixture(autouse=True)
def create_dc_job(setup):
    api = setup['api']
    job_title = f"automation job {_today} {faker.zipcode()}"
    dc_job_payload = {"title": job_title,
                      "teamId": setup['team_id'],
                      "projectId": setup['project_id'],
                      "type": "DATA_COLLECTION"}

    res = api.post_create_dc_job_v2(team_id=setup['team_id'], payload=dc_job_payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    job_data = res.json_response.get('data')
    assert job_data.get('type') == 'DATA_COLLECTION'
    dc_job_id = job_data['id']

    return {'dc_job_id': dc_job_id}


# post /work/pin/generate
def test_post_dc_job_generate_pin(setup, create_dc_job):
    api = setup['api']

    payload_generate_pin = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prefix": "qa",
        "suffix": "test",
        "length": "10",
        "number": "10",
        "duration": "10",
        "recoverable": "true"
    }

    res_generate_pin = api.post_dc_pin_generate(team_id=setup['team_id'], payload=payload_generate_pin)
    assert res_generate_pin.status_code == 200
    assert res_generate_pin.json_response['message'] == 'success'


def test_post_dc_job_generate_pin_invalid_cookies(setup, create_dc_job):
    api_invalid = QualityFlowApiWork()

    payload_generate_pin = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prefix": "qa",
        "suffix": "test",
        "length": "10",
        "number": "10",
        "duration": "10",
        "recoverable": "true"
    }

    res_generate_pin = api_invalid.post_dc_pin_generate(team_id=setup['team_id'], payload=payload_generate_pin)
    assert res_generate_pin.status_code == 401
    assert res_generate_pin.json_response['message'] == 'Please login'


def test_post_dc_job_generate_pin_invalid_payload(setup):
    api = setup['api']

    res_generate_pin = api.post_dc_pin_generate(team_id=setup['team_id'], payload="")
    assert res_generate_pin.status_code == 400


@pytest.mark.skip(reason="Test scripts not valid because there is no checking mechanism for team_id on the BackEnd code")
@pytest.mark.parametrize('name, team_id, status_code, message', [
    ('not exist', 'fkreek0mvml', 203, 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 203, 'Access Denied')
])
def test_post_dc_job_generate_pin_invalid_team_id(setup, create_dc_job, name, team_id, status_code, message):
    api = setup['api']

    payload_generate_pin = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prefix": "qa",
        "suffix": "test",
        "length": "10",
        "number": "10",
        "duration": "10",
        "recoverable": "true"
    }

    res_generate_pin = api.post_dc_pin_generate(team_id=team_id, payload=payload_generate_pin)
    assert res_generate_pin.status_code == status_code
    assert res_generate_pin.json_response['message'] == message


# post /work/pin/list
def test_post_dc_job_query_pin(setup, create_dc_job):
    api = setup['api']

    payload_generate_pin = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prefix": "qa",
        "suffix": "test",
        "length": "10",
        "number": "10",
        "duration": "10",
        "recoverable": "true"
    }

    res_generate_pin = api.post_dc_pin_generate(team_id=setup['team_id'], payload=payload_generate_pin)
    assert res_generate_pin.status_code == 200
    assert res_generate_pin.json_response['message'] == 'success'

    payload_query_list = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "queryString": "",
        "pageNum": 1,
        "pageSize": 50
    }

    res_query_pin = api.post_dc_pin_list(team_id=setup['team_id'], payload=payload_query_list)
    assert res_query_pin.status_code == 200
    assert res_query_pin.json_response['message'] == 'success'

    data = res_query_pin.json_response['data']
    assert data['totalElements'] == 10


def test_post_dc_job_query_pin_invalid_cookies(setup, create_dc_job):
    api_invalid = QualityFlowApiWork()
    api = setup['api']

    payload_generate_pin = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prefix": "qa",
        "suffix": "test",
        "length": "10",
        "number": "10",
        "duration": "10",
        "recoverable": "true"
    }

    res_generate_pin = api.post_dc_pin_generate(team_id=setup['team_id'], payload=payload_generate_pin)
    assert res_generate_pin.status_code == 200
    assert res_generate_pin.json_response['message'] == 'success'

    payload_query_list = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "queryString": "",
        "pageNum": 1,
        "pageSize": 50
    }

    res_query_pin = api_invalid.post_dc_pin_list(team_id=setup['team_id'], payload=payload_query_list)
    assert res_query_pin.status_code == 401
    assert res_query_pin.json_response['message'] == 'Please login'


def test_post_dc_job_query_pin_invalid_payload(setup, create_dc_job):
    api = setup['api']

    payload_generate_pin = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prefix": "qa",
        "suffix": "test",
        "length": "10",
        "number": "10",
        "duration": "10",
        "recoverable": "true"
    }

    res_generate_pin = api.post_dc_pin_generate(team_id=setup['team_id'], payload=payload_generate_pin)
    assert res_generate_pin.status_code == 200
    assert res_generate_pin.json_response['message'] == 'success'

    res_query_pin = api.post_dc_pin_list(team_id=setup['team_id'], payload="")
    assert res_query_pin.status_code == 400


@pytest.mark.parametrize('name, team_id, status_code, message', [
    ('not exist', 'fkreek0mvml', 203, 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 203, 'Access Denied')
])
def test_post_dc_job_query_pin_invalid_team_id(setup, create_dc_job, name, team_id, status_code, message):
    api = setup['api']

    payload_query_list = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "queryString": "",
        "pageNum": 1,
        "pageSize": 50
    }

    res_query_pin = api.post_dc_pin_list(team_id=team_id, payload=payload_query_list)
    assert res_query_pin.status_code == status_code
    assert res_query_pin.json_response['message'] == message


# post /work/pin/update-status
def test_post_dc_job_pin_update_status(setup, create_dc_job):
    api = setup['api']

    payload_generate_pin = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prefix": "qa",
        "suffix": "test",
        "length": "10",
        "number": "1",
        "duration": "1",
        "recoverable": "true"
    }

    res_generate_pin = api.post_dc_pin_generate(team_id=setup['team_id'], payload=payload_generate_pin)
    assert res_generate_pin.status_code == 200
    assert res_generate_pin.json_response['message'] == 'success'

    payload_query_list = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "queryString": "",
        "pageNum": 1,
        "pageSize": 50
    }

    res_query_pin = api.post_dc_pin_list(team_id=setup['team_id'], payload=payload_query_list)
    assert res_query_pin.status_code == 200
    assert res_query_pin.json_response['message'] == 'success'
    data = res_query_pin.json_response['data']
    assert data['totalElements'] == 1
    pin_id = data['content'][0]['id']

    payload_update_status_pin = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "pinIdList": [
            pin_id
        ],
        "status": "DISABLED"
    }

    res_update_status_pin = api.post_dc_pin_update_status(team_id=setup['team_id'], payload=payload_update_status_pin)
    assert res_update_status_pin.status_code == 200
    assert res_update_status_pin.json_response['message'] == 'success'

    res_query_pin_2 = api.post_dc_pin_list(team_id=setup['team_id'], payload=payload_query_list)
    data_list_2 = res_query_pin_2.json_response['data']
    assert data_list_2['content'][0]['pinStatus'] == 'DISABLED'


def test_post_dc_job_pin_update_status_invalid_cookies(setup, create_dc_job):
    api = setup['api']
    api_invalid = QualityFlowApiWork()

    payload_generate_pin = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prefix": "qa",
        "suffix": "test",
        "length": "10",
        "number": "1",
        "duration": "1",
        "recoverable": "true"
    }

    res_generate_pin = api.post_dc_pin_generate(team_id=setup['team_id'], payload=payload_generate_pin)
    assert res_generate_pin.status_code == 200
    assert res_generate_pin.json_response['message'] == 'success'

    payload_query_list = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "queryString": "",
        "pageNum": 1,
        "pageSize": 50
    }

    res_query_pin = api.post_dc_pin_list(team_id=setup['team_id'], payload=payload_query_list)
    assert res_query_pin.status_code == 200
    assert res_query_pin.json_response['message'] == 'success'
    data = res_query_pin.json_response['data']
    assert data['totalElements'] == 1
    pin_id = data['content'][0]['id']

    payload_update_status_pin = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "pinIdList": [
            pin_id
        ],
        "status": "DISABLED"
    }

    res_update_status_pin = api_invalid.post_dc_pin_update_status(team_id=setup['team_id'], payload=payload_update_status_pin)
    assert res_update_status_pin.status_code == 401
    assert res_update_status_pin.json_response['message'] == 'Please login'


def test_post_dc_job_pin_update_status_invalid_payload(setup, create_dc_job):
    api = setup['api']

    res_update_status_pin = api.post_dc_pin_update_status(team_id=setup['team_id'], payload="")
    assert res_update_status_pin.status_code == 400

@pytest.mark.skip(reason="Test scripts not valid because there is no checking mechanism for team_id on the BackEnd code")
@pytest.mark.parametrize('name, team_id, status_code, message', [
    ('not exist', 'fkreek0mvml', 203, 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 203, 'Access Denied')
])
def test_post_dc_job_query_pin_invalid_team_id(setup, create_dc_job, name, team_id, status_code, message):
    api = setup['api']

    payload_update_status_pin = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "pinIdList": [
            "45f42748-482b-4265-8a8c-73efa872b32b"
        ],
        "status": "DISABLED"
    }

    res_update_status_pin = api.post_dc_pin_update_status(team_id=team_id, payload=payload_update_status_pin)
    assert res_update_status_pin.status_code == status_code
    assert res_update_status_pin.json_response['message'] == message


# post /work/pin/batch-update
def test_post_dc_job_pin_batch_update(setup, create_dc_job):
    api = setup['api']

    payload_generate_pin = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prefix": "qa",
        "suffix": "test",
        "length": "10",
        "number": "10",
        "duration": "1",
        "recoverable": "true"
    }

    res_generate_pin = api.post_dc_pin_generate(team_id=setup['team_id'], payload=payload_generate_pin)
    assert res_generate_pin.status_code == 200
    assert res_generate_pin.json_response['message'] == 'success'

    payload_batch_update = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "pinIdList": [],
        "selectAll": "true",
        "query": "",
        "sessionStatus": "",
        "pinExpired": "",
        "targetExpireTime": "2100-02-01T08:00:00Z"
    }

    res_batch_update = api.post_dc_pin_batch_update(team_id=setup['team_id'], payload=payload_batch_update)
    assert res_batch_update.status_code == 200
    assert res_batch_update.json_response['message'] == 'success'

    payload_query_list = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "queryString": "",
        "pageNum": 1,
        "pageSize": 50
    }

    res_query_pin = api.post_dc_pin_list(team_id=setup['team_id'], payload=payload_query_list)
    assert res_query_pin.status_code == 200
    assert res_query_pin.json_response['message'] == 'success'
    data_list = res_query_pin.json_response['data']
    assert data_list['content'][0]['expireTime'] == '2100-02-01T08:00:00Z'
    assert data_list['content'][1]['expireTime'] == '2100-02-01T08:00:00Z'
    assert data_list['content'][2]['expireTime'] == '2100-02-01T08:00:00Z'
    assert data_list['content'][3]['expireTime'] == '2100-02-01T08:00:00Z'
    assert data_list['content'][4]['expireTime'] == '2100-02-01T08:00:00Z'
    assert data_list['content'][5]['expireTime'] == '2100-02-01T08:00:00Z'
    assert data_list['content'][6]['expireTime'] == '2100-02-01T08:00:00Z'
    assert data_list['content'][7]['expireTime'] == '2100-02-01T08:00:00Z'
    assert data_list['content'][8]['expireTime'] == '2100-02-01T08:00:00Z'
    assert data_list['content'][9]['expireTime'] == '2100-02-01T08:00:00Z'


def test_post_dc_job_pin_batch_update_invalid_cookies(setup, create_dc_job):
    api_invalid = QualityFlowApiWork()

    payload_batch_update = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "pinIdList": [],
        "selectAll": "true",
        "query": "",
        "sessionStatus": "",
        "pinExpired": "",
        "targetExpireTime": "2100-02-01T08:00:00Z"
    }

    res_batch_update = api_invalid.post_dc_pin_batch_update(team_id=setup['team_id'], payload=payload_batch_update)
    assert res_batch_update.status_code == 401
    assert res_batch_update.json_response['message'] == 'Please login'


def test_post_dc_job_pin_batch_update_invalid_payload(setup, create_dc_job):
    api = setup['api']

    res_batch_update = api.post_dc_pin_batch_update(team_id=setup['team_id'], payload="")
    assert res_batch_update.status_code == 400


@pytest.mark.parametrize('name, team_id, status_code, message', [
    ('not exist', 'fkreek0mvml', 203, 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 203, 'Access Denied')
])
def test_post_dc_job_pin_batch_update_invalid_team_id(setup, create_dc_job, name, team_id, status_code, message):
    api = setup['api']

    payload_batch_update = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "pinIdList": [],
        "selectAll": "true",
        "query": "",
        "sessionStatus": "",
        "pinExpired": "",
        "targetExpireTime": "2100-02-01T08:00:00Z"
    }

    res_batch_update = api.post_dc_pin_batch_update(team_id=team_id, payload=payload_batch_update)
    assert res_batch_update.status_code == status_code
    assert res_batch_update.json_response['message'] == message


# post /work/pin/batch-count
def test_post_dc_job_pin_batch_count(setup, create_dc_job):
    api = setup['api']

    payload_generate_pin = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prefix": "qa",
        "suffix": "test",
        "length": "10",
        "number": "10",
        "duration": "1",
        "recoverable": "true"
    }

    res_generate_pin = api.post_dc_pin_generate(team_id=setup['team_id'], payload=payload_generate_pin)
    assert res_generate_pin.status_code == 200
    assert res_generate_pin.json_response['message'] == 'success'

    payload_batch_count = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "pinIdList": [],
        "selectAll": "false",
        "query": "",
        "sessionStatus": "Available",
        "pinExpired": ""
    }

    res_batch_count = api.post_dc_pin_batch_count(team_id=setup['team_id'], payload=payload_batch_count)
    assert res_batch_count.status_code == 200
    assert res_batch_count.json_response['message'] == 'success'
    assert res_batch_count.json_response['data'] == 10


def test_post_dc_job_pin_batch_count_invalid_cookies(setup, create_dc_job):
    api_invalid = QualityFlowApiWork()

    payload_batch_count = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "pinIdList": [],
        "selectAll": "false",
        "query": "",
        "sessionStatus": "Available",
        "pinExpired": ""
    }

    res_batch_count = api_invalid.post_dc_pin_batch_count(team_id=setup['team_id'], payload=payload_batch_count)
    assert res_batch_count.status_code == 401
    assert res_batch_count.json_response['message'] == 'Please login'


def test_post_dc_job_pin_batch_count_invalid_payload(setup, create_dc_job):
    api = setup['api']

    res_batch_count = api.post_dc_pin_batch_count(team_id=setup['team_id'], payload="")
    assert res_batch_count.status_code == 400


@pytest.mark.skip(reason="Test scripts not valid because there is no checking mechanism for team_id on the BackEnd code")
@pytest.mark.parametrize('name, team_id, status_code, message', [
    ('not exist', 'fkreek0mvml', 203, 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 203, 'Access Denied')
])
def test_post_dc_job_pin_batch_update_invalid_team_id(setup, create_dc_job, name, team_id, status_code, message):
    api = setup['api']

    payload_batch_count = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "pinIdList": [],
        "selectAll": "false",
        "query": "",
        "sessionStatus": "Available",
        "pinExpired": ""
    }

    res_batch_count = api.post_dc_pin_batch_count(team_id=team_id, payload=payload_batch_count)
    assert res_batch_count.status_code == status_code
    assert res_batch_count.json_response['message'] == message


# get /work/pin/session-status-list
def test_get_dc_job_pin_session_status_list(setup, create_dc_job):
    api = setup['api']

    payload_generate_pin = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prefix": "qa",
        "suffix": "test",
        "length": "10",
        "number": "10",
        "duration": "1",
        "recoverable": "true"
    }

    res_generate_pin = api.post_dc_pin_generate(team_id=setup['team_id'], payload=payload_generate_pin)
    assert res_generate_pin.status_code == 200
    assert res_generate_pin.json_response['message'] == 'success'

    res_session_list = api.get_dc_pin_session_status_list(team_id=setup['team_id'])
    assert res_session_list.status_code == 200
    assert res_session_list.json_response['message'] == 'success'

    data_list = res_session_list.json_response['data']
    assert len(data_list) == 11
    assert data_list[0] == 'Available'
    assert data_list[1] == 'In Progress'
    assert data_list[2] == 'Abandoned'
    assert data_list[3] == 'Post Processing'
    assert data_list[4] == 'Post Processed'
    assert data_list[5] == 'Quota Full'
    assert data_list[6] == 'Completed'
    assert data_list[7] == 'Auto-Rejected'
    assert data_list[8] == 'System Error'
    assert data_list[9] == 'Undefined'
    assert data_list[10] == 'Expired'


def test_get_dc_job_pin_session_status_list_invalid_cookies(setup, create_dc_job):
    api_invalid = QualityFlowApiWork()

    res_session_list = api_invalid.get_dc_pin_session_status_list(team_id=setup['team_id'])
    assert res_session_list.status_code == 401
    assert res_session_list.json_response['message'] == 'Please login'


@pytest.mark.skip(reason="Test scripts not valid because there is no checking mechanism for team_id on the BackEnd code")
@pytest.mark.parametrize('name, team_id, status_code, message', [
    ('not exist', 'fkreek0mvml', 203, 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 203, 'Access Denied')
])
def test_get_dc_job_pin_session_status_list_invalid_team_id(setup, create_dc_job, name, team_id, status_code, message):
    api = setup['api']

    res_session_list = api.get_dc_pin_session_status_list(team_id=team_id)
    assert res_session_list.status_code == status_code
    assert res_session_list.json_response['message'] == message