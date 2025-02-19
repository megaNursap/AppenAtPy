import pytest
import allure
from adap.api_automation.services_config.requestor_proxy import RP
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id, get_user_api_key

pytestmark = [pytest.mark.regression_core, pytest.mark.adap_api_uat, pytest.mark.adap_api_uat]

@allure.parent_suite('RP/me:get')
@pytest.mark.cross_team
@pytest.mark.RequestorProxy
@pytest.mark.parametrize('user_role_type, expected_status',
                         [('internal_app_role', 200),
                          ('cf_internal_role', 200),
                          ('team_admin', 200),
                          ('org_admin', 200),
                          ('standard_user', 200),
                          ('multi_team_user', 200)])
def test_access_to_me_endpoint_rp(user_role_type, expected_status):
    """
    This test ensures that all user types are able to access the me endpoint through requester proxy
    """
    username = get_test_data(user_role_type, 'email')
    password = get_test_data(user_role_type, 'password')

    rp = RP()
    rp.get_valid_sid(username, password)

    res = rp.me_endpoint_rp()
    res.assert_response_status(expected_status)


@allure.parent_suite('/switch_current_team/{team-id}:post')
@allure.parent_suite('/switch_api_team/{team-id}:post')
@pytest.mark.cross_team
@pytest.mark.parametrize('user_role_type, expected_status',
                         [('internal_app_role', 204),
                          ('cf_internal_role', 204),
                          ('team_admin', 204),
                          ('org_admin', 204),
                          ('standard_user', 204),
                          ('multi_team_user', 204)])
def test_switch_team_endpoint_valid_jwt(user_role_type, expected_status):
    """
    This test ensures that all user types are able to change their current and api team through requester proxy
    """
    username = get_test_data(user_role_type, 'email')
    password = get_test_data(user_role_type, 'password')

    rp = RP()
    rp.get_valid_sid(username, password)

    res_current_team = rp.switch_current_team_rp(get_user_team_id(user_role_type,1))
    res_current_team.assert_response_status(expected_status)

    res_api_team = rp.switch_api_team_rp(get_user_team_id(user_role_type, 1))
    res_api_team.assert_response_status(expected_status)

# deprecated tests
# @allure.parent_suite('/switch_current_team/{team-id}:post')
# @allure.parent_suite('/switch_api_team/{team-id}:post')
# @pytest.mark.cross_team
# @pytest.mark.RequestorProxy
# @pytest.mark.parametrize('user_role_type, expected_status',
#                          [('internal_app_role', 401),
#                           ('cf_internal_role', 401),
#                           ('team_admin', 401),
#                           ('org_admin', 401),
#                           ('standard_user', 401),
#                           ('multi_team_user', 401)])
# def test_switch_team_endpoint_invalid_jwt(user_role_type, expected_status):
#     """
#     This test ensures that a jwt token is required to make the request to switch teams through RP
#     """
#     rp = RP("invalid-jwt")
#     res_current_team = rp.switch_current_team_rp(get_user_team_id(user_role_type, 1))
#     res_current_team.assert_response_status(expected_status)
#     res_current_team.assert_job_message("Missing userId in JWT")
#
#     res_api_team = rp.switch_api_team_rp(get_user_team_id(user_role_type, 1))
#     res_api_team.assert_response_status(expected_status)
#     res_api_team.assert_job_message("Missing userId in JWT")


@allure.parent_suite('/switch_current_team/{team-id}:post')
@allure.parent_suite('/switch_api_team/{team-id}:post')
@pytest.mark.cross_team
@pytest.mark.RequestorProxy
@pytest.mark.parametrize('user_role_type, expected_status',
                         [('internal_app_role', 403),
                          ('cf_internal_role', 403),
                          ('team_admin', 403),
                          ('org_admin', 403),
                          ('standard_user', 403),
                          ('multi_team_user', 403)])
