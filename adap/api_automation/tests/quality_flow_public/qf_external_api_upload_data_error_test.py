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


@pytest.fixture(scope="module", autouse=True)
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
@pytest.mark.upload_data
def test_invalid_upload_data_project_without_team_id(setup):
    file_name = get_data_file("/authors.csv")
    api = QualityFlowExternalApiProject(api_key=api_key)

    res = api.post_upload_data_project(project_id=setup['project_id'],
                                       file_name=file_name,
                                       api_key=api_key)
    response = res.json_response

    assert res.status_code == 403
    assert response.get('message', False) == 'Access Denied'


@pytest.mark.qf_public_api
@pytest.mark.upload_data
def test_invalid_upload_data_project_without_project_id(setup):
    file_name = get_data_file("/authors.csv")
    api = QualityFlowExternalApiProject(api_key=api_key)

    res = api.post_upload_data_project(team_id=setup['team_id'],
                                       file_name=file_name,
                                       api_key=api_key)

    assert res.status_code == 400


@pytest.mark.qf_public_api
@pytest.mark.upload_data
def test_invalid_upload_data_project_with_invalid_auth(setup):
    file_name = get_data_file("/authors.csv")
    api = QualityFlowExternalApiProject()

    res = api.post_upload_data_project(team_id=setup['team_id'],
                                       project_id=setup['project_id'],
                                       file_name=file_name)

    assert res.status_code == 401
