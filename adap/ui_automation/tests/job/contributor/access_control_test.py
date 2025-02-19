import re
import time

import allure
import pytest
from faker import Faker

from adap.api_automation.utils.data_util import get_user_info, get_user_password, get_test_data
from adap.support.generate_test_data.adap.verify_email import verify_user_email_akon
from adap.ui_automation.utils.selenium_utils import find_element, create_screenshot

pytestmark = pytest.mark.regression_core

@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.skip_hipaa
@pytest.mark.ip_test
@pytest.mark.flaky(reruns=2)
def test_contributor_login_with_valid_credentials(app_test):
    """
      Access verification - contributor with valid credentials
    """
    email = get_user_info('test_contributor_task')['email']
    username = get_user_info('test_contributor_task')['user_name']
    password = get_user_password('test_contributor_task')
    app_test.user.login_as_contributor(user_name=email, password=password)
    time.sleep(2)
    create_screenshot(app_test.driver, "test_contributor_login_with_valid_credentials")
    app_test.verification.current_url_contains("/annotate")
    # app_test.verification.logo_is_displayed_on_page()
    app_test.user.verify_user_name(username)


@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.ip_test
@pytest.mark.flaky(reruns=2)
@allure.issue("https://appen.atlassian.net/browse/DO-11508", "BUG  on Integration DO-11508")
def test_contributor_able_to_view_task_dashboard(app_test):
    """
      As a contributor, I should be able to view the task wall
    """
    email = get_user_info('test_ui_contributor1')['email']
    password = get_user_password('test_ui_contributor1')
    app_test.user.login_as_contributor(user_name=email, password=password)
    create_screenshot(app_test.driver, "test_contributor_able_to_view_task_dashboard")
    app_test.driver.switch_to.frame(app_test.driver.find_elements("tag_name","iframe")[0])
    # app_test.verification.text_present_on_page("Welcome to the Figure Eight job listing page!")
    try:
        app_test.navigation.click_btn("Skip Tour")
    except:
        pass
    create_screenshot(app_test.driver, "Available Jobs: test_contributor_able_to_view_task_dashboard ")

    app_test.verification.text_present_on_page("Available Jobs")
    # app_test.user.contributor.open_first_available_job_from_task_wall()
    # app_test.verification.current_url_contains("/identity-service")


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.skip_hipaa
@pytest.mark.flaky(reruns=2)
def test_contributor_sign_out(app_test):
    """
     Contributor is able to sign out
    """
    email = get_user_info('test_ui_contributor1')['email']
    password = get_user_password('test_ui_contributor1')
    app_test.user.login_as_contributor(user_name=email, password=password)
    app_test.user.logout()
    app_test.verification.text_present_on_page("Appen Contributor Portal")


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.fed_ui
@pytest.mark.flaky(reruns=2)
def test_tasks_login_with_valid_credentials(app_test):
    """
    Task page: Access verification - contributor with valid credentials
    """
    email = get_user_info('test_contributor_task')['email']
    username = get_user_info('test_contributor_task')['user_name']
    password = get_user_password('test_contributor_task')
    app_test.user.login_as_contributor_tasks(user_name=email, password=password)
    if pytest.env == 'fed':
        app_test.verification.current_url_contains('/task-force')
    else:
        app_test.verification.current_url_contains("/account")
        app_test.user.verify_user_name(username)


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.fed_ui
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.flaky(reruns=2)
# https://appen.atlassian.net/browse/CW-7954
def test_contributor_task_sign_out(app_test):
    """
    Task page: Contributor is able to sign out
    """
    email = get_user_info('test_contributor_task')['email']
    password = get_user_password('test_contributor_task')
    app_test.user.login_as_contributor_tasks(user_name=email, password=password)
    app_test.user.logout()
    app_test.verification.current_url_contains("/identity")
    app_test.verification.text_present_on_page("Login")


@pytest.mark.adap_ui_uat
@pytest.mark.flaky(reruns=2)
def test_create_new_account_for_contributor_task(app_test):
    app_test.user.task.open_home_page()
    app_test.navigation.click_link('Register')

    app_test.verification.text_present_on_page("Name")
    app_test.verification.text_present_on_page("Email")
    app_test.verification.text_present_on_page("Password ")
    app_test.verification.text_present_on_page("I agree to Appen's")
    app_test.verification.text_present_on_page("Already have an account?")

    account_name = app_test.faker.name()
    account_email = "sandbox+"+ re.sub('[^a-zA-Z0-9]', '', (account_name+app_test.faker.zipcode())) + '@figure-eight.com'

    admin_password = get_test_data('test_account', 'password')
    admin_api_key = get_test_data('test_account', 'api_key')

    app_test.user.activate_invited_user(user_name=account_name,
                                        user_email=account_email,
                                        user_password=admin_password
                                        )

    verify_user_email_akon(account_email, pytest.env, admin_api_key)

    app_test.user.task.open_home_page()

    app_test.user.task.login_as(account_email, admin_password)

    app_test.verification.text_present_on_page(account_name)
    app_test.verification.text_present_on_page('Jobs')

    app_test.verification.text_present_on_page('LEVEL STATISTICS')
    app_test.verification.text_present_on_page('Job History')
    app_test.verification.text_present_on_page('Select a Job title that interests you and start a Task')


@pytest.mark.adap_ui_uat
@allure.issue("https://appen.atlassian.net/browse/DO-11508", "BUG  on Integration DO-11508")
@pytest.mark.flaky(reruns=2)
def test_create_new_account_for_contributor_account(app_test):
    app_test.user.contributor.open_home_page()
    app_test.navigation.click_link('Continue to Sign In')
    app_test.navigation.click_link('Register')

    app_test.verification.text_present_on_page("Name")
    app_test.verification.text_present_on_page("Email")
    app_test.verification.text_present_on_page("Password ")
    app_test.verification.text_present_on_page("I agree to Appen's")
    app_test.verification.text_present_on_page("Already have an account?")

    account_name = app_test.faker.name()
    account_email = "sandbox+"+ re.sub('[^a-zA-Z0-9]', '', (account_name+app_test.faker.zipcode())) + '@figure-eight.com'

    admin_password = get_test_data('test_account', 'password')
    admin_api_key = get_test_data('test_account', 'api_key')

    app_test.user.activate_invited_user(user_name=account_name,
                                        user_email=account_email,
                                        user_password=admin_password
                                        )

    verify_user_email_akon(account_email, pytest.env, admin_api_key)

    app_test.user.contributor.open_home_page()

    app_test.user.contributor.login_as(account_email, admin_password)

    app_test.driver.switch_to.frame(app_test.driver.find_elements("tag_name","iframe")[0])
    try:
        app_test.navigation.click_btn("Skip Tour")
    except:
        pass

    create_screenshot(app_test.driver, "Available Jobs: test_create_new_account_for_contributor_account ")
    app_test.verification.text_present_on_page("Available Jobs")
    app_test.driver.switch_to.default_content()
    app_test.verification.text_present_on_page(account_name)
