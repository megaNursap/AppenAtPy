from adap.api_automation.services_config.make import Make
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.in_platform_audit import IPA_API
from adap.ui_automation.utils.selenium_utils import split_text, modify_text

pytestmark = pytest.mark.regression_ipa

TEST_DATA = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('taxonomy', "")
USER_EMAIL = get_user_email('test_account')
PASSWORD = get_user_password('test_account')
API_KEY = get_user_api_key('test_account')
_ipa = IPA_API(API_KEY)


@pytest.fixture(scope="module")
def quality_audit_job(app):
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


def test_units_taxonomy_qa(app, quality_audit_job):
    builder = Builder(API_KEY, env=pytest.env)
    resp = builder.get_json_job_status(TEST_DATA)

    actual_num_units = resp.json_response['units_count']
    actual_label_name = quality_audit_job[0]["label"]

    expected_num_units = app.job.ipa.get_all_units_on_page()

    assert len(expected_num_units) == actual_num_units
    assert expected_num_units[0]['data'] == actual_label_name
    assert expected_num_units[0]['answer'] >= 1


def test_customize_question_taxonomy_qa(app, quality_audit_job):
    all_units = app.job.ipa.get_all_units_on_page()
    question_on_detailed_view = all_units[0]['data']
    default_question = quality_audit_job[0]["label"]

    app.job.ipa.customize_question()
    assert default_question == app.job.ipa.get_question_by_index(), "The default name of question in customize " \
                                                                    "question modal different "

    number_of_answer_on_customize_question_modal = app.job.ipa.get_number_of_answer_in_customize_question()
    assert number_of_answer_on_customize_question_modal == 5, "The count of answer for taxonomy question %s not equal " \
                                                              "5 " % default_question

    question_in_customize_question = app.job.ipa.get_question_by_index()

    assert question_in_customize_question == question_on_detailed_view, 'The name of set question different from ' \
                                                                        'question displayed on detailed view'


def test_view_details_taxonomy_qa(app, quality_audit_job):
    app.navigation.refresh_page()
    type_of_taxonomy_question = quality_audit_job[0]['type']
    type_modify_question = modify_text(type_of_taxonomy_question, "[A-Z][a-z]*")

    taxonomy_question = _ipa.get_aggregations_distribution(TEST_DATA).json_response[0]['name']

    unit = app.job.ipa.get_all_units_on_page()[3]['unit_id']

    audit_info = _ipa.get_audit_info_for_unit(TEST_DATA, unit).json_response
    number_of_answer_taxonomy_question = audit_info['fields'][taxonomy_question]['answer_distribution']['total_count']

    app.job.ipa.view_details_by_unit_id(unit)

    assert app.job.ipa.get_number_of_question_in_view_details(type_modify_question) == len(
        quality_audit_job), "The number of " \
                            "question on " \
                            "detail view " \
                            "modal for text " \
                            "incorrect "

    assert app.job.ipa.answer_in_view_details(
        "Taxonomy_qa") == number_of_answer_taxonomy_question / 2, "The number of answer for " \
                                                                  "taxonomy question incorrect "

    app.job.ipa.close_view_details()


def test_approve_question_taxonomy_quality_audit(app, quality_audit_job):
    app.navigation.refresh_page()
    approve_unit = app.job.ipa.get_all_units_on_page()[0]['unit_id']
    question_text_name = quality_audit_job[0]['name']

    app.job.ipa.view_details_by_unit_id(approve_unit)
    app.job.ipa.approve_question()
    app.job.ipa.close_view_details()

    correct_taxonomy = \
        _ipa.get_audit_info_for_unit(TEST_DATA, approve_unit).json_response['fields'][question_text_name]['audit'][
            'correct']
    assert app.job.ipa.get_all_units_on_page()[0]['audited']
    assert correct_taxonomy


