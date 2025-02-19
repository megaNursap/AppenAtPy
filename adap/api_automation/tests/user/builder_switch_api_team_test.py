import pytest
import allure
import random
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user_team_id, get_user_api_key

pytestmark = [pytest.mark.regression_core, pytest.mark.new_auth]

@allure.parent_suite('/users/switch_api_team/{team-id}:post')
@pytest.mark.cross_team
@pytest.mark.parametrize('user_role_type, expected_status',
                         [('internal_app_role', 200),
                          ('cf_internal_role', 200),
                          ('no_logged_user', 401),
                          ('team_admin', 200),
                          ('org_admin', 200),
                          ('standard_user', 200)])
def test_switch_api_team_builder(user_role_type, expected_status):
    user = Builder(get_user_api_key(user_role_type))
    team = get_user_team_id('multi_team_user', 1)

    res_api_team = user.switch_api_team(team)
    res_api_team.assert_response_status(expected_status)

    res_account_info = user.get_account_info()
    res_account_info.assert_response_status(expected_status)
    if res_account_info.status_code == 200:
        assert res_account_info.json_response['api_team_id'] == team, "The team_id does not match!"


@allure.parent_suite('/users/switch_api_team/{team-id}:post')
@allure.parent_suite('/jobs:post')
@pytest.mark.cross_team
def test_switch_api_team_multi_team_user():
    """
    This test switches the api team of a user and verifies that a job created through the api is attached
    to the right team
    """
    user = Builder(get_user_api_key('multi_team_user'))

    # The user is only part of the the last 2 teams in the team_id list
    i = random.randint(1, 2)
    api_team = get_user_team_id('multi_team_user', i)
    res = user.switch_api_team(api_team)
    res.assert_response_status(200)

    res_account_info = user.get_account_info()
    res_account_info.assert_response_status(200)
    assert res_account_info.json_response['api_team_id'] == api_team, "The team_id does not match!"

    res_job = user.create_job()
    res_job.assert_response_status(200)

    # verify that the team_id in the json is the same as the api team
    assert api_team == res_job.json_response.get('team_id')
