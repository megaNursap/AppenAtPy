"""
https://appen.atlassian.net/browse/QED-2588 error panel for video annotation oa job
https://appen.atlassian.net/browse/QED-2589 delete,hidden frame count
"""
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.api_automation.services_config.builder import Builder as JobAPI
import time
from adap.e2e_automation.services_config.job_api_support import generate_job_link

pytestmark = [pytest.mark.regression_video_annotation, pytest.mark.skipif(pytest.env != "integration", reason="Only integration enabled feature")]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/video_annotation/video.csv")


@pytest.fixture(scope="module")
def create_job_for_videoanno(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.video_annotation_object_tracking_cml,
                                        job_title="Testing ontology attribute for video annotation", units_per_page=5)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Video Shapes Ontology')
    ontology_file = get_data_file("/video_annotation/nested_ontology.json")
    app.ontology.upload_ontology(ontology_file)

    app.ontology.expand_nested_ontology_by_name("Nest1")
    app.ontology.expand_nested_ontology_by_name("Nest2")
    app.ontology.expand_nested_ontology_by_name("Nest3")
    app.ontology.search_class_by_name("Nest4", found=True)

    app.ontology.click_edit_class('Nest4')

    # app.navigation.click_link('Ontology Attributes')
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
    # pulldown menu, required
    app.ontology.ontology_attribute.select_question_type_from_dropdown('Pulldown Menu')
    app.ontology.ontology_attribute.add_checkbox_group_or_multiple_choice_or_pulldown_menu_question("Pulldown Menu",
                                                                                                    "add pulldown menu question",
                                                                                                    "label0", "label1")
    # text box, required
    app.ontology.ontology_attribute.select_question_type_from_dropdown('Text Box (Single Line)')
    app.ontology.ontology_attribute.manage_single_checkbox_or_textbox_question("Text Box (Single Line)",
                                                                               "add text box single line")
    app.navigation.click_checkbox_by_text('Required', index=-1)
    app.navigation.click_btn('Done')
    app.navigation.click_btn('Save')

    # launch job
    app.job.open_action("Settings")
    if pytest.env == 'fed':
        app.navigation.click_link("Select Contributor Channels")
        app.job.select_hosted_channel_by_index(save=True)
    else:
        external_chkbox = app.driver.find_elements('xpath',"//label[contains(text(),'External')]")
        general_opt = app.driver.find_elements('xpath',"//span[contains(text(),'General')]")
        if len(general_opt) == 0:
            assert len(external_chkbox) > 0, "Checkbox 'External' not found"
            external_chkbox[0].click()
            app.navigation.click_link('Save')

    app.job.open_tab('LAUNCH')
    app.navigation.click_link("Launch Job")

    job = JobAPI(API_KEY, job_id=job_id)

    job.wait_until_status('running', 120)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    return job_id


