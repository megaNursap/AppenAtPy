from allure_commons.types import AttachmentType

from adap.api_automation.services_config.make import Make
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.in_platform_audit import IPA_API
from adap.ui_automation.utils.selenium_utils import split_text

pytestmark = pytest.mark.regression_ipa

TEST_DATA = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('text', "")
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


def test_units_text_ipa(app, ipa_job):
    builder = Builder(API_KEY, env=pytest.env)
    resp = builder.get_json_job_status(TEST_DATA)

    actual_num_units = resp.json_response['units_count']
    actual_label_name = ipa_job[0]["label"]

    expected_num_units = app.job.ipa.get_all_units_on_page()

    assert len(expected_num_units) == actual_num_units
    assert expected_num_units[0]['data'] == actual_label_name
    assert expected_num_units[0]['answer'] >= 1


def test_customize_question_text_ipa(app, ipa_job):
    all_units = app.job.ipa.get_all_units_on_page()
    question_on_detailed_view = all_units[0]['data']
    default_question = ipa_job[0]["label"]
    question_name = ipa_job[2]["label"]

    app.job.ipa.customize_question()
    assert default_question == app.job.ipa.get_question_by_index(), "The default name of question in customize " \
                                                                    "question modal different "

    number_of_answer_on_customize_question_modal = app.job.ipa.get_number_of_answer_in_customize_question()
    assert number_of_answer_on_customize_question_modal == 0, "The count of answer for text question %s should be " \
                                                              "empty " % default_question

    question_in_customize_question = app.job.ipa.get_question_by_index()

    assert question_in_customize_question == question_on_detailed_view, "The name of chosen question different"

    app.job.ipa.change_customize_question(question_name, True)

    question_on_detailed_view = app.job.ipa.get_all_units_on_page()[0]['data']
    assert question_name == question_on_detailed_view, 'The name of set question different from ' \
                                                       'question displayed on detailed view '
    app.job.ipa.customize_question()
    app.job.ipa.change_customize_question(default_question, True)


def test_absence_of_answer_customize_question_modal_textarea_ipa(app, ipa_job):
    app.navigation.refresh_page()
    question_name = ipa_job[2]["label"]

    app.job.ipa.customize_question()
    app.job.ipa.change_customize_question(question_name)
    number_of_answer_on_customize_question_modal = app.job.ipa.get_number_of_answer_in_customize_question()
    assert number_of_answer_on_customize_question_modal == 0, "The count of answer for question %s on customize " \
                                                              "question modal should be empty" % question_name

    question_in_customize_question = app.job.ipa.get_question_by_index()
    app.job.ipa.change_customize_question(question_name, True)

    all_units = app.job.ipa.get_all_units_on_page()
    question_on_detailed_view = all_units[0]['data']

    assert question_on_detailed_view == question_in_customize_question, "The name of question different of selected " \
                                                                        "question %s and displayed on detail view %s" \
                                                                        % question_in_customize_question \
                                                                        % question_on_detailed_view


def test_load_each_text_input(app, ipa_job):
    app.navigation.refresh_page()
    all_units = app.job.ipa.get_all_units_on_page()
    question_name = ipa_job[3]["label"]

    actual_answer = _ipa.get_aggregations_distribution(TEST_DATA).json_response[3]
    assert 'aggregations_distribution' in actual_answer, "The key 'aggregations_distribution' missed in json response"
    actual_answer = actual_answer['aggregations_distribution']['values'][0]['name']
    app.job.ipa.customize_question()
    app.job.ipa.change_customize_question(question_name, True)
    expected_answer_on_detailed_view = app.job.ipa.get_all_units_on_page()[len(all_units) - 1]['answer_input']
    assert actual_answer == split_text(expected_answer_on_detailed_view, 0), "The text input loaded incorrect"


def test_view_details_text_ipa(app, ipa_job):
    app.navigation.refresh_page()
    type_of_text_question = ipa_job[0]['type']
    type_of_textarea_question = ipa_job[2]['type']

    text_question = _ipa.get_aggregations_distribution(TEST_DATA).json_response[0]['name']
    textarea_question = _ipa.get_aggregations_distribution(TEST_DATA).json_response[1]['name']

    unit = app.job.ipa.get_all_units_on_page()[3]['unit_id']

    audit_info = _ipa.get_audit_info_for_unit(TEST_DATA, unit).json_response
    number_of_answer_text_question = audit_info['fields'][text_question]['answer_distribution']['total_count']
    number_of_answer_textarea_question = audit_info['fields'][textarea_question]['answer_distribution']['total_count']

    app.job.ipa.view_details_by_unit_id(unit)

    assert app.job.ipa.get_number_of_question_in_view_details(type_of_text_question) == len(ipa_job), "The number of " \
                                                                                                      "question on " \
                                                                                                      "detail view " \
                                                                                                      "modal for text " \
                                                                                                      "incorrect "
    assert app.job.ipa.get_number_of_question_in_view_details(type_of_textarea_question) == 2, "The number " \
                                                                                               "of question " \
                                                                                               "on detail " \
                                                                                               "view modal " \
                                                                                               "for " \
                                                                                               "textarea " \
                                                                                               "incorrect "

    assert app.job.ipa.answer_in_view_details("Color") == number_of_answer_text_question, "The number of answer for " \
                                                                                          "text question incorrect "
    assert app.job.ipa.answer_in_view_details(
        "Describe the odor of flower") == number_of_answer_textarea_question, "The number of answer for" \
                                                                              " textarea question incorrect "
    app.job.ipa.close_view_details()


