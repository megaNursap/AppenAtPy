from adap.api_automation.services_config.make import Make
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.in_platform_audit import IPA_API

pytestmark = pytest.mark.regression_ipa

TEST_DATA = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('ratings', "")
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


def test_units_ratings_ipa(app, ipa_job):
    builder = Builder(API_KEY, env=pytest.env)
    resp = builder.get_json_job_status(TEST_DATA)

    actual_num_units = resp.json_response['units_count']
    actual_label_name = ipa_job[0]["label"]

    expected_num_units = app.job.ipa.get_all_units_on_page()

    assert len(expected_num_units) == actual_num_units
    assert expected_num_units[0]['data'] == actual_label_name
    assert expected_num_units[0]['answer'] >= 1


def test_customize_question_ratings_ipa(app, ipa_job):
    question_name = ipa_job[1]["label"]

    all_question_require = _ipa.get_aggregations_distribution(TEST_DATA).json_response[0]['aggregations_distribution'][
        'values']
    all_question = _ipa.get_aggregations_distribution(TEST_DATA).json_response[1]['aggregations_distribution']['values']

    all_units = app.job.ipa.get_all_units_on_page()
    question_on_detailed_view = all_units[0]['data']
    app.job.ipa.customize_question()
    question_in_customize_question = app.job.ipa.get_question_by_index()
    assert question_in_customize_question == question_on_detailed_view, "The name of chosen question different"
    assert len(
        all_question_require) == app.job.ipa.get_number_of_answer_in_customize_question(), "The selected answers of " \
                                                                                           "require question not displayed in " \
                                                                                           "customize question "
    app.job.ipa.change_customize_question(question_name)
    assert len(all_question) == app.job.ipa.get_number_of_answer_in_customize_question(), "The selected answers of " \
                                                                                          "optional question not displayed in " \
                                                                                          "customize question "

    app.job.ipa.change_customize_question(question_name, True)

    question_on_detailed_view = app.job.ipa.get_all_units_on_page()[0]['data']
    assert question_name == question_on_detailed_view, 'The name of set question different from ' \
                                                       'question displayed on detailed view '


def test_answer_distributions_optional_ratings_ipa(app, ipa_job):
    app.navigation.refresh_page()
    question_name = ipa_job[1]["label"]
    payload_all_units = {"filters": {"question": {"name": "your_rating_for_this_color", "values": []}}}
    all_units = _ipa.search_unit_for_audit(TEST_DATA, payload_all_units).json_response
    total_count_answer_of_unit = all_units['units'][1]['fields'][0]['answer_distribution']['total_count']

    app.job.ipa.customize_question()
    app.job.ipa.change_customize_question(question_name, True)

    all_units = app.job.ipa.get_all_units_on_page()
    question_on_detailed_view = all_units[0]['answer']
    assert question_on_detailed_view == total_count_answer_of_unit


def test_view_details_rating_ipa(app, ipa_job):
    app.navigation.refresh_page()
    type_of_question = ipa_job[0]['type']
    number_of_answer_first_question = ipa_job[0]['children']
    number_of_answer_second_question = ipa_job[1]['children']

    first_unit = app.job.ipa.get_all_units_on_page()[0]['unit_id']
    app.job.ipa.view_details_by_unit_id(first_unit)

    assert app.job.ipa.get_number_of_question_in_view_details(type_of_question) == len(ipa_job)
    assert app.job.ipa.answer_in_view_details("Your rating for this food") == len(number_of_answer_first_question)
    assert app.job.ipa.answer_in_view_details("Your rating for this color") == len(number_of_answer_second_question)
    app.job.ipa.close_view_details()


def test_approve_question_ratings_ipa(app, ipa_job):
    payload = {"filters": {"question": {"name": "your_rating_for_this_food", "values": []}}}
    app.navigation.refresh_page()
    approve_unit = app.job.ipa.get_all_units_on_page()[0]['unit_id']
    # question_name = ipa_job[0]['name']

    app.job.ipa.view_details_by_unit_id(approve_unit)
    app.job.ipa.approve_question()
    app.job.ipa.close_view_details()

    correct = _ipa.post_job_and_field_accuracy(TEST_DATA, payload).json_response['job']['fields'][1]['correct']
    assert app.job.ipa.get_all_units_on_page()[0]['audited']
    assert correct == 1


def test_reject_question_ratings_ipa(app, ipa_job):
    app.navigation.refresh_page()
    payload = {"filters": {"question": {"name": "your_rating_for_this_food", "values": []}}}
    reject_unit = app.job.ipa.get_all_units_on_page()[0]['unit_id']
    question_name = ipa_job[0]['name']

    app.job.ipa.view_details_by_unit_id(reject_unit)
    app.job.ipa.reject_question()
    app.job.ipa.select_correct_answer("2")
    app.job.ipa.close_view_details()

    correct = _ipa.post_job_and_field_accuracy(TEST_DATA, payload).json_response['job']['fields'][0]['correct']
    assert app.job.ipa.get_all_units_on_page()[0]['audited']
    assert correct == 3


def test_add_reason_rating_ipa(app, ipa_job):
    app.navigation.refresh_page()
    reject_unit = app.job.ipa.get_all_units_on_page()[2]['unit_id']
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


def test_filter_by_label(app, ipa_job):
    app.navigation.refresh_page()
    app.job.ipa.customize_question()
    app.job.ipa.filter_by_label([1, 5], 'Your rating for this color', True)
    expected_num_units = app.job.ipa.get_all_units_on_page()
    actual_num_units = \
    _ipa.get_aggregations_distribution(TEST_DATA).json_response[0]['aggregations_distribution']['values'][1][
        'count']
    assert len(expected_num_units) == int(actual_num_units), "After filtering by rating label %s, the count of unit " \
                                                             "different "
