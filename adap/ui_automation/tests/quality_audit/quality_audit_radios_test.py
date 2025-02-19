from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.e2e_automation.services_config.contributor_ui_support import answer_questions_on_page
from adap.e2e_automation.services_config.job_api_support import generate_job_link


pytestmark = pytest.mark.regression_ipa


TEST_DATA = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get("radio_default", "")
USER_EMAIL = get_user_email('test_account')
PASSWORD = get_user_password('test_account')
API_KEY = get_user_api_key('test_account')


@pytest.fixture(scope="module")
def ipa_job():
    copied_job = Builder(API_KEY)

    copied_job_resp = copied_job.copy_job(TEST_DATA, "all_units")
    copied_job_resp.assert_response_status(200)

    job_id = copied_job_resp.json_response['id']
    copied_job.job_id = job_id
    copied_job.launch_job()
    copied_job.wait_until_status("running", max_time=60)

    return job_id


@pytest.mark.regression_ipa
def test_generate_aggregations_radios(app_test, ipa_job):
    """
    Checks that the 'Generate Aggregations' button works without errors for Radios CML
    """

    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    job_link = generate_job_link(ipa_job, API_KEY, pytest.env)
    app_test.navigation.open_page(job_link)

    app_test.user.task.wait_until_job_available_for_contributor(job_link)
    answer_questions_on_page(
        app_test.driver, tq_dict='', mode='radio_button', values=['cat', 'dog', 'something_else']
    )
    app_test.job.judgements.click_submit_judgements()

    app_test.job.ipa.open_quality_audit_page(ipa_job)

    app_test.navigation.click_link("Generate Aggregations")
    assert app_test.verification.wait_untill_text_present_on_the_page('Setup Audit', 60)
    app_test.navigation.click_link("Setup Audit")

    app_test.verification.text_present_on_page(
        "Select up to 3 different columns from your source data to display in the audit preview. "
        "Please note that at least 1 source data column is required for the preview."
    )
