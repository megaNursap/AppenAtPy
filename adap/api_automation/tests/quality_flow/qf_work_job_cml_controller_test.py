"""
https://api-kepler.integration.cf3.us/work/swagger-ui/index.html#/job-cml-controller
"""

import pytest
from faker import Faker
import datetime

from adap.api_automation.services_config.quality_flow import QualityFlowApiWork, QualityFlowApiProject
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_api,
              pytest.mark.regression_qf,
              mark_env]

faker = Faker()

_today = datetime.datetime.now().strftime("%Y_%m_%d")


@pytest.fixture(scope="module")
def setup():
    username = get_test_data('qf_user', 'email')
    password = get_test_data('qf_user', 'password')
    default_project = get_test_data('qf_user', 'default_project')
    team_id = get_user_team_id('qf_user')
    api = QualityFlowApiWork()
    api.get_valid_sid(username, password)
    return {
        "username": username,
        "password": password,
        "team_id": team_id,
        "api": api,
        "default_project": default_project
    }


@pytest.fixture(scope="module")
def new_project(setup):
    username = get_test_data('qf_user', 'email')
    password = get_test_data('qf_user', 'password')

    api = QualityFlowApiProject()
    api.get_valid_sid(username, password)
    team_id = setup['team_id']

    project_name = f"automation project {_today} {faker.zipcode()}: work controller - cml "
    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "UNIT_ONLY"}

    res = api.post_create_project(team_id=team_id, payload=payload)
    assert res.status_code == 200

    response = res.json_response
    data = response.get('data')
    assert data, "Project data has not been found"

    # create job
    job_api = QualityFlowApiWork()
    job_api.get_valid_sid(username, password)
    payload = {"title": "New  WORK job - cml test",
               "teamId": team_id,
               "projectId": data['id'],
               "type": "WORK",
               "flowId": '',
               "templateDisplayNm": "No use template",
               "templateType": {"index": 1},
               "cml": {"js": "",
                       "css": "",
                       "cml": "<cml:audio_annotation source-data='{{audio_url}}' name='Annotate the thing' validates='required' />",
                       "instructions": "Test CML API update"}
               }

    res = job_api.post_create_job_v2(team_id=team_id, payload=payload)
    assert res.status_code == 200

    return {
        "id": data['id'],
        "team_id": data['teamId'],
        "version": data['version'],
        "jobs": [res.json_response['data']['id']]
    }


#   get cml
def test_get_cml_invalid_cookies(setup):
    api = QualityFlowApiWork()
    team_id = setup['team_id']
    project = setup['default_project']
    job_id = project['work_jobs'][0]

    res = api.get_cml(team_id=team_id, job_id=job_id)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message, status', [
    ('empty', '', 'must not be empty', 400),
    ('not exist', 'fkreek0mvml', 'Access Denied', 203),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied', 203)
])
def test_get_cml_invalid_team_id(setup, name, team_id, message, status):
    api = setup['api']
    project = setup['default_project']
    job_id = project['work_jobs'][0]

    res = api.get_cml(team_id=team_id, job_id=job_id)
    assert res.status_code == status
    assert res.json_response['message'] == message


@pytest.mark.parametrize('name, job_id, error_msg', [
    ('empty', '', 'must not be empty'),
    ('not exist', 'fkreek0mvml', 'No template found')
])
def test_get_cml_invalid_job_id(setup, name, job_id, error_msg):
    api = setup['api']
    team_id = setup['team_id']

    res = api.get_cml(team_id=team_id, job_id=job_id)
    assert res.status_code == 400
    assert res.json_response['message'] == error_msg


def test_get_cml_valid(setup):
    api = setup['api']
    team_id = setup['team_id']
    project = setup['default_project']
    job_id = project['work_jobs'][-1]

    res = api.get_cml(team_id=team_id, job_id=job_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response.get('data')
    assert data, "Data has not been found"
    assert data['jobId'] == job_id
    assert data['teamId'] == team_id

    assert data['instructions'], "instructions have not been found"
    assert data['cml'], "cml has not been found"
    assert data['validators'] == ["required"]
    assert sorted(data['tags']) == sorted(["radios", "radio"])


# --------  put cml -------
def test_put_cml_invalid_cookies(setup):
    api = QualityFlowApiWork()
    team_id = setup['team_id']

    res = api.put_cml(team_id=team_id, payload={})
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message, status', [
    ('not exist', 'fkreek0mvml', 'Access Denied', 203),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied', 203)
])
def test_put_cml_invalid_team_id(setup, name, team_id, message, status):
    api = setup['api']

    res = api.put_cml(team_id=team_id, payload={})
    assert res.status_code == status
    assert res.json_response['message'] == message


def test_put_cml_invalid_payload(setup):
    api = setup['api']
    team_id = setup['team_id']

    res = api.put_cml(team_id=team_id, payload={})
    assert res.status_code == 400

    required_fields = {'id': 'must not be empty',
                       'version': 'must not be null',
                       'jobId': 'must not be empty'}

    for k, v in required_fields.items():
        assert f"{k}: {v}" in res.json_response['message']


