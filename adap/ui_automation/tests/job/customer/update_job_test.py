import pytest
import time
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.api_automation.utils.data_util import *

pytestmark = [
    pytest.mark.regression_core,
    pytest.mark.adap_ui_uat,
    pytest.mark.adap_uat
]


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.fed_ui
def test_update_title_and_instructions(app_test):
    """
    Customer is able to update Title and Instructions
    """
    api_key = get_user_api_key('test_ui_account')
    email = get_user_email('test_ui_account')
    password = get_user_password('test_ui_account')

    resp = JobAPI(api_key).create_job()
    job_id = resp.json_response['id']
    assert resp.status_code == 200, "Job was not created!"

    app_test.user.login_as_customer(user_name=email, password=password)

    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(job_id)

    app_test.job.open_tab("DESIGN")
    time.sleep(4)

    app_test.job.design.update_job_title("Updated Title")
    app_test.navigation.click_btn(btn_name="Save")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Job saved successfully.", max_time=10
    )

    app_test.job.design.update_job_instructions("test: Instructions updated", section='Overview', mode='add')
    app_test.job.design.update_job_instructions("test: Step 1", section='Steps', mode='add')
    time.sleep(4)
    app_test.navigation.click_btn("Save")
    time.sleep(4)
    app_test.navigation.refresh_page()

    app_test.job.design.verify_job_title("Updated Title")
    # TODO verify that text present in specific section
    app_test.verification.text_present_on_page("test: Instructions updated")
    app_test.verification.text_present_on_page("test: Step 1")


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.fed_ui
def test_update_job_design_with_ge(app_test):
    """
        Customer is able to update the job design with the GE
    """
    api_key = get_user_api_key('test_ui_account')
    email = get_user_email('test_ui_account')
    password = get_user_password('test_ui_account')

    resp = JobAPI(api_key).create_job()
    job_id = resp.json_response['id']
    assert resp.status_code == 200, "Job was not created!"

    app_test.user.login_as_customer(user_name=email, password=password)

    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(job_id)

    app_test.job.open_tab("DESIGN")

    app_test.job.design.ge.click_button_for_section(btn_name="Edit",section="Question")

    app_test.job.design.ge.side_panel_open_general_options()

    app_test.job.design.ge.add_choice_for_tq("The new label")
    app_test.navigation.refresh_page()
    app_test.verification.text_present_on_page("The new label")


# @pytest.mark.skip(reason="not working")
# def test_update_cml(app_test):
#     """
#     Customer is able to update CML
#     """
#     email = get_user_info('test_ui_account')['email']
#     password = get_user_password('test_ui_account')
#     app_test.user.login_as_customer(user_name=email, password=password)
#
#     app_test.mainMenu.jobs_page()
#
#     app_test.job.create_new_job_from_template(template_type="Transcription",
#                                               job_type="Audio Transcription")
#
#     app_test.navigation.click_btn("Next: Design your job")
#     app_test.job.open_tab("DESIGN")
#
#     app_test.job.design.switch_to_code_editor()
#
#     app_test.job.design.add_line_to_cml("test line")
#
#     app_test.navigation.click_btn("Save")
#     try:
#         app_test.navigation.click_btn('Save changes')
#     except:
#        pass
#
#     app_test.navigation.refresh_page()
#     app_test.verification.text_present_on_page("test line")


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
def test_update_report_settings(app_test):
    """
    Customer is able to update report settings
    """
    email = get_user_email('test_predefined_jobs')
    password = get_user_password('test_predefined_jobs')

    predifined_jobs = pytest.data.predefined_data
    job_id = predifined_jobs['job_with_judgments'][pytest.env]

    app_test.user.login_as_customer(user_name=email, password=password)

    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(job_id)

    app_test.job.open_tab("Results")
    app_test.navigation.click_link("Advanced Report Settings")

    app_test.verification.text_present_on_page("Aggregation")
    app_test.verification.text_present_on_page("Advanced Options")
    app_test.verification.text_present_on_page("Include Untrusted Judgments in Full Data")

    old_checkbox_status = app_test.navigation.get_checkbox_status_by_text("Include Untrusted Judgments in Full Data")
    app_test.navigation.click_checkbox_by_text("Include Untrusted Judgments in Full Data")

    app_test.navigation.click_link("Save")
    app_test.navigation.click_link("Advanced Report Settings")

    current_checkbox_status = app_test.navigation.get_checkbox_status_by_text(
        "Include Untrusted Judgments in Full Data")

    assert old_checkbox_status != current_checkbox_status, "Checkbox status has not been changed"


@pytest.mark.ui_uat
@pytest.mark.fed_ui
def test_add_data_to_job_design(app_test):
    """
    Customer is able to add data to job design
    """
    email = get_user_info('test_ui_account')['email']
    password = get_user_password('test_ui_account')
    app_test.user.login_as_customer(user_name=email, password=password)

    app_test.mainMenu.jobs_page()
    app_test.job.create_new_job_from_scratch()
    app_test.navigation.click_btn("Next: Design your job")

    app_test.navigation.click_link("Insert Data")
    app_test.verification.text_present_on_page("Add Your Data")
    # rebrand changed the feature
    # app_test.navigation.click_btn("Preview")
    #
    # app_test.verification.element_is_visible_on_the_page("//ul[@class='ge-Editor__elementList']")
    # app_test.verification.text_present_on_page("Checkbox")
    # app_test.verification.text_present_on_page("Ratings")
    # app_test.verification.text_present_on_page("Image Annotation")
    #
    # app_test.job.design.ge.add_question("Ratings")

    # app_test.verification.text_present_on_page("Choose a rating")
    # app_test.verification.text_present_on_page("Very Negative")
    #
    # app_test.navigation.click_btn("Save")
    # app_test.navigation.refresh_page()
    #
    # app_test.verification.text_present_on_page("Choose a rating")


@pytest.mark.ui_uat
@pytest.mark.prod_bug
def test_change_job_owner(app_test):
    """
    prod bug https://appen.atlassian.net/browse/ADAP-2171
    verify user is able to change job owner
    """
    email = get_user_info('test_ui_account')['email']
    password = get_user_password('test_ui_account')
    api_key = get_user_api_key('test_ui_account')

    app_test.user.login_as_customer(user_name=email, password=password)
    app_test.mainMenu.jobs_page()
    app_test.job.create_new_job_from_scratch()
    app_test.navigation.click_btn("Next: Design your job")
    app_test.user.close_guide()
    app_test.navigation.click_btn("Save")
    job_id = app_test.job.grab_job_id()

    app_test.job.open_action('Settings')
    app_test.user.close_guide()
    app_test.job.open_settings_tab("Admin")

    job_owner = app_test.job.get_job_owner()

    new_owner = get_user_info('test_account')['email']
    app_test.job.set_up_job_owner(new_owner)
    app_test.navigation.click_btn("Save")

    app_test.navigation.refresh_page()
    actual_new_owner = app_test.job.get_job_owner()

    assert job_owner != actual_new_owner
    assert new_owner == actual_new_owner

    api = JobAPI(api_key)
    res = api.get_json_job_status(job_id)
    assert res.json_response['support_email'] == new_owner

