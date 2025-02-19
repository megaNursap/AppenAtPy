import datetime
import pytest
import json
import appen_project_flow_sdk
from appen_project_flow_sdk.apis.tags import public_api_controller_api
from appen_project_flow_sdk.model.project_dto import ProjectDTO
from faker import Faker
from adap.api_automation.services_config.quality_flow import QualityFlowApiProject
from adap.api_automation.utils.data_util import get_test_data, get_data_file

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


@pytest.fixture(autouse=True)
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

    api_client = appen_project_flow_sdk.ApiClient(configuration)

    api_instance = public_api_controller_api.PublicApiControllerApi(api_client)

    api_response = api_instance.create_project(body=project_dto, query_params=query_params, skip_deserialization=True)

    response = api_response.response.data.decode("UTF-8")
    json_response = json.loads(response)
    assert json_response['message'] == 'success'
    assert json_response['code'] == 200
    assert json_response['data']['name'] == project_name

    project_id = json_response['data']['id']


    return {
        "project_id": project_id
    }


@pytest.mark.qf_sdk_api
@pytest.mark.parametrize('file_type, data_file', [
    ('csv', '/authors.csv'),
    ('tsv', '/authors.tsv'),
])
def test_sdk_upload_data_project_valid(setup, file_type, data_file):

    file_name = get_data_file(data_file)
    body = open(file_name, 'rb')

    query_params_upload = {
        'projectId': setup['project_id'],
        'teamId': str(team_id),
        'fileName': file_name
    }

    api_client = appen_project_flow_sdk.ApiClient(configuration)
    api_instance = public_api_controller_api.PublicApiControllerApi(api_client)

    api_response_upload = api_instance.upload(query_params=query_params_upload, body=body, content_type='application/octet-stream')

    response_upload = api_response_upload.response.data.decode("UTF-8")
    json_response = json.loads(response_upload)
    assert json_response['details'] == 'successfully uploaded'
    assert json_response['fileName'] == file_name
    assert json_response['projectId'] == setup['project_id']

    # Delete project send API
    api_delete = QualityFlowApiProject()
    api_delete.get_valid_sid(username, password)

    res = api_delete.delete_project(project_id=setup['project_id'], team_id=team_id, version_id=0)
    response = res.json_response
    assert res.status_code == 200
    assert response.get('message', False) == 'success'
