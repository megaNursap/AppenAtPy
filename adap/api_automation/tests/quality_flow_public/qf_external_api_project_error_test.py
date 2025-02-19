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


@pytest.fixture(scope="module", autouse=True)
def setup():
    project_name = f"automation project {_today} {faker.zipcode()}"
    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "UNIT_ONLY"}
    return {
        "payload": payload,
        "project_name": project_name,
    }


@pytest.mark.qf_public_api
@pytest.mark.qf_api_smoke
@pytest.mark.create_project
def test_create_project_external_has_role_but_quality_flow_not_enabled(setup):
    """
    user is denied due to not enabled on team
    """
    team_id = get_test_data('user_no_qf', 'teams')[0]['id']
    api_key = get_test_data('user_no_qf', 'api_key')
    api = QualityFlowExternalApiProject(api_key=api_key)

    res = api.post_create_project(team_id=team_id, payload=setup['payload'], headers=api.headers)
    response = res.json_response
    assert res.status_code == 403
    assert response.get('message', False) == 'Access Denied'


@pytest.mark.qf_public_api
@pytest.mark.qf_api_smoke
@pytest.mark.create_project
def test_can_not_create_project_with_invalid_auth(setup):
    """
    Verify that user can not create QF project via API without authorization
    """
    team_id = get_test_data('qf_user_api', 'teams')[0]['id']
    api = QualityFlowExternalApiProject()

    res = api.post_create_project(team_id=team_id, payload=setup['payload'])
    assert res.status_code == 401


@pytest.mark.qf_public_api
@pytest.mark.create_project
def test_can_not_create_project_without_team_id_parameter(setup):
    """
    Verify that user can not create QF project via API without teamId parameter
    """

    api_key = get_test_data('qf_user_api', 'api_key')
    api = QualityFlowExternalApiProject(api_key=api_key)

    res = api.post_create_project(payload=setup['payload'], headers=api.headers)
    response = res.json_response
    assert res.status_code == 403
    assert response.get('message', False) == 'Access Denied'


@pytest.mark.qf_public_api
@pytest.mark.qf_api_smoke
@pytest.mark.create_project
def test_can_not_create_project_without_name(setup):
    """
    Verify that user can not create project without "name" in body request
    """

    payload = {"description": setup['project_name'],
               "unitSegmentType": "UNIT_ONLY"}

    team_id = get_test_data('qf_user_api', 'teams')[0]['id']
    api_key = get_test_data('qf_user_api', 'api_key')
    api = QualityFlowExternalApiProject(api_key=api_key)

    res = api.post_create_project(team_id=team_id, payload=payload, headers=api.headers)
    response = res.json_response
    assert res.status_code == 400
    assert response.get('message', False) == 'name: project name cannot be empty; '


@pytest.mark.flaky(reruns=3)
@pytest.mark.qf_public_api
@pytest.mark.create_project
def test_can_not_create_project_with_empty_name_value(setup):
    """
    Verify that user can not create project with empty "name" in body request
    """

    payload = {
        "name": "",
        "description": setup['project_name'],
        "unitSegmentType": "UNIT_ONLY"}

    team_id = get_test_data('qf_user_api', 'teams')[0]['id']
    api_key = get_test_data('qf_user_api', 'api_key')
    api = QualityFlowExternalApiProject(api_key=api_key)

    res = api.post_create_project(team_id=team_id, payload=payload, headers=api.headers)
    response = res.json_response
    assert res.status_code == 400
    assert response.get('message',
                        False) == 'name: must at lease contain 1 character and less than 255 characters; name: project name cannot be empty; '



# Product Changed (Description/unitSegmentType field no longer Required in order to create project)

# @pytest.mark.qf_public_api
# @pytest.mark.qf_api_smoke
# @pytest.mark.create_project
# def test_can_not_create_project_without_description(setup):
#     """
#     Verify that user can not create project without "description" in body request
#     """
#
#     payload = {
#         "name": setup['project_name'],
#         "unitSegmentType": "UNIT_ONLY"}
#
#     team_id = get_test_data('qf_user_api', 'teams')[0]['id']
#     api_key = get_test_data('qf_user_api', 'api_key')
#     api = QualityFlowExternalApiProject(api_key=api_key)
#
#     res = api.post_create_project(team_id=team_id, payload=payload, headers=api.headers)
#     response = res.json_response
#     assert res.status_code == 400
#     assert response.get('message', False) == 'description: description cannot be empty; '


# @pytest.mark.qf_public_api
# @pytest.mark.qf_api_smoke
# @pytest.mark.create_project
# def test_can_not_create_project_with_empty_description_value(setup):
#     """
#     Verify that user can not create project with empty "description" in body request
#     """
#
#     payload = {
#         "name": setup['project_name'],
#         "description": "",
#         "unitSegmentType": "UNIT_ONLY"}
#
#     team_id = get_test_data('qf_user_api', 'teams')[0]['id']
#     api_key = get_test_data('qf_user_api', 'api_key')
#     api = QualityFlowExternalApiProject(api_key=api_key)
#
#     res = api.post_create_project(team_id=team_id, payload=payload, headers=api.headers)
#     response = res.json_response
#     assert res.status_code == 400
#     assert response.get('message', False) == 'description: description cannot be empty; '


# @pytest.mark.qf_public_api
# @pytest.mark.create_project
# def test_can_not_create_project_with_empty_unitSegmentType_value(setup):
#     """
#     Verify that user can not create project without "unitSegmentType" in body request
#     """
#
#     payload = {
#         "name": setup['project_name'],
#         "description": setup['project_name']}
#
#     team_id = get_test_data('qf_user_api', 'teams')[0]['id']
#     api_key = get_test_data('qf_user_api', 'api_key')
#     api = QualityFlowExternalApiProject(api_key=api_key)
#
#     res = api.post_create_project(team_id=team_id, payload=payload, headers=api.headers)
#     response = res.json_response
#     assert res.status_code == 400
#     assert response.get('message', False) == 'unitSegmentType: must not be null; '
