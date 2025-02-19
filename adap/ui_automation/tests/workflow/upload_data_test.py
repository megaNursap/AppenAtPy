"""
Upload data to WF tests
"""
import time

import allure
import pytest
from adap.e2e_automation.workflow_e2e_test import payload1
from adap.api_automation.utils.data_util import get_user_info, generate_random_wf_name, get_data_file, \
    count_row_in_file, get_user_email, get_user_api_key, get_user_password
from adap.e2e_automation.services_config.job_api_support import create_job_from_config_api

pytestmark = [pytest.mark.wf_ui,
              pytest.mark.adap_ui_uat,
              pytest.mark.adap_uat,
              pytest.mark.regression_wf]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')


# router not working on fed
@pytest.fixture(scope="module")
def create_wf(app):
    """
    create_wf  - pytest fixture
    """
    global WF_ID

    job_id = create_job_from_config_api({"job": payload1["job"]}, pytest.env, API_KEY)

    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.workflows_page()
    app.navigation.click_link("Create Workflow")
    wf_name = generate_random_wf_name()
    app.workflow.fill_up_wf_name(wf_name)

    sample_file = get_data_file("/upload_data_files/workflows/shared-test-data-sets/customer_01_sample_22.csv")
    app.job.data.upload_file(sample_file)
    app.navigation.click_link("Canvas")

    app.workflow.select_operator.connect_job_to_wf(job_id, 580, 370)

    WF_ID = app.workflow.grab_wf_id()


@pytest.mark.ui_uat
@pytest.mark.fed_ui_smoke_wf
def test_access_data_tab(app_test):
    """
    test_access_data_tab
    """
    job_id = create_job_from_config_api({"job": payload1["job"]}, pytest.env, API_KEY)

    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.workflows_page()
    app_test.navigation.click_link("Create Workflow")
    wf_name = generate_random_wf_name()
    app_test.workflow.fill_up_wf_name(wf_name)

    app_test.verification.element_is('active', 'Canvas', is_not=True)

    app_test.verification.text_present_on_page('Drop your data file here or ')
    app_test.verification.text_present_on_page('.csv, .tsv, .xls, .xlsx, .ods')


@pytest.mark.dependency()
@pytest.mark.ui_uat
@pytest.mark.wip_wf
@pytest.mark.workflow_deploy
def test_upload_data(app, create_wf):
    """
     test_upload_data
     """
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(WF_ID)

    app.verification.element_is('disabled', 'Next: Add Steps')

    sample_file = get_data_file("/upload_data_files/workflows/shared-test-data-sets/customer_01_sample_22.csv")
    file_rows = count_row_in_file(sample_file)

    app.job.data.upload_file(sample_file)
    app.navigation.click_link("Data")
    app.verification.text_present_on_page("customer_01_sample_22.csv")

    app.verification.element_is('disabled', 'Next: Add Steps', is_not=True)

    rows_ui = app.workflow.data.count_rows_for_uploaded_file("customer_01_sample_22.csv")
    assert file_rows == rows_ui


@pytest.mark.dependency(depends=["test_upload_data"])
@pytest.mark.ui_uat
def test_add_more_data(app, create_wf):
    """
    test_add_more_data
    """
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(WF_ID)
    app.navigation.click_link("Data")
    # '.xls'
    for file_type in ['.csv', '.tsv', '.xlsx', '.ods']:
        sample_file = get_data_file("/authors" + file_type)
        app.navigation.click_link("Add More Data")
        app.job.data.upload_file(sample_file)

        app.navigation.refresh_page()
        app.verification.text_present_on_page("authors" + file_type)


@pytest.mark.dependency(depends=["test_upload_data"])
def test_upload_data_json_not_supported(app, create_wf):
    """
    test_upload_data_json_not_supported
    """
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(WF_ID)
    app.navigation.click_link("Data")

    sample_file = get_data_file("/authors.json")
    app.navigation.click_link("Add More Data")
    app.job.data.upload_file(sample_file, close_modal_window=False, wait_time=5)
    app.verification.text_present_on_page("Error: wrong file type")
    app.navigation.close_modal_window()


