from adap.api_automation.services_config.make import Make
from adap.api_automation.services_config.ontology_management import OntologyManagement
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.in_platform_audit import IPA_API

pytestmark = pytest.mark.regression_ipa

TEST_DATA = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('image_annotation', "")
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
    return [cml_tags, ontology.json_response]


def test_units_image_annotation_ipa(app, ipa_job):
    builder = Builder(API_KEY, env=pytest.env)
    resp = builder.get_json_job_status(TEST_DATA)

    actual_num_units = resp.json_response['units_count']
    actual_label_name = ipa_job[0][0]["label"]

    expected_num_units = app.job.ipa.get_all_units_on_page()

    assert len(expected_num_units) == actual_num_units
    assert expected_num_units[0]['data'] == actual_label_name
    assert expected_num_units[0]['answer'] == 3


def test_customize_question_image_annotation_ipa(app, ipa_job):
    app.navigation.refresh_page()
    question_name = ipa_job[0][0]["label"]
    all_ontology = len(ipa_job[1])

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


def test_view_details_image_annotation_ipa(app, ipa_job):
    app.navigation.refresh_page()
    all_ontology = len(ipa_job[1])
    type_of_question = ipa_job[0][0]['type']
    first_unit = app.job.ipa.get_all_units_on_page()[0]['unit_id']
    app.job.ipa.view_details_by_unit_id(first_unit)
    assert app.job.ipa.get_number_of_question_in_view_details(type_of_question) == len(ipa_job[0]), "The number of " \
                                                                                                    "question not the " \
                                                                                                    "same as in Job "

    assert app.job.ipa.get_label_of_question_view_details("Question 1") == "Shape with no ontology", "The label of " \
                                                                                                     "Image " \
                                                                                                     "annotation " \
                                                                                                     "different or absent "

    app.verification.wait_untill_text_present_on_the_page("Sweets", 30)

    assert app.job.ipa.get_number_of_ontology_view_details() == all_ontology, "On Details View the number of ontology " \
                                                                              "incorrect "

    list_of_judgment = app.job.ipa.open_judgment_dropdown("aggregated")
    assert list_of_judgment[0].text == "aggregated", "The Judgment List doesn't rendered on Details View"

    app.job.ipa.close_view_details()


def test_approve_question_image_annotation_ipa(app, ipa_job):
    app.navigation.refresh_page()
    approve_unit = app.job.ipa.get_all_units_on_page()[0]['unit_id']
    app.job.ipa.view_details_by_unit_id(approve_unit)
    app.job.ipa.approve_question()
    app.job.ipa.close_view_details()
    correct = \
    _ipa.get_audit_info_for_unit(TEST_DATA, approve_unit).json_response['fields']['shape_without_ontology']['audit'][
        'correct']
    assert app.job.ipa.get_all_units_on_page()[0]['audited']
    assert correct


def test_reject_question_image_annotation_ipa(app, ipa_job):
    app.navigation.refresh_page()
    reject_unit = app.job.ipa.get_all_units_on_page()[0]['unit_id']
    app.job.ipa.view_details_by_unit_id(reject_unit)
    app.job.ipa.reject_question()
    app.job.ipa.edit_reason()
    app.job.ipa.mark_all_that_apply()
    app.job.ipa.close_view_details()
    audit = _ipa.get_audit_info_for_unit(TEST_DATA, reject_unit).json_response['fields']['shape_without_ontology'][
        'audit']
    correct = audit['correct']
    fixed_reason = audit['fixed_reasons'][0]
    assert app.job.ipa.get_all_units_on_page()[0]['audited']
    assert not correct, "The question doesn't marked as incorrect"
    assert fixed_reason == 'Too many annotations'

    app.job.ipa.view_details_by_unit_id(reject_unit)
    app.job.ipa.edit_reason()
    app.job.ipa.mark_all_that_apply()
    app.job.ipa.close_view_details()


def test_add_reason_image_annotation_ipa(app, ipa_job):
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


def test_filter_by_audit_unaudited(app, ipa_job):
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


def test_filter_by_label(app, ipa_job):
    app.navigation.refresh_page()
    app.job.ipa.customize_question()
    app.job.ipa.filter_by_label([2, 4])
    audited_unit_on_page = app.job.ipa.get_all_units_on_page()
    assert len(audited_unit_on_page) == 4


def test_side_bar_information(app, ipa_job):
    payload = {"filters": {"question": {"name": "shape_without_ontology", "values": []}}}
    app.navigation.refresh_page()
    side_bar_info = app.job.ipa.get_side_bar_information_finalized_units()
    actual_raw_audit = side_bar_info[0]['audited']
    actual_job_accuracy = side_bar_info[0]['job_accuracy']
    expected_raw_audited = _ipa.post_job_and_field_accuracy(TEST_DATA, payload).json_response['job']['audited']
    expected_job_accuracy = _ipa.post_job_and_field_accuracy(TEST_DATA, payload).json_response['job']['accuracy']
    assert str(
        expected_raw_audited) == actual_raw_audit, f"The raws audited on UI {actual_raw_audit} render incorrect count"
    assert "{:.0%}".format(expected_job_accuracy) == actual_job_accuracy


def test_edit_image_annotation_qa(app, ipa_job):

    ontology_names = [i['class_name'] for i in ipa_job[1]]
    edit_unit = app.job.ipa.get_all_units_on_page()[7]['unit_id']
    # update data to initial state
    payload = {"fields": {
        "shape_without_ontology": {"correct": True, "answers": [], "reason": "", "custom_answers": [], "fixed_reasons": []}}}
    res = _ipa.add_audit(TEST_DATA, edit_unit, payload)
    res.assert_response_status(201)

    app.navigation.refresh_page()

    app.job.ipa.view_details_by_unit_id(edit_unit)
    app.job.ipa.reject_question()
    app.verification.wait_untill_text_present_on_the_page("aggregated", 30)
    app.job.ipa.edit_annotation_tool("Image annotation", btn_name='aggregated', index=2)

    # annotate selected judgment by new ontology class
    app.job.ipa.get_number_of_ontology_view_details()
    count_of_ann_before_edit = app.job.ipa.get_shape_annotation_count(ontology_names)
    assert count_of_ann_before_edit['Salty'] == 0, "Selected judgment should have EMPTY 'Salty' class"
    app.verification.wait_until_text_disappear_on_the_page('aggregated', 10)
    app.image_annotation.annotate_image(mode='ontology', value={"Salty": 1})

    app.job.ipa.close_view_details()
    app.job.ipa.view_details_by_unit_id(edit_unit)

    app.job.ipa.get_number_of_ontology_view_details()
    list_of_judgment = app.job.ipa.open_judgment_dropdown("audit")
    assert list_of_judgment[0].text == "audit", "The Judgment List incorrect rendered on Details View"
    count_of_ann_after_edit = app.job.ipa.get_shape_annotation_count(['Sweets', 'Fruit', 'Vegetable', 'Salty'])
    assert count_of_ann_after_edit['Salty'] == 1, "Audit judgment should have 1 'Salty' class"
