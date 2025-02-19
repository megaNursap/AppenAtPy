
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name
from adap.api_automation.utils.data_util import *

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

pytestmark = [pytest.mark.regression_ac_project_process, pytest.mark.regression_ac]


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



def test_qual_process_acadamy_mapping(app, login_and_create_project):
    app.ac_project.process.new_process("Qualification Process")
    app.ac_project.process.new_process_details({"Process Name": process_name,
                                                "Process Description": " test description"
                                                })

    app.ac_project.process.copy_modules_from_process("Test Qualification process - quiz and academies")

    app.navigation.click_btn("Start")

    # Academy and Quiz module data
    academy_courses_input_data = [{'Academy': 'Needs Met Academy'}, {'Academy':'Project Nile Academy'}, {'Academy':'The E-A-T Academy'}]
    internal_quiz_input_data = [
        {'Quiz': '01Random quiz',
         'Max Exam Attempts': '3',
         'Subset Size': '1',
         'Passing Score': '2'
         },
        {
            'Quiz': '02 Manual Quiz',
            'Max Exam Attempts': '3',
            'Subset Size': '1',
            'Passing Score': '2'
        },
        {
            'Quiz': '03 Manual Quiz',
            'Max Exam Attempts': '3',
            'Subset Size': '2',
            'Passing Score': '1'
        }
    ]

    academy_course_modules = app.ac_project.process._find_modules_by_name('Complete Academy Course')
    for i in range(len(academy_course_modules)):
        app.ac_project.process.edit_module_in_process('Complete Academy Course', i)
        app.ac_project.process.take_academy.edit_academy_course({"SELECT ACADEMY COURSE": academy_courses_input_data[i]['Academy']})
        app.navigation.click_btn("Update & Close")

    internal_quiz_modules = app.ac_project.process._find_modules_by_name('Take Internal Quiz')
    for i in range(len(internal_quiz_modules)):
        app.ac_project.process.edit_module_in_process('Take Internal Quiz', i)
        app.ac_project.process.take_quize.edit_quiz({"Quiz":internal_quiz_input_data[i]['Quiz'],"Maximum attempts": internal_quiz_input_data[i]['Max Exam Attempts'],
                                                     "Subset size": internal_quiz_input_data[i]['Subset Size'],
                                                     "Passing score": internal_quiz_input_data[i]['Passing Score'] })
        app.navigation.click_btn("Update & Close")

    app.navigation.click_btn("Create Qualification  Process")
    app.verification.text_present_on_page("Save Updates")

    app.navigation.click_btn("Exit")
    app.ac_project.registration.fill_out_fields(data={
        "Select Registration process": "Acac Register"})
    #
    # New feature Project Access Replaced this Test:
    #
    # app.navigation.click_btn("Next: Recruitment")
    # app.verification.text_present_on_page("Recruitment")
    # app.navigation.click_btn("Save")
    # app.navigation.click_btn("Next: Invoice & Payment")
    # app.verification.text_present_on_page("Invoice & Payment")
    # app.ac_project.process.load_project_pay_type({"Rate Type": "By Task",
    #                                               "Project Business Unit": "CR"})
    #
    # app.verification.text_present_on_page("Project Tools")
    # app.navigation.click_btn("Next: Project Tools")
    #
    # app.navigation.click_btn("Project Access")
    # app.verification.text_present_on_page("Project Access")
    #
    # app.verification.text_present_on_page("User Project Page")
    # app.navigation.click_btn("Next: User Project Page")
    #
    # app.navigation.switch_to_frame("project-mappings-iframe")
    #
    #
    # # Verification on project setup page
    # actual_quiz_data = app.ac_project.project_config_table_data("Project Quiz Mappings")
    # actual_academy_course_data = app.ac_project.project_config_table_data("Project Academy Mappings")
    #
    # #verify input data table match with internal_quiz_data by checking each row
    #
    # for i in range(len(internal_quiz_input_data)):
    #     assert app.ac_project.verify_input_row_match_config_table_row(internal_quiz_input_data[i], actual_quiz_data)
    #
    # for j in range(len(academy_courses_input_data)):
    #     assert app.ac_project.verify_input_row_match_config_table_row(academy_courses_input_data[j], actual_academy_course_data)
    #
    # assert len(academy_courses_input_data) == len(actual_academy_course_data)
    # assert len(internal_quiz_input_data) == len(actual_quiz_data)


