
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
def test_create_qual_quiz(app, login_and_create_project):
    app.ac_project.registration.new_process("Qualification Process")

    app.ac_project.process.new_process_details({"Process Name": process_name,
                                                "Process Description":" test description"
                                               })


    app.ac_project.process.copy_modules_from_process("Automation Qual Quiz")

    app.navigation.click_btn("Start")

    app.verification.text_present_on_page("Take Language Certification Quiz")
    app.verification.text_present_on_page("Have the user take the selected language quiz in platform to test/verify language skills for specified locales.")

    app.verification.text_present_on_page("Take Translation Quiz")

    assert app.ac_project.process.get_current_process_modules() == ['Take Language Certification Quiz', 'Take Translation Quiz']


@pytest.mark.dependency(depends=["test_create_qual_quiz"])
def test_preview_qual_quizzes(app, login_and_create_project):

    for module in ["Take Language Certification Quiz", "Take Translation Quiz"]:
        app.ac_project.process.preview_module_from_process(module)

        assert app.ac_project.process.get_modal_window_header() == "Preview Qualification Process"
        if module == "Take Translation Quiz":
            app.ac_project.process.verify_module_name_in_preview_window("STEP 2: Take Translation Quiz")
        else:
            app.ac_project.process.verify_module_name_in_preview_window(module)

        app.ac_project.process.switch_to_process_preview_iframe()
        app.verification.text_present_on_page("Question")

        app.driver.switch_to.default_content()
        app.navigation.switch_to_frame("page-wrapper")
        time.sleep(5)
        app.navigation.click_btn("Exit Preview Mode")


@pytest.mark.dependency(depends=["test_preview_qual_quizzes"])
def test_edit_qual_quizzes(app, login_and_create_project):
    app.ac_project.process.edit_module_in_process("Take Language Certification Quiz")

    app.ac_project.process.take_quize.edit_quiz({"LOCALE":"Italian (Italy)",
                                                 "Language quiz": "Test language certification quiz"},
                                                action="Update & Close")

    app.ac_project.process.preview_module_from_process("Take Language Certification Quiz")

    app.ac_project.process.switch_to_process_preview_iframe()
    app.verification.text_present_on_page("Test language certification quiz")
    app.verification.text_present_on_page("Which is the most abundant gas in the earth's atmosphere?")

    app.driver.switch_to.default_content()
    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn("Exit Preview Mode")

    # /////////////////////////////
    app.ac_project.process.edit_module_in_process("Take Translation Quiz")

    app.ac_project.process.take_quize.edit_quiz({"LOCALE": "English (Brazil)",
                                                 "TRANSLATE TO LOCALE": "English (Brazil)",
                                                 "TRANSLATION QUIZ":  "Test language certification quiz"
                                                 },
                                                action="Update & Close")

    app.ac_project.process.preview_module_from_process("Take Translation Quiz")

    app.ac_project.process.switch_to_process_preview_iframe()
    app.verification.text_present_on_page("Test language certification quiz")
    app.verification.text_present_on_page("Which is the most abundant gas in the earth's atmosphere?")

    app.driver.switch_to.default_content()
    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn("Exit Preview Mode")

    app.navigation.click_btn('Cancel')
    app.verification.text_present_on_page("Registration and Qualification")

#     ============================================================
#     ============================================================
#     ============================================================
#     ============================================================

@pytest.mark.dependency(depends=["test_edit_qual_quizzes"])
def test_create_reg_quiz(app, login_and_create_project):
    app.ac_project.registration.new_process("Registration Process")

    app.ac_project.process.new_process_details({"Process Name": process_name,
                                                "Process Description":" test description"
                                               })


    app.ac_project.process.copy_modules_from_process("Automation REG Quiz")

    app.navigation.click_btn("Start")

    app.verification.text_present_on_page("Take Language Certification Quiz")
    app.verification.text_present_on_page("Have the user take the selected language quiz in platform to test/verify language skills for specified locales.")

    app.verification.text_present_on_page("Take Translation Quiz")

    assert app.ac_project.process.get_current_process_modules() == ['Take Language Certification Quiz', 'Take Translation Quiz']


@pytest.mark.dependency(depends=["test_create_reg_quiz"])
def test_preview_reg_quizzes(app, login_and_create_project):

    for module in ["Take Language Certification Quiz", "Take Translation Quiz"]:
        app.ac_project.process.preview_module_from_process(module)

        assert app.ac_project.process.get_modal_window_header() == "Preview Registration Process"
        if module == "Take Translation Quiz":
            app.ac_project.process.verify_module_name_in_preview_window("STEP 2: Take Translation Quiz")
        else:
            app.ac_project.process.verify_module_name_in_preview_window(module)

        app.ac_project.process.switch_to_process_preview_iframe()
        app.verification.text_present_on_page("Test Translation")
        app.verification.text_present_on_page("The food is delicious.")

        app.driver.switch_to.default_content()
        app.navigation.switch_to_frame("page-wrapper")
        time.sleep(5)
        app.navigation.click_btn("Exit Preview Mode")


@pytest.mark.dependency(depends=["test_preview_reg_quizzes"])
def test_edit_reg_quizzes(app, login_and_create_project):
    app.ac_project.process.edit_module_in_process("Take Language Certification Quiz")

    app.ac_project.process.take_quize.edit_quiz({"LOCALE":"Italian (Italy)",
                                                 "Language quiz": "Test language certification quiz"},
                                                action="Update & Close")

    app.ac_project.process.preview_module_from_process("Take Language Certification Quiz")

    app.ac_project.process.switch_to_process_preview_iframe()
    app.verification.text_present_on_page("Test language certification quiz")
    app.verification.text_present_on_page("Which is the most abundant gas in the earth's atmosphere?")

    app.driver.switch_to.default_content()
    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn("Exit Preview Mode")

    # /////////////////////////////
    app.ac_project.process.edit_module_in_process("Take Translation Quiz")

    app.ac_project.process.take_quize.edit_quiz({"LOCALE": "English (Brazil)",
                                                 "TRANSLATE TO LOCALE": "English (Brazil)",
                                                 "TRANSLATION QUIZ":  "Test language certification quiz"
                                                 },
                                                action="Update & Close")

    app.ac_project.process.preview_module_from_process("Take Translation Quiz")

    app.ac_project.process.switch_to_process_preview_iframe()
    app.verification.text_present_on_page("Test language certification quiz")
    app.verification.text_present_on_page("Which is the most abundant gas in the earth's atmosphere?")

    app.driver.switch_to.default_content()
    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn("Exit Preview Mode")

    app.navigation.click_btn('Cancel')
    app.verification.text_present_on_page("Registration and Qualification")
