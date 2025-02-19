"""
https://appen.atlassian.net/browse/QED-1515
"""
import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.plss import create_plss_job
from adap.ui_automation.utils.selenium_utils import *
from adap.data import annotation_tools_cml as data

pytestmark = [pytest.mark.regression_plss, pytest.mark.fed_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')


@pytest.fixture(scope="module")
def tx_job(app):
    job_id = create_plss_job(app, API_KEY, data.plss_cml, USER_EMAIL, PASSWORD)
    return job_id


def test_annotate_plss(app_test, tx_job):
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(tx_job)
    app_test.job.preview_job()
    app_test.plss.activate_iframe_by_index(0)
    time.sleep(5)
    app_test.plss.full_screen()
    app_test.plss.single_hotkey('f')
    app_test.plss.fill_image(300, 300)
    app_test.plss.full_screen()
    app_test.plss.deactivate_iframe()
    app_test.plss.submit_test_validators()
    time.sleep(5)
    app_test.verification.text_present_on_page("No changes were made to the annotation")

    for i in range(1, 5):
        time.sleep(5)
        app_test.plss.activate_iframe_by_index(i)
        time.sleep(2)
        app_test.plss.full_screen()
        app_test.plss.single_hotkey('f')
        app_test.plss.fill_image(50, 50)
        app_test.plss.full_screen()
        app_test.plss.deactivate_iframe()

    app_test.plss.submit_test_validators()
    time.sleep(10)
    app_test.verification.text_present_on_page("Validation succeeded")

