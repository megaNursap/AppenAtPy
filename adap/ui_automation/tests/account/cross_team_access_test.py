from adap.api_automation.utils.data_util import *
import logging

log = logging.getLogger(__name__)
USER_EMAIL_TEAM1 = get_user_email('multi_team_user')
PASSWORD_TEAM1 = get_user_password('multi_team_user')
API_KEY_TEAM1 = get_user_api_key('multi_team_user')

USER_EMAIL_TEAM2 = get_user_email('internal_app_role')
PASSWORD_TEAM2 = get_user_password('internal_app_role')
API_KEY_TEAM2 = get_user_api_key('internal_app_role')


@pytest.mark.regression_core
@pytest.mark.prod_bug
# @allure.issue("https://appen.atlassian.net/browse/ADAP-533", "BUG ADAP-533")
def test_user_can_switch_between_teams(app):
    with allure.step("Test user can switch between teams"):
        app.user.login_as_customer(user_name=USER_EMAIL_TEAM1, password=PASSWORD_TEAM1)
        log.info("Check current user team is in pre-requisite state and reset if not")
        if not app.user.verify_user_team_name(USER_EMAIL_TEAM1, do_assert=False):
            log.info("Detected wrong userteam set. Switching..")
            app.user.switch_user_team(USER_EMAIL_TEAM1)

        log.info("Start test")
        app.user.verify_user_team_name(USER_EMAIL_TEAM1)

        app.user.switch_user_team(USER_EMAIL_TEAM2)

        app.user.verify_user_team_name(USER_EMAIL_TEAM2)

        app.user.switch_user_team(USER_EMAIL_TEAM1)
