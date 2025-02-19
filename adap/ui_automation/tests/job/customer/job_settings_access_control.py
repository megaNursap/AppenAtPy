import time

import pytest

from adap.api_automation.services_config.builder import find_all_jobs_with_status_for_user
from adap.api_automation.utils.data_util import get_user_info, get_user_api_key, get_data_file, get_user_password
from adap.api_automation.services_config.builder import Builder

pytestmark = [
    pytest.mark.regression_core,
    pytest.mark.adap_ui_uat,
    pytest.mark.adap_uat
]

username = get_user_info('test_predefined_jobs')['user_name']
password = get_user_password('test_predefined_jobs')
api_key = get_user_api_key('test_predefined_jobs')


@pytest.fixture(scope="module")
def login_as_customer_and_open_job(request, app):
    app.user.login_as_customer(user_name=username, password=password)
    app.mainMenu.jobs_page()
    if pytest.env == 'fed':
        # create job
        job = Builder(api_key)
        job.create_simple_job_with_test_questions()
        job.launch_job()
        json_status = job.get_json_job_status()
        json_status.assert_response_status(200)
        assert 'running' == json_status.json_response['state']

    user_jobs = find_all_jobs_with_status_for_user(api_key)['running']
    assert len(user_jobs) > 0, "Jobs with status %s have not been found"
    job = user_jobs[0]
    app.job.open_job_with_id(job)
    app.job.verify_job_id_is(job)


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.fed_ui
@pytest.mark.fed_ui_smoke
def test_access_quality_control_settings_page(app, login_as_customer_and_open_job):
    """
    Customer - Verify Job's Tab navigation
    """
    app.job.open_tab("DATA")
    app.verification.current_url_contains("/units")
    app.job.open_tab("DESIGN")
    app.verification.current_url_contains("/editor")
    app.job.open_tab("QUALITY")
    app.verification.current_url_contains("/test_questions")
    app.job.open_tab("LAUNCH")
    app.verification.current_url_contains("/launch")
    app.job.open_tab("MONITOR")
    app.verification.current_url_contains("/dashboard")
    app.job.open_tab("RESULTS")
    app.verification.current_url_contains("/reports")


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.fed_ui
@pytest.mark.fed_ui_smoke
def test_access_job_tq_page(app, login_as_customer_and_open_job):
    """
    Customer is able to access the test questions settings page
    """
    app.job.open_tab("DESIGN")
    app.job.open_action("Settings")

    app.job.open_settings_tab("Quality Control,Test Questions")
    app.verification.current_url_contains("/settings/test_questions")
    # this text is removed on the page
    # app.verification.text_present_on_page("Test Question Settings")
    app.verification.text_present_on_page("Minimum Accuracy")
    app.verification.text_present_on_page("Contributors must maintain this accuracy throughout the job")

    app.job.open_settings_tab("Quality Control,Quality Control Settings")
    app.verification.current_url_contains("/settings/quality_control")
    app.verification.text_present_on_page("Minimum Time Per Page")
    # this text is removed on the page
    # app.verification.text_present_on_page("Maximum Judgments")
    app.verification.text_present_on_page("Disable Google Translate for Contributors")
    app.verification.text_present_on_page("Contributor Answer Distribution Rules")



@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.fed_ui
@pytest.mark.fed_ui_smoke
def test_dynamic_judgment(app, login_as_customer_and_open_job):
    """
    Dynamic Judgments page
    """
    app.job.open_tab("DESIGN")
    app.job.open_action("Settings")
    app.job.open_settings_tab("Quality Control,Dynamic Judgments")
    app.verification.current_url_contains("/settings/judgments")
    app.verification.text_present_on_page("Dynamic Judgment Collection")
    app.verification.text_present_on_page("Dynamically collect judgments")
    app.verification.text_present_on_page("If contributors disagree on an answer, the job will automatically request additional judgments")

    app.navigation.click_checkbox_by_text("Dynamically collect judgments")

    app.verification.text_present_on_page("Max Judgments per Row")
    app.verification.text_present_on_page("Recommended: 2-5 judgments/row")
    app.navigation.fill_out_input_by_name(name='maxJudgmentsPerUnit', value='3')

    app.verification.text_present_on_page("Enabled Questions")
    app.verification.text_present_on_page("Select the questions that determine if more judgments are needed")
    app.verification.text_present_on_page("Available Questions")
    app.verification.text_present_on_page("Selected Questions")
    app.verification.text_present_on_page("Criteria to stop collecting judgments")
    app.verification.text_present_on_page("Please select one of the two options to stop collecting judgments:")

    app.verification.text_present_on_page("Minimum Confidence")
    app.verification.text_present_on_page("Recommended: at least 0.7")
    app.navigation.fill_out_input_by_name(name='minUnitConfidenceField', value='0.5')

    app.navigation.click_bytext("Matching Judgments")
    time.sleep(2)
    app.verification.text_present_on_page("We'll continue collecting judgments until 'n' judgments match. By default, 'n' is equivalent to the value specified for the Judgments per Row setting.")
    app.verification.text_present_on_page("Recommended: at least 0.7", is_not=False)
    invalid_matching_judgement_value = '0'
    app.navigation.fill_out_input_by_name(name='autoMatchCount', value=invalid_matching_judgement_value)
    time.sleep(2)
    app.verification.text_present_on_page(f"must be greater than {invalid_matching_judgement_value}")

    app.navigation.click_bytext("Minimum Confidence")
    time.sleep(3)
    app.verification.text_present_on_page(
        "We'll continue collecting judgments", is_not=False)






