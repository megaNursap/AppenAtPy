from adap.api_automation.services_config.quality_flow import QualityFlowExternalApiProject, QualityFlowApiProject
import pytest
import time
import datetime
from faker import Faker
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id, get_user_api_key, get_data_file
from adap.api_automation.services_config.endpoints.quality_flow_endpoints import *

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_api,
              pytest.mark.regression_qf,
              mark_env]

faker = Faker()

_today = datetime.datetime.now().strftime("%Y_%m_%d")
username = get_test_data('qf_user_api', 'email')
password = get_test_data('qf_user_api', 'password')
api_key = get_test_data('qf_user_api', 'api_key')


@pytest.fixture(autouse=True)
def setup():
    team_id = get_test_data('qf_user_api', 'teams')[0]['id']
    project_name = f"automation project {_today} {faker.zipcode()}"
    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "UNIT_ONLY"}

    api = QualityFlowExternalApiProject(api_key=api_key)
    res = api.post_create_project(team_id=team_id, payload=payload, headers=api.headers)
    response = res.json_response
    data = response.get('data')
    project_id = data.get('id', False)

    return {
        "team_id": team_id,
        "project_id": project_id
    }


@pytest.mark.qf_public_api
@pytest.mark.qf_api_smoke
@pytest.mark.upload_data
@pytest.mark.parametrize('file_type, data_file', [
    ('csv', '/authors.csv'),
    ('tsv', '/authors.tsv'),
])
def test_upload_data_project_valid(setup, file_type, data_file):
    file_name = get_data_file(data_file)
    api = QualityFlowExternalApiProject(api_key=api_key)

    res = api.post_upload_data_project(team_id=setup['team_id'],
                                       project_id=setup['project_id'],
                                       file_name=file_name,
                                       api_key=api_key)

    response = res.json_response
    assert res.status_code == 201
    assert response.get('details', False) == 'successfully uploaded'
    assert response.get('batchNum', False) == 1
    assert response.get('fileName', False) == file_name

    # Delete Project request (remove delete_project method after admin user update)

    api_delete = QualityFlowApiProject()
    api_delete.get_valid_sid(username, password)

    res = api_delete.delete_project(project_id=setup['project_id'], team_id=setup['team_id'], version_id=0)
    response = res.json_response
    assert res.status_code == 200
    assert response.get('message', False) == 'success'


# @pytest.mark.qf_public_api
# @pytest.mark.qf_api_smoke
# @pytest.mark.upload_data
# def test_upload_multiple_data_project_valid(setup):
#     file_name = get_data_file("/authors.tsv")
#     api = QualityFlowExternalApiProject(api_key=api_key)
#
#     res = api.post_upload_data_project(team_id=setup['team_id'],
#                                        project_id=setup['project_id'],
#                                        file_name=file_name,
#                                        api_key=api_key)
#
#     response = res.json_response
#     assert res.status_code == 201
#     assert response.get('batchNum', False) == 1
#
#     res = api.post_upload_data_project(team_id=setup['team_id'],
#                                        project_id=setup['project_id'],
#                                        file_name=file_name,
#                                        api_key=api_key)
#
#     response = res.json_response
#     assert res.status_code == 201
#     assert response.get('batchNum', False) == 2
#
#     # Delete Project request (remove delete_project method after admin user update)
#
#     api_delete = QualityFlowApiProject()
#     api_delete.get_valid_sid(username, password)
#
#     res = api_delete.delete_project(project_id=setup['project_id'], team_id=setup['team_id'], version_id=0)
#     response = res.json_response
#     assert res.status_code == 200
#     assert response.get('message', False) == 'success'
