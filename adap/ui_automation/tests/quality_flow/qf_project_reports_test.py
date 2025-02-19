import time

import pytest
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from adap.api_automation.utils.data_util import get_test_data
from adap.ui_automation.utils.selenium_utils import find_element, click_element_by_xpath

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")
pytestmark = [pytest.mark.qf_ui,
              pytest.mark.regression_qf,
              pytest.mark.qf_uat_ui,
              mark_env]


@pytest.fixture(scope="module")
def qf_login(app):
    username = get_test_data('qf_user_ui', 'email')
    password = get_test_data('qf_user_ui', 'password')
    project_id = get_test_data('qf_user_ui', 'download_report_project')['id']

    app.user.login_as_customer(username, password)
    app.quality_flow.open_project_by_id(project_id)


def test_qf_project_report_tab(app, qf_login):
    app.navigation.click_link('Dashboard')
    app.quality_flow.dashboard.open_tab('Reports (Downloadable)')
    app.verification.current_url_contains('/dashboard/reports')

    app.verification.text_present_on_page('Report Type')
    app.verification.text_present_on_page('Action')

    app.verification.text_present_on_page('Job Daily Report')
    app.verification.text_present_on_page('Contributor Daily Report')
    app.verification.text_present_on_page('Download Report')


@pytest.mark.parametrize('name, file_name', [
    ('Job Daily Report', 'JOB_DAILY-5895'),
    ('Contributor Daily Report', 'CONTRIBUTOR_DAILY')
])
def test_qf_download_report(app, qf_login, name, file_name):
    app.navigation.click_link('Dashboard')
    app.quality_flow.dashboard.open_tab('Reports (Downloadable)')

    app.quality_flow.dashboard.project_reports.download_report(name)
    app.navigation.click_bytext("Check progress and download")

    app.navigation.wait_for_element_to_be_clickable(app.driver, app.quality_flow.dashboard._DOWNLOAD_BUTTON)
    app.navigation.click_element_by_xpath(app.driver, app.quality_flow.dashboard._DOWNLOAD_BUTTON)
    app.navigation.click_element_by_xpath(app.driver, app.quality_flow.dashboard._CLOSE_BATCH_JOB_POPUP)


    time.sleep(30)
    app.verification.verify_file_present_in_dir(file_name, app.temp_path_file, contains=True)
