
import time

from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name
from adap.api_automation.utils.data_util import *

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

pytestmark = [pytest.mark.regression_ac_project_process, pytest.mark.regression_ac, pytest.mark.ac_process]


@pytest.fixture(scope="module")
def login_and_create_project(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.ac_project.create_new_project()
    customer = app.ac_project.identify_customer(pytest.env)
    global process_name
    project_name = generate_project_name()
    process_name = "Reg Sign Doc Process "+project_name[1]

    app.ac_project.overview.fill_out_fields(data={
        "Project Title": project_name[0],
        "Project Alias": project_name[1],
        "Project Description": "New Project Description",
        "Customer": customer,
        "Project Type": "Express",
        "Task Type": "Express",
        "Task Volume": "Very Low"
    })

    app.navigation.click_btn('Next: Registration and Qualification')


@pytest.mark.dependency()
def test_create_sing_document_reg_process(app, login_and_create_project):
    app.ac_project.registration.new_process("Registration Process")

    app.ac_project.process.new_process_details({"Process Name": process_name,
                                                "Process Description":" test description"
                                               })


    app.ac_project.process.copy_modules_from_process("Automation Reg Sign Document")

    app.navigation.click_btn("Start")

    app.verification.text_present_on_page("Sign Document")
    app.verification.text_present_on_page("Have the user review and digitally sign a document.")


@pytest.mark.dependency(depends=["test_create_sing_document_reg_process"])
def test_preview_sing_document_reg_process(app, login_and_create_project):
    app.ac_project.process.preview_module_from_process("Sign Document")

    assert app.ac_project.process.get_modal_window_header() == "Preview Registration Process"
    app.ac_project.process.verify_module_name_in_preview_window("Sign Document")

    app.ac_project.process.switch_to_process_preview_iframe()
    app.verification.text_present_on_page("I understand and agree")
    app.verification.text_present_on_page("I Do Not Agree")
    # app.verification.text_present_on_page("Password")

    app.driver.switch_to.default_content()
    app.navigation.switch_to_frame("page-wrapper")
    time.sleep(5)
    app.navigation.click_btn("Exit Preview Mode")


@pytest.mark.dependency(depends=["test_preview_sing_document_reg_process"])
def test_edit_existing_sing_document_reg_process(app, login_and_create_project):
    app.ac_project.process.edit_module_in_process("Sign Document")

    app.ac_project.process.sign_document.select_existing_document("QA Support Agreement")
    app.navigation.click_btn("Update & Close")

    app.ac_project.process.preview_module_from_process("Sign Document")
    app.ac_project.process.switch_to_process_preview_iframe()
    app.verification.text_present_on_page("This is a test agreement that your must electronically signed.")
    app.verification.text_present_on_page("Congratulations, you're just a few steps away to get activated on the project!")

    app.driver.switch_to.default_content()
    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn("Exit Preview Mode")


@pytest.mark.dependency(depends=["test_edit_existing_sing_document_reg_process"])
def test_create_new_sing_document(app, login_and_create_project):
    app.ac_project.process.edit_module_in_process("Sign Document")

    app.ac_project.process.sign_document.create_new_document({"DOCUMENT TITLE":"test title",
                                                              "REQUIRED":"1",
                                                              "Add Internal Notes":"1",
                                                              "INTERNAL NOTES": "test notes",
                                                              "DOCUMENT CONTENT": " Test Content"},
                                                             action="Update & Close")

    app.ac_project.process.preview_module_from_process("Sign Document")

    app.ac_project.process.switch_to_process_preview_iframe()
    app.verification.text_present_on_page("Test Content")

    app.driver.switch_to.default_content()
    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn("Exit Preview Mode")

    app.navigation.click_btn('Cancel')
    app.verification.text_present_on_page("Registration and Qualification")



# ///////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////


@pytest.mark.dependency(depends=["test_create_new_sing_document"])
def test_create_sing_document_qual_process(app, login_and_create_project):
    app.ac_project.registration.new_process("Qualification Process")

    app.ac_project.process.new_process_details({"Process Name": process_name,
                                                "Process Description":" test description"
                                               })


    app.ac_project.process.copy_modules_from_process("Automation Qual Sign Document")

    app.navigation.click_btn("Start")

    app.verification.text_present_on_page("Sign Document")
    app.verification.text_present_on_page("Have the user review and digitally sign a document.")


@pytest.mark.dependency(depends=["test_create_sing_document_qual_process"])
def test_preview_sing_document_qual_process(app, login_and_create_project):
    app.ac_project.process.preview_module_from_process("Sign Document")

    assert app.ac_project.process.get_modal_window_header() == "Preview Qualification Process"
    app.ac_project.process.verify_module_name_in_preview_window("Sign Document")

    app.ac_project.process.switch_to_process_preview_iframe()
    app.verification.text_present_on_page("I understand and agree")
    app.verification.text_present_on_page("I Do Not Agree")

    app.driver.switch_to.default_content()
    app.navigation.switch_to_frame("page-wrapper")
    time.sleep(5)
    app.navigation.click_btn("Exit Preview Mode")


@pytest.mark.dependency(depends=["test_preview_sing_document_qual_process"])
def test_edit_existing_sing_document_qual_process(app, login_and_create_project):
    app.ac_project.process.edit_module_in_process("Sign Document")

    app.ac_project.process.sign_document.select_existing_document("QA Support Agreement")
    app.navigation.click_btn("Update & Close")

    app.ac_project.process.preview_module_from_process("Sign Document")
    app.ac_project.process.switch_to_process_preview_iframe()
    app.verification.text_present_on_page("This is a test agreement that your must electronically signed.")
    app.verification.text_present_on_page("Congratulations, you're just a few steps away to get activated on the project!")

    app.driver.switch_to.default_content()
    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn("Exit Preview Mode")


@pytest.mark.dependency(depends=["test_edit_existing_sing_document_qual_process"])
def test_create_new_sing_document_qual_process(app, login_and_create_project):
    app.ac_project.process.edit_module_in_process("Sign Document")

    app.ac_project.process.sign_document.create_new_document({"DOCUMENT TITLE":" Qual test title",
                                                              "REQUIRED":"1",
                                                              "Add Internal Notes":"1",
                                                              "INTERNAL NOTES": "test notes",
                                                              "DOCUMENT CONTENT": " Test Content Qual Process"},
                                                             action="Update & Close")

    app.ac_project.process.preview_module_from_process("Sign Document")

    app.ac_project.process.switch_to_process_preview_iframe()
    app.verification.text_present_on_page("Test Content Qual Process")

    app.driver.switch_to.default_content()
    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn("Exit Preview Mode")

    app.navigation.click_btn('Cancel')
    app.verification.text_present_on_page("Registration and Qualification")
