
from adap.api_automation.services_config.make import Make
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.in_platform_audit import IPA_API

pytestmark = pytest.mark.regression_ipa

TEST_DATA = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('html_tag', "")
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

    all_answers = [len(all_answer['aggregations_distribution']['values']) for all_answer in _ipa.get_aggregations_distribution(TEST_DATA).json_response]
    name_questions = [name_question['name'] for name_question in _ipa.get_aggregations_distribution(TEST_DATA).json_response]
    my_dictionary = {name_questions[i]: all_answers[i] for i in range(len(name_questions))}

    return [cml_tags, my_dictionary]


def test_units_html_tags_ipa(app, ipa_job):
    builder = Builder(API_KEY, env=pytest.env)
    resp = builder.get_json_job_status(TEST_DATA)

    assert resp.status_code == 200

    actual_num_units = resp.json_response['units_count']
    actual_label_name = ipa_job[0][0]["label"]

    expected_num_units = app.job.ipa.get_all_units_on_page()

    assert len(expected_num_units) == actual_num_units
    assert expected_num_units[0]['data'] == actual_label_name
    assert expected_num_units[0]['answer'] >= 1, "The number of answer should be more then 1"
    assert expected_num_units[0]['answer'] <= 3, "The number of answer should be less then 3 or equal 3"


def test_view_details_rendering_with_html_tag_ipa(app, ipa_job):
    app.navigation.refresh_page()
    type_of_questions = [question_type['type'].upper for question_type in ipa_job[0]]
    first_name_of_question = ipa_job[0][0]['label']
    first_unit = app.job.ipa.get_all_units_on_page()[0]['unit_id']
    app.job.ipa.view_details_by_unit_id(first_unit)
    assert [type_of_question in app.job.ipa.get_type_question_grid_view() for type_of_question in type_of_questions]
    assert app.job.ipa.answer_in_view_details(first_name_of_question) == 2
    app.job.ipa.close_view_details()


def test_customize_question_mixed_cml_element_ipa(app, ipa_job):
    for index, question_name in enumerate(ipa_job[0]):
        q_l = question_name["label"]
        q_n = question_name["name"]
        all_units = app.job.ipa.get_all_units_on_page()
        question_on_detailed_view = all_units[0]['data']
        app.job.ipa.customize_question()
        question_in_customize_question = app.job.ipa.get_question_by_index()
        app.job.ipa.change_customize_question(q_l)
        assert question_in_customize_question == question_on_detailed_view, "The name of chosen question different"
        assert ipa_job[1][q_n] == app.job.ipa.get_number_of_answer_in_customize_question(), "The selected answers of " \
                                                                                              "question not displayed in " \
                                                                                              "customize question "
        app.job.ipa.change_customize_question(q_l, True)
