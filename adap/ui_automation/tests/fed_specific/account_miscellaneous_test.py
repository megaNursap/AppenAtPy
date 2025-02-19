import time
import pytest
from faker import Faker

from adap.api_automation.utils.data_util import *
from adap.api_automation.utils.data_util import generate_random_string
from adap.api_automation.services_config.management import Management

pytestmark = pytest.mark.fed_ui_smoke
user_email = get_user_email('cf_internal_role')
password = get_user_password('cf_internal_role')
api_key = get_user_api_key('cf_internal_role')
faker = Faker()
invite_user_name = (faker.name().lower()+faker.zipcode()).replace(' ', '')
invite_user_email = invite_user_name + '@appen.com'
# newly created user will use same password as test_ui_account
invite_user_password = get_user_password('test_ui_account')


@pytest.fixture(scope="module")
def login_as_customer(app):
    app.user.login_as_customer(user_name=user_email, password=password)


@pytest.mark.dependency()
@pytest.mark.fed_ui
def test_invite_user_and_activate_user(app, login_as_customer):
    """
      JIRA https://appen.atlassian.net/browse/QED-1163
      cf internal invite new user, register this new user, after registration, this user can also invite others
    """
    app.mainMenu.account_menu("Account")
    app.navigation.click_link("Teams")
    time.sleep(2)

    # invite user
    app.user.invite_user(invite_user_email)
    app.user.logout()

    # sign up user being invited
    app.user.customer.open_home_page()
    app.navigation.click_link('Sign up!')
    time.sleep(2)
    app.user.activate_invited_user(invite_user_name, invite_user_email, invite_user_password)

    # newly registered user can also invite new users
    app.mainMenu.account_menu("Account")
    app.navigation.click_link("Teams")
    time.sleep(2)
    new_user_name = (faker.name() + faker.zipcode()).replace(' ', '')
    new_user_email = new_user_name + '@appen.com'
    app.user.invite_user(new_user_email)
    app.user.logout()

    # revoke newly created user team admin permission, make it standard user,  login again to check hosted channel
    # https://appen.atlassian.net/browse/QED-1211
    new_user_res = Management(api_key).revoke_user_team_admin_access(invite_user_email)
    new_user_res.assert_response_status(204)
    app.user.login_as_customer(user_name=invite_user_email, password=invite_user_password)
    app.mainMenu.hostedchannels_page()
    app.verification.current_url_contains("secure.cf3.us/make/account/hosted_channels")
    app.verification.text_present_on_page("New Hosted Channel")
    app.verification.text_present_on_page("Upload metadata")
    app.verification.text_present_on_page("Invite Contributor to Channel")


@pytest.mark.dependency(depends=["test_invite_user_and_activate_user"])
def test_upgrade_user_and_check_plan(app, login_as_customer):
    """
    JIRA https://appen.atlassian.net/browse/QED-1215
    remove user from cf_internal team, upgrade it to be a new team, check the basic plan
    """
    app.user.login_as_customer(user_name=user_email, password=password)
    app.mainMenu.account_menu("Account")
    app.navigation.click_link("Teams")
    time.sleep(2)

    # remove user from cf_internal team
    app.user.remove_user_from_team(invite_user_email)

    # upgrade user to create a new team
    app.mainMenu.account_menu("Users")
    time.sleep(3)
    # somehow, click_link sometimes work, sometime not work, so I use xpath instead
    # app.navigation.click_link("Users")
    app.driver.find_element('xpath',"//a[contains(@href, '/make/admin/users')]").click()

    new_team = generate_random_string()
    app.user.create_new_team(new_team, invite_user_email)
    app.navigation.refresh_page()
    time.sleep(4)

    # check plan on team user page and team details page
    # app.navigation.click_link(new_team)
    app.driver.find_element('xpath',"//a[contains(@href, '/make/admin/teams') and text() = '%s']" % new_team).click()
    time.sleep(3)
    user_plan = app.user.get_user_plan_name_for_fed()
    assert user_plan == 'enterprise'
    team_plan = app.user.get_team_plan_name_for_fed()
    assert user_plan == team_plan


@pytest.mark.fed_ui
def test_check_api_documentation(app, login_as_customer):
    """
    https://appen.atlassian.net/browse/QED-1216
    check API documentation
    """
    app.mainMenu.account_menu("Account")
    app.navigation.click_link("API")
    time.sleep(2)
    app.navigation.click_link('View API Documentation')
    time.sleep(2)
    app.verification.current_url_contains("secure.cf3.us/api-documentation")
    app.verification.text_present_on_page("Account Info")
    app.verification.text_present_on_page("Job Create/Update")
    app.verification.text_present_on_page("Manage Job Data")
    app.verification.text_present_on_page("Job Status")
    app.verification.text_present_on_page("Monitor Contributors")
    app.verification.text_present_on_page("Manage Job Settings")
    app.verification.text_present_on_page("Job Results")
    app.verification.text_present_on_page("Hosted Channels")
    app.verification.text_present_on_page("Cross Team Access")
