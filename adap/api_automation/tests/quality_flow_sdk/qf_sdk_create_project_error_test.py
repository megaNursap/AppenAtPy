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


@pytest.mark.qf_sdk_api
def test_sdk_create_project_quality_flow_not_enabled(setup):
    team_id_no_qf = get_test_data('user_no_qf', 'teams')[0]['id']
    api_key_no_qf = get_test_data('user_no_qf', 'api_key')

    configuration.api_key['Authorization'] = 'Token token=' + api_key_no_qf

    query_params = {
        'teamId': str(team_id_no_qf),
    }

    api_client = appen_project_flow_sdk.ApiClient(configuration)

    api_instance = public_api_controller_api.PublicApiControllerApi(api_client)

    try:
        api_response = api_instance.create_project(body=setup['project_dto'], query_params=query_params,
                                                   skip_deserialization=True)
        return api_response

    except appen_project_flow_sdk.ApiException as e:
        response = e.body.decode("UTF-8")
        json_response = json.loads(response)
        assert json_response['message'] == 'Access Denied'
        assert json_response['code'] == 403


@pytest.mark.flaky(reruns=3)
@pytest.mark.qf_sdk_api
def test_sdk_can_not_create_project_with_invalid_auth(setup):
    api_client = appen_project_flow_sdk.ApiClient(configuration)

    api_instance = public_api_controller_api.PublicApiControllerApi(api_client)

    try:
        api_response = api_instance.create_project(body=setup['project_dto'], query_params=setup['query_params'],
                                                   skip_deserialization=True)
        return api_response

    except appen_project_flow_sdk.ApiException as e:
        assert e.status == 401
        assert e.reason == 'Unauthorized'
        assert e.body == b'You need to sign in or sign up before continuing.'


@pytest.mark.qf_sdk_api
def test_sdk_can_not_create_project_without_empty_team_id(setup):
    configuration.api_key['Authorization'] = 'Token token=' + api_key

    query_params = {
        'teamId': "",
    }

    api_client = appen_project_flow_sdk.ApiClient(configuration)

    api_instance = public_api_controller_api.PublicApiControllerApi(api_client)

    try:
        api_response = api_instance.create_project(body=setup['project_dto'], query_params=query_params,
                                                   skip_deserialization=True)
        return api_response

    except appen_project_flow_sdk.ApiException as e:
        response = e.body.decode("UTF-8")
        json_response = json.loads(response)
        assert json_response['message'] == 'Access Denied'
        assert json_response['code'] == 402


@pytest.mark.qf_sdk_api
def test_sdk_can_not_create_project_without_team_id(setup):
    configuration.api_key['Authorization'] = 'Token token=' + api_key

    query_params = {}

    api_client = appen_project_flow_sdk.ApiClient(configuration)

    api_instance = public_api_controller_api.PublicApiControllerApi(api_client)

    try:
        api_response = api_instance.create_project(body=setup['project_dto'], query_params=query_params,
                                                   skip_deserialization=True)
        return api_response

    except appen_project_flow_sdk.ApiTypeError as e:
        response = e.args[0]
        assert response == "RequestQueryParams missing 1 required arguments: ['teamId']"


@pytest.mark.flaky(reruns=3)
@pytest.mark.qf_sdk_api
def test_sdk_can_not_create_project_with_empty_name_value(setup):
    configuration.api_key['Authorization'] = 'Token token=' + api_key

    project_dto = ProjectDTO(
        name="",
        description="Description",
        unitSegmentType="UNIT_ONLY"
    )

    api_client = appen_project_flow_sdk.ApiClient(configuration)

    api_instance = public_api_controller_api.PublicApiControllerApi(api_client)

    try:
        api_response = api_instance.create_project(body=project_dto, query_params=setup['query_params'],
                                                   skip_deserialization=True)
        return api_response

    except appen_project_flow_sdk.ApiException as e:
        response = e.body.decode("UTF-8")
        json_response = json.loads(response)
        assert json_response[
                   'message'] == "name: project name cannot be empty; name: must at lease contain 1 character and less than 255 characters; "
        assert json_response['code'] == 400


@pytest.mark.qf_sdk_api
def test_sdk_can_not_create_project_without_name(setup):
    configuration.api_key['Authorization'] = 'Token token=' + api_key

    try:
        project_dto = ProjectDTO(description="Description", unitSegmentType="UNIT_ONLY")
        return project_dto

    except TypeError as e:
        message = e.args[0]
        assert message == "__new__() missing 1 required keyword-only argument: 'name'"


@pytest.mark.qf_sdk_api
def test_sdk_can_not_create_project_without_description(setup):
    configuration.api_key['Authorization'] = 'Token token=' + api_key

    try:
        project_dto = ProjectDTO(name=setup['project_name'], unitSegmentType="UNIT_ONLY")
        return project_dto

    except TypeError as e:
        message = e.args[0]
        assert message == "__new__() missing 1 required keyword-only argument: 'description'"


@pytest.mark.qf_sdk_api
def test_sdk_can_not_create_project_without_unitSegmentType(setup):
    configuration.api_key['Authorization'] = 'Token token=' + api_key

    try:
        project_dto = ProjectDTO(name=setup['project_name'], description="Description")
        return project_dto

    except TypeError as e:
        message = e.args[0]
        assert message == "__new__() missing 1 required keyword-only argument: 'unitSegmentType'"
