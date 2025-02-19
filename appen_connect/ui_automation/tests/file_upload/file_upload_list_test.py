"""
https://appen.atlassian.net/browse/QED-2550
"""
import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.js_utils import scroll_to_page_bottom
import datetime

pytestmark = [pytest.mark.ac_ui_uat, pytest.mark.regression_ac_file_upload, pytest.mark.ac_file_upload]


@pytest.fixture(scope="module")
def login(app):
    USER_NAME = get_user_email('test_ui_account')
    PASSWORD = get_user_password('test_ui_account')
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.navigation.click_link('Partner Home')
    # app.navigation.click_link('Falcon')
    app.navigation.click_link('File Upload')
    app.navigation.click_btn('File Upload')
    app.navigation.switch_to_frame("page-wrapper")


def test_filter_by_file_upload_status(app, login):
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")
    for status in ['Completed', 'Failed', 'Deleted', 'Processing']:
        app.file_upload.filter_file_upload_list_by(status=status)
        all_file_upload_status = app.file_upload.uploaded_file_status()
        time.sleep(2)
        for x in all_file_upload_status:
            assert status == x['status']


def test_file_upload_list_show_items(app, login):
    all_reports = app.file_upload.get_num_of_all_reports()
    for reports_num in [5, 15, 20]:
        app.navigation.refresh_page()
        app.navigation.switch_to_frame("page-wrapper")
        app.file_upload.set_up_show_items(reports_num)
        time.sleep(4)
        expected_reports = min(reports_num, all_reports)
        reports_on_page = app.file_upload.count_file_upload_rows_on_page()
        assert reports_on_page == expected_reports


def test_open_file_upload_list_page(app, login):
    app.verification.text_present_on_page("File Upload")
    app.verification.text_present_on_page("FILE NAME")
    app.verification.text_present_on_page("DATE OF WORK")
    app.verification.text_present_on_page("PROJECTS")
    app.verification.text_present_on_page("UPLOAD TYPE")
    app.verification.text_present_on_page("CREATED AT")
    app.verification.text_present_on_page("STATUS")


def test_filter_by_upload_type(app, login):
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")
    app.file_upload.filter_file_upload_list_by(upload_type='Productivity Data')
    app.verification.text_present_on_page("Productivity Data")
    assert app.verification.count_text_present_on_page("Quality Data") == 0
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")
    app.file_upload.filter_file_upload_list_by(upload_type='Quality Data')
    assert app.verification.count_text_present_on_page("Productivity Data") == 0
    app.verification.text_present_on_page("Quality Data")


def test_filter_by_project_name(app, login):
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")
    app.file_upload.filter_file_upload_list_by(project_name_or_id='Golden Project Eng')
    app.file_upload.click_toggle_for_file_upload_details()
    app.verification.text_present_on_page("TEMPLATE")
    app.verification.text_present_on_page("Golden Project Eng (6821)")


def test_filter_by_project_id(app, login):
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")
    app.file_upload.filter_file_upload_list_by(project_name_or_id='6821')
    app.file_upload.click_toggle_for_file_upload_details()
    app.verification.text_present_on_page("TEMPLATE")
    app.verification.text_present_on_page("Golden Project Eng (6821)")
