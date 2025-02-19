"""
[UI]Automate Invoice check pre-upload of invoices for User warnings
https://appen.atlassian.net/browse/QED-2343
[AC] Automate Invoice check pre-upload of invoices for Project & User Warnings
https://appen.atlassian.net/browse/QED-2339
"""
import time
import pytest

from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.js_utils import scroll_to_page_bottom

pytestmark = [pytest.mark.regression_ac_file_upload, pytest.mark.regression_ac, pytest.mark.ac_file_upload]


@pytest.fixture(scope="module")
def set_up(app):
    USER_NAME = get_user_email('test_ui_account')
    PASSWORD = get_user_password('test_ui_account')

    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.navigation.click_link('Partner Home')
    app.navigation.click_link('File Upload')
    app.navigation.click_btn('File Upload')
    app.navigation.switch_to_frame("page-wrapper")


@pytest.mark.parametrize('scenario, file_name, template',
                         [
                             ("user_warning", "/file_with_user_invoice_warning_test.xlsx", "SRT - Basic_Automation")
                             # https://appen.atlassian.net/browse/ACE-14248
                             # ("project_and_user_warning", "/file_with_user_invoice_project_and_user_warning_test.xlsx", "SRT - basic")
                         ])
def test_upload_file_user_warnings(app, set_up, tmpdir, scenario, file_name, template):
    random_prefix = app.faker.zipcode()

    app.navigation.click_btn("Upload New File")

    NEW_FILE_NAME = "file_upload_project_invoice_warning_{}.xlsx".format(random_prefix)

    sample_file = get_data_file(file_name)
    new_sample = copy_file_with_new_name(sample_file, tmpdir, NEW_FILE_NAME)

    app.file_upload.enter_data({
        "Client": "Falcon",
        "Upload Type": "Productivity Data (Invoicing)",
        "Upload File": new_sample
    })

    assert app.file_upload.get_uploaded_files_on_selection_page() == [NEW_FILE_NAME]

    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn('Next: Template')

    app.file_upload.enter_data({
        "Templates": template
    })

    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn("Next: Column Connection")
    time.sleep(10)

    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn("Next: Project Mapping")
    time.sleep(10)

    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn("Next: User Mapping")
    time.sleep(10)

    app.navigation.click_btn("Next: Preview")

    scroll_to_page_bottom(app.driver)
    time.sleep(2)
    app.file_upload.enter_data({
        "fixedAmount": "1"
    })
    app.navigation.click_btn("Finish and Upload Data")

    time.sleep(5)
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")

    assert app.file_upload.get_report_status_for_file(NEW_FILE_NAME) == "Data error"