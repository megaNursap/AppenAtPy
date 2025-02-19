import datetime
import time
import urllib.request
from urllib.parse import urlparse
from urllib.parse import parse_qs
import shutil

import os

import pytest
import json
import appen_project_flow_sdk
from appen_project_flow_sdk.apis.tags import public_api_controller_api
from appen_project_flow_sdk.model.finalized_dataset import FinalizedDataset
from appen_project_flow_sdk.model.project_dto import ProjectDTO
from faker import Faker
from adap.api_automation.services_config.quality_flow import QualityFlowApiProject
from adap.api_automation.utils.data_util import get_test_data, get_data_file, read_csv_file, unzip_file

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
    api_key = get_test_data('qf_user_api', 'api_key')
    team_id = get_test_data('qf_user_api', 'teams')[0]['id']
    project_id = '0e1ad975-e34d-4ed7-a444-33c79ffa9aa3'

    return {
        "team_id": team_id,
        "project_id": project_id,
        "api_key": api_key
    }


@pytest.mark.qf_sdk_api
def test_sdk_download_data_project_valid(setup, tmpdir):
    query_params_download = {
        'projectId': setup['project_id'],
        'teamId': setup['team_id']
    }
    body = FinalizedDataset(type='FINALIZED_DATASET')

    api_client = appen_project_flow_sdk.ApiClient(configuration)

    api_instance = public_api_controller_api.PublicApiControllerApi(api_client)

    # Send request to download
    api_response_download = api_instance.download(query_params=query_params_download, body=body, skip_deserialization=True)

    header_dict = api_response_download.response.headers
    location = header_dict['location']
    parsed_url = urlparse(location)
    file_id = parse_qs(parsed_url.query)['fileId'][0]
    time.sleep(5)
    # status check
    query_params_download_status = {
        'fileId': file_id,
        'teamId': setup['team_id']
    }
    api_response_download_status = api_instance.download_status(query_params=query_params_download_status)

    count = 5
    downloadable_url = None
    while api_response_download_status is not None and count > 0:
        data = api_response_download_status.response.data.decode("UTF-8")
        json_response = json.loads(data)
        if json_response['details'] == 'DOWNLOAD_PREPARE':
            count -= 1
            time.sleep(5)
            api_response_download_status = api_instance.download_status(query_params=query_params_download_status)
        elif json_response['details'] == 'DOWNLOAD_READY':
            downloadable_url = json_response['downloadableUrl']
            break

    file_path = tmpdir + '/download_data.zip'
    with urllib.request.urlopen(downloadable_url) as x_response, open(file_path, 'wb') as out_file:
        shutil.copyfileobj(x_response, out_file)

    unzip_file(file_path)
    files = os.listdir(tmpdir)
    matching_file_names = [file for file in files if "DATA_SET" in file]
    file_name_csv = "/" + matching_file_names[0]
    csv_file = tmpdir + file_name_csv

    content_column = read_csv_file(csv_file, 'jobStatus')

    assert len(content_column) == 5
    assert [x == 'FINALIZED' for x in content_column]
