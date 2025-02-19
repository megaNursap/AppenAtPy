import time
import pytest

from adap.api_automation.utils.data_util import *
pytestmark = pytest.mark.fed_ui_smoke
user_email = get_user_email('org_admin')
password = get_user_password('org_admin')


@pytest.fixture(scope="module")
def login_as_customer(app):
    app.user.login_as_customer(user_name=user_email, password=password)


@pytest.mark.fed_ui
def test_sso_page_showup(app, login_as_customer):
    """
      JIRA https://appen.atlassian.net/browse/QED-1213
      navigate between different pages from account, SSO page can always show up correctly
    """
    app.mainMenu.account_menu("Account")

    app.navigation.click_link("Teams")
    app.verification.current_url_contains("secure.cf3.us/make/account/teams")
    app.verification.text_present_on_page(user_email)
    time.sleep(2)
    app.navigation.click_link("SSO")
    time.sleep(2)
    app.verification.current_url_contains("secure.cf3.us/make/account/sso/setup")
    app.verification.text_present_on_page('Setup SSO')

    app.navigation.click_link("Profile")
    time.sleep(2)
    app.verification.current_url_contains("secure.cf3.us/make/account/profile")
    app.verification.text_present_on_page('Edit Profile')

    # go to SSO page again to verify it shows up correctly
    app.navigation.click_link("SSO")
    time.sleep(2)
    app.verification.current_url_contains("secure.cf3.us/make/account/sso/setup")
    app.verification.text_present_on_page('Setup SSO')