@allure.issue("https://appen.atlassian.net/browse/AT-5619", "BUG  on Integration  AT-5619")
# @allure.issue("https://appen.atlassian.net/browse/AT-5623", "BUG  on Integration  AT-5623")
@pytest.mark.dependency()
def test_error_panel(app, create_job_for_videoanno):
    job_link = generate_job_link(create_job_for_videoanno, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.close_guide()
    time.sleep(2)

    app.video_annotation.activate_iframe_by_index(0)
    app.video_annotation.click_error_log_panel()
    assert app.video_annotation.get_error_log_items() == 0
    app.video_annotation.click_error_log_panel()
    app.video_annotation.annotate_frame(mode='ontology', value={"Nest4": 1}, annotate_shape='box')
    app.video_annotation.click_x_go_back_to_panel()
    app.video_annotation.click_error_log_panel()
    assert app.video_annotation.get_error_log_items() == 1
    assert app.video_annotation.get_error_log_item_title() == 'Nest4 1'
    assert app.video_annotation.get_error_log_item_frame() == 'Check frames 1 to 25'
    assert app.video_annotation.get_error_log_item_footer() == 'Start fixing'
    app.video_annotation.click_error_log_panel()


@allure.issue("https://appen.atlassian.net/browse/AT-5619", "BUG  on Integration  AT-5619")
# @allure.issue("https://appen.atlassian.net/browse/AT-5623", "BUG  on Integration  AT-5623")
@pytest.mark.dependency(depends=["test_error_panel"])
def test_error_icon_and_eclipse(app, create_job_for_videoanno):
    app.video_annotation.click_classes_or_objects_tab('OBJECTS')
    app.video_annotation.error_icon_is_displayed(item_name='Nest4 1', displayed=True)
    app.video_annotation.eclipse_is_displayed(item_name='Nest4 1', displayed=True)
    app.video_annotation.next_frame()
    app.video_annotation.error_icon_is_displayed(item_name='Nest4 1', displayed=True)
    app.video_annotation.next_frame()
    app.video_annotation.error_icon_is_displayed(item_name='Nest4 1', displayed=True)


@allure.issue("https://appen.atlassian.net/browse/AT-5619", "BUG  on Integration  AT-5619")
# @allure.issue("https://appen.atlassian.net/browse/AT-5623", "BUG  on Integration  AT-5623")
@pytest.mark.dependency(depends=["test_error_icon_and_eclipse"])
def test_fill_attributes_and_save(app, create_job_for_videoanno):
    app.video_annotation.previous_frame()
    app.video_annotation.previous_frame()
    app.video_annotation.click_ontology_item('Nest4 1')
    checkbox_group = ['label0', 'label1']
    app.annotation.ontology_attribute_annotate.select_value_for_checkbox_group(checkbox_group)
    app.annotation.ontology_attribute_annotate.save_ontology_attribute()
    app.verification.text_present_on_page('Required Field')
    assert app.verification.count_text_present_on_page('Required Field') == 3
    app.annotation.ontology_attribute_annotate.select_value_for_multiple_choice('label0')
    assert app.verification.count_text_present_on_page('Required Field') == 2
    app.annotation.ontology_attribute_annotate.select_value_for_pulldown_menu()
    assert app.verification.count_text_present_on_page('Required Field') == 1
    app.annotation.ontology_attribute_annotate.input_textbox_single_line('single line')
    assert app.verification.count_text_present_on_page('Required Field') == 0
    app.annotation.ontology_attribute_annotate.save_ontology_attribute()
    app.verification.text_present_on_page('Changes saved')
    app.video_annotation.deactivate_iframe()


@allure.issue("https://appen.atlassian.net/browse/AT-5619", "BUG  on Integration  AT-5619")
# @allure.issue("https://appen.atlassian.net/browse/AT-5623", "BUG  on Integration  AT-5623")
def test_mark_as_hidden_on_form_panel(app, create_job_for_videoanno):
    app.video_annotation.activate_iframe_by_index(1)
    app.video_annotation.annotate_frame(mode='ontology', value={"Nest4": 1}, annotate_shape='box')
    assert app.video_annotation.get_frame_info_on_form_panel() == 'FRAME 1'
    app.video_annotation.next_frame()
    assert app.video_annotation.get_frame_info_on_form_panel() == 'FRAME 2'
    app.video_annotation.previous_frame()
    assert app.video_annotation.get_frame_info_on_form_panel() == 'FRAME 1'
    app.video_annotation.click_eclipse_menu_on_form_panel_to_delete_or_hidden_object(item_name='Nest4 1', hidden=True)
    app.video_annotation.object_is_hidden()
    app.video_annotation.click_eclipse_menu_on_form_panel_to_delete_or_hidden_object(item_name='Nest4 1', visible=True)
    app.video_annotation.object_is_hidden(is_not=False)


@allure.issue("https://appen.atlassian.net/browse/AT-5619", "BUG  on Integration  AT-5619")
# @allure.issue("https://appen.atlassian.net/browse/AT-5623", "BUG  on Integration  AT-5623")
def test_delete_from_all_frames_on_form_panel(app, create_job_for_videoanno):
    app.video_annotation.click_eclipse_menu_on_form_panel_to_delete_or_hidden_object(item_name='Nest4 1', delete=True)
    app.video_annotation.click_classes_or_objects_tab('OBJECTS')
    assert app.video_annotation.no_object_yet() == 'NO OBJECTS YET'
    app.video_annotation.click_classes_or_objects_tab('CLASSES')
    app.video_annotation.deactivate_iframe()


@allure.issue("https://appen.atlassian.net/browse/AT-5619", "BUG  on Integration  AT-5619")
# @allure.issue("https://appen.atlassian.net/browse/AT-5623", "BUG  on Integration  AT-5623")
def test_mark_as_hidden_and_delete_on_objects_tab(app, create_job_for_videoanno):
    app.video_annotation.activate_iframe_by_index(2)
    app.video_annotation.annotate_frame(mode='ontology', value={"Nest4": 1}, annotate_shape='box')
    app.video_annotation.click_x_go_back_to_panel()
    app.video_annotation.click_classes_or_objects_tab('OBJECTS')
    assert app.video_annotation.get_frame_info_on_object_panel() == 'FRAME 1'
    app.video_annotation.next_frame()
    assert app.video_annotation.get_frame_info_on_object_panel() == 'FRAME 2'
    app.video_annotation.previous_frame()
    assert app.video_annotation.get_frame_info_on_object_panel() == 'FRAME 1'
    app.video_annotation.click_eclipse_menu_on_object_panel_to_delete_or_hidden_object(item_name='Nest4 1', hidden=True)
    app.video_annotation.click_classes_or_objects_tab('OBJECTS')
    app.video_annotation.click_eclipse_menu_on_object_panel_to_delete_or_hidden_object(item_name='Nest4 1', visible=True)
    app.video_annotation.click_classes_or_objects_tab('OBJECTS')
    app.video_annotation.click_eclipse_menu_on_object_panel_to_delete_or_hidden_object(item_name='Nest4 1', delete=True)
    app.video_annotation.click_classes_or_objects_tab('OBJECTS')
    assert app.video_annotation.no_object_yet() == 'NO OBJECTS YET'
    app.video_annotation.deactivate_iframe()