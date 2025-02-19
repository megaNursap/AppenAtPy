
import time

from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name
from adap.api_automation.utils.data_util import *

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

pytestmark = [pytest.mark.regression_ac_project_process,  pytest.mark.regression_ac, pytest.mark.ac_process]


@pytest.fixture(scope="module")
def login_and_create_project(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.ac_project.create_new_project()
    customer = app.ac_project.identify_customer(pytest.env)

    global process_name
    project_name = generate_project_name()
    process_name = "Internal Quiz Process "+project_name[1]

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
def test_create_internal_quiz(app, login_and_create_project):
    app.ac_project.registration.new_process("Qualification Process")

    app.ac_project.process.new_process_details({"Process Name": process_name,
                                                "Process Description":" test description"
                                               })


    app.ac_project.process.copy_modules_from_process("Automation Qual Take Internal Quiz")

    app.navigation.click_btn("Start")

    app.verification.text_present_on_page("Take Internal Locale Based Quiz")
    app.verification.text_present_on_page("Have the user take the selected quiz in platform if from the specified locale.")


@pytest.mark.dependency(depends=["test_create_internal_quiz"])
def test_preview_internal_quiz(app, login_and_create_project):
    app.ac_project.process.preview_module_from_process("Take Internal Locale Based Quiz")

    assert app.ac_project.process.get_modal_window_header() == "Preview Qualification Process"
    app.ac_project.process.verify_module_name_in_preview_window("Take Internal Locale Based Quiz")

    app.ac_project.process.switch_to_process_preview_iframe()
    app.verification.text_present_on_page("for testing")
    app.verification.text_present_on_page("Question")
    app.verification.text_present_on_page("Query")

    app.driver.switch_to.default_content()
    app.navigation.switch_to_frame("page-wrapper")
    time.sleep(5)
    app.navigation.click_btn("Exit Preview Mode")


@pytest.mark.dependency(depends=["test_preview_internal_quiz"])
def test_edit_internal_quize(app, login_and_create_project):
    app.ac_project.process.edit_module_in_process("Take Internal Locale Based Quiz")

    app.ac_project.process.take_quize.edit_quiz({"Quiz":"Superhero Quiz",
                                                  "Locale":"Italian (Italy)",
                                                  "Maximum attempts": "3",
                                                  "Subset size": "1",
                                                  "Passing score": "90"},
                                                action="Update & Close")

    app.ac_project.process.preview_module_from_process("Take Internal Locale Based Quiz")

    app.ac_project.process.switch_to_process_preview_iframe()
    app.verification.text_present_on_page("Get to know more about your superheroes")
    app.verification.text_present_on_page("Name this Superhero:")

    app.driver.switch_to.default_content()
    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn("Exit Preview Mode")

    app.navigation.click_btn('Cancel')
    app.verification.text_present_on_page("Registration and Qualification")

#     ============================================================
#     ============================================================
#     ============================================================
#     ============================================================


@pytest.mark.dependency(depends=["test_edit_internal_quize"])
def test_create_internal_quiz_reg_process(app, login_and_create_project):
    app.ac_project.registration.new_process("Registration Process")

    app.ac_project.process.new_process_details({"Process Name": process_name,
                                                "Process Description":" test description"
                                               })


    app.ac_project.process.copy_modules_from_process("Automation Reg Take Internal Quiz")

    app.navigation.click_btn("Start")

    app.verification.text_present_on_page("Take Internal Locale Based Quiz")
    app.verification.text_present_on_page("Have the user take the selected quiz in platform if from the specified locale.")


@pytest.mark.dependency(depends=["test_create_internal_quiz_reg_process"])
def test_preview_internal_quiz_reg_process(app, login_and_create_project):
    app.ac_project.process.preview_module_from_process("Take Internal Locale Based Quiz")

    assert app.ac_project.process.get_modal_window_header() == "Preview Registration Process"
    app.ac_project.process.verify_module_name_in_preview_window("Take Internal Locale Based Quiz")

    app.ac_project.process.switch_to_process_preview_iframe()
    app.verification.text_present_on_page("for testing")
    app.verification.text_present_on_page("Question")
    app.verification.text_present_on_page("Query")

    app.driver.switch_to.default_content()
    app.navigation.switch_to_frame("page-wrapper")
    time.sleep(5)
    app.navigation.click_btn("Exit Preview Mode")


@pytest.mark.dependency(depends=["test_preview_internal_quiz_reg_process"])
def test_edit_internal_quiz_reg_process(app, login_and_create_project):
    app.ac_project.process.edit_module_in_process("Take Internal Locale Based Quiz")

    app.ac_project.process.take_quize.edit_quiz({"Quiz":"AA Demo quiz",
                                                  "Locale":"Italian (Italy)",
                                                  "UNLIMITED":"1",
                                                  "Subset size": "1",
                                                  "Passing score": "90"},
                                                action="Update & Close")

    app.ac_project.process.preview_module_from_process("Take Internal Locale Based Quiz")

    app.ac_project.process.switch_to_process_preview_iframe()
    app.verification.text_present_on_page("AA Demo quiz instructions here.")
    app.verification.text_present_on_page("Question here.")

    app.driver.switch_to.default_content()
    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn("Exit Preview Mode")

    app.navigation.click_btn('Cancel')
    app.verification.text_present_on_page("Registration and Qualification")

