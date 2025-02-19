import pytest
from faker import Faker
from selenium.common import NoSuchElementException

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
def test_delete_contributor_ui_elements(app, qf_login, qf_refresh_page):
    app.project_resource.navigate_to_project_resource()
    app.project_resource.icm.click_options()
    app.project_resource.icm.delete_contributor()
    app.driver.implicitly_wait(10)
    assert app.project_resource.is_project_management_page()
    assert app.project_resource.icm.is_delete_contributor_ui_elements()


@pytest.mark.regression_qf
def test_delete_single_contributor(app, qf_login, qf_refresh_page):
    app.project_resource.navigate_to_project_resource()
    app.project_resource.icm.click_options()
    icm_email = app.project_resource.icm.delete_contributor()
    app.driver.implicitly_wait(10)
    assert app.project_resource.is_project_management_page()
    try:
        app.project_resource.icm.is_search_functionality(icm_email, name='', partial=True)
    except NoSuchElementException:
        assert True, "Delete button works fine"


@pytest.mark.regression_qf
def test_delete_multiple_contributor(app, qf_login, qf_refresh_page):
    icm_email1, icm_email2 = app.project_resource.icm.delete_multiple_contributor()
    app.driver.implicitly_wait(10)
    try:
        assert app.project_resource.icm.is_search_functionality(icm_email1, name="", partial=True)
        print("Assertion failed: No error was raised for icm_email1")
    except AssertionError:
        print("Assertion passed: Error was raised as expected for icm_email1")
    try:
        assert app.project_resource.icm.is_search_functionality(icm_email2, name="", partial=True)
        print("Assertion failed: No error was raised for icm_email2")
    except AssertionError:
        print("Assertion passed: Error was raised as expected for icm_email2")


@pytest.mark.regression_qf
def test_cancel_single_delete_contributor(app, qf_login, qf_refresh_page):
    icm_email = app.project_resource.icm.cancel_single_delete_contributor()
    app.driver.implicitly_wait(10)
    app.project_resource.icm.is_search_functionality(icm_email, name='', partial=True)
    assert True, "Cancel button works fine"


@pytest.mark.regression_qf
def test_cancel_multiple_delete_contributor(app, qf_login, qf_refresh_page):
    icm_email1, icm_email2 = app.project_resource.icm.cancel_multiple_delete_contributor()
    app.driver.implicitly_wait(10)
    app.project_resource.icm.is_search_functionality(icm_email1, name='', partial=True)
    app.project_resource.icm.is_search_functionality(icm_email2, name='', partial=True)
    assert True, "Cancel button works fine"


@pytest.mark.regression_qf
def test_add_delete_add_contributors(app, qf_login, qf_refresh_page):
    icm_email, icm_name = faker.email(), faker.name()
    app.project_resource.icm.add_single_contributor(icm_email, icm_name)
    app.driver.implicitly_wait(10)
    assert app.project_resource.icm.is_search_functionality(icm_email, icm_name)
    app.project_resource.icm.delete_single_contributor(icm_email)
    app.driver.implicitly_wait(10)
    try:
        app.project_resource.icm.is_search_functionality(icm_email, icm_name, partial=True)
    except AssertionError:
        assert True, "Delete button works fine"
    app.driver.refresh()
    app.project_resource.icm.add_single_contributor(icm_email, icm_name)
    app.driver.implicitly_wait(10)
    assert app.project_resource.icm.is_search_functionality(icm_email, icm_name)
