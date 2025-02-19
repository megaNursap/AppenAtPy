from adap.api_automation.services_config.quality_flow import QualityFlowExternalApiProject, QualityFlowApiProject
import pytest
import time
import datetime
from faker import Faker
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id, get_user_api_key, get_data_file, \
    save_file_with_content, read_csv_file
from adap.api_automation.services_config.endpoints.quality_flow_endpoints import *

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_api,
              pytest.mark.regression_qf,
              mark_env]

faker = Faker()

_today = datetime.datetime.now().strftime("%Y_%m_%d")
username = get_test_data('qf_user_api', 'email')
password = get_test_data('qf_user_api', 'password')


@pytest.fixture(scope="module")
def setup():
    api_key = get_test_data('qf_user_api', 'api_key')
    team_id = get_test_data('qf_user_api', 'teams')[0]['id']
    project_id = '0e1ad975-e34d-4ed7-a444-33c79ffa9aa3'

    payload_no_filters = {"type": "FINALIZED_DATASET"}
    payload_with_filters = {
        "type": "FINALIZED_DATASET",
        "filter": {
            "startDate": "2023-01-15T00:00:00Z",
            "endDate": "2023-03-17T00:00:00Z"
        }}

    return {
        "team_id": team_id,
        "project_id": project_id,
        "api_key": api_key,
        "payload_no_filters": payload_no_filters,
        "payload_with_filters": payload_with_filters
    }


@pytest.mark.qf_public_api
@pytest.mark.download_data
@pytest.mark.qf_api_smoke
def test_download_data_project_no_team_id(setup):
    api = QualityFlowExternalApiProject(api_key=setup['api_key'])
    res = api.post_download_data_project(project_id=setup['project_id'],
                                         payload=setup['payload_no_filters'],
                                         headers=api.headers)

    response = res.json_response
    assert res.status_code == 403
    assert response.get('message', False) == 'Access Denied'


@pytest.mark.qf_public_api
@pytest.mark.qf_api_smoke
@pytest.mark.download_data
def test_download_data_project_with_invalid_auth(setup):
    api = QualityFlowExternalApiProject()
    res = api.post_download_data_project(project_id=setup['project_id'],
                                         team_id=setup['team_id'],
                                         payload=setup['payload_no_filters'])

    assert res.status_code == 401


@pytest.mark.qf_public_api
@pytest.mark.download_data
def test_download_data_project_no_project_id(setup):
    api = QualityFlowExternalApiProject(api_key=setup['api_key'])
    res = api.post_download_data_project(
        team_id=setup['team_id'],
        payload=setup['payload_no_filters'],
        headers=api.headers)

    assert res.status_code == 400


@pytest.mark.qf_public_api
@pytest.mark.qf_api_smoke
@pytest.mark.download_data
def test_download_data_project_no_payload(setup):
    api = QualityFlowExternalApiProject(api_key=setup['api_key'])
    res = api.post_download_data_project(project_id=setup['project_id'],
                                         team_id=setup['team_id'],
                                         headers=api.headers)

    response = res.json_response
    assert res.status_code == 400
    assert response.get('message',
                        False) == 'Required request body is missing: public org.springframework.http.ResponseEntity<com.appen.kepler.app.publicapi.dto.download.DownloadResponse> com.appen.kepler.app.publicapi.controller.PublicApiController.download(java.lang.String,java.lang.String,com.appen.kepler.app.publicapi.dto.download.DownloadRequest)'


@pytest.mark.qf_public_api
@pytest.mark.download_data
def test_download_data_project_with_empty_filter(setup):
    payload_with_empty_filters = {
        "type": "FINALIZED_DATASET",
        "filter": {
            "startDate": "",
            "endDate": ""
        }}

    api = QualityFlowExternalApiProject(api_key=setup['api_key'])
    res = api.post_download_data_project(project_id=setup['project_id'],
                                         team_id=setup['team_id'],
                                         payload=payload_with_empty_filters,
                                         headers=api.headers)

    response = res.json_response
    assert res.status_code == 400
    assert response.get('details',
                        False) == "check proper report type is specified, filter dates must match ISO format yyyy-MM-ddTHH:mm:ssZ."


@pytest.mark.qf_public_api
@pytest.mark.download_data
def test_download_data_project_with_invalid_filter(setup):
    payload_with_invalid_filters = {
        "type": "FINALIZED_DATASET",
        "filter": {
            "startDate": "2023-01T00:00:00Z",
            "endDate": "2023-03-17T00:00:00Z"
        }}

    api = QualityFlowExternalApiProject(api_key=setup['api_key'])
    res = api.post_download_data_project(project_id=setup['project_id'],
                                         team_id=setup['team_id'],
                                         payload=payload_with_invalid_filters,
                                         headers=api.headers)

    assert res.status_code == 400


@pytest.mark.qf_public_api
@pytest.mark.download_data
def test_download_data_project_with_invalid_auth_for_status(setup):
    api = QualityFlowExternalApiProject(api_key=setup['api_key'])
    res = api.post_download_data_project(project_id=setup['project_id'],
                                         team_id=setup['team_id'],
                                         payload=setup['payload_no_filters'],
                                         headers=api.headers)

    response = res.headers
    assert res.status_code == 202
    location = response.get('location')

    res = api.get_download_data_status_project(location=location)
    assert res.status_code == 401


@pytest.mark.qf_public_api
@pytest.mark.download_data
def test_download_data_project_with_expired_link_after_5_minutes(setup):
    api = QualityFlowExternalApiProject(api_key=setup['api_key'])
    res = api.post_download_data_project(project_id=setup['project_id'],
                                         team_id=setup['team_id'],
                                         payload=setup['payload_with_filters'],
                                         headers=api.headers)

    response = res.headers
    assert res.status_code == 202
    location = response.get('location')

    downloadable_url = api.wait_until_download_ready("DOWNLOAD_READY", 20, location=location, headers=api.headers)
    time.sleep(310)

    res = api.get_content_downloadable_url_project(url=downloadable_url)

    assert res.status_code == 403
