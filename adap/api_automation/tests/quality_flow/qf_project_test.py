"""
swagger - https://api-kepler.sandbox.cf3.us/project/swagger-ui/index.html#/Project%20Controller
"""
from adap.api_automation.services_config.quality_flow import QualityFlowApiProject
import pytest
import datetime
from faker import Faker
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id

# TODO create test data on Sandbox

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

    project_name = f"automation project {_today} {faker.zipcode()} for delete tests"
    payload = {"name": project_name,
               "description": project_name
               # "unitSegmentType": "UNIT_ONLY"
               }

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


#    get projects
def test_get_projects_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']

    payload = {"pageNumber": 1, "pageSize": 30, "sortModel": [], "filterModel": {}}
    res = api.get_list_of_projects(team_id=team_id, payload=payload)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_get_projects_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    payload = {"pageNumber": 1, "pageSize": 30, "sortModel": [], "filterModel": {}}
    res = api.get_list_of_projects(team_id=team_id, payload=payload)
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_get_list_of_projects(setup):
    api = setup['api']
    team_id = setup['team_id']

    payload = {"pageNumber": 1, "pageSize": 5, "sortModel": [], "filterModel": {}}
    res = api.get_list_of_projects(team_id=team_id, payload=payload)

    data = res.json_response.get('data', False)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    assert data, "Projects data have not been found for user"

    projects_list = data.get('list', [])
    assert len(projects_list) == 5, "Number on projects not matched to totalElements"

    for project in projects_list:
        assert project.get('teamId', None) == team_id

    # why owner is None


#  ------- create project --------
def test_create_project_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']

    payload = {"name": "test 0819 1",
               "description": "test 0819 1",
               "unitSegmentType": "UNIT_ONLY"}

    res = api.post_create_project(team_id=team_id, payload=payload)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_create_project_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    payload = {"name": "test",
               "description": "test"
               # "unitSegmentType": "UNIT_ONLY"
               }
    res = api.post_create_project(team_id=team_id, payload=payload)
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.parametrize('name, payload, status_code, error_msg', [
    ('empty', {}, 400, 'name: project name cannot be empty; '),
    ('name is empty', {"name": "",
                       "description": "test"}, 400, 'name: project name cannot be empty; name: must at lease '
                                                    'contain 1 character and less than 255 characters; '),
    ('name > 255 chars', {"name": "q" * 256,
                          "description": "test"}, 400, 'name: must at lease contain 1 character and less '
                                                       'than 255 characters; '),
    # ('unitSegmentType is empty', {"name": "test"}, 400, 'unitSegmentType: must not be null; description: description cannot be empty; '),
    # ('description is empty', {"name": "QF project with empty description", "unitSegmentType": "UNIT_ONLY"}, 400, 'description: description cannot be empty; '),
    # ('description is empty string', {"name": f"QF project with empty string description - {faker.zipcode()}", "description": "", "unitSegmentType": "UNIT_ONLY"}, 400, 'description: description cannot be empty; ')
])
def test_create_project_invalid_payload(setup, name, payload, status_code, error_msg):
    api = setup['api']
    team_id = setup['team_id']
    res = api.post_create_project(team_id=team_id, payload=payload)

    assert res.status_code == status_code
    actual_errors = res.json_response.get('message', '')
    assert sorted(actual_errors.lower().split('; ')) == sorted(error_msg.lower().split('; '))


def test_create_project_valid(setup):
    """
    user is able to create project with valid data
    """

    api = setup['api']
    team_id = setup['team_id']

    project_name = f"automation project {_today} {faker.zipcode()}"
    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "UNIT_ONLY"}

    res = api.post_create_project(team_id=team_id, payload=payload)
    response = res.json_response

    assert res.status_code == 200
    assert response.get('message', False) == 'success'

    data = response.get('data')
    assert data, "Project data has not been found"
    assert data.get('name', False) == project_name
    assert data.get('description', False) == project_name
    assert data.get('status', False) == "ACTIVE"
    assert data.get('unitSegmentType', False) == "UNIT_ONLY"
    assert data.get('teamId', False) == team_id
    assert data.get('version', False) == 0