def test_switch_team_endpoint_invalid_sid(user_role_type, expected_status):
    """
    This test ensures that a jwt token is required to make the request to switch teams through RP
    """
    rp = RP()
    res_current_team = rp.switch_current_team_rp(get_user_team_id(user_role_type, 1))
    res_current_team.assert_response_status(expected_status)
    # res_current_team.assert_job_message("Missing userId in JWT")

    res_api_team = rp.switch_api_team_rp(get_user_team_id(user_role_type, 1))
    res_api_team.assert_response_status(expected_status)
    # res_api_team.assert_job_message("Missing userId in JWT")


@allure.parent_suite('/switch_current_team/{team-id}:post')
@allure.parent_suite('/switch_api_team/{team-id}:post')
@pytest.mark.cross_team
@pytest.mark.parametrize('user_role_type, expected_status',
                         [('internal_app_role', 422),
                          ('cf_internal_role', 422),
                          ('team_admin', 422),
                          ('standard_user', 422)])
def test_switch_team_endpoint_invalid_team(user_role_type, expected_status):
    """
    This test ensures that you cannot switch to a team that you're not part of. Does not include org admin
    since they have access to all teams within an org
    """
    username = get_test_data(user_role_type, 'email')
    password = get_test_data(user_role_type, 'password')

    rp = RP()
    rp.get_valid_sid(username, password)

    res_current_team = rp.switch_current_team_rp(get_user_team_id(user_role_type, 0))
    res_current_team.assert_response_status(expected_status)
    res_current_team.assert_job_message("Unprocessable Entity")

    res_api_team = rp.switch_api_team_rp(get_user_team_id(user_role_type, 0))
    res_api_team.assert_response_status(expected_status)
    res_api_team.assert_job_message("Unprocessable Entity")


@allure.parent_suite('/switch_current_team/{team-id}:post')
@allure.parent_suite('/switch_api_team/{team-id}:post')
@pytest.mark.cross_team
@pytest.mark.parametrize('user_role_type, expected_status',
                         [('internal_app_role', 422),
                          ('cf_internal_role', 422),
                          ('team_admin', 422),
                          ('standard_user', 422)])
def test_switch_team_endpoint_invalid_team_sid(user_role_type, expected_status):
    """
    This test ensures that you cannot switch to a team that you're not part of. Does not include org admin
    since they have access to all teams within an org
    """
    username = get_test_data(user_role_type, 'email')
    password = get_test_data(user_role_type, 'password')

    rp = RP()
    rp.get_valid_sid(username, password)

    res_current_team = rp.switch_current_team_rp(get_user_team_id(user_role_type, 0))
    res_current_team.assert_response_status(expected_status)
    res_current_team.assert_job_message("Unprocessable Entity")

    res_api_team = rp.switch_api_team_rp(get_user_team_id(user_role_type, 0))
    res_api_team.assert_response_status(expected_status)
    res_api_team.assert_job_message("Unprocessable Entity")


@allure.parent_suite('/switch_current_team/{team-id}:post')
@allure.parent_suite('/switch_api_team/{team-id}:post')
@allure.parent_suite('/users/teams:get')
@pytest.mark.cross_team
def test_switch_team_endpoint_org_admin():
    """
    This test ensures that an org admin can switch their api and current team to any team in the organization
    """
    user = Builder(get_user_api_key('org_admin'))

    # Gets list of teams for the user -- from builder
    teams = user.get_user_teams()

    username = get_test_data('org_admin', 'email')
    password = get_test_data('org_admin', 'password')

    rp = RP()
    rp.get_valid_sid(username, password)

    # Iterates through the list of teams in the org and updates the org admin's current team and api team
    for i in range(0, len(teams.json_response)):
        res_current_team = rp.switch_current_team_rp(teams.json_response[i]['id'])
        res_current_team.assert_response_status(204)

        res_api_team = rp.switch_api_team_rp(teams.json_response[i]['id'])
        res_api_team.assert_response_status(204)
