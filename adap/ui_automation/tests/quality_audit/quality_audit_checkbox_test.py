
from adap.api_automation.services_config.make import Make
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.in_platform_audit import IPA_API
from adap.e2e_automation.services_config.contributor_ui_support import answer_questions_on_page
from adap.e2e_automation.services_config.job_api_support import generate_job_link

pytestmark = pytest.mark.regression_ipa

TEST_DATA = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('checkbox', "")
USER_EMAIL = get_user_email('test_account')
PASSWORD = get_user_password('test_account')
API_KEY = get_user_api_key('test_account')
_ipa = IPA_API(API_KEY)


@pytest.fixture(scope="module")
def ipa_job(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.job.ipa.open_quality_audit_page(TEST_DATA)
    make = Make(API_KEY)
    resp = make.get_jobs_cml_tag(TEST_DATA)
    cml_tags = resp.json_response
    try:
        app.navigation.click_link("Generate Aggregations")
    except:
        pass

    if app.verification.wait_untill_text_present_on_the_page('Setup Audit', 5):
        app.navigation.click_link("Setup Audit")

        app.verification.text_present_on_page(
            "Select up to 3 different columns from your source data to display in the audit preview. "
            "Please note that at least 1 source data column is required for the preview.")

        app.job.ipa.customize_data_source("image_url", "Image", action="Continue")
    return cml_tags


def test_units_checkbox_ipa(app, ipa_job):
    builder = Builder(API_KEY, env=pytest.env)
    resp = builder.get_json_job_status(TEST_DATA)

    actual_num_units = resp.json_response['units_count']
    actual_label_name = ipa_job[0]["label"]

    expected_num_units = app.job.ipa.get_all_units_on_page()

    assert len(expected_num_units) == actual_num_units
    assert expected_num_units[0]['data'] == actual_label_name
    assert expected_num_units[0]['answer'] == 2


def test_customize_question_checkbox_ipa(app, ipa_job):
    question_name = ipa_job[1]["label"]

    all_question_require = _ipa.get_aggregations_distribution(TEST_DATA).json_response[0]['aggregations_distribution']['values']
    all_question = _ipa.get_aggregations_distribution(TEST_DATA).json_response[1]['aggregations_distribution']['values']

    all_units = app.job.ipa.get_all_units_on_page()
    question_on_detailed_view = all_units[0]['data']
    app.job.ipa.customize_question()
    question_in_customize_question = app.job.ipa.get_question_by_index()
    assert question_in_customize_question == question_on_detailed_view, "The name of chosen question different"
    assert len(all_question_require) == app.job.ipa.get_number_of_answer_in_customize_question(), "The selected answers of " \
                                                                                       "question not displayed in " \
                                                                                       "customize question "
    app.job.ipa.change_customize_question(question_name)
    assert len(all_question) == app.job.ipa.get_number_of_answer_in_customize_question(), "The selected answers of " \
                                                                                       "question not displayed in " \
                                                                                       "customize question "
    app.job.ipa.change_customize_question(question_name, True)

    question_on_detailed_view = app.job.ipa.get_all_units_on_page()[0]['data']
    assert question_name == question_on_detailed_view, 'The name of set question different from ' \
                                                       'question displayed on detailed view '


def test_view_details_checkbox_ipa(app, ipa_job):
    app.navigation.refresh_page()
    type_of_question = ipa_job[0]['type']
    first_unit = app.job.ipa.get_all_units_on_page()[0]['unit_id']
    app.job.ipa.view_details_by_unit_id(first_unit)
    assert app.job.ipa.get_number_of_question_in_view_details(type_of_question) == len(ipa_job)
    assert app.job.ipa.answer_in_view_details("Is number?") == 2
    app.job.ipa.close_view_details()


def test_approve_question_checkbox_ipa(app, ipa_job):
    payload = {"filters":{"question":{"name":"is_fruit","values":[]}}}
    app.navigation.refresh_page()
    approve_unit = app.job.ipa.get_all_units_on_page()[0]['unit_id']
    app.job.ipa.view_details_by_unit_id(approve_unit)
    app.job.ipa.approve_question()
    app.job.ipa.close_view_details()
    approve = _ipa.post_job_and_field_accuracy(TEST_DATA, payload).json_response['job']['fields'][0]['correct']
    assert app.job.ipa.get_all_units_on_page()[0]['audited']
    assert approve == 6


def test_reject_question_checkbox_ipa(app, ipa_job):
    payload = {"filters":{"question":{"name":"is_fruit","values":[]}}}
    app.navigation.refresh_page()
    reject_unit = app.job.ipa.get_all_units_on_page()[0]['unit_id']
    app.job.ipa.view_details_by_unit_id(reject_unit)
    app.job.ipa.reject_question()
    app.job.ipa.select_correct_answer("seven")
    app.job.ipa.close_view_details()
    correct = _ipa.post_job_and_field_accuracy(TEST_DATA, payload).json_response['job']['fields'][0]['correct']
    audited = _ipa.post_job_and_field_accuracy(TEST_DATA, payload).json_response['job']['fields'][0]['audited']
    reject = audited - correct
    assert app.job.ipa.get_all_units_on_page()[0]['audited']
    assert reject == 1


def test_add_reason_checkbox_ipa(app, ipa_job):
    app.navigation.refresh_page()
    reject_unit = app.job.ipa.get_all_units_on_page()[1]['unit_id']
    app.job.ipa.view_details_by_unit_id(reject_unit)
    app.job.ipa.reject_question()
    app.job.ipa.add_reason("This question rejected")

    app.job.ipa.close_view_details()
    app.job.ipa.view_details_by_unit_id(reject_unit)
    app.job.ipa.reject_question()
    app.job.ipa.edit_reason()

    app.verification.text_present_on_page("This question rejected")
    app.job.ipa.clear_reason()
    app.job.ipa.approve_question()
    app.job.ipa.close_view_details()


@pytest.mark.regression_ipa
def test_judgments_parquet_file_generation_checkbox(app, ipa_job):
    """
    Checks that the Judgments parquet file generates without errors for the Checkbox CML
    """

    copied_job = Builder(API_KEY)

    copied_job_resp = copied_job.copy_job(TEST_DATA, "all_units")
    copied_job_resp.assert_response_status(200)

    job_id = copied_job_resp.json_response['id']
    copied_job.job_id = job_id
    app.mainMenu.jobs_page()
    assert app.verification.wait_untill_text_present_on_the_page(text="Jobs", max_time=10)
    app.job.open_job_with_id(job_id)

    app.job.open_tab("DESIGN")
    app.job.open_tab("LAUNCH")

    app.navigation.fill_out_input_by_name(name='judgments', value=1)
    app.navigation.click_btn(btn_name="Save Changes")

    copied_job.launch_job()
    copied_job.wait_until_status("running", max_time=60)

    job_link = generate_job_link(job_id, API_KEY, pytest.env)
    app.navigation.open_page(job_link)

    app.user.task.wait_until_job_available_for_contributor(job_link)

    for _ in range(2):
        answer_questions_on_page(
            app.driver, tq_dict='', mode='cml_checkbox', values=['seven']
        )
        app.job.judgements.click_submit_judgements()

    app.job.ipa.open_quality_audit_page(job_id)

    app.navigation.click_link("Generate Aggregations")
    assert app.verification.wait_untill_text_present_on_the_page('Setup Audit', 60)
    app.navigation.click_link("Setup Audit")

    app.verification.text_present_on_page(
        "Select up to 3 different columns from your source data to display in the audit preview. "
        "Please note that at least 1 source data column is required for the preview."
    )
