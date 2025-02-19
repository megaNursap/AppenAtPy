import time

from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.api_automation.tests.job.manage_contributor_test import predifined_jobs
from adap.api_automation.utils.data_util import *

pytestmark = [
    pytest.mark.regression_core,
    pytest.mark.adap_ui_uat,
    pytest.mark.adap_uat
]

@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@allure.issue("https://appen.atlassian.net/browse/ADAP-2579", "Sandbox bug ADAP-2579")
def test_download_results(app_test):
    """
       Customer is able to download full report
    """
    user = get_user_info('test_predefined_jobs')
    email = user['email']
    password = get_user_password('test_predefined_jobs')
    job_id = predifined_jobs['job_with_judgments'][pytest.env]

    app_test.user.login_as_customer(user_name=email, password=password)

    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(job_id)
    app_test.job.open_tab("RESULTS")

    app_test.job.results.download_report("Full", job_id)
    time.sleep(10)

    file_name_zip = "/" + app_test.job.results.get_file_report_name(job_id, "Full")
    full_file_name_zip = app_test.temp_path_file + file_name_zip
    assert file_exists(full_file_name_zip)
    # app_test.verification.text_present_on_page("Please wait while your report is being generated.")


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.skip_hipaa
def test_access_internal_link(app_test):
    """
       Customer is able to access internal link
    """
    user = get_user_info('test_predefined_jobs')
    email = user['email']
    password = get_user_password('test_predefined_jobs')
    job_id = predifined_jobs['job_with_judgments'][pytest.env]

    app_test.user.login_as_customer(user_name=email, password=password)

    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(job_id)
    app_test.job.open_action("Settings")
    app_test.job.open_settings_tab("Contributors")

    internal_link = app_test.job.get_internal_link_for_job()
    app_test.user.logout()
    app_test.navigation.open_page(internal_link)

    user = get_user_info('test_contributor_task')
    email = user['email']
    password = get_user_password('test_contributor_task')
    username = user['user_name']
    # https://appen.atlassian.net/browse/CW-7954 bug
    # app_test.user.task.login(user_name=email, password=password)
    # app_test.user.verify_user_name(username)


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
def test_dashboard(app_test):
    """
       Customer is able to see dashboard
    """
    user = get_user_info('test_predefined_jobs')
    email = user['email']
    password = get_user_password('test_predefined_jobs')
    job_id = predifined_jobs['job_with_judgments'][pytest.env]

    app_test.user.login_as_customer(user_name=email, password=password)

    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(job_id)
    app_test.job.open_tab("MONITOR")
    time.sleep(30)
    # app_test.verification.wait_untill_text_present_on_the_page("Trust/Untrusted Judgments", 20)
    app_test.verification.text_present_on_page("Contributor Funnel")
    app_test.verification.text_present_on_page("Contributor Satisfaction Score")
    app_test.verification.text_present_on_page("Test Questions")


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
def test_ui_launch_job(app_test):
    """
       Customer is able to launch job
    """
    api_key = get_user_api_key('test_ui_account')

    # # create job with title, instructions, data and test questions
    job = JobAPI(api_key)
    job.create_simple_job_with_test_questions()

    user = get_user_info('test_ui_account')
    email = user['email']
    password = get_user_password('test_ui_account')

    app_test.user.login_as_customer(user_name=email, password=password)

    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(job.job_id)
    app_test.job.open_tab("QUALITY")
    app_test.navigation.click_link("Next: Launch Job")

    app_test.navigation.click_link("Launch Job")

    job.wait_until_status('running', 120)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    app_test.navigation.refresh_page()

    current_status = app_test.job.get_job_status()
    assert current_status == "Running", "Expected status: %s, \n Actual status: %s" %("Running", current_status)