def test_create_project_duplicated_name_not_allowed(setup):
    """
    project name must be unique
    """
    api = setup['api']
    team_id = setup['team_id']

    project_name = f"automation project {_today} {faker.zipcode()} unique name"
    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "UNIT_ONLY"}

    res = api.post_create_project(team_id=team_id, payload=payload)
    response = res.json_response

    assert res.status_code == 200
    assert response.get('message', False) == 'success'

    data = response.get('data', {})
    assert data.get('name', False) == project_name

    res = api.post_create_project(team_id=team_id, payload=payload)
    response = res.json_response
    assert res.status_code == 200
    assert response.get('message', False).lower() == 'project name already exists.'


def test_create_project_with_segments(setup):
    api = setup['api']
    team_id = setup['team_id']

    project_name = f"automation project {_today} {faker.zipcode()} SEGMENTED"
    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "SEGMENTED"}

    res = api.post_create_project(team_id=team_id, payload=payload)
    response = res.json_response

    assert res.status_code == 200
    assert response.get('message', False) == 'success'

    data = response.get('data')
    assert data, "Project data has not been found"
    assert data.get('name', False) == project_name
    assert data.get('description', False) == project_name
    assert data.get('status', False) == "ACTIVE"
    assert data.get('unitSegmentType', False) == "SEGMENTED"
    assert data.get('teamId', False) == team_id
    assert data.get('version', False) == 0


# ---- update project ------
def test_update_project_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    payload = {
        "id": 712,
        "name": "updated test 00001",
        "description": "updated test 00001",
        "unitSegmentType": "UNIT_ONLY"
    }

    res = api.put_update_project(team_id=team_id, payload=payload)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_update_projects_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    payload = {
        "id": 712,
        "name": "updated test 00001",
        "description": "updated test 00001",
        "unitSegmentType": "UNIT_ONLY"
    }
    res = api.put_update_project(team_id=team_id, payload=payload)
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_update_project_not_exist(setup):
    api = setup['api']
    team_id = setup['team_id']
    payload = {
        "id": 712000000,
        "name": "updated test 00001",
        "description": "updated test 00001",
        "unitSegmentType": "UNIT_ONLY"
    }
    res = api.put_update_project(team_id=team_id, payload=payload)
    assert res.status_code == 203
    assert res.json_response['message'] == "Unauthorized"


def test_update_project_valid(setup):
    """
    user is able to update name, description and unitSegmentType for project
    """
    api = setup['api']
    team_id = setup['team_id']

    project_name = f"automation project {_today} {faker.zipcode()} for update"
    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "UNIT_ONLY"}

    res = api.post_create_project(team_id=team_id, payload=payload)
    response = res.json_response

    assert res.status_code == 200
    assert response.get('message', False) == 'success'
    data = response.get('data')
    assert data, "Project data has not been found"
    assert data.get('name', False) == project_name
    assert data.get('description', False) == project_name
    assert data.get('version', False) == 0
    assert data.get('unitSegmentType', False) == "UNIT_ONLY"

    project_id = data.get('displayId', False)
    assert project_id, "displayId has not been found"

    data['name'] = data['name'] + ": done"
    data['description'] = data['description'] + ": done"

    res = api.put_update_project(team_id=team_id, payload=data)
    assert res.status_code == 200
    response = res.json_response

    assert response.get('message', False) == 'success'
    updated_data = response.get('data')
    assert updated_data, "Project data has not been found"
    assert updated_data.get('name', False) == data['name']
    assert updated_data.get('description', False) == data['description']
    assert updated_data.get('displayId', False) == project_id
    assert updated_data.get('version', False) == 1


# ------------------ Project info  -----------------
# ------------------ /detail  -----------------
def test_get_project_details_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup["default_project"]['id']

    res = api.get_project_details(project_id=project_id, team_id=team_id)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_get_project_detail_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup["default_project"]['id']

    res = api.get_project_details(project_id=project_id, team_id=team_id)
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.parametrize('name, project_id', [
    ('empty', ''),
    ('not exist', 1000000),
    ('other user', "78a7d0af-1c4f-4ace-9cfd-5e34aa450dac")
])
def test_get_project_detail_invalid_project_id(setup, name, project_id):
    api = setup['api']
    team_id = setup["team_id"]

    res = api.get_project_details(project_id=project_id, team_id=team_id)
    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'


def test_get_project_details_valid(setup):
    api = setup['api']
    team_id = setup["team_id"]
    project = setup["default_project"]

    res = api.get_project_details(project_id=project['id'], team_id=team_id)
    response = res.json_response

    assert res.status_code == 200
    assert response.get('message', False) == 'success'

    data = response.get('data')
    assert data, "Project data has not been found"
    assert data.get('name', False) == project['name']
    assert data.get('description', False) == project['description']
    assert data.get('status', False) == project['status']
    assert data.get('unitSegmentType', False) == project['unitSegmentType']
    assert data.get('teamId', False) == team_id
    assert data.get('version', False) == project['version']


