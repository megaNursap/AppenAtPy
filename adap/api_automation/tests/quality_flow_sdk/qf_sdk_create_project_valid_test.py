import datetime
import pytest
import json
import appen_project_flow_sdk
from appen_project_flow_sdk.apis.tags import public_api_controller_api
from appen_project_flow_sdk.model.project_dto import ProjectDTO
from faker import Faker
from adap.api_automation.services_config.quality_flow import QualityFlowApiProject
from adap.api_automation.utils.data_util import get_test_data

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_api_sdk,
              mark_env]

faker = Faker()

_today = datetime.datetime.now().strftime("%Y_%m_%d")
username = get_test_data('qf_user_api', 'email')
password = get_test_data('qf_user_api', 'password')
team_id = get_test_data('qf_user_api', 'teams')[0]['id']
api_key = get_test_data('qf_user_api', 'api_key')

configuration = appen_project_flow_sdk.Configuration(
    host='https://api.integration.cf3.us/v1'
)

configuration.api_key['Authorization'] = 'Token token=' + api_key


@pytest.fixture(scope="module")
def setup():
    project_name = f"automation project {_today} {faker.zipcode()}"

    query_params = {
        'teamId': str(team_id),
    }
    project_dto = ProjectDTO(
        name=project_name,
        description="Description",
        unitSegmentType="UNIT_ONLY"
    )

    return {
        "project_dto": project_dto,
        "project_name": project_name,
        "query_params": query_params
    }

@pytest.fixture(scope="module")
def teardown():
    # Delete project send API
    api_delete = QualityFlowApiProject()
    api_delete.get_valid_sid(username, password)

    res = api_delete.delete_project(project_id=setup['project_id'], team_id=team_id, version_id=0)
    response = res.json_response
    assert res.status_code == 200
    assert response.get('message', False) == 'success'


@pytest.mark.dependency
@pytest.mark.qf_sdk_api
def test_sdk_create_project_valid(setup):
    global project_id

    api_client = appen_project_flow_sdk.ApiClient(configuration)

    api_instance = public_api_controller_api.PublicApiControllerApi(api_client)

    api_response = api_instance.create_project(body=setup['project_dto'], query_params=setup['query_params'],
                                               skip_deserialization=True)

    response = api_response.response.data.decode("UTF-8")
    json_response = json.loads(response)
    assert json_response['message'] == 'success'
    assert json_response['code'] == 200
    assert json_response['data']['name'] == setup['project_name']

    project_id = json_response['data']['id']


@pytest.mark.dependency(depends=["test_sdk_create_project_valid"])
def test_sdk_can_not_create_project_with_same_name(setup):
    api_client = appen_project_flow_sdk.ApiClient(configuration)

    api_instance = public_api_controller_api.PublicApiControllerApi(api_client)

    api_response = api_instance.create_project(body=setup['project_dto'], query_params=setup['query_params'], skip_deserialization=True)

    response = api_response.response.data.decode("UTF-8")
    json_response = json.loads(response)
    assert json_response['message'] == 'Project name already exists.'
    assert json_response['code'] == 3016

    # Delete project send API
    api_delete = QualityFlowApiProject()
    api_delete.get_valid_sid(username, password)

    res = api_delete.delete_project(project_id=project_id, team_id=team_id, version_id=0)
    response = res.json_response
    assert res.status_code == 200
    assert response.get('message', False) == 'success'
