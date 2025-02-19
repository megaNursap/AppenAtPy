import allure
import pytest

from adap.api_automation.utils.data_util import *

pytestmark = [
               pytest.mark.regression_core,
               pytest.mark.adap_ui_uat,
               pytest.mark.adap_uat
]


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.fed_ui
@pytest.mark.fed_ui_smoke
# @allure.issue("https://appen.atlassian.net/browse/JW-122", "BUG  on Sandbox JW-122")
@allure.issue("https://appen.atlassian.net/browse/ADAP-2860", "BUG  on Sandbox ADAP-2860")
def test_create_job_from_template(app_test):
    """
    Customer is able to create a job from a template
    """
    email = get_user_email('test_ui_account')
    password = get_user_password('test_ui_account')
    app_test.user.login_as_customer(user_name=email, password=password)

    app_test.mainMenu.jobs_page()

    app_test.job.create_new_job_from_template(template_type="Data Categorization",
                                              job_type="Image Categorization")
    app_test.user.close_guide()
    app_test.navigation.click_btn("Next: Design Your job")
    job_id = app_test.job.grab_job_id()

    app_test.navigation.click_btn("Save")
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(job_id)
    app_test.save_job_for_tear_down(job_id, get_user_api_key('test_ui_account'))


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.fed_ui
@pytest.mark.fed_ui_smoke
@allure.issue("https://appen.atlassian.net/browse/ADAP-2558", "BUG Sandbox ADAP-2558")
def test_create_job_from_scratch(app_test):
    """
    Customer is able to create a job from scratch
    """
    email = get_user_info('test_ui_account')['email']
    password = get_user_password('test_ui_account')
    app_test.user.login_as_customer(user_name=email, password=password)

    app_test.mainMenu.jobs_page()
    app_test.job.create_new_job_from_scratch()
    app_test.user.close_guide()
    app_test.navigation.click_btn("Next: Design your job")
    job_id = app_test.job.grab_job_id()
    app_test.navigation.click_btn("Save")