def test_put_cml_valid(setup, new_project):
    api = setup['api']
    team_id = setup['team_id']
    job_id = new_project['jobs'][0]

    res = api.get_cml(team_id=team_id, job_id=job_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    initial_job_config = res.json_response.get('data')

    initial_cml = initial_job_config['cml']
    new_cml = initial_cml.replace("Annotate the thing", "Annotate the thing - updated")
    new_instruction = "Instructions updated"

    initial_job_config['cml'] = new_cml
    initial_job_config['instructions'] = new_instruction

    res = api.put_cml(team_id=team_id, payload=initial_job_config)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response.get('data')
    assert data, "Data has not been found"
    assert data['jobId'] == job_id
    assert data['teamId'] == team_id
    assert data['cml'] == new_cml

    assert data['instructions'] == new_instruction


# # ----- post cml/clone
# def test_post_clone_cml_invalid_cookies(setup):
#     api = QualityFlowApiWork()
#     team_id = setup['team_id']
#     project = setup['default_project']
#     job_id = project['work_jobs'][0]
#
#     res = api.post_cml_clone(team_id=team_id, job_id=job_id, copied_from='')
#     assert res.status_code == 401
#     assert res.json_response['message'] == 'Please login'
#
#
# @pytest.mark.parametrize('name, team_id, message', [
#     ('empty', '', 'Unauthorized'),
#     ('not exist', 'fkreek0mvml', 'Access Denied'),
#     ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
# ])
# def test_post_clone_cml_invalid_team_id(setup, name, team_id, message):
#     api = setup['api']
#     project = setup['default_project']
#     job_id = project['work_jobs'][0]
#
#     res = api.post_cml_clone(team_id=team_id, job_id=job_id, copied_from='')
#     assert res.status_code == 203
#     assert res.json_response['message'] == message
#
# deprecated
# def test_post_clone_cml_invalid_job_id(setup):
#     api = setup['api']
#     team_id = setup['team_id']
#     project = setup['default_project']
#     job_id = project['work_jobs'][0]
#
#     res = api.post_cml_clone(team_id=team_id, job_id='', copied_from=job_id)
#     assert res.status_code == 400
#     assert res.json_response['message'] == 'must not be empty'


def test_post_clone_cml_invalid_copy_job_id(setup):
    api = setup['api']
    team_id = setup['team_id']
    project = setup['default_project']
    job_id = project['work_jobs'][0]

    res = api.post_cml_clone(team_id=team_id, job_id=job_id, copied_from='')
    assert res.status_code == 400
    assert res.json_response['message'] == 'must not be empty'


def test_post_clone_cml_valid(setup, new_project):
    api = setup['api']
    team_id = setup['team_id']
    project = setup['default_project']
    copy_job_id = project['work_jobs'][0]
    job_id = new_project['jobs'][0]

    res = api.post_cml_clone(team_id=team_id, job_id=job_id, copied_from=copy_job_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'Job partial cloned, but not cml/ontology'


#  -------------- delete cml --------------
def test_delete_cml_invalid_cookies(setup):
    api = QualityFlowApiWork()
    team_id = setup['team_id']
    project = setup['default_project']
    job_id = project['work_jobs'][0]

    res = api.delete_cml(team_id=team_id, job_id=job_id)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_delete_cml_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project = setup['default_project']
    job_id = project['work_jobs'][0]

    res = api.delete_cml(team_id=team_id, job_id=job_id)
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_delete_cml_invalid_job_id(setup):
    api = setup['api']
    team_id = setup['team_id']

    res = api.delete_cml(team_id=team_id, job_id='')
    assert res.status_code == 400
    assert res.json_response['message'] == 'must not be empty'


def test_delete_cml_valid(setup, new_project):
    api = setup['api']
    team_id = setup['team_id']
    job_id = new_project['jobs'][0]

    res = api.delete_cml(team_id=team_id, job_id=job_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    res = api.get_cml(team_id=team_id, job_id=job_id)
    assert res.status_code == 400
    assert res.json_response['message'] == 'No template found'

# deprecated
# def test_post_clone_cml_job_cml_empty(setup, new_project):
#     api = setup['api']
#     team_id = setup['team_id']
#     project = setup['default_project']
#     copy_job_id = project['work_jobs'][0]
#     job_id = new_project['jobs'][0]
#
#     res = api.get_cml(team_id=team_id, job_id=job_id)
#
#     if res.status_code != 400:
#         res = api.delete_cml(team_id=team_id, job_id=job_id)
#         assert res.status_code == 200
#
#     res = api.post_cml_clone(team_id=team_id, job_id=job_id, copied_from=copy_job_id)
#     assert res.status_code == 200
#     assert res.json_response['message'] == 'success'
#
#     res = api.get_cml(team_id=team_id, job_id=job_id)
#     assert res.status_code == 200
#     assert res.json_response['message'] == 'success'

# TODO increase test coverage for cml endpoints
