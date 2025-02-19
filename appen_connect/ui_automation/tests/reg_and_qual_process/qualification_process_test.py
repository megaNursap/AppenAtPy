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
    process_name = "Other Quizs Process " + project_name[1]

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
def test_create_new_quizzes_process(app, login_and_create_project):
    app.ac_project.process.new_process("Qualification Process")

    app.verification.text_present_on_page("Process Details")
    app.verification.text_present_on_page("Process Name")
    app.verification.text_present_on_page("Process Description")
    app.verification.text_present_on_page("Copy Modules From an Existing Process")


@pytest.mark.dependency(depends=["test_create_new_quizzes_process"])
def test_qual_process_required_fields(app, login_and_create_project):
    app.navigation.click_btn("Start")

    app.verification.text_present_on_page("Process name is a required field.")
    app.verification.text_present_on_page("Process description is a required field.")

    app.ac_project.process.cancel_process_creation()


@pytest.mark.dependency(depends=["test_qual_process_required_fields"])
def test_qual_process_process_details(app, login_and_create_project):

    app.ac_project.process.new_process("Qualification Process")

    app.ac_project.process.new_process_details({"Process Name": process_name,
                                                "Process Description": " test description"
                                                })

    app.ac_project.process.copy_modules_from_process("Automation Simple Qualification Process")

    app.navigation.click_btn("Start")
    time.sleep(2)

    app.verification.text_present_on_page("Process Builder")
    app.verification.text_present_on_page(process_name)
    app.verification.text_present_on_page("Select Modules")

    app.verification.text_present_on_page("Complete Academy Course")
    app.verification.text_present_on_page("Download Secure Browser")
    app.verification.text_present_on_page("Face Register")
    app.verification.text_present_on_page("Perform Manual Work")
    app.verification.text_present_on_page("Send Email")
    app.verification.text_present_on_page("Sign Document")
    app.verification.text_present_on_page("Take External Exam")
    app.verification.text_present_on_page("Take Internal Locale Based Quiz")
    app.verification.text_present_on_page("Take Internal Quiz")
    app.verification.text_present_on_page("Take Language Certification Quiz")
    app.verification.text_present_on_page("Take Translation Quiz")


@pytest.mark.dependency(depends=["test_qual_process_process_details"])
def test_qual_process_preview_modules(app, login_and_create_project):

    modules = {"Complete Academy Course": "", "Perform Manual Work": "4"}

    for module in modules:
        app.ac_project.process.preview_module_from_process(module)

        assert app.ac_project.process.get_modal_window_header() == "Preview Qualification Process"
        _step = f"STEP {modules[module]}: " if modules[module] else ""
        app.ac_project.process.verify_module_name_in_preview_window(_step + module)
        app.navigation.click_btn("Exit Preview Mode")


@pytest.mark.dependency(depends=["test_qual_process_preview_modules"])
def test_qual_process_preview_whole_process(app, login_and_create_project):
    app.navigation.click_btn("Preview Process")
    assert app.ac_project.process.get_modal_window_header() == "Preview Qualification Process"
    app.ac_project.process.verify_module_name_in_preview_window("STEP 1: Complete Academy Course")
    app.ac_project.process.carousel_preview_process_click("Next")
    app.ac_project.process.verify_module_name_in_preview_window("STEP 2: Download Secure Browser")

    app.ac_project.process.carousel_preview_process_click("Next")
    app.ac_project.process.verify_module_name_in_preview_window("STEP 3: Face Register")

    app.ac_project.process.carousel_preview_process_click("Next")
    app.ac_project.process.verify_module_name_in_preview_window("STEP 4: Perform Manual Work")
    app.navigation.click_btn("Exit Preview Mode")


@pytest.mark.dependency(depends=["test_qual_process_preview_whole_process"])
def test_qual_process_remove_module(app, login_and_create_project):
    before_modules = app.ac_project.process.get_current_process_modules()

    app.ac_project.process.remove_module_from_process("Download Secure Browser")
    after_modules = app.ac_project.process.get_current_process_modules()

    assert len(before_modules) - 1 == len(after_modules)
    assert "Download Secure Browser" not in after_modules


