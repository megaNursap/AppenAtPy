import time

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.e2e_automation.services_config.contributor_ui_support import answer_questions_on_page
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.api_automation.services_config.in_platform_audit import IPA_API
from adap.ui_automation.utils.js_utils import element_to_the_middle

pytestmark = pytest.mark.regression_ipa

TEST_DATA = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get("radio_default", "")
USER_EMAIL = get_user_email('test_account')
PASSWORD = get_user_password('test_account')
API_KEY = get_user_api_key('test_account')
_ipa = IPA_API(API_KEY)


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
    # return 1905799


def test_access_ipa_no_judgements(app_test, ipa_job):
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(ipa_job)

    ipa_url = "https://client.{env}.cf3.us/jobs/{job}/audit".format(env=pytest.env, job=ipa_job)

    app_test.navigation.open_page(ipa_url)
    app_test.user.close_guide()

    app_test.verification.text_present_on_page("Unsupported job")
    app_test.verification.text_present_on_page("This job is not yet supported by Quality Audit")


@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.dependency()
def test_submit_judgements_ipa(app_test, ipa_job):
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    job_link = generate_job_link(ipa_job, API_KEY, pytest.env)
    app_test.navigation.open_page(job_link)
    # app_test.user.close_guide()

    app_test.user.task.wait_until_job_available_for_contributor(job_link)
    answer_questions_on_page(app_test.driver, tq_dict='', mode='radio_button', values=['cat', 'dog', 'something_else'])
    app_test.job.judgements.click_submit_judgements()

    copied_job = Builder(API_KEY)
    copied_job.job_id = ipa_job

    running_time = 0
    current_count = 0
    row_finalized = False
    while (current_count != 5) and (running_time < 4):
        time.sleep(15)
        res = copied_job.get_rows_and_judgements()
        current_count = len(res.json_response)
        print(res.json_response)
        if current_count == 5:
            row_finalized = True
        running_time += 1
    assert row_finalized, "Units have not been finalized"


@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.dependency(depends=["test_submit_judgements_ipa"])
def test_view_details_ipa(app, ipa_job):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(ipa_job)

    ipa_url = "https://client.{env}.cf3.us/jobs/{job}/audit".format(env=pytest.env, job=ipa_job)

    app.navigation.open_page(ipa_url)

    try:
        time.sleep(4)
        app.navigation.click_link("Generate Aggregations")
    except:
        pass

    # app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Setup Audit', 300)
    app.navigation.click_link("Setup Audit")

    app.verification.text_present_on_page(
        "Setup your audit by selecting sample amount, source data, and question to display in audit preview")

    app.verification.text_present_on_page(
        "Select up to 3 different columns from your source data to display in the audit preview. "
        "Please note that at least 1 source data column is required for the preview.")

    app.verification.text_present_on_page("Select question to use as preview for audit. You can also filter rows by "
                                          "answers to the selected question.")

    app.job.ipa.title_present_in_modal_box('Audit Configuration')
    app.verification.text_present_on_page('Data Source For Audit Preview')
    app.verification.text_present_on_page('Question For Audit Preview')
    app.verification.text_present_on_page('Sample Units Amount')

    app.job.ipa.customize_sampling_units()
    app.job.ipa.customize_data_source("image_url", "Text", action="Create")

    all_units = app.job.ipa.get_all_units_on_page()
    assert len(all_units) == 5


@pytest.mark.dependency(depends=["test_view_details_ipa"])
def test_approve_reject_question_ipa(app, ipa_job):
    all_units = app.job.ipa.get_all_units_on_page()
    unit_approve = all_units[0]['unit_id']
    unit_reject = all_units[1]['unit_id']
    unit_unaudited = all_units[2]['unit_id']

    app.job.ipa.view_details_by_unit_id(unit_approve)
    app.job.ipa.approve_question()
    # assert app.job.quality_audit.get_question_status() == 'approved'
    # app.navigation.close_modal_window()
    app.navigation.click_link('Save and Close')

    app.job.ipa.view_details_by_unit_id(unit_reject)
    app.job.ipa.reject_question()
    # assert app.job.quality_audit.get_question_status() == 'rejected'
    # app.navigation.close_modal_window()
    app.navigation.click_link('Save and Close')

    updated_units = app.job.ipa.get_all_units_on_page()
    assert find_dict_in_array_by_value(updated_units, 'unit_id', unit_approve)['audited']
    assert find_dict_in_array_by_value(updated_units, 'unit_id', unit_reject)['audited']
    assert not find_dict_in_array_by_value(updated_units, 'unit_id', unit_unaudited)['audited']

#
@pytest.mark.dependency(depends=["test_approve_reject_question_ipa"])
def test_add_reason_ipa(app, ipa_job):
    all_units = app.job.ipa.get_all_units_on_page()
    unit_reject = all_units[1]['unit_id']
    unit_approve = all_units[0]['unit_id']
    unit_not_audited = all_units[2]['unit_id']

    # --- add reason for rejected question
    app.job.ipa.view_details_by_unit_id(unit_reject)
    # element_to_the_middle(app.driver, app.driver.find_element('xpath',"//a[text()='Add Reason']"))
    # app.navigation.click_link("Add Reason")
    # app.verification.text_present_on_page("Reason:")

    app.job.ipa.add_reason("reason - test - rejected")
    # app.navigation.close_modal_window()
    app.navigation.click_link('Save and Close')

    app.job.ipa.view_details_by_unit_id(unit_reject)
    app.job.ipa.edit_reason()
    app.verification.text_present_on_page("reason - test")
    # app.navigation.close_modal_window()
    app.navigation.click_link('Close')

    # --- add reason for approved question
    app.job.ipa.view_details_by_unit_id(unit_approve)

    app.job.ipa.add_reason("reason - test - approved")
    # app.navigation.close_modal_window()
    app.navigation.click_link('Save and Close')

    app.job.ipa.view_details_by_unit_id(unit_approve)
    app.job.ipa.edit_reason()
    app.verification.text_present_on_page("reason - test - approved")
    # app.navigation.close_modal_window()
    app.navigation.click_link('Close')

    # not audited
    app.job.ipa.view_details_by_unit_id(unit_not_audited)
    app.verification.text_present_on_page("Add Reason", is_not=False)
    # app.navigation.close_modal_window()
    app.navigation.click_link('Close')


# @pytest.mark.skip(reason="Bug.  https://appen.atlassian.net/browse/CW-8518")
@pytest.mark.dependency(depends=["test_add_reason_ipa"])
def test_view_by_audited_unaudited_ipa(app, ipa_job):
    app.navigation.refresh_page()
    data = {"Audited": 2, "Unaudited": 3}
    for key, value in data.items():
        app.job.ipa.filter_audit_status(key)
        app.job.ipa.apply_filters()
        all_units = app.job.ipa.get_all_units_on_page()
        assert len(all_units) == value, f"Total {key} units on page is not equal {value}"
    app.job.ipa.remove_filters()