@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.fed_ui
@pytest.mark.fed_ui_smoke
def test_access_job_contributors_page(app, login_as_customer_and_open_job):
    """
        Customer is able to access the contributors  settings page
        """
    app.job.open_tab("DESIGN")
    app.job.open_action("Settings")
    app.job.open_settings_tab("Contributors")
    app.verification.current_url_contains("/settings/channels")
    if pytest.env == 'fed':
        app.verification.text_present_on_page("Selected Channels")
        app.verification.text_present_on_page("Select Contributor Channels")
    else:
        app.verification.text_present_on_page("Post job to global network of qualified contributors")
        app.verification.text_present_on_page("External")
        app.verification.text_present_on_page("Internal")


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.fed_ui
@pytest.mark.fed_ui_smoke
def test_access_job_sharing_visibility_settings_page(app, login_as_customer_and_open_job):
    """
        Customer is able to access the Sharing/Visibility  settings page
        """
    app.job.open_tab("DESIGN")
    app.job.open_action("Settings")
    app.job.open_settings_tab("Sharing/Visibility")
    app.verification.current_url_contains("/settings/sharing_visibility")
    app.verification.text_present_on_page("Sharing")
    app.verification.text_present_on_page("Visibility")
    app.verification.text_present_on_page("Share Job prior to launch")


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
def test_access_job_payments_settings_page(app, login_as_customer_and_open_job):
    """
        Customer is able to access the  Payments  settings page
        """
    app.job.open_tab("DESIGN")
    app.job.open_action("Settings")
    app.job.open_settings_tab("Pay")
    app.verification.current_url_contains("/settings/pay")
    app.verification.text_present_on_page("Payment Settings")
    app.verification.text_present_on_page(
        "Set the number of rows displayed on each page and the payment amount per page.")
    app.verification.text_present_on_page("Rows per Page")
    app.verification.text_present_on_page("Price per Page")


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.fed_ui
@pytest.mark.fed_ui_smoke
def test_access_job_api_settings_page(app, login_as_customer_and_open_job):
    """
        Customer is able to access the API  settings page
        """
    app.job.open_tab("DESIGN")
    app.job.open_action("Settings")
    app.job.open_settings_tab("API")
    app.verification.current_url_contains("/settings/api")
    app.verification.text_present_on_page("Webhook")
    app.verification.text_present_on_page("Webhook URL")
    app.verification.text_present_on_page("Job Details")
    app.verification.text_present_on_page("Turn on automatic launching of rows")
    app.verification.text_present_on_page("Job continues to run when cost exceeds initial estimate")
    app.verification.text_present_on_page("Rows remain finalized")
    app.verification.text_present_on_page("Rows should be completed in order")


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.fed_ui
@pytest.mark.fed_ui_smoke
def test_access_job_admin_settings_page(app, login_as_customer_and_open_job):
    """
        Customer is able to access the admin  settings page
    """
    app.job.open_tab("DESIGN")
    app.job.open_action("Settings")
    app.job.open_settings_tab("Admin")
    app.verification.current_url_contains("/settings/admin")
    app.verification.text_present_on_page("Job Type")
    app.verification.text_present_on_page("Quality Control")
    app.verification.text_present_on_page("Alerts")
    app.verification.text_present_on_page("Webhook")
    app.verification.text_present_on_page("Minimum Test Questions in Quiz Mode")
    app.verification.text_present_on_page("Quiz Mode")
