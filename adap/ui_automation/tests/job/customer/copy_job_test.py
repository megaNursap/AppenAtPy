import time
from adap.api_automation.services_config.builder import Builder as JobAPI, Builder
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.pandas_utils import collect_data_from_ui_table

pytestmark = pytest.mark.regression_core

api_key = get_user_api_key('test_ui_account')
email = get_user_email('test_ui_account')
password = get_user_password('test_ui_account')


@pytest.fixture(scope="module")
def create_job(app):
    global job_id

    sample_file = get_data_file("/authors.csv")

    job = JobAPI(api_key)
    resp = job.create_job_with_csv(sample_file)
    job_id = job.job_id
    assert resp.status_code == 200, "Job was not created"
    app.user.login_as_customer(user_name=email, password=password)


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
# https://appen.atlassian.net/browse/CW-7985
def test_copy_job_with_all_rows(app, create_job):
    """
    Customer is able to copy job with all rows
    """

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")

    old_job_id = app.job.grab_job_id()
    old_job_data = collect_data_from_ui_table(app.driver)

    app.job.open_action("Copy,All Rows")
    job_window = app.driver.window_handles[0]
    app.navigation.click_btn("Copy")

    new_job = app.driver.window_handles[1]
    app.navigation.switch_to_window(new_job)

    time.sleep(4)
    app.user.close_guide()
    app.job.open_tab("DATA")
    app.navigation.refresh_page()

    new_job_id = app.job.grab_job_id()
    time.sleep(4)
    new_job_data = collect_data_from_ui_table(app.driver)

    assert old_job_id != new_job_id, "New job has not been created"
    app.verification.assert_data_frame_equals(old_job_data, new_job_data)
    app.driver.close()
    app.navigation.switch_to_window(job_window)


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
def test_copy_job_with_no_rows(app, create_job):
    """
    Customer is able to copy job with no rows
    """
    app.navigation.refresh_page()
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    app.job.open_action("Copy,No Rows")

    job_window = app.driver.window_handles[0]
    app.navigation.click_btn("Copy")
    new_job = app.driver.window_handles[1]
    app.navigation.switch_to_window(new_job)

    app.user.close_guide()

    new_job_id = app.job.grab_job_id()
    assert job_id != new_job_id, "New job has not been created"

    app.job.open_tab("DATA")
    app.navigation.refresh_page()
    app.user.close_guide()
    app.verification.text_present_on_page("Drop your data file here or ")
    app.driver.close()
    app.navigation.switch_to_window(job_window)


@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
def test_copy_job_with_tqs_rows(app_test):

    # create job with title, instructions, data and test questions
    job = Builder(api_key)
    job.create_simple_job_with_test_questions()
    job_id = job.job_id

    app_test.user.login_as_customer(user_name=email, password=password)

    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(job_id)
    app_test.job.open_tab("QUALITY")

    app_test.job.open_tab("DATA")
    app_test.job.open_action("Copy,Test Questions Only")
    app_test.navigation.click_btn("Copy")
    new_job = app_test.driver.window_handles[1]
    app_test.navigation.switch_to_window(new_job)

    new_job_id = app_test.job.grab_job_id()
    assert job_id != new_job_id, "New job has not been created"
#     todo verify number of TQs

#      todo verify copy job with unfinalized rows