# ------------------ /data-summary  -----------------
def test_get_project_data_summary_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup["default_project"]['id']

    res = api.get_project_data_summary(project_id=project_id, team_id=team_id)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_get_project_data_summary_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup["default_project"]['id']

    res = api.get_project_data_summary(project_id=project_id, team_id=team_id)
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.parametrize('name, project_id', [
    ('empty', ''),
    ('not exist', 1000000),
    ('other user', "78a7d0af-1c4f-4ace-9cfd-5e34aa450dac")
])
def test_get_project_data_summary_invalid_project_id(setup, name, project_id):
    api = setup['api']
    team_id = setup["team_id"]

    res = api.get_project_data_summary(project_id=project_id, team_id=team_id)
    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'


def test_get_project_data_summary_valid(setup):
    api = setup['api']
    team_id = setup["team_id"]
    project = setup["default_project"]

    res = api.get_project_data_summary(project_id=project['id'], team_id=team_id)
    response = res.json_response

    assert res.status_code == 200
    assert response.get('message', False) == 'success'

    data = response.get('data')
    assert data, "Project data has not been found"
    assert data.get('projectId', False) == project['id']
# To match the code with the swagger, we need to comment some of the below response keys
    required_data = ["totalUnits",
                     #"newUnits",
                     #"assignedUnits",
                     #"judgeableUnits",
                     #"finalizedUnits",
                     "lastUpdated",
                     #"qaRejectedUnits",
                     #"qaAcceptedUnits",
                     #"qaModifiedUnits",
                     #"qaRejectedPendingUnits",
                     #"qaModifiedPendingUnits",
                     #"disputeAcceptedUnits",
                     #"disputeRejectedUnits",
                     #"feedbackDisputedUnits",
                     "submittedUnits",
                     "submittedUnitGroups",
                     "totalUnitGroups",
                     "audioTranscriptionTotalDuration",
                     #"runningBatchJobCount",
                     "submittedPercentage"]

    for param in required_data:
        assert param in data.keys()


#  --------- Delete project ------------------------
def test_delete_project_invalid_cookies(setup, new_project):
    api = QualityFlowApiProject()
    team_id = new_project['team_id']
    project_id = new_project["id"]
    version = new_project["version"]

    res = api.delete_project(project_id=project_id, team_id=team_id, version_id=version)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_delete_project_invalid_team_id(setup, name, team_id, new_project, message):
    api = setup['api']
    project_id = new_project["id"]
    version = new_project["version"]

    res = api.delete_project(project_id=project_id, team_id=team_id, version_id=version)
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.parametrize('name, project_id', [
    ('empty', ''),
    ('not exist', 1000000),
    ('other user', "78a7d0af-1c4f-4ace-9cfd-5e34aa450dac")
])
def test_delete_invalid_project_id(setup, name, project_id):
    api = setup['api']
    team_id = setup["team_id"]

    res = api.delete_project(project_id=project_id, team_id=team_id, version_id=0)
    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'


def test_delete_invalid_project_version(setup, new_project):
    api = setup['api']
    project_id = new_project["id"]
    team_id = new_project['team_id']

    res = api.delete_project(project_id=project_id, team_id=team_id, version_id=2)
    assert res.status_code == 400
    assert res.json_response['message'].lower() == 'data not found.'


def test_delete_project_valid(setup, new_project):
    api = setup['api']
    project_id = new_project["id"]
    team_id = new_project['team_id']
    version = new_project['version']

    res = api.delete_project(project_id=project_id, team_id=team_id, version_id=version)
    response = res.json_response
    assert res.status_code == 200
    assert response.get('message', False) == 'success'

    data = response.get('data')
    assert data, "Project data has not been found"
    assert data.get('status', False) == "INACTIVE"
    assert data.get('version', False) == 1

    # check project detail
    res = api.get_project_details(project_id, team_id)
    assert res.status_code == 200
    response = res.json_response
    assert response.get('message', False) == 'success'

    data = response.get('data')
    assert data, "Project data has not been found"
    assert data.get('status', False) == "INACTIVE"
    assert data.get('version', False) == 1