def test_reject_question_taxonomy_quality_adit(app, quality_audit_job):
    payload = {"fields": {
        "taxonomy_qa": {"correct": True, "answers": [], "reason": "", "custom_answers": [], "fixed_reasons": []}}}
    app.navigation.refresh_page()

    reject_unit = app.job.ipa.get_all_units_on_page()[0]['unit_id']
    res = _ipa.add_audit(TEST_DATA, reject_unit, payload)
    res.assert_response_status(201)

    question_name = quality_audit_job[0]['name']

    app.job.ipa.view_details_by_unit_id(reject_unit)
    app.job.ipa.reject_question()
    actual_answer = app.job.ipa.select_taxonomy_item("DAIRY > Milk")

    app.job.ipa.close_view_details()

    correct = _ipa.get_audit_info_for_unit(TEST_DATA, reject_unit).json_response['fields'][question_name]['audit'][
        'correct']
    expected_answer = \
        _ipa.get_audit_info_for_unit(TEST_DATA, reject_unit).json_response['fields'][question_name]['audit'][
            'custom_answers'][0]
    assert app.job.ipa.get_all_units_on_page()[0]['audited']
    assert expected_answer == actual_answer, f"The expected answer {expected_answer} but actual {actual_answer}"
    assert not correct


def test_filter_by_audit_unaudited_taxonomy_qa(app, quality_audit_job):
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


def test_filter_by_confidence_score(app, quality_audit_job):
    payload = {"filters": {"question": {"name": "taxonomy_qa", "values": []}}}
    app.navigation.refresh_page()

    all_units = _ipa.search_unit_for_audit(TEST_DATA, payload).json_response['units']
    expected_confidence_scores = [confidence_score['fields'][0]['confidence'] for confidence_score in all_units]

    count_confidence_less_fifty = len([i for i in expected_confidence_scores if i < 0.5])

    app.job.ipa.filter_confidence_score(0, 50)
    app.job.ipa.apply_filters()
    audited_unit_on_page = app.job.ipa.get_all_units_on_page()
    assert len(audited_unit_on_page) == count_confidence_less_fifty, "Count of units on page after filtering by " \
                                                                     "confidence INCORRECT "


def test_side_bar_information_taxonomy_qa(app, quality_audit_job):
    payload = {"filters": {"question": {"name": "taxonomy_qa", "values": []}}}
    app.navigation.refresh_page()
    side_bar_info = app.job.ipa.get_side_bar_information_finalized_units()
    actual_raw_audit = side_bar_info[0]['audited']
    actual_job_accuracy = side_bar_info[0]['job_accuracy']
    expected_raw_audited = _ipa.post_job_and_field_accuracy(TEST_DATA, payload).json_response['job']['audited']
    expected_job_accuracy = _ipa.post_job_and_field_accuracy(TEST_DATA, payload).json_response['job']['accuracy']
    if (expected_job_accuracy * 100) % 5 == 0:
        assert "{:.0%}".format(expected_job_accuracy) == actual_job_accuracy
    else:
        assert "{:.2%}".format(expected_job_accuracy) == actual_job_accuracy
    assert int(
        actual_raw_audit) == expected_raw_audited, f"The total of units on Grid View {expected_raw_audited} not the same as on side bar {actual_raw_audit} "


def test_filter_by_answer_taxonomy_qa(app, quality_audit_job):
    app.navigation.refresh_page()
    app.job.ipa.customize_question()
    app.job.ipa.filter_by_label([0, 3])
    all_units_after_filter = app.job.ipa.get_all_units_on_page()
    filtered_units_on_page = app.job.ipa.get_side_bar_unit_information(
        ['Filtered Units', 'Audited', 'Filtered Job Accuracy'])
    assert len(all_units_after_filter) == int(filtered_units_on_page[0][
                                                  'filtered units']), f"The total of units on Grid View {all_units_after_filter} not the same as on side bar {filtered_units_on_page} after filtering by answer "
