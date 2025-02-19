import pytest
import allure
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user_email, get_user_api_key

pytestmark = [pytest.mark.regression_core, pytest.mark.new_auth, pytest.mark.adap_api_uat]


@allure.parent_suite('/account:get')
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.devspace
def test_get_user_account_info():
    api_key = get_user_api_key('org_admin')
    email = get_user_email('org_admin')

    act = Builder(api_key)

    resp = act.get_account_info()
    resp.assert_response_status(200)
    assert resp.json_response['email'] == email, "Email doesn't match!"
    assert resp.json_response['api_team_id'], "api_team_id should not be empty"


@allure.parent_suite('/users/teams:get')
@pytest.mark.cross_team
@pytest.mark.parametrize('user_role_type, expected_status',
                         [('internal_app_role', 200),
                          ('cf_internal_role', 200),
                          ('team_admin', 200),
                          ('org_admin', 200),
                          ('standard_user', 200),
                          ('multi_team_user', 200)])
def test_get_users_teams(user_role_type, expected_status):
    user = Builder(get_user_api_key(user_role_type))

    res = user.get_user_teams()
    res.assert_response_status(expected_status)
    assert res.json_response is not None