@pytest.mark.dependency(depends=["test_add_more_data"])
@pytest.mark.ui_uat
def test_delete_data(app, create_wf):
    """
    test_delete_data
    """
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(WF_ID)
    app.navigation.click_link("Data")

    app.verification.text_present_on_page("authors.csv")
    app.workflow.data.delete_file_from_data("authors.csv")
    app.verification.text_present_on_page("authors.csv", False)


@pytest.mark.dependency(depends=["test_upload_data"])
@pytest.mark.ui_uat
def test_view_data(app, create_wf):
    """
    test_view_data
    """
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(WF_ID)
    app.navigation.click_link("Data")

    app.workflow.data.review_file("customer_01_sample_22.csv", WF_ID)

    app.verification.text_present_on_page("customer_01_sample_22.csv")
    app.verification.text_present_on_page("This is a preview of the firs")
    app.navigation.browser_back()
    app.verification.text_present_on_page("Delete All Data")

#     TODO add verification - 25 units should be shown


@pytest.mark.dependency(depends=["test_upload_data"])
@pytest.mark.ui_uat
@allure.issue("https://appen.atlassian.net/browse/JW-124","BUG: JW-124")
def test_download_file(app, create_wf):
    """
    test_download_file
    """
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(WF_ID)
    app.navigation.click_link("Data")

    app.workflow.data.download_file("customer_01_sample_22.csv")
    app.verification.verify_file_present_in_dir("customer_01_sample_22.csv", app.temp_path_file, contains=True)


@pytest.mark.dependency(depends=["test_upload_data"])
@pytest.mark.ui_uat
def test_delete_all_data(app, create_wf):
    """
    test_delete_all_data
    """
    app.navigation.browser_back()
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(WF_ID)
    app.navigation.click_link("Data")

    app.navigation.click_link("Delete All Data")
    app.navigation.click_link("Delete")

    app.verification.text_present_on_page('Drop your data file here or ')
    app.verification.text_present_on_page('.csv, .tsv, .xls, .xlsx, .ods')
    app.verification.text_present_on_page("Supported Formats")

# TODO data uploading status

# @allure.issue("https://appen.atlassian.net/browse/CP-2425")
def test_upload_file_with_blank_header(app_test):
    """
    test_upload_file_with_blank_header
    """
    job_id = create_job_from_config_api({"job": payload1["job"]}, pytest.env, API_KEY)
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.workflows_page()
    app_test.navigation.click_link("Create Workflow")
    wf_name = generate_random_wf_name()
    app_test.workflow.fill_up_wf_name(wf_name)

    sample_file = get_data_file("/upload_data_files/blank_headers.csv")
    app_test.job.data.upload_file(sample_file, wait_time=5, close_modal_window=False)
    app_test.verification.text_present_on_page("One of the uploaded headers was blank. This can happen when a row contains more columns than defined in your header row or one of your headers contains no permitted characters (alphanumeric).")

# @allure.issue("https://appen.atlassian.net/browse/CP-2425")
@pytest.mark.ui_uat
def test_upload_file_with_duplicated_columns(app_test):
    """
    test_upload_file_with_duplicated_columns
    """
    job_id = create_job_from_config_api({"job": payload1["job"]}, pytest.env, API_KEY)
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.workflows_page()
    app_test.navigation.click_link("Create Workflow")
    wf_name = generate_random_wf_name()
    app_test.workflow.fill_up_wf_name(wf_name)

    sample_file = get_data_file("/upload_data_files/dup_headers.csv")
    app_test.job.data.upload_file(sample_file, wait_time=5, close_modal_window=False)
    time.sleep(5)
    app_test.verification.text_present_on_page(
        "The uploaded file contains duplicate headers: possible_brands. Please ensure your data file has unique column header names and try again.")

