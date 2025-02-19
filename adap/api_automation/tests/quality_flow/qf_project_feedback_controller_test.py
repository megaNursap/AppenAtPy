"""
https://api-kepler.integration.cf3.us/project/swagger-ui/index.html#/Feedback Controller
"""

from adap.api_automation.services_config.quality_flow import QualityFlowApiProject
import pytest
import datetime
from faker import Faker
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id
from adap.perf_platform.utils.logging import get_logger

LOGGER = get_logger(__name__)

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
    api = QualityFlowApiProject()
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
    api = setup['api']
    team_id = setup['team_id']

    project_name = f"automation project {_today} {faker.zipcode()}: feedback testing "
    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "UNIT_ONLY"}

    res = api.post_create_project(team_id=team_id, payload=payload)
    assert res.status_code == 200

    response = res.json_response
    data = response.get('data')
    assert data, "Project data has not been found"

    return {
        "id": data['id'],
        "team_id": data['teamId'],
        "version": data['version']
    }


# --------Feedback Statistics-------------------------------------
def test_get_feedback_statistics_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project = setup['default_project']
    project_id = project['id']

    res = api.get_feedback_statistics(team_id=team_id, project_id=project_id)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'

@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_feedback_statistics_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project = setup['default_project']
    project_id = project['id']

    res = api.get_feedback_statistics(team_id=team_id, project_id=project_id)
    assert res.status_code == 203
    assert res.json_response['message'] == message

@pytest.mark.parametrize('name, project_id', [
    ('empty', ''),
    ('not exist', 'fkreek0mvml'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b')
])
def test_feedback_statistics_invalid_project_id(setup, name, project_id):
    api = setup['api']
    team_id = setup['team_id']

    res = api.get_feedback_statistics(team_id=team_id, project_id=project_id)
    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'

def test_get_feedback_statistics_valid(setup):
    api = setup['api']
    team_id = setup['team_id']
    project_id = setup['default_project']['id']

    res = api.get_feedback_statistics(team_id=team_id, project_id=project_id)
    assert res.status_code == 200

    response = res.json_response
    assert response.get('message', False) == 'success'
    data = response.get('data')
    assert data.get('totalFeedbackUnits', False) == 0
    assert data.get('pendingUnits', False) == 0
    assert data.get('disputedUnits', False) == 0
    assert data.get('resolvedUnits', False) == 0


# --------Feedback Columns-------------------------------------

def test_get_feedback_columns_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project = setup['default_project']
    project_id = project['id']

    res = api.get_feedback_columns(team_id=team_id, project_id=project_id)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'

@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_feedback_columns_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project = setup['default_project']
    project_id = project['id']

    res = api.get_feedback_columns(team_id=team_id, project_id=project_id)
    assert res.status_code == 203
    assert res.json_response['message'] == message

@pytest.mark.parametrize('name, project_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Unauthorized'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Unauthorized')
])
def test_feedback_columns_invalid_project_id(setup, name, project_id, message):
    api = setup['api']
    team_id = setup['team_id']

    res = api.get_feedback_columns(team_id=team_id, project_id=project_id)
    assert res.status_code == 203
    assert res.json_response['message'] == message

def test_get_feedback_columns_valid(setup):
    api = setup['api']
    team_id = setup['team_id']
    project_id = setup['default_project']['id']

    res = api.get_feedback_columns(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    response = res.json_response
    assert response.get('message', False) == 'success'

    data = res.json_response["data"]
    assert data["columnDefs"][0]["headerName"] == "unit"
    assert list(filter(lambda x: x['group'] != 'unit', data["columnDefs"][0]['children'])) == []

    assert data["columnDefs"][0]['children'][0]['displayName'] == 'Unit ID'
    assert data["columnDefs"][0]['children'][0]['searchKey'] == 'unitDisplayId'
    assert data["columnDefs"][0]['children'][0]['filterType'] == 'text'
    assert sorted(data["columnDefs"][0]['children'][0]['displayStyle']) == sorted(['link', 'visible'])

    assert data["columnDefs"][0]['children'][1]['displayName'] == 'Status'
    assert data["columnDefs"][0]['children'][1]['searchKey'] == 'jobStatus'
    assert data["columnDefs"][0]['children'][1]['filterType'] == 'set'
    assert sorted(data["columnDefs"][0]['children'][1]['displayStyle']) == sorted(['tag', 'visible'])


# --------Feedback Columns-------------------------------------

def test_post_feedback_list_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project = setup['default_project']
    project_id = project['id']

    payload = {"projectId": project_id, "filterModel": {}, "queryString": ""}
    res = api.post_feedback_list(team_id=team_id, project_id=project_id, payload=payload)

    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'

@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_post_feedback_list_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project = setup['default_project']
    project_id = project['id']

    payload = {"projectId": project_id, "filterModel": {}, "queryString": ""}
    res = api.post_feedback_list(team_id=team_id, project_id=project_id, payload=payload)

    assert res.status_code == 203
    assert res.json_response['message'] == message

@pytest.mark.parametrize('name, project_id', [
    ('empty', ''),
    ('not exist', 'fkreek0mvml'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b')
])
def test_post_feedback_list_invalid_project_id(setup, name, project_id):
    api = setup['api']
    team_id = setup['team_id']

    payload = {"projectId": project_id, "filterModel": {}, "queryString": ""}
    res = api.post_feedback_list(team_id=team_id, project_id=project_id, payload=payload)

    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'

def test_post_feedback_list_valid(setup):
    api = setup['api']
    team_id = setup['team_id']
    project_id = setup['default_project']['id']

    payload = {"startRow": 0, "endRow": 0, "filterModel": {}, "sortModel": [], "queryString": ""}
    res = api.post_feedback_list(team_id=team_id, project_id=project_id, payload=payload)

    response = res.json_response

    assert res.status_code == 200
    assert response.get('message', False) == 'success'

    data = response.get('data')
    assert data.get('units', False) == []
    assert data.get('lastRow', False) == 0
    assert data.get('secondaryColumnFields', False) is None
    assert data.get('totalElements', False) == 0