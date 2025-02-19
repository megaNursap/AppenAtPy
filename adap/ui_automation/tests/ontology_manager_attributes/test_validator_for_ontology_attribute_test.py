"""
https://appen.atlassian.net/browse/QED-1985
1. create ontology attribute with different questions.
2. check test validators
"""
import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.selenium_utils import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_ontology_attribute, pytest.mark.fed_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/image_annotation/catdog.csv")


@pytest.fixture(scope="module")
def create_shape_job(app):
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.image_annotation_cml,
                                        job_title="Testing ontology attribute", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Annotation Ontology')

    ontology_file = get_data_file("/image_annotation/ontology.json")
    app.ontology.upload_ontology(ontology_file)
    app.verification.text_present_on_page("Classes Created")

    app.ontology.click_edit_class('dog')
    app.ontology.ontology_attribute.click_edit_ontology_attribute()
    # single checkbox, default checked, required
    app.ontology.ontology_attribute.select_question_type_from_dropdown('Checkbox')
    app.ontology.ontology_attribute.manage_single_checkbox_or_textbox_question("Checkbox", "add single checkbox")
    app.navigation.click_checkbox_by_text('Defaults checked?')
    # checkbox group, required
    app.ontology.ontology_attribute.select_question_type_from_dropdown('Checkbox Group')
    app.ontology.ontology_attribute.add_checkbox_group_or_multiple_choice_or_pulldown_menu_question("Checkbox Group",
                                                                                                    "add checkbox group question",
                                                                                                    "label0", "label1")
    app.ontology.ontology_attribute.add_tips_and_hints_in_additional_options("Checkbox Group", "hints", "result_header")
    # multiple choice, required
    app.ontology.ontology_attribute.select_question_type_from_dropdown('Multiple Choice')
    app.ontology.ontology_attribute.add_checkbox_group_or_multiple_choice_or_pulldown_menu_question("Multiple Choice",
                                                                                                    "add multiple choice question",
                                                                                                    "label0", "label1")
    # pulldown menu, not required
    app.ontology.ontology_attribute.select_question_type_from_dropdown('Pulldown Menu')
    app.ontology.ontology_attribute.add_checkbox_group_or_multiple_choice_or_pulldown_menu_question("Pulldown Menu",
                                                                                                    "add pulldown menu question",
                                                                                                    "label0", "label1")
    app.navigation.click_checkbox_by_text('Required', index=-1)
    # text box, required
    app.ontology.ontology_attribute.select_question_type_from_dropdown('Text Box (Single Line)')
    app.ontology.ontology_attribute.manage_single_checkbox_or_textbox_question("Text Box (Single Line)",
                                                                               "add text box single line")
    app.navigation.click_checkbox_by_text('Required', index=-1)
    app.navigation.click_btn('Done')
    app.navigation.click_btn('Save')
    app.job.preview_job()
    return job_id


@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
def test_submit_without_annotation(app, create_shape_job):
    time.sleep(5)
    app.image_annotation.submit_test_validators()
    app.verification.text_present_on_page('This field is required.')
    assert app.verification.count_text_present_on_page('This field is required.') == 2


@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
def test_submit_without_save_annotation(app, create_shape_job):
    for i in range(2):
        app.image_annotation.activate_iframe_by_index(i)
        app.image_annotation.annotate_with_ontology_attribute(mode='ontology', value={"dog": 1}, max_annotate=5)
        app.image_annotation.deactivate_iframe()
    app.image_annotation.submit_test_validators()
    app.verification.text_present_on_page('Missing Answers for Ontology Attributes')
    assert app.verification.count_text_present_on_page('Missing Answers for Ontology Attributes') == 2


@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.dependency()
def test_required_fields_for_question(app, create_shape_job):
    app.image_annotation.activate_iframe_by_index(0)
    if not app.annotation.ontology_attribute_annotate.ontology_attribute_show_in_sidepanel():
        app.image_annotation.annotate_with_ontology_attribute(mode='ontology', value={"dog": 1}, max_annotate=5)
    app.verification.text_present_on_page('add single checkbox')
    app.verification.text_present_on_page('add checkbox group question')
    app.verification.text_present_on_page('add multiple choice question')
    app.verification.text_present_on_page('add pulldown menu question')
    app.verification.text_present_on_page('add text box single line')
    app.annotation.ontology_attribute_annotate.input_textbox_single_line('single line')
    app.annotation.ontology_attribute_annotate.save_ontology_attribute()
    app.verification.text_present_on_page('Required Field')
    assert app.verification.count_text_present_on_page('Required Field') == 2


@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.dependency(depends=["test_required_fields_for_question"])
def test_save_question_successfully(app, create_shape_job):
    app.annotation.ontology_attribute_annotate.select_value_for_multiple_choice('label0')
    assert app.verification.count_text_present_on_page('Required Field') == 1
    checkbox_group = ['label0', 'label1']
    app.annotation.ontology_attribute_annotate.select_value_for_checkbox_group(checkbox_group)
    assert app.verification.count_text_present_on_page('Required Field') == 0
    app.annotation.ontology_attribute_annotate.save_ontology_attribute()
    app.verification.text_present_on_page('Changes saved')
    app.image_annotation.deactivate_iframe()
