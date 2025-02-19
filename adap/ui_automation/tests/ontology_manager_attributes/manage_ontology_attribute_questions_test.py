"""
https://appen.atlassian.net/browse/QED-1982
1. create ontology attribute with different questions.
2. edit ontology attribute
3. delete ontology attribute
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

    ontology_file = get_data_file("/image_annotation/ontology_with_question.json")
    app.ontology.upload_ontology(ontology_file)
    app.verification.text_present_on_page("Classes Created")

    return job_id

@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.dependency()
def test_verify_question_from_ontology_upload(app, create_shape_job):
    app.ontology.click_edit_class('cat')
    app.ontology.ontology_attribute.click_edit_ontology_attribute()
    assert app.ontology.ontology_attribute.get_number_of_questions('Checkbox') == 1
    app.navigation.click_btn('Cancel')
    app.navigation.click_btn('Cancel')


@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.dependency(depends=["test_verify_question_from_ontology_upload"])
def test_cancel_create_question(app, create_shape_job):
    app.ontology.click_edit_class('dog')
    app.ontology.ontology_attribute.click_edit_ontology_attribute()
    assert not app.verification.link_is_disable('Done')
    assert not app.verification.link_is_disable('Cancel')
    app.ontology.ontology_attribute.select_question_type_from_dropdown('Checkbox')
    assert not app.verification.link_is_disable('Cancel')
    app.verification.link_is_disable('Done')
    app.navigation.click_btn('Cancel')
    app.navigation.click_btn('Cancel')


@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.dependency(depends=["test_cancel_create_question"])
def test_create_single_checkbox_question(app, create_shape_job):
    app.ontology.click_edit_class('dog')
    app.ontology.ontology_attribute.click_edit_ontology_attribute()
    app.ontology.ontology_attribute.select_question_type_from_dropdown('Checkbox')
    app.verification.link_is_disable('Done')
    app.ontology.ontology_attribute.manage_single_checkbox_or_textbox_question("Checkbox", "add single checkbox")
    app.navigation.click_checkbox_by_text('Defaults checked?')
    time.sleep(1)
    app.verification.checkbox_by_text_is_selected('Required')
    app.navigation.click_checkbox_by_text('Required')
    time.sleep(1)
    app.navigation.click_btn('Done')
    time.sleep(1)
    app.navigation.click_btn('Save')

    app.ontology.click_edit_class('dog')
    app.ontology.ontology_attribute.click_edit_ontology_attribute()
    assert app.ontology.ontology_attribute.get_number_of_questions('Checkbox') == 1
    app.navigation.click_btn('Cancel')
    app.navigation.click_btn('Cancel')


@pytest.mark.dependency(depends=["test_create_single_checkbox_question"])
def test_edit_single_checkbox_question(app, create_shape_job):
    app.ontology.click_edit_class('dog')
    app.ontology.ontology_attribute.click_edit_ontology_attribute()
    assert not app.verification.link_is_disable('Done')
    app.ontology.ontology_attribute.manage_single_checkbox_or_textbox_question("Checkbox", "edit single checkbox")
    app.navigation.click_checkbox_by_text('Defaults checked?')
    time.sleep(1)
    app.navigation.click_checkbox_by_text('Required')
    time.sleep(1)
    app.navigation.click_btn('Done')
    time.sleep(1)
    app.navigation.click_btn('Save')


@pytest.mark.dependency(depends=["test_edit_single_checkbox_question"])
def test_copy_single_checkbox_question(app, create_shape_job):
    app.ontology.click_edit_class('dog')
    app.ontology.ontology_attribute.click_edit_ontology_attribute()
    app.ontology.ontology_attribute.copy_question("Checkbox")
    assert app.ontology.ontology_attribute.get_number_of_questions("Checkbox") == 2
    app.navigation.click_btn('Done')
    time.sleep(1)
    app.navigation.click_btn('Save')

    app.ontology.click_edit_class('dog')
    app.ontology.ontology_attribute.click_edit_ontology_attribute()
    assert app.ontology.ontology_attribute.get_number_of_questions('Checkbox') == 2
    app.navigation.click_btn('Cancel')
    app.navigation.click_btn('Cancel')


@pytest.mark.dependency(depends=["test_copy_single_checkbox_question"])
def test_delete_single_checkbox_question(app, create_shape_job):
    app.ontology.click_edit_class('dog')
    app.ontology.ontology_attribute.click_edit_ontology_attribute()
    app.ontology.ontology_attribute.delete_question("Checkbox")
    app.ontology.ontology_attribute.delete_question("Checkbox")
    app.navigation.click_btn('Done')
    time.sleep(1)
    app.navigation.click_btn('Save')

    app.ontology.click_edit_class('dog')
    app.ontology.ontology_attribute.click_edit_ontology_attribute()
    assert app.ontology.ontology_attribute.get_number_of_questions('Checkbox') == 0
    app.navigation.click_btn('Cancel')
    app.navigation.click_btn('Cancel')


@pytest.mark.dependency(depends=["test_delete_single_checkbox_question"])
def test_create_checkbox_group_question_with_hints(app, create_shape_job):
    app.ontology.click_edit_class('dog')
    app.ontology.ontology_attribute.click_edit_ontology_attribute()
    app.ontology.ontology_attribute.select_question_type_from_dropdown('Checkbox Group')
    app.verification.link_is_disable('Done')
    app.ontology.ontology_attribute.add_checkbox_group_or_multiple_choice_or_pulldown_menu_question("Checkbox Group",
                                                                                   "add checkbox group question", "label0", "label1")
    app.verification.checkbox_by_text_is_selected('Required')
    app.navigation.click_checkbox_by_text('Required')
    time.sleep(2)
    app.ontology.ontology_attribute.add_tips_and_hints_in_additional_options("Checkbox Group", "hints", "result_header")
    app.navigation.click_btn('Done')
    time.sleep(2)
    app.navigation.click_btn('Save')

    app.ontology.click_edit_class('dog')
    app.ontology.ontology_attribute.click_edit_ontology_attribute()
    assert app.ontology.ontology_attribute.get_number_of_questions('Checkbox Group') == 1
    app.navigation.click_btn('Cancel')
    app.navigation.click_btn('Cancel')


@pytest.mark.dependency(depends=["test_create_checkbox_group_question_with_hints"])
def test_create_multiple_choice_question(app, create_shape_job):
    app.ontology.click_edit_class('dog')
    app.ontology.ontology_attribute.click_edit_ontology_attribute()
    app.ontology.ontology_attribute.select_question_type_from_dropdown('Multiple Choice')
    app.verification.link_is_disable('Done')
    app.ontology.ontology_attribute.add_checkbox_group_or_multiple_choice_or_pulldown_menu_question("Multiple Choice",
                                                                                   "add multiple choice question", "label0", "label1")
    app.navigation.click_checkbox_by_text('Required')
    time.sleep(2)
    app.navigation.click_btn('Done')
    time.sleep(2)
    app.navigation.click_btn('Save')

    app.ontology.click_edit_class('dog')
    app.ontology.ontology_attribute.click_edit_ontology_attribute()
    assert app.ontology.ontology_attribute.get_number_of_questions('Multiple Choice') == 1
    app.navigation.click_btn('Cancel')
    app.navigation.click_btn('Cancel')


@pytest.mark.dependency(depends=["test_create_multiple_choice_question"])
def test_create_pulldown_menu_question(app, create_shape_job):
    app.ontology.click_edit_class('dog')
    app.ontology.ontology_attribute.click_edit_ontology_attribute()
    app.ontology.ontology_attribute.select_question_type_from_dropdown('Pulldown Menu')
    app.verification.link_is_disable('Done')
    app.ontology.ontology_attribute.add_checkbox_group_or_multiple_choice_or_pulldown_menu_question("Pulldown Menu",
                                                                                   "add pulldown menu question", "label0", "label1")
    app.navigation.click_checkbox_by_text('Required')
    time.sleep(2)
    app.navigation.click_btn('Done')
    time.sleep(2)
    app.navigation.click_btn('Save')

    app.ontology.click_edit_class('dog')
    app.ontology.ontology_attribute.click_edit_ontology_attribute()
    assert app.ontology.ontology_attribute.get_number_of_questions('Pulldown Menu') == 1
    app.navigation.click_btn('Cancel')
    app.navigation.click_btn('Cancel')


@pytest.mark.dependency(depends=["test_create_pulldown_menu_question"])
def test_create_textbox_question(app, create_shape_job):
    app.ontology.click_edit_class('dog')
    app.ontology.ontology_attribute.click_edit_ontology_attribute()
    app.ontology.ontology_attribute.select_question_type_from_dropdown('Text Box (Single Line)')
    app.verification.link_is_disable('Done')
    app.ontology.ontology_attribute.manage_single_checkbox_or_textbox_question("Text Box (Single Line)", "add text box single line")
    app.navigation.click_checkbox_by_text('Required')
    time.sleep(2)
    app.navigation.click_btn('Done')
    time.sleep(2)
    app.navigation.click_btn('Save')

    app.ontology.click_edit_class('dog')
    app.ontology.ontology_attribute.click_edit_ontology_attribute()
    assert app.ontology.ontology_attribute.get_number_of_questions('Text Box (Single Line)') == 1
    app.navigation.click_btn('Cancel')
    app.navigation.click_btn('Cancel')


@pytest.mark.skip(reason="TBF - https://appen.atlassian.net/browse/QED-3012")
@pytest.mark.dependency(depends=["test_create_textbox_question"])
def test_data_units_page(app, create_shape_job):
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(create_shape_job)
    app.job.open_tab('Data')
    units = app.job.data.find_all_units_with_status('new')
    first_unit = units['unit id'][0]
    app.job.data.open_unit_by_id(first_unit)
    app.verification.current_url_contains("/units/%s" % first_unit)
    app.image_annotation.activate_iframe_on_unit_page()
    app.image_annotation.annotate_with_ontology_attribute(mode='ontology', value={"dog": 1}, max_annotate=5)
    assert app.annotation.ontology_attribute_annotate.ontology_attribute_show_in_sidepanel()
    app.verification.text_present_on_page('add checkbox group question')
    app.verification.text_present_on_page('add multiple choice question')
    app.verification.text_present_on_page('add pulldown menu question')
    app.verification.text_present_on_page('add text box single line')
    app.annotation.ontology_attribute_annotate.input_textbox_single_line('single line')
    app.annotation.ontology_attribute_annotate.save_ontology_attribute()
    app.verification.text_present_on_page('Required Field')
    time.sleep(2)
    app.image_annotation.deactivate_iframe()


@pytest.mark.skip(reason="TBF - https://appen.atlassian.net/browse/QED-3012")
@pytest.mark.dependency(depends=["test_data_units_page"])
def test_delete_all_questions(app, create_shape_job):
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(create_shape_job)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Annotation Ontology')
    app.ontology.click_edit_class('dog')
    app.ontology.ontology_attribute.click_edit_ontology_attribute()
    app.ontology.ontology_attribute.delete_all_questions()
    app.navigation.click_btn('Done')
    time.sleep(1)
    app.navigation.click_btn('Save')