@pytest.mark.dependency(depends=["test_qual_process_remove_module"])
def test_qual_process_create(app, login_and_create_project):
    app.navigation.click_btn("Create Qualification  Process")
    app.verification.text_present_on_page("Save Updates")
    app.navigation.click_btn("Exit")

    reg_process = app.ac_project.registration.get_current_qualification_process_info()
    print(reg_process)
    assert reg_process['name'] == process_name
    assert reg_process['modules'] == ['1 - Complete Academy Course', '2 - Face Register', '3 - Perform Manual Work']
#     TODO add verification : created by


@pytest.mark.dependency(depends=["test_qual_process_create"])
def test_qual_process_preview_form(app, login_and_create_project):
    # app.ac_project.registration.click_gear_menu_item_for_process(process_name=process_name,
    #                                                              process_type='Qualification Process',
    #                                                              menu_action='Preview')
    app.ac_project.registration.click_preview_process("Qualification")
    time.sleep(3)

    app.verification.text_present_on_page('Preview Qualification Process')
    app.ac_project.process.verify_module_name_in_preview_window("STEP 1: Complete Academy Course")

    app.ac_project.process.carousel_preview_process_click("Next")
    app.ac_project.process.verify_module_name_in_preview_window("STEP 2: Face Register")

    app.ac_project.process.carousel_preview_process_click("Next")
    app.ac_project.process.verify_module_name_in_preview_window("STEP 3: Perform Manual Work")

    app.navigation.click_btn("Exit Preview Mode")


@pytest.mark.dependency(depends=["test_qual_process_preview_form"])
def test_qual_process_edit_cancel(app, login_and_create_project):
    time.sleep(10)
    qual_process = app.ac_project.registration.get_current_qualification_process_info()

    app.ac_project.registration.click_gear_menu_item_for_process(process_name=process_name,
                                                                 process_type='Qualification Process',
                                                                 menu_action='Edit')

    time.sleep(3)
    app.ac_project.process.remove_module_from_process('Face Register')

    app.ac_project.process.click_cancel_process_creation()

    updated_qual_process = app.ac_project.registration.get_current_qualification_process_info()

    assert qual_process == updated_qual_process


@pytest.mark.dependency(depends=["test_qual_process_edit_cancel"])
def test_qual_process_edit_save(app, login_and_create_project):
    time.sleep(10)
    app.ac_project.registration.click_gear_menu_item_for_process(process_name=process_name,
                                                                 process_type='Qualification Process',
                                                                 menu_action='Edit')

    time.sleep(3)
    app.ac_project.process.remove_module_from_process('Face Register')

    app.navigation.click_btn("Save Updates")
    app.navigation.click_btn("Exit")

    updated_qual_process = app.ac_project.registration.get_current_qualification_process_info()

    assert updated_qual_process['modules'] == ['1 - Complete Academy Course', '2 - Perform Manual Work']


@pytest.mark.dependency(depends=["test_qual_process_edit_save"])
def test_qual_process_edit_no_access(app, login_and_create_project):
    app.ac_project.registration.fill_out_fields(data={
        "Select Qualification process": "QA Demo Qualification"})
    time.sleep(10)

    qual_process = app.ac_project.registration.get_current_qualification_process_info()

    app.ac_project.registration.click_gear_menu_item_for_process(process_name='QA Demo Qualification',
                                                                 process_type='Qualification Process',
                                                                 menu_action='Edit')

    time.sleep(3)
    # TODO verify status for remote btn
    app.ac_project.process.remove_module_from_process('Send Email')

    app.navigation.click_btn("Save Updates")
    app.navigation.click_btn("Exit")

    updated_qual_process = app.ac_project.registration.get_current_qualification_process_info()

    assert updated_qual_process == qual_process
