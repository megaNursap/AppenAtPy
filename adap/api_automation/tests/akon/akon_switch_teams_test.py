import pytest
import allure
from adap.api_automation.services_config.akon import AkonUser
from adap.api_automation.utils.data_util import get_user_api_key, get_user_team_id, get_akon_id

pytestmark = pytest.mark.regression_core


@allure.parent_suite('/me:get')
@pytest.mark.cross_team
@pytest.mark.akon
@pytest.mark.adap_api_uat
@pytest.mark.parametrize('user_role_type, expected_status',
                         [('internal_app_role', 200),
                          ("no_logged_user", 401),
                          ('cf_internal_role', 200),
                          ('team_admin', 403),
                          ('org_admin', 403),
                          ('standard_user', 403)])
def test_access_to_me_endpoint(user_role_type, expected_status):
    # Initializes an instance of an akon user
    user = AkonUser(get_user_api_key(user_role_type))

    # Stores the current team, api team, and akon id of the user
    res = user.get_akon_info()
    res.assert_response_status(expected_status)

    if expected_status == 200:
        assert user.current_team_id is not None
        assert user.api_team_id is not None
        assert user.team_ids is not None


@allure.parent_suite('/users/{akon-uuid}/switch_current_team/{team-id}:post')
@allure.parent_suite('/users/{akon-uuid}/switch_api_team/{team-id}:post')
@pytest.mark.cross_team
@pytest.mark.akon
@pytest.mark.adap_api_uat
@pytest.mark.parametrize('user_role_type, expected_status',
                         [('internal_app_role', 204),
                          ('cf_internal_role', 204),
                          ('no_logged_user', 404),
                          ('team_admin', 403),
                          ('org_admin', 403),
                          ['standard_user', 403]])
def test_access_to_switch_team_endpoint(user_role_type, expected_status):
    user = AkonUser(get_user_api_key(user_role_type))

    res_current_team = user.switch_current_team(get_user_team_id('multi_team_user', 1), get_akon_id(user_role_type))
    res_current_team.assert_response_status(expected_status)

    res_api_team = user.switch_api_team(get_user_team_id('multi_team_user', 1), get_akon_id(user_role_type))
    res_api_team.assert_response_status(expected_status)


@allure.parent_suite('/users/{akon-uuid}/switch_current_team/{team-id}:post')
@pytest.mark.cross_team
@pytest.mark.akon
@pytest.mark.parametrize('user_role_type, expected_status',
                         [('internal_app_role', 200),
                          ('cf_internal_role', 200)])
def test_switch_current_team_invalid_team(user_role_type, expected_status):
    """
    This test ensures that the internal_app role can't switch another user's current team to
    a team that they don't belong to.
    """
    user = AkonUser(get_user_api_key(user_role_type))

    res = user.get_akon_info()
    res.assert_response_status(expected_status)

    # makes the request for switch multi_team_user's team to a team that they're on using internal_app_role's api key
    resp = user.switch_current_team(get_user_team_id('multi_team_user', 0), get_akon_id('multi_team_user'))
    resp.assert_response_status(422)
    resp.assert_error_message_v2("User is not part of this team")


@allure.parent_suite('/users/{akon-uuid}/switch_current_team/{team-id}:post')
@pytest.mark.cross_team
@pytest.mark.akon
def test_switch_current_team_nonexistent_team():
    user = AkonUser(get_user_api_key('internal_app_role'))

    res = user.get_akon_info()
    res.assert_response_status(200)

    resp = user.switch_current_team("nonexistentteam", get_akon_id('multi_team_user'))
    resp.assert_response_status(404)
    resp.assert_error_message_v2("There was an error switching teams")


@allure.parent_suite('/users/{akon-uuid}/switch_current_team/{team-id}:post')
@pytest.mark.cross_team
@pytest.mark.akon
def test_switch_current_team_nonexistent_user():
    user = AkonUser(get_user_api_key('internal_app_role'))

    res = user.get_akon_info()
    res.assert_response_status(200)

    resp = user.switch_current_team(get_user_team_id('multi_team_user', 0), "nonexistentuser")
    resp.assert_response_status(404)


@allure.parent_suite('/users/{akon-uuid}/switch_current_team/{team-id}:post')
@pytest.mark.cross_team
@pytest.mark.akon
@pytest.mark.adap_api_uat
@pytest.mark.parametrize('user_role_type, expected_status',
                         [('internal_app_role', 200),
                          ('cf_internal_role', 200)])
def test_switch_current_team_valid_team(user_role_type, expected_status):
    """
    This test ensures that the internal_app role can switch a user's current team to a team that they belong to
    """
    user = AkonUser(get_user_api_key(user_role_type))

    res = user.get_akon_info()
    res.assert_response_status(expected_status)

    resp = user.switch_current_team(get_user_team_id('multi_team_user', 1), get_akon_id('multi_team_user'))
    resp.assert_response_status(204)


@allure.parent_suite('/users/{akon-uuid}/switch_api_team/{team-id}:post')
@pytest.mark.cross_team
@pytest.mark.adap_api_uat
def test_switch_api_team_invalid_team():
    """
    This test ensures that the internal_app role can't switch a user's api team to a team that they don't belong to
    """
    user = AkonUser(get_user_api_key('internal_app_role'))

    res = user.get_akon_info()
    res.assert_response_status(200)

    # makes the request for switch multi_team_user's team to a team that they're on using internal_app_role's api key
    resp = user.switch_api_team(get_user_team_id('multi_team_user', 0), get_akon_id('multi_team_user'))
    resp.assert_response_status(422)
    resp.assert_error_message_v2("User is not part of this team")


@allure.parent_suite('/users/{akon-uuid}/switch_api_team/{team-id}:post')
@pytest.mark.cross_team
@pytest.mark.akon
@pytest.mark.adap_api_uat
@pytest.mark.parametrize('user_role_type, expected_status',
                         [('internal_app_role', 200),
                          ('cf_internal_role', 200)])
def test_switch_api_team_valid_team(user_role_type, expected_status):
    """
    This test ensures that the internal_app role can switch a user's current team to a team that they belong to
    """
    user = AkonUser(get_user_api_key(user_role_type))

    res = user.get_akon_info()
    res.assert_response_status(expected_status)

    resp = user.switch_api_team(get_user_team_id('multi_team_user', 1), get_akon_id('multi_team_user'))
    resp.assert_response_status(204)


@allure.parent_suite('/users/{akon-uuid}/switch_api_team/{team-id}:post')
@pytest.mark.cross_team
def test_switch_api_team_nonexistent_team():
    user = AkonUser(get_user_api_key('internal_app_role'))

    res = user.get_akon_info()
    res.assert_response_status(200)

    resp = user.switch_api_team("nonexistentteam", get_akon_id('multi_team_user'))
    resp.assert_response_status(404)
    resp.assert_error_message_v2("There was an error switching teams")


@allure.parent_suite('/users/{akon-uuid}/switch_api_team/{team-id}:post')
@pytest.mark.cross_team
def test_switch_api_team_nonexistent_user():
    user = AkonUser(get_user_api_key('internal_app_role'))

    res = user.get_akon_info()
    res.assert_response_status(200)

    resp = user.switch_api_team(get_user_team_id('multi_team_user', 0), "nonexistentuser")
    resp.assert_response_status(404)
