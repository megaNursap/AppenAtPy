from adap.api_automation.services_config.make import Make
from adap.api_automation.services_config.ontology_management import OntologyManagement
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.in_platform_audit import IPA_API
from adap.ui_automation.utils.selenium_utils import modify_text

pytestmark = pytest.mark.regression_ipa

TEST_DATA = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('text_annotation', "")
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

    ontology = OntologyManagement().get_json_ontology_report(TEST_DATA, API_KEY)
    all_ontology = len(ontology.json_response)
    return [cml_tags, all_ontology]


def test_units_text_annotation_ipa(app, ipa_job):
    builder = Builder(API_KEY, env=pytest.env)
    resp = builder.get_json_job_status(TEST_DATA)

    actual_num_units = resp.json_response['units_count']
    actual_label_name = ipa_job[0][0]["label"]

    expected_num_units = app.job.ipa.get_all_units_on_page()

    assert len(expected_num_units) == actual_num_units
    assert expected_num_units[0]['data'] == actual_label_name
    assert expected_num_units[0]['answer'] == 3


def test_customize_question_text_annotation_ipa(app, ipa_job):
    app.navigation.refresh_page()
    question_name = ipa_job[0][0]["label"]
    all_ontology = ipa_job[1]

    all_units = app.job.ipa.get_all_units_on_page()
    question_on_detailed_view = all_units[0]['data']
    app.job.ipa.customize_question()
    question_in_customize_question = app.job.ipa.get_question_by_index()
    assert question_in_customize_question == question_on_detailed_view, "The name of chosen question different"

    assert all_ontology == app.job.ipa.get_number_of_answer_in_customize_question(), "The selected answers of " \
                                                                                     "question not displayed in " \
                                                                                     "customize question {} "

    question_on_detailed_view = app.job.ipa.get_all_units_on_page()[0]['data']
    assert question_name == question_on_detailed_view, 'The name of set question different from ' \
                                                       'question displayed on detailed view '


def test_view_details_text_annotation_ipa(app, ipa_job):
    app.navigation.refresh_page()
    type_of_question = ipa_job[0][0]['type']
    type_que = modify_text(type_of_question, "[A-Z][a-z]*")
    all_ontology = ipa_job[1]
    first_unit = app.job.ipa.get_all_units_on_page()[0]['unit_id']
    app.job.ipa.view_details_by_unit_id(first_unit)
    assert app.job.ipa.get_number_of_question_in_view_details(type_que) == len(ipa_job[0]), "The number of " \
                                                                                            "question not the " \
                                                                                            "same as in Job "

    assert app.job.ipa.get_label_of_question_view_details("Question 1") == "Label Text", "The label of " \
                                                                                         "Image " \
                                                                                         "annotation " \
                                                                                         "different or absent "

    app.verification.wait_untill_text_present_on_the_page("Aggregation", 30)

    assert app.job.ipa.get_number_of_ontology_view_details() == all_ontology, "On Details View shouldn't display ontology for " \
                                                                              "text annotation "

    list_of_judgment = app.job.ipa.open_judgment_dropdown("Aggregation")
    assert list_of_judgment[0].text == "Aggregation", "The Judgment List incorrect rendered on Details View"

    app.job.ipa.close_view_details()


def test_approve_question_text_annotation_ipa(app, ipa_job):
    app.navigation.refresh_page()
    approve_unit = app.job.ipa.get_all_units_on_page()[0]['unit_id']
    app.job.ipa.view_details_by_unit_id(approve_unit)
    app.job.ipa.approve_question()
    app.job.ipa.close_view_details()
    correct = \
        _ipa.get_audit_info_for_unit(TEST_DATA, approve_unit).json_response['fields']['source_data']['audit'][
            'correct']
    assert app.job.ipa.get_all_units_on_page()[0]['audited']
    assert correct


def test_reject_question_text_annotation_ipa(app, ipa_job):
    app.navigation.refresh_page()
    reject_unit = app.job.ipa.get_all_units_on_page()[0]['unit_id']
    app.job.ipa.view_details_by_unit_id(reject_unit)
    app.job.ipa.reject_question()
    app.job.ipa.close_view_details()
    audit = _ipa.get_audit_info_for_unit(TEST_DATA, reject_unit).json_response['fields']['source_data'][
        'audit']
    correct = audit['correct']
    assert app.job.ipa.get_all_units_on_page()[0]['audited']
    assert not correct, "The question doesn't marked as incorrect"


