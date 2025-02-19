"""
https://api-kepler.sandbox.cf3.us/work/swagger-ui/index.html#/job-resource-controller
"""
import time

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

    project_name = f"automation project {_today} {faker.zipcode()}: work controller - resource "
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
    # return {'id': '3e7c3560-b595-478b-9ca9-38ed377d8501', 'team_id': 'f8fb3aaf-f3f1-437a-9bb8-170c136e9084', 'version': 0, 'jobs': ['fd79c89f-1305-48d5-a778-b1476b487510']}



#  get resources
def test_get_resource_invalid_cookies(setup):
    api = QualityFlowApiWork()
    team_id = setup['team_id']
    project = setup['default_project']
    job_id = project['work_jobs'][0]

    res = api.get_resource(team_id=team_id, job_id=job_id, resource_type='ontology')
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_get_resource_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project = setup['default_project']
    job_id = project['work_jobs'][0]

    res = api.get_resource(team_id=team_id, job_id=job_id, resource_type='ontology')
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_get_resource_empty_job_id(setup):
    api = setup['api']
    team_id = setup['team_id']

    res = api.get_resource(team_id=team_id, job_id="", resource_type='ontology')
    assert res.status_code == 403
    assert res.json_response['message'] == 'Unauthorized'


def test_get_resource_valid(setup):
    api = setup['api']
    team_id = setup['team_id']
    project = setup['default_project']
    job_id = project['work_jobs'][1]

    res = api.get_resource(team_id=team_id, job_id=job_id, resource_type='ontology')
    assert res.status_code == 200

    assert res.json_response == [{'class_name': 'price',
                                  'description': '',
                                  'display_color': '#ad878e',
                                  'relationship_types': []},
                                 {'class_name': 'total',
                                  'description': '',
                                  'display_color': '#651FFF',
                                  'relationship_types': []}]


# post resources
def test_post_resource_invalid_cookies(setup):
    api = QualityFlowApiWork()
    team_id = setup['team_id']
    project = setup['default_project']
    job_id = project['work_jobs'][0]

    res = api.post_resource(team_id=team_id, job_id=job_id, resource_type='ontology', payload={})
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_post_resource_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project = setup['default_project']
    job_id = project['work_jobs'][0]

    res = api.post_resource(team_id=team_id, job_id=job_id, resource_type='ontology', payload={})
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_post_resource_empty_payload(setup, new_project):
    api = setup['api']
    team_id = setup['team_id']
    job_id = new_project['jobs'][0]

    res = api.post_resource(team_id=team_id, job_id=job_id, resource_type='ontology', payload={})
    assert res.status_code == 500


def test_post_resource_valid(setup, new_project):
    api = setup['api']
    team_id = setup['team_id']
    job_id = new_project['jobs'][0]
    payload = {
              "resource_team_id": team_id,
              "resource_type": "ontology",
              "resource_contents":'[{"description": "","class_name": "cat","display_color": "#FF1744", "relationship_types": []},{"description": "","class_name": "dog","display_color": "#651FFF","relationship_types": []}]'
            }
    res = api.post_resource(team_id=team_id, job_id=job_id, resource_type='ontology', payload=payload)
    assert res.status_code == 204

    res = api.get_resource(team_id=team_id, job_id=job_id, resource_type='ontology')
    assert res.status_code == 200

    assert res.json_response == [
        {
            "description": "",
            "class_name": "cat",
            "display_color": "#FF1744",
            "relationship_types": []
        },
        {
            "description": "",
            "class_name": "dog",
            "display_color": "#651FFF",
            "relationship_types": []
        }
    ]


# delete resources
def test_delete_resource_invalid_cookies(setup, new_project):
    api = QualityFlowApiWork()
    team_id = setup['team_id']
    job_id = new_project['jobs'][0]

    res = api.delete_resource(team_id=team_id, job_id=job_id, resource_type='ontology')
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_delete_resource_invalid_team_id(setup, new_project, name, team_id, message):
    api = setup['api']
    job_id = new_project['jobs'][0]

    res = api.delete_resource(team_id=team_id, job_id=job_id, resource_type='ontology')
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_delete_resource_empty_job_id(setup):
    api = setup['api']
    team_id = setup['team_id']

    res = api.delete_resource(team_id=team_id, job_id="", resource_type='ontology')
    assert res.status_code == 403
    assert res.json_response['message'] == 'Unauthorized'


def test_delete_valid(setup, new_project):
    api = setup['api']
    team_id = setup['team_id']
    job_id = new_project['jobs'][0]

    res = api.get_resource(team_id=team_id, job_id=job_id, resource_type='ontology')
    assert res.status_code == 200

    if not isinstance(res.json_response, list) and res.json_response.get('message', False) == "Not resource found":
        # first add ontology
        payload = {
            "resource_team_id": team_id,
            "resource_type": "ontology",
            "resource_contents": '[{"description": "","class_name": "cat","display_color": "#FF1744", "relationship_types": []},{"description": "","class_name": "dog","display_color": "#651FFF","relationship_types": []}]'
        }
        res = api.post_resource(team_id=team_id, job_id=job_id, resource_type='ontology', payload=payload)
        assert res.status_code == 204

    res = api.delete_resource(team_id=team_id, job_id=job_id, resource_type='ontology')
    assert res.status_code == 204

    res = api.get_resource(team_id=team_id, job_id=job_id, resource_type='ontology')
    assert res.status_code == 200

    assert res.json_response.get('message', False) == "Not resource found"


# get resource data
def test_get_resource_data_invalid_cookies(setup):
    api = QualityFlowApiWork()
    team_id = setup['team_id']
    project = setup['default_project']
    job_id = project['work_jobs'][0]

    res = api.get_resource_data(team_id=team_id, job_id=job_id, resource_type='ontology')
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_get_resource_data_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project = setup['default_project']
    job_id = project['work_jobs'][0]

    res = api.get_resource_data(team_id=team_id, job_id=job_id, resource_type='ontology')
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_get_resource_data_empty_job_id(setup):
    api = setup['api']
    team_id = setup['team_id']

    res = api.get_resource_data(team_id=team_id, job_id="", resource_type='ontology')
    assert res.status_code == 403
    assert res.json_response['message'] == 'Unauthorized'


def test_resource_data_valid(setup, new_project):
    api = setup['api']
    team_id = setup['team_id']
    job_id = new_project['jobs'][0]

    res = api.get_resource(team_id=team_id, job_id=job_id, resource_type='ontology')
    assert res.status_code == 200

    if not isinstance(res.json_response, list) and res.json_response.get('message', False) == "Not resource found":
        # first add ontology
        payload = {
            "resource_team_id": team_id,
            "resource_type": "ontology",
            "resource_contents": '[{"description": "","class_name": "cat","display_color": "#FF1744", "relationship_types": []},{"description": "","class_name": "dog","display_color": "#651FFF","relationship_types": []}]'
        }
        res = api.post_resource(team_id=team_id, job_id=job_id, resource_type='ontology', payload=payload)
        assert res.status_code == 204

    res = api.get_resource_data(team_id=team_id, job_id=job_id, resource_type='ontology')
    assert res.status_code == 200
    assert res.json_response == [{'description': '', 'class_name': 'cat', 'display_color': '#FF1744', 'relationship_types': []}, {'description': '', 'class_name': 'dog', 'display_color': '#651FFF', 'relationship_types': []}]


    # TODO expend test coverage