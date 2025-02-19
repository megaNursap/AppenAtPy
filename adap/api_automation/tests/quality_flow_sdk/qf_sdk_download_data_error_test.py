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
def test_sdk_can_not_download_data_with_empty_team_id(setup):
    query_params_download = {
        'projectId': setup['project_id'],
        'teamId': ""
    }
    body = FinalizedDataset(type='FINALIZED_DATASET')

    api_client = appen_project_flow_sdk.ApiClient(configuration)

    api_instance = public_api_controller_api.PublicApiControllerApi(api_client)

    try:
        api_response_download = api_instance.download(query_params=query_params_download, body=body,
                                                  skip_deserialization=True)
        return api_response_download

    except appen_project_flow_sdk.ApiValueError as e:
        response = e.args[0]
        assert response == "Invalid value '' for type UUID at ('args[0]',)"


@pytest.mark.qf_sdk_api
def test_sdk_can_not_download_data_without_team_id(setup):
    query_params_download = {
        'projectId': setup['project_id']
    }
    body = FinalizedDataset(type='FINALIZED_DATASET')

    api_client = appen_project_flow_sdk.ApiClient(configuration)

    api_instance = public_api_controller_api.PublicApiControllerApi(api_client)

    try:
        api_response_download = api_instance.download(query_params=query_params_download, body=body,
                                                  skip_deserialization=True)
        return api_response_download

    except appen_project_flow_sdk.ApiTypeError as e:
        response = e.args[0]
        assert response == "RequestQueryParams missing 1 required arguments: ['teamId']"


@pytest.mark.qf_sdk_api
def test_sdk_can_not_download_data_with_empty_project_id(setup):
    query_params_download = {
        'projectId': "",
        'teamId': setup['team_id']
    }
    body = FinalizedDataset(type='FINALIZED_DATASET')

    api_client = appen_project_flow_sdk.ApiClient(configuration)

    api_instance = public_api_controller_api.PublicApiControllerApi(api_client)

    try:
        api_response_download = api_instance.download(query_params=query_params_download, body=body,
                                                  skip_deserialization=True)
        return api_response_download

    except appen_project_flow_sdk.ApiValueError as e:
        response = e.args[0]
        assert response == "Invalid value '' for type UUID at ('args[0]',)"


@pytest.mark.qf_sdk_api
def test_sdk_can_not_download_data_without_project_id(setup):
    query_params_download = {
        'teamId': setup['team_id']
    }
    body = FinalizedDataset(type='FINALIZED_DATASET')

    api_client = appen_project_flow_sdk.ApiClient(configuration)

    api_instance = public_api_controller_api.PublicApiControllerApi(api_client)

    try:
        api_response_download = api_instance.download(query_params=query_params_download, body=body,
                                                  skip_deserialization=True)
        return api_response_download

    except appen_project_flow_sdk.ApiTypeError as e:
        response = e.args[0]
        assert response == "RequestQueryParams missing 1 required arguments: ['projectId']"


@pytest.mark.qf_sdk_api
def test_sdk_download_without_valid_dataset(setup, tmpdir):
    try:
        body = FinalizedDataset(type='')
        return body
    except appen_project_flow_sdk.ApiValueError as e:
        response = e.args[0]
        assert response == "Invalid value  passed in to <class 'appen_project_flow_sdk.model.finalized_dataset.FinalizedDataset.MetaOapg.properties.type'>, allowed_values=dict_keys(['FINALIZED_DATASET', 'JOB_DAILY', 'DATA_SET_GROUP', 'TAG_ERROR_DETAIL', 'REVIEW_TAG_ERROR_DETAIL'])"
