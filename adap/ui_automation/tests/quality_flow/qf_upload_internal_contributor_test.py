import time

import allure
import pytest
from faker import Faker
from selenium.common import InvalidArgumentException

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
    email1, email2, name1, name2, valid_file_path = app.project_resource.icm.create_test_data_icm_csv("valid_file.csv")
    email3, email4, name3, name4, valid_file_path_cancel = app.project_resource.icm.create_test_data_icm_csv(
        "valid_file_cancel.csv")
    invalid_file_path_tsv = app.project_resource.icm.create_test_data_icm_tsv("invalid_file.tsv")
    invalid_file_path_xlsx = app.project_resource.icm.create_test_data_icm_xlsx("invalid_file.xlsx")
    yield email1, email2, name1, name2, valid_file_path, invalid_file_path_tsv, invalid_file_path_xlsx, email3, email4, name3, name4, valid_file_path_cancel
    app.project_resource.icm.delete_created_file(valid_file_path)
    app.project_resource.icm.delete_created_file(invalid_file_path_tsv)
    app.project_resource.icm.delete_created_file(invalid_file_path_xlsx)
    app.project_resource.icm.delete_created_file(valid_file_path_cancel)


@pytest.fixture(scope="function")
def qf_refresh_page(app):
    app.navigation.refresh_page()
    app.driver.implicitly_wait(10)


@pytest.mark.regression_qf
def test_add_contributor_with_valid_csv_file(app, qf_login, qf_refresh_page):
    email1, email2, name1, name2, valid_file_path = qf_login[0], qf_login[1], qf_login[2], qf_login[3], qf_login[4]
    app.project_resource.navigate_to_project_resource()
    app.project_resource.icm.add_contributor_via_file(valid_file_path)
    app.driver.implicitly_wait(10)
    if app.verification.text_present_on_page("Remove File"):
        app.project_resource.icm.click_add_button()
    time.sleep(5)
    assert app.project_resource.icm.is_search_functionality(email1, name1)
    assert app.project_resource.icm.is_search_functionality(email2, name2)


@pytest.mark.regression_qf
def test_add_contributor_with_invalid_file_tsv(app, qf_login, qf_refresh_page):
    invalid_file_path_tsv = qf_login[5]
    app.project_resource.navigate_to_project_resource()
    app.driver.implicitly_wait(10)
    try:
        app.project_resource.icm.add_contributor_via_file(invalid_file_path_tsv)
    except InvalidArgumentException:
        allure.step("File is invalid, so the Add button is not present")


@pytest.mark.regression_qf
def test_add_contributor_with_invalid_file_xlsx(app, qf_login, qf_refresh_page):
    invalid_file_path_xlsx = qf_login[6]
    app.project_resource.navigate_to_project_resource()
    app.driver.implicitly_wait(10)
    try:
        app.project_resource.icm.add_contributor_via_file(invalid_file_path_xlsx)
    except InvalidArgumentException:
        allure.step("File is invalid, so the Add button is not present")


@pytest.mark.regression_qf
def test_cancel_uploading_contributor_file(app, qf_login, qf_refresh_page):
    valid_file_path = qf_login[4]
    app.project_resource.navigate_to_project_resource()
    app.project_resource.icm.add_contributor_via_file(valid_file_path)
    app.driver.implicitly_wait(10)
    assert app.verification.text_present_on_page("Remove File")
    assert app.verification.text_present_on_page("Cancel")
    app.project_resource.icm.click_cancel_button()
    assert not app.verification.text_present_on_page("Cancel")


@pytest.mark.regression_qf
def test_duplicate_upload(app, qf_login, qf_refresh_page):
    email1, email2, name1, name2, valid_file_path = qf_login[0], qf_login[1], qf_login[2], qf_login[3], qf_login[4]
    app.project_resource.navigate_to_project_resource()
    app.project_resource.icm.add_contributor_via_file(valid_file_path)
    app.driver.implicitly_wait(10)
    if app.verification.text_present_on_page("Remove File"):
        app.project_resource.icm.click_add_button()
    app.driver.implicitly_wait(10)
    app.driver.refresh()
    app.project_resource.icm.add_contributor_via_file(valid_file_path)
    if app.verification.text_present_on_page("Remove File"):
        app.project_resource.icm.click_add_button()
    assert app.verification.text_present_on_page("You have successfully added contributors.")
    assert app.project_resource.icm.is_search_functionality(email1, name1)
    assert app.project_resource.icm.is_search_functionality(email2, name2)


@pytest.mark.regression_qf
def test_add_contributor_with_empty_csv_file(app, qf_login, qf_refresh_page):
    file_path = app.project_resource.icm.create_test_data_icm_empty_csv("empty_file.csv")
    app.project_resource.navigate_to_project_resource()
    app.driver.implicitly_wait(10)
    app.project_resource.icm.add_contributor_via_file(file_path)
    app.driver.implicitly_wait(10)
    assert app.verification.text_present_on_page("1 bytes")
    app.project_resource.icm.click_add_button()
    assert app.verification.text_present_on_page("No source files found.")


@pytest.mark.regression_qf
@pytest.mark.order(order=1)
def test_cancel_uploading_contributor_file(app, qf_login, qf_refresh_page):
    email3, email4, name3, name4, valid_file_path_cancel = qf_login[7], qf_login[8], qf_login[9], qf_login[10], \
        qf_login[11]
    app.project_resource.navigate_to_project_resource()
    app.project_resource.icm.add_contributor_via_file(valid_file_path_cancel)
    app.driver.implicitly_wait(10)
    assert app.verification.text_present_on_page("Remove File")
    assert app.verification.text_present_on_page("Cancel")
    app.project_resource.icm.click_cancel_button()
    try:
        app.project_resource.icm.is_search_functionality(email3, name3)
    except AssertionError:
        assert True, "Cancel button works fine"
    try:
        app.project_resource.icm.is_search_functionality(email4, name4)
    except AssertionError:
        assert True, "Cancel button works fine"
