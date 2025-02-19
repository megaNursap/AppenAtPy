import re
import time

import allure

from adap.api_automation.utils.data_util import *
from adap.support.generate_test_data.adap.verify_email import verify_user_email_akon
from adap.ui_automation.utils.selenium_utils import go_to_page, find_element
from adap.api_automation.services_config.builder import Builder

pytestmark = pytest.mark.regression_core

user_email = get_user_email('test_ui_account')
username = get_user_name('test_ui_account')
password = get_user_password('test_ui_account')
api_key = get_user_api_key('test_ui_account')
team_id = get_user_team_id('test_ui_account')
team_name = get_user_team_name('test_ui_account')


@pytest.fixture(scope="module")
def login_as_customer(request, app):
    app.user.login_as_customer(user_name=user_email, password=password)


# "Create a new job" text will only show on home page when user already has a job, so we create a new job for fed in case it does not have anything
@pytest.mark.ui_uat
@pytest.mark.ui_smoke
@pytest.mark.fed_ui
@pytest.mark.fed_ui_smoke
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.br_wip
def test_login_with_valid_credentials(app, login_as_customer):
    """
    Customer: Access verification - customer with valid credentials
    """
    if pytest.env == 'fed':
        resp = Builder(api_key).create_job()
        resp.assert_response_status(200)

    app.mainMenu.home_page()
    app.verification.current_url_contains("/welcome")
    app.verification.text_present_on_page("Start From Scratch")
    app.verification.text_present_on_page("Featured Job Templates")
    app.mainMenu.jobs_page()
    app.user.verify_user_name(username)


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.fed_ui
@pytest.mark.fed_ui_smoke
@allure.issue("https://appen.atlassian.net/browse/JW-91", "BUG  on Sandbox JW-91")
def test_view_account_info(app, login_as_customer):
    """
    Customer should be able to view my account info
    """
    app.mainMenu.account_menu("Account")
    app.verification.current_url_contains("/account/profile")
    app.verification.text_present_on_page("Edit Profile")
    app.verification.text_present_on_page("First & Last Name")
    app.verification.text_present_on_page("Current Password")
    app.verification.text_present_on_page("Enter New Password")
    app.verification.text_present_on_page("Confirm Password")

    app.navigation.click_link("Teams")
    app.verification.current_url_contains("/account/teams")
    app.verification.text_present_on_page(team_name)
    # app.verification.text_present_on_page("Invite Members")
    # app.verification.text_present_on_page("Want to invite someone to join the team?")
    # fed does not have "Funds" tab
    if pytest.env != "fed":
        app.navigation.click_link("Funds")
        time.sleep(3)
        app.verification.current_url_contains("/account/funds")
        app.verification.text_present_on_page("Add Funds")
        app.verification.text_present_on_page("Amount")
        app.verification.text_present_on_page("Current Funds")

    app.navigation.click_link("Jobs")
    app.verification.current_url_contains("/jobs")
    app.verification.text_present_on_page("Jobs In Progress")
    app.verification.text_present_on_page("Job Cost Report")
    app.verification.text_present_on_page("Contact Us")

    app.navigation.click_link("API")
    app.verification.current_url_contains("/account/api")
    # app.verification.text_present_on_page("API Key")
    # app.verification.text_present_on_page("Your API key")
    app.verification.text_present_on_page("View API Documentation")
    user_api_key = app.user.customer.get_customer_api_key()
    assert user_api_key != '', "API Key has not been found"


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.fed_ui
@pytest.mark.fed_ui_smoke
def test_sign_out(app, login_as_customer):
    """
    Customer is able to sign out
    """
    app.user.logout()
    app.verification.current_url_contains("/sessions/new")
    app.verification.text_present_on_page("Don't have an account?")


