"""
https://appen.atlassian.net/browse/QED-2021
This test covers:
1. create peer review job
2. test validator peer review job
"""
import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.annotation import create_peer_review_job
from adap.data import annotation_tools_cml as data

mark_only_sandbox = pytest.mark.skipif(not pytest.running_in_preprod_sandbox, reason="Only sandbox and staging has predefined job")
pytestmark = [pytest.mark.regression_ontology_attribute,  mark_only_sandbox]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
URL_PREDEFINED_JOB_ID = pytest.data.predefined_data['ontology_attribute_output'].get(pytest.env)['url_output']
JSON_PREDEFINED_JOB_ID = pytest.data.predefined_data['ontology_attribute_output'].get(pytest.env)['json_output']


def test_peer_review_for_json_and_url_output_job(tmpdir_factory, app):
    for predefine_job in [URL_PREDEFINED_JOB_ID, JSON_PREDEFINED_JOB_ID]:
        tmpdir = tmpdir_factory.mktemp('data')
        job_id = create_peer_review_job(tmpdir, API_KEY, predefine_job, data.image_annotation_peer_review_cml)
        app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
        app.mainMenu.jobs_page()
        app.job.open_job_with_id(job_id)

        app.job.open_tab('Design')
        app.navigation.click_link('Manage Image Annotation Ontology')

        # TODO Code can be removed after fix AT-4766
        if predefine_job == URL_PREDEFINED_JOB_ID:
            ontology_file = get_data_file("/image_annotation/1592701_peer_review_OA.json")
        else:
            ontology_file = get_data_file("/image_annotation/1592702_peer_review_OA.json")

        # TODO Code will be reused after fix AT-4766
        # ontology_file = get_data_file("/image_annotation/ontology.json")
        app.ontology.upload_ontology(ontology_file)
        app.verification.text_present_on_page("Classes Created")

        # TODO Code will be reused after fix AT-4766
        # app.ontology.click_edit_class('dog')
        # app.ontology.ontology_attribute.click_edit_ontology_attribute()
        # single checkbox, default checked, required
        # app.ontology.ontology_attribute.select_question_type_from_dropdown('Checkbox')
        # app.ontology.ontology_attribute.manage_single_checkbox_or_textbox_question("Checkbox", "add single checkbox")
        # app.navigation.click_checkbox_by_text('Defaults checked?')
        # checkbox group, required

        # app.ontology.ontology_attribute.select_question_type_from_dropdown('Checkbox Group')
        # app.ontology.ontology_attribute.add_checkbox_group_or_multiple_choice_or_pulldown_menu_question("Checkbox Group",
        #                                                                                                 "add checkbox group question",
        #                                                                                                 "label0", "label1")
        # app.ontology.ontology_attribute.add_option("Checkbox Group", "more label", "more value")
        # app.ontology.ontology_attribute.add_tips_and_hints_in_additional_options("Checkbox Group", "hints", "result_header")
        # # multiple choice, required
        # app.ontology.ontology_attribute.select_question_type_from_dropdown('Multiple Choice')
        # app.ontology.ontology_attribute.add_checkbox_group_or_multiple_choice_or_pulldown_menu_question("Multiple Choice",
        #                                                                                                 "add multiple choice question",
        #                                                                                                 "label0", "label1")
        # # pulldown menu, required
        # app.ontology.ontology_attribute.select_question_type_from_dropdown('Pulldown Menu')
        # app.ontology.ontology_attribute.add_checkbox_group_or_multiple_choice_or_pulldown_menu_question("Pulldown Menu",
        #                                                                                                 "add pulldown menu question",
        #                                                                                                 "label0", "label1")
        # # text box, required
        # app.ontology.ontology_attribute.select_question_type_from_dropdown('Text Box (Single Line)')
        # app.ontology.ontology_attribute.manage_single_checkbox_or_textbox_question("Text Box (Single Line)",
        #                                                                            "add text box single line")
        # app.navigation.click_checkbox_by_text('Required', index=-1)
        # app.navigation.click_btn('Done')
        # app.navigation.click_btn('Save')

        # app.ontology.ontology_attribute.select_question_type_from_dropdown('Checkbox Group')
        # app.ontology.ontology_attribute.add_checkbox_group_or_multiple_choice_or_pulldown_menu_question("Checkbox Group",
        #                                                                                                 "add checkbox group question",
        #                                                                                                 "label0", "label1")
        #
        # app.ontology.ontology_attribute.add_option("Checkbox Group", "more label", "more value")
        # app.ontology.ontology_attribute.add_tips_and_hints_in_additional_options("Checkbox Group", "hints", "result_header")
        # # multiple choice, required
        # app.ontology.ontology_attribute.select_question_type_from_dropdown('Multiple Choice')
        # app.ontology.ontology_attribute.add_checkbox_group_or_multiple_choice_or_pulldown_menu_question("Multiple Choice",
        #                                                                                                 "add multiple choice question",
        #                                                                                                 "label0", "label1")
        # # pulldown menu, required
        # app.ontology.ontology_attribute.select_question_type_from_dropdown('Pulldown Menu')
        # app.ontology.ontology_attribute.add_checkbox_group_or_multiple_choice_or_pulldown_menu_question("Pulldown Menu",
        #                                                                                                 "add pulldown menu question",
        #                                                                                                 "label0", "label1")
        # # text box, required
        # app.ontology.ontology_attribute.select_question_type_from_dropdown('Text Box (Single Line)')
        # app.ontology.ontology_attribute.manage_single_checkbox_or_textbox_question("Text Box (Single Line)",
        #                                                                            "add text box single line")
        # app.navigation.click_checkbox_by_text('Required', index=-1)
        # app.navigation.click_btn('Done')
        # app.navigation.click_btn('Save')

        job_window = app.driver.window_handles[0]
        app.job.preview_job()
        time.sleep(8)
        app.image_annotation.submit_test_validators()
        app.verification.text_present_on_page('Validation succeeded')

        app.image_annotation.activate_iframe_by_index(0)
        app.image_annotation.go_to_object_panel()
        app.verification.text_present_on_page('add single checkbox')
        app.verification.text_present_on_page('add checkbox group question')
        app.verification.text_present_on_page('add multiple choice question')
        app.verification.text_present_on_page('add pulldown menu question')
        app.verification.text_present_on_page('add text box single line')

        checkbox_group = ['label0', 'label1']
        app.annotation.ontology_attribute_annotate.select_value_for_checkbox_group(checkbox_group)
        app.annotation.ontology_attribute_annotate.save_ontology_attribute()
        app.verification.text_present_on_page('Required Field')
        assert app.verification.count_text_present_on_page('Required Field') == 1
        app.annotation.ontology_attribute_annotate.select_value_for_checkbox_group(checkbox_group)
        app.annotation.ontology_attribute_annotate.save_ontology_attribute()
        app.verification.text_present_on_page('Changes saved')
        app.image_annotation.deactivate_iframe()
        app.image_annotation.submit_test_validators()
        app.verification.text_present_on_page('Validation succeeded')

        app.driver.close()
        app.navigation.switch_to_window(job_window)
        app.user.logout()