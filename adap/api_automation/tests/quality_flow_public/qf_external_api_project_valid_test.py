import datetime

import pytest
from faker import Faker

from adap.api_automation.services_config.quality_flow import QualityFlowApiProject
from adap.api_automation.services_config.quality_flow import QualityFlowExternalApiProject
from adap.api_automation.utils.data_util import get_test_data

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_api,
              pytest.mark.regression_qf,
              mark_env]

faker = Faker()

_today = datetime.datetime.now().strftime("%Y_%m_%d")
username = get_test_data('qf_user_api', 'email')
password = get_test_data('qf_user_api', 'password')
api_key = get_test_data('qf_user_api', 'api_key')


@pytest.fixture(scope="module")
def setup():
    project_name = f"automation project {_today} {faker.zipcode()}"
    payload = {"name": project_name}
    team_id = get_test_data('qf_user_api', 'teams')[0]['id']

    return {
        "payload": payload,
        "project_name": project_name,
        "team_id":team_id
    }


@pytest.mark.dependency
@pytest.mark.qf_public_api
@pytest.mark.qf_api_smoke
@pytest.mark.create_project
def test_create_project_valid_external(setup):
    """
    user is able to create project with valid data
    the test_account user must be provisioned to be on a team with quality_flow_enabled set to true
    """
    global project_id

    api = QualityFlowExternalApiProject(api_key=api_key)
    project_name = setup['project_name']

    res = api.post_create_project(team_id=setup["team_id"], payload=setup['payload'], headers=api.headers)
    response = res.json_response
    assert res.status_code == 200
    assert response.get('message', False) == 'success'

    data = response.get('data')
    assert data, "Project data has not been found"
    assert data.get('name', False) == project_name
    assert data.get('status', False) == "ACTIVE"
    assert data.get('teamId', False) == setup["team_id"]
    assert data.get('version', False) == 0

    project_id = data.get('id', False)


@pytest.mark.dependency(depends=["test_create_project_valid_external"])
@pytest.mark.qf_public_api
@pytest.mark.qf_api_smoke
@pytest.mark.create_project
def test_can_not_create_project_with_same_name(setup):
    """
    Validate that user can not create a project with same project name
    """

    api = QualityFlowExternalApiProject(api_key=api_key)

    res = api.post_create_project(team_id=setup["team_id"], payload=setup['payload'], headers=api.headers)
    response = res.json_response
    assert res.status_code == 200
    assert response.get('message', False) == 'Project name already exists.'

    """
    TO DO: Remove delete_project method after admin user update 
    """

    api_delete = QualityFlowApiProject()
    api_delete.get_valid_sid(username, password)

    res = api_delete.delete_project(project_id=project_id, team_id=setup["team_id"], version_id=0)
    response = res.json_response
    assert res.status_code == 200
    assert response.get('message', False) == 'success'

def test_create_project_with_description(setup):
    """
        Validate that user can create a project with description
    """
    project_name = f"QF project with description API test {_today} {faker.zipcode()}"

    payload_with_description = {"name": project_name,
               "description": project_name}

    api = QualityFlowExternalApiProject(api_key=api_key)

    res = api.post_create_project(team_id=setup["team_id"], payload=payload_with_description, headers=api.headers)
    response = res.json_response
    assert res.status_code == 200
    assert response.get('message', False) == 'success'

    data = response.get('data')
    assert data, "Project data has not been found"
    assert data.get('name', False) == project_name
    assert data.get('description', False) == project_name
    assert data.get('status', False) == "ACTIVE"
    assert data.get('teamId', False) == setup["team_id"]
    assert data.get('version', False) == 0

    project_id_new = data.get('id', False)

    """
    TO DO: Remove delete_project method after admin user update 
    """

    api_delete = QualityFlowApiProject()
    api_delete.get_valid_sid(username, password)

    res = api_delete.delete_project(project_id=project_id_new, team_id=setup["team_id"], version_id=0)
    response = res.json_response
    assert res.status_code == 200
    assert response.get('message', False) == 'success'