# @pytest.mark.ui_uat
# @pytest.mark.adap_ui_uat
# @pytest.mark.adap_uat
# @pytest.mark.skip(reason="@figure-eight.com is deprecated")
# def test_create_trial_account(app):
#     app.user.customer.open_home_page()
#     app.navigation.click_link('Sign up!')
#     faker = Faker()
#     new_name = (faker.name() + faker.zipcode()).replace(' ', '')
#     find_element(app.driver, '//*[@id="user-name"]').send_keys(new_name)
#     find_element(app.driver, '//*[@id="user-email"]').send_keys(new_name + '@figure-eight.com')
#     find_element(app.driver, '//*[@id="user_password"]').send_keys('2*q246*Test1290!')
#     find_element(app.driver, '//input[@id="terms"]/..').click()
#     find_element(app.driver, '//input[@type="submit"]').click()
#     app.user.close_guide()
#     app.verification.text_present_on_page("Welcome to Appen, %s" % new_name)
#     app.verification.text_present_on_page("Your trial subscription has started - good for 1,000 data rows")


@pytest.mark.ui_uat
@pytest.mark.fed_ui
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.fed_ui_smoke
def test_reset_password(app_test):
    _user_email = get_user_info('test_ui_reset_password')['email']
    _password = get_user_password('test_ui_reset_password')
    app_test.user.login_as_customer(user_name=_user_email, password=_password)
    app_test.mainMenu.account_menu(submenu='Account')
    app_test.user.customer.reset_password(current_password=_password, new_password="yvYfUE8nFfQwebwCTLG9!")
    app_test.user.logout()
    time.sleep(5)
    app_test.user.login_as_customer(user_name=_user_email, password='yvYfUE8nFfQwebwCTLG9!')
    app_test.mainMenu.account_menu(submenu='Account')
    app_test.user.customer.reset_password(current_password="yvYfUE8nFfQwebwCTLG9!", new_password=_password)


@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
def test_forgot_password_access_control(app):
    app.user.customer.open_home_page()
    app.verification.current_url_contains("/sessions/new")
    find_element(app.driver, '//*[@name="session[email]"]').send_keys("forgot_password@appen.com")
    app.navigation.click_btn('Continue')
    app.navigation.click_link('Forgot Password?')
    app.verification.current_url_contains("/password_resets/new")
    app.verification.text_present_on_page('Reset Password')
    time.sleep(2)

    find_element(app.driver, '//*[@name="email"]').send_keys("forgot_password@appen.com")

    app.navigation.click_link('Submit')
    app.verification.text_present_on_page("Please check your email for instructions on how to reset your password. "
                                          "You will be redirected to sign in page")
    time.sleep(4)
    app.verification.current_url_contains("/sessions/new")


@allure.issue("https://appen.atlassian.net/browse/ADAP-1801", 'Bug: ADAP-1801')
@pytest.mark.skip(reason='Bug: ADAP-1801')
@pytest.mark.adap_uat
def test_create_requestor_account(app_test):
    app_test.user.customer.open_home_page()

    app_test.navigation.click_link('Sign up!')

    app_test.verification.text_present_on_page("Name")
    app_test.verification.text_present_on_page("Work Email")
    app_test.verification.text_present_on_page("Password")
    app_test.verification.text_present_on_page("I agree to Appen's")
    app_test.verification.text_present_on_page("Already have an account?")

    account_name = app_test.faker.name()
    account_email = "sandbox+" + re.sub('[^a-zA-Z0-9]', '',
                                        (account_name + app_test.faker.zipcode())) + '@figure-eight.com'

    admin_password = get_test_data('test_account', 'password')
    admin_api_key = get_test_data('test_account', 'api_key')

    app_test.user.activate_invited_user(user_name=account_name,
                                        user_email=account_email,
                                        user_password=admin_password
                                        )

    verify_user_email_akon(account_email, pytest.env, admin_api_key)

    app_test.user.customer.login_as(account_email, admin_password)

    app_test.verification.text_present_on_page('Job Templates')
    app_test.verification.current_url_contains('/welcome')