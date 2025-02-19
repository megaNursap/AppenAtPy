from adap.api_automation.services_config.make import Make
from adap.api_automation.services_config.ontology_management import OntologyManagement
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.in_platform_audit import IPA_API

pytestmark = pytest.mark.regression_ipa

TEST_DATA = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('image_segmentation', "")
USER_EMAIL = get_user_email('test_account')
PASSWORD = get_user_password('test_account')
API_KEY = get_user_api_key('test_account')
_ipa = IPA_API(API_KEY)


@pytest.fixture(scope="module")
def qa_job(app):
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
    return [cml_tags, ontology.json_response]


def test_edit_image_segmentation_qa(app, qa_job):

    ontology_names = [i['class_name'] for i in qa_job[1]]
    edit_unit = app.job.ipa.get_all_units_on_page()[2]['unit_id']

    # update data to initial state
    payload = {"fields": {
        "annotation": {"correct": True, "answers": [], "reason": "", "custom_answers": [], "fixed_reasons": []}}}
    res = _ipa.add_audit(TEST_DATA, edit_unit, payload)
    res.assert_response_status(201)

    app.navigation.refresh_page()

    judgment = _ipa.get_all_judgment(TEST_DATA, edit_unit).json_response['judgments'][0]['id']

    app.job.ipa.view_details_by_unit_id(edit_unit)
    app.job.ipa.reject_question()
    app.job.ipa.get_number_of_ontology_view_details()
    app.verification.wait_untill_text_present_on_the_page(judgment, 30)
    list_of_judgment = app.job.ipa.open_judgment_dropdown(f'{judgment}')
    assert "audit" not in list_of_judgment, "The Judgment List should not contain audit judgment"
    app.job.ipa.select_judgment_from_drop_down()
    app.job.ipa.edit_annotation_tool("Image segmentation", btn_name=f'{judgment}', index=1)

    # annotate selected judgment by new ontology class
    app.job.ipa.get_number_of_ontology_view_details()
    app.verification.wait_until_text_disappear_on_the_page(judgment, 10)
    app.navigation.click_bytext(ontology_names[5])
    app.plss.full_screen()
    app.plss.single_hotkey('f')
    app.plss.fill_image(300, 300)
    app.plss.full_screen()

    app.job.ipa.close_view_details()
    app.job.ipa.view_details_by_unit_id(edit_unit)

    app.job.ipa.get_number_of_ontology_view_details()
    list_of_judgment = app.job.ipa.open_judgment_dropdown("audit")
    assert list_of_judgment[0].text == "audit", "The Judgment List incorrect rendered on Details View"
