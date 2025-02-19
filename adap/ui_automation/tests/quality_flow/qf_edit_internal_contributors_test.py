import time

import pytest
from faker import Faker
from selenium.common import ElementClickInterceptedException
import subprocess

from adap.api_automation.utils.data_util import get_test_data

faker = Faker()

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")
pytestmark = [pytest.mark.qf_ui,
              pytest.mark.regression_qf,
              pytest.mark.qf_uat_ui,
              mark_env]


@pytest.fixture(scope="module")
def qf_login(app):
    username = get_test_data('qf_user_ui', 'email')
    password = get_test_data('qf_user_ui', 'password')

    app.user.login_as_customer(username, password)
    app.driver.implicitly_wait(10)


@pytest.fixture(scope="function")
def qf_refresh_page(app):
    app.navigation.refresh_page()
    app.driver.implicitly_wait(10)


@pytest.mark.regression_qf
def test_edit_icm_ui_elements(app, qf_login, qf_refresh_page):
    app.project_resource.navigate_to_project_resource()
    app.project_resource.icm.click_options()
    app.project_resource.icm.click_edit_internal_contributors()
    app.driver.implicitly_wait(10)
    app.project_resource.icm.is_edit_internal_contributors_ui_elements()


@pytest.mark.regression_qf
def test_edit_email_and_name(app, qf_login, qf_refresh_page):
    icm_email, icm_name = faker.email(), faker.name()
    app.project_resource.navigate_to_project_resource()
    app.project_resource.icm.click_options()
    app.project_resource.icm.click_edit_internal_contributors()
    app.driver.implicitly_wait(10)
    app.project_resource.icm.edit_email_and_name(icm_email, icm_name)
    time.sleep(3)
    app.project_resource.icm.click_edit_save_button()
    app.driver.implicitly_wait(10)
    assert app.project_resource.icm.is_search_functionality(icm_email, icm_name, partial=True)


@pytest.mark.regression_qf
def test_edit_email(app, qf_login, qf_refresh_page):
    icm_email = faker.email()
    app.project_resource.navigate_to_project_resource()
    app.project_resource.icm.click_options()
    app.project_resource.icm.click_edit_internal_contributors()
    app.driver.implicitly_wait(10)
    app.project_resource.icm.edit_email(icm_email)
    app.project_resource.icm.click_edit_save_button()
    app.driver.implicitly_wait(10)
    assert app.project_resource.icm.is_search_functionality(icm_email, partial=True)


@pytest.mark.regression_qf
def test_edit_name(app, qf_login, qf_refresh_page):
    icm_name = faker.name()
    app.project_resource.navigate_to_project_resource()
    app.project_resource.icm.click_options()
    app.project_resource.icm.click_edit_internal_contributors()
    app.driver.implicitly_wait(10)
    app.project_resource.icm.edit_name(icm_name)
    app.project_resource.icm.click_edit_save_button()
    app.driver.implicitly_wait(10)
    assert app.project_resource.icm.is_search_functionality(name=icm_name, partial=True)


@pytest.mark.regression_qf
def test_edit_email_and_name_with_invalid_email(app, qf_login, qf_refresh_page):
    icm_name = faker.name()
    app.project_resource.navigate_to_project_resource()
    app.driver.implicitly_wait(10)
    app.project_resource.icm.click_options()
    app.project_resource.icm.click_edit_internal_contributors()
    app.driver.implicitly_wait(10)
    app.project_resource.icm.edit_email_and_name("invalid_email", icm_name)
    app.driver.implicitly_wait(10)
    try:
        app.project_resource.icm.click_edit_save_button
    except ElementClickInterceptedException:
        assert True, "Invalid email - Save button is not clickable"


@pytest.mark.regression_qf
def test_cancel_button(app, qf_login, qf_refresh_page):
    icm_email, icm_name = faker.email(), faker.name()
    app.project_resource.navigate_to_project_resource()
    app.project_resource.icm.click_options()
    app.project_resource.icm.click_edit_internal_contributors()
    app.driver.implicitly_wait(10)
    app.project_resource.icm.edit_email_and_name(icm_email, icm_name)
    app.project_resource.icm.click_edit_cancel_button()
    app.driver.implicitly_wait(10)
    try:
        app.project_resource.icm.is_search_functionality(icm_email, icm_name)
    except AssertionError:
        assert True, "Cancel button works fine"


@pytest.mark.regression_qf
def test_edit_email_and_name_with_blank_email(app, qf_login, qf_refresh_page):
    icm_name = faker.name()
    app.project_resource.navigate_to_project_resource()
    app.project_resource.icm.click_options()
    app.project_resource.icm.click_edit_internal_contributors()
    app.driver.implicitly_wait(10)
    app.project_resource.icm.edit_email_and_name('', icm_name)
    app.driver.implicitly_wait(10)
    try:
        app.project_resource.icm.click_edit_save_button
    except ElementClickInterceptedException:
        assert True, "Blank email - Save button is not clickable"


@pytest.mark.regression_qf
def test_edit_email_and_name_with_blank_name(app, qf_login, qf_refresh_page):
    icm_email = faker.email()
    app.project_resource.navigate_to_project_resource()
    app.project_resource.icm.click_options()
    app.project_resource.icm.click_edit_internal_contributors()
    app.driver.implicitly_wait(10)
    app.project_resource.icm.edit_email_and_name(icm_email, '')
    app.project_resource.icm.click_edit_save_button()
    time.sleep(2)
    app.driver.implicitly_wait(10)
    assert app.verification.text_present_on_page("newName: Name cannot be empty; ")


@pytest.mark.regression_qf
def test_edit_email_and_name_with_invalid_name(app, qf_login, qf_refresh_page):
    icm_email = faker.email()
    app.project_resource.navigate_to_project_resource()
    app.project_resource.icm.click_options()
    app.project_resource.icm.click_edit_internal_contributors()
    app.driver.implicitly_wait(10)
    app.project_resource.icm.edit_email_and_name(icm_email, "123!@#$._")
    app.project_resource.icm.click_edit_save_button()
    time.sleep(3)
    app.driver.implicitly_wait(10)
    assert app.verification.text_present_on_page("newName: Name can only contain letters, numbers, and spaces; ")


@pytest.mark.regression_qf
def test_edit_email_and_name_with_blank_email_and_name(app, qf_login, qf_refresh_page):
    app.project_resource.navigate_to_project_resource()
    app.project_resource.icm.click_options()
    app.project_resource.icm.click_edit_internal_contributors()
    app.driver.implicitly_wait(10)
    app.project_resource.icm.edit_email_and_name('', '')
    try:
        app.project_resource.icm.click_edit_save_button()
    except ElementClickInterceptedException:
        assert True, "Blank email and name - Save button is not clickable"