def test_add_reason_text_annotation_ipa(app, ipa_job):
    app.navigation.refresh_page()
    reject_unit = app.job.ipa.get_all_units_on_page()[1]['unit_id']
    app.job.ipa.view_details_by_unit_id(reject_unit)
    app.job.ipa.reject_question()
    app.job.ipa.add_reason("This question rejected")
    app.job.ipa.mark_all_that_apply('Incorrect spans', 'source_data')

    app.job.ipa.close_view_details()

    audit = _ipa.get_audit_info_for_unit(TEST_DATA, reject_unit).json_response['fields']['source_data'][
        'audit']
    fixed_reason = audit['fixed_reasons'][0]
    assert fixed_reason == 'Incorrect spans'

    app.job.ipa.view_details_by_unit_id(reject_unit)
    app.job.ipa.reject_question()
    app.job.ipa.edit_reason()

    app.verification.text_present_on_page("This question rejected")
    app.job.ipa.clear_reason()
    app.job.ipa.mark_all_that_apply('Incorrect spans', 'source_data')
    app.job.ipa.approve_question()
    app.job.ipa.close_view_details()


def test_filter_by_audit_unaudited_text_annotation_ipa(app, ipa_job):
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


def test_filter_by_label_text_annotation_ipa(app, ipa_job):
    app.navigation.refresh_page()
    app.job.ipa.customize_question()
    app.job.ipa.filter_by_label([0, 3])
    audited_unit_on_page = app.job.ipa.get_all_units_on_page()
    assert len(audited_unit_on_page) == 2


def test_side_bar_information_text_annotation_ipa(app, ipa_job):
    payload = {"filters": {"question": {"name": "source_data", "values": []}}}
    app.navigation.refresh_page()
    side_bar_info = app.job.ipa.get_side_bar_information_finalized_units()
    actual_raw_audit = side_bar_info[0]['audited']
    actual_job_accuracy = side_bar_info[0]['job_accuracy']
    actual_total_of_units = side_bar_info[0]['total of units']
    expected_raw_audited = _ipa.post_job_and_field_accuracy(TEST_DATA, payload).json_response['job']['audited']
    expected_job_accuracy = _ipa.post_job_and_field_accuracy(TEST_DATA, payload).json_response['job']['accuracy']
    expected_total_of_units = _ipa.post_job_and_field_accuracy(TEST_DATA, payload).json_response['job']['units']
    assert str(
        expected_raw_audited) == actual_raw_audit, f"The raws audited on UI {actual_raw_audit} render incorrect count"
    if (expected_job_accuracy * 100) % 5 == 0:
        assert "{:.0%}".format(expected_job_accuracy) == actual_job_accuracy
    else:
        assert "{:.2%}".format(expected_job_accuracy) == actual_job_accuracy
    assert int(
        actual_total_of_units) == expected_total_of_units, f"The total of units on Grid View {expected_total_of_units} not the same as on side bar {actual_total_of_units} "


def test_edit_text_annotation_qa(app, ipa_job):
    edit_unit = app.job.ipa.get_all_units_on_page()[3]['unit_id']
    # update data to initial state
    payload = {"fields": {
        "source_data": {"correct": True, "answers": [], "reason": "", "custom_answers": [], "fixed_reasons": []}}}
    res = _ipa.add_audit(TEST_DATA, edit_unit, payload)
    res.assert_response_status(201)

    app.navigation.refresh_page()

    app.job.ipa.view_details_by_unit_id(edit_unit)
    app.job.ipa.reject_question()
    app.verification.wait_untill_text_present_on_the_page("Aggregation", 30)
    app.job.ipa.edit_annotation_tool("Text annotation", btn_name='Aggregation', index=1)

    # annotate selected judgment by new span
    app.job.ipa.get_number_of_ontology_view_details()
    app.verification.wait_until_text_disappear_on_the_page('Aggregation', 10)
    app.text_annotation.click_token('Italian')
    app.text_annotation.click_span('City')

    app.job.ipa.close_view_details()
    app.job.ipa.view_details_by_unit_id(edit_unit)

    app.job.ipa.edit_annotation_tool("Text annotation", btn_name='audit', index=1)
    app.job.ipa.get_number_of_ontology_view_details()
    new_span = app.text_annotation.get_word_count_with_label('City', 'Italian')
    assert new_span == 1, "The incorrect number of span in edited text"