def test_approve_question_text_ipa(app, ipa_job):
    app.navigation.refresh_page()
    approve_unit = app.job.ipa.get_all_units_on_page()[0]['unit_id']
    question_text_name = ipa_job[0]['name']
    question_textarea_name = ipa_job[2]['name']

    app.job.ipa.view_details_by_unit_id(approve_unit)
    app.job.ipa.approve_question()
    app.job.ipa.approve_question(4)
    app.job.ipa.close_view_details()

    correct_text = \
        _ipa.get_audit_info_for_unit(TEST_DATA, approve_unit).json_response['fields'][question_text_name]['audit'][
            'correct']
    correct_textarea = \
        _ipa.get_audit_info_for_unit(TEST_DATA, approve_unit).json_response['fields'][question_textarea_name]['audit'][
            'correct']
    assert app.job.ipa.get_all_units_on_page()[0]['audited']
    assert correct_text
    assert correct_textarea


def test_reject_question_text_ipa(app, ipa_job):
    payload = {
        "fields": {"color": {"correct": True, "answers": [], "reason": "", "custom_answers": [], "fixed_reasons": []},
                   "describe_the_taste_of_this_fruit": {"correct": True, "answers": [], "reason": "",
                                                        "custom_answers": [], "fixed_reasons": []}}}

    app.navigation.refresh_page()
    reject_unit = app.job.ipa.get_all_units_on_page()[0]['unit_id']

    res = _ipa.add_audit(TEST_DATA, reject_unit, payload)
    res.assert_response_status(201)

    question_name = ipa_job[0]['name']

    app.job.ipa.view_details_by_unit_id(reject_unit)
    app.job.ipa.reject_question()
    app.job.ipa.add_answer("Yellow")
    actual_answer = app.job.ipa.get_selected_value('color')

    app.job.ipa.close_view_details()

    correct = _ipa.get_audit_info_for_unit(TEST_DATA, reject_unit).json_response['fields'][question_name]['audit'][
        'correct']
    expected_answer = \
        _ipa.get_audit_info_for_unit(TEST_DATA, reject_unit).json_response['fields'][question_name]['audit'][
            'custom_answers'][0]
    assert app.job.ipa.get_all_units_on_page()[0]['audited']
    assert expected_answer == actual_answer, f"The expected answer {expected_answer} but actual {actual_answer}"
    assert not correct


def test_add_reason_text_ipa(app, ipa_job):
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


def test_filter_by_audit_unaudited_text_ipa(app, ipa_job):
    app.navigation.refresh_page()
    units_on_page = app.job.ipa.get_all_units_on_page()
    audited_count = 0
    unaudited_count = 0
    for unit in units_on_page:
        if unit['audited']:
            audited_count += 1
        else:
            unaudited_count += 1
    app.job.ipa.filter_audit_status('Audited')
    app.job.ipa.apply_filters()
    audited_unit_on_page = app.job.ipa.get_all_units_on_page()
    assert audited_count == len(
        audited_unit_on_page), f"View By audited unit shows incorrect should be {audited_count}, but {audited_unit_on_page}"
    app.job.ipa.filter_audit_status('Unaudited')
    app.job.ipa.apply_filters()
    unaudited_unit_on_page = app.job.ipa.get_all_units_on_page()
    assert unaudited_count == len(
        unaudited_unit_on_page), f"View By unaudited unit shows incorrect should be {unaudited_count}, but {unaudited_unit_on_page} "
    app.job.ipa.remove_filters()


def test_side_bar_information_text_ipa(app, ipa_job):
    payload = {"filters": {"question": {"name": "color", "values": []}}}
    app.navigation.refresh_page()
    side_bar_info = app.job.ipa.get_side_bar_information_finalized_units()
    actual_raw_audit = side_bar_info[0]['audited']
    actual_job_accuracy = side_bar_info[0]['job_accuracy']
    expected_raw_audited = _ipa.post_job_and_field_accuracy(TEST_DATA, payload).json_response['job']['audited']
    expected_job_accuracy = _ipa.post_job_and_field_accuracy(TEST_DATA, payload).json_response['job']['accuracy']
    assert str(
        expected_raw_audited) == actual_raw_audit, f"The raws audited on UI {actual_raw_audit} render incorrect count"
    assert "{:.2%}".format(expected_job_accuracy) == actual_job_accuracy


def test_sort_by_confidence_text_ipa(app, ipa_job):
    app.navigation.refresh_page()
    question_name = ipa_job[0]["label"]

    app.job.ipa.customize_question()
    app.job.ipa.change_customize_question(question_name, True)

    units_on_page = app.job.ipa.get_all_units_on_page()
    ascending = all(l['unit_id'] == s['unit_id'] for l, s in
                    zip(units_on_page, sorted(units_on_page, key=lambda x: x['unit_id'])))
    assert ascending, "The units not in ascending order"

    app.job.ipa.sorting_by("High to Low")
    units_on_page = app.job.ipa.get_all_units_on_page()

    id_of_first_unit = units_on_page[0]['unit_id']
    assert id_of_first_unit == '2296277222', "The units not sort by confidence Low to High"

    app.job.ipa.sorting_by("Low to High")
    units_on_page = app.job.ipa.get_all_units_on_page()
    id_of_first_unit = units_on_page[0]['unit_id']
    allure.attach(app.driver.get_screenshot_as_png(), name="Screenshot",
                  attachment_type=AttachmentType.PNG)
    assert id_of_first_unit == '2296277225', "The units not sort by confidence Low to High"

    app.job.ipa.sorting_by()
    units_on_page = app.job.ipa.get_all_units_on_page()
    descending = all(l['unit_id'] == s['unit_id'] for l, s in
                     zip(units_on_page, sorted(units_on_page, key=lambda x: x['unit_id'], reverse=True)))
    assert descending, "The units not in descending order"
