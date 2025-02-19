"""
create new project
1. Login to https://[pytest.env].cf3.us
2. Navigate to https://[pytest.env].cf3.us/qrp/core/partners/project/newProject
3. Generate project name
4. Populate Project Overview form
"""
import datetime
import time

import pytest

from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.js_utils import scroll_to_page_bottom
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name

pytestmark = [pytest.mark.regression_ac_project_config, pytest.mark.regression_ac, pytest.mark.ac_ui_new_project]

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

global project_name


@pytest.fixture(scope="module")
def login(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)


@pytest.mark.dependency()
@pytest.mark.ac_ui_uat
def test_create_new_project(app, login):

    app.ac_project.create_new_project()
    app.verification.text_present_on_page("Project Setup")
    app.verification.text_present_on_page("Project Overview")
    app.verification.text_present_on_page("Registration and Qualification")
    app.verification.text_present_on_page("Project Tools")
    app.verification.text_present_on_page("Recruitment")
    app.verification.text_present_on_page("Invoice & Payment")
    app.verification.text_present_on_page("User Project Page")
    app.verification.text_present_on_page("Support Team")
    app.verification.text_present_on_page("Preview")

    assert app.ac_project.project_setup_status() == '0%'


@pytest.mark.ac_ui_uat
@pytest.mark.dependency(depends=["test_create_new_project"])
def test_overview_page(app, login):
    global project_name

    project_name = generate_project_name()
    customer = app.ac_project.identify_customer(pytest.env)
    app.ac_project.overview.fill_out_fields(data={
        "Project Title": "SMOKE_" + project_name[0],
        "Project Alias": "ST_" + project_name[1],
        "Project Description": "Question|Option1|Option2|Option3",
        "Customer": customer,
        "Project Type": "Express",
        "Task Type": "Transcription",
        "Task Volume": "Very Low"
    })


    app.navigation.click_btn('Save')
    app.ac_project.overview.load_project(data={
        "Project Title": f"Appen SMOKE_{project_name[0]} (ST_{project_name[1]})",
        "Project Alias": "ST_" + project_name[1],
        "Project Name": f"Appen SMOKE_{project_name[0]} (ST_{project_name[1]})",
        "Customer": "Appen Internal",
        "Project Type": "Express",
        "Task Type": "TRANSCRIPTION",
        "Task Volume": "VERY_LOW"
    })

    app.navigation.click_btn('Next: Registration and Qualification')
    # BUG https://appen.atlassian.net/browse/ACE-7343
    # assert app.ac_project.project_setup_status() == '15%'


@pytest.mark.ac_ui_uat
@pytest.mark.dependency(depends=["test_overview_page"])
def test_registration_page(app, login):
    app.verification.text_present_on_page("Registration and Qualification")
    app.verification.text_present_on_page("Registration Process")
    app.verification.text_present_on_page("Qualification Process")

    if pytest.env == "prod":
        app.ac_project.registration.fill_out_fields(data={
            "Select Registration process": "A Simple Registration Process",
            "Select Qualification process": "A Simple Qualification Process"})
    else:
        app.ac_project.registration.fill_out_fields(data={
            "Select Registration process": "A Simple Registration Process",
            "Select Qualification process": "A Simple Qualification Process"
    })
    app.ac_project.registration.click_preview_process("Registration")
    app.verification.text_present_on_page("Preview Registration Process")
    app.verification.text_present_on_page("Send Email")
    app.navigation.click_btn('Exit Preview Mode')

    app.ac_project.registration.click_preview_process("Qualification")
    app.verification.text_present_on_page("Preview Qualification Process")
    app.verification.text_present_on_page("Send Email")
    app.navigation.click_btn('Exit Preview Mode')

    app.navigation.click_btn('Save')
    app.ac_project.registration.load_project(data={
        "Select Registration process": "A Simple Registration Process",
        "Select Qualification process": "A Simple Qualification Process"
    })

    app.navigation.click_btn('Next: Recruitment')
    # assert app.ac_project.project_setup_status() == '29%'


@pytest.mark.ac_ui_uat
@pytest.mark.dependency(depends=["test_registration_page"])
def test_recruitment_page(app, login):
    app.verification.text_present_on_page("Recruitment")
    app.verification.text_present_on_page("Locale Tenants")
    app.verification.text_present_on_page("The project locale tenants for each locale.")
    app.verification.text_present_on_page("Hiring Targets")
    app.verification.text_present_on_page("The project hiring targets for each locate.")
    app.verification.text_present_on_page("Blocking rules prevent raters from working on certain other projects")
    # app.verification.text_present_on_page("Intelligent Attributes")
    app.verification.text_present_on_page("Linked Projects")
    app.verification.text_present_on_page("Add Notes to Recruiting Team")

    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Canada", tenant='Appen Ltd. (Contractor)')

    tomorrow_date = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%m/%d/%Y")
    app.ac_project.recruitment.add_target(language='English', region='Canada', restrict_country='Canada',
                                          deadline=tomorrow_date, target='12')

    app.ac_project.recruitment.fill_out_fields({"Blocking Rules": "1"})

    if pytest.env == 'prod':
        app.ac_project.recruitment.add_block_project("Name error api")
        app.ac_project.recruitment.click_permanent_btn("Name error api")
    else:
        app.ac_project.recruitment.add_block_project("Project NameQATest")
        app.ac_project.recruitment.click_permanent_btn("Project NameQATest")

    # app.ac_project.recruitment.fill_out_fields({"Intelligent Attributes": "1"})

    app.ac_project.recruitment.fill_out_fields({"Linked Projects": "1"})

    app.ac_project.recruitment.add_linked_project("Figure-Eight Testing")
    # app.ac_project.recruitment.add_linked_project("testFigure8")

    app.ac_project.recruitment.fill_out_fields({"Add Notes to Recruiting Team": "1",
                                                "Recruiting Notes": "Test Notes to Recruiting Team"})

    app.navigation.click_btn('Save')
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="Canada", tenant='Appen Ltd.', tenant_type='Contractor')

    formatted_date = (custom_strftime('%b {S}, %Y', (datetime.date.today() + datetime.timedelta(days=30))))

    # Changing this verification because of the defect https://appen.atlassian.net/browse/ACE-8076

    app.ac_project.recruitment.verify_regular_hiring_target_row_present_on_page(language='English', region='Canada',
                                                                                restrict_country='Canada',
                                                                                deadline=formatted_date, target='12', status = 'DRAFT')

    app.ac_project.recruitment.fill_out_fields({"Target Screening and Data Requirements": "1"})
    app.ac_project.recruitment.fill_out_fields(data={
        "Select target audience group": "isa 90"})

    app.ac_project.recruitment.load_project(data={"BLOCK PROJECT": "Project NameQATest",
                                                  "LINKED PROJECT": "Figure-Eight Testing",
                                                  "Recruiting Notes": "Test Notes to Recruiting Team"})


    app.navigation.click_btn("Next: Invoice & Payment")
    # assert app.ac_project.project_setup_status() == '43%'


@pytest.mark.ac_ui_uat
@pytest.mark.dependency(depends=["test_recruitment_page"])
def test_payment_page(app, login):
    app.verification.text_present_on_page("Invoice & Payment")
    # app.verification.text_present_on_page("Workday Task ID")
    app.verification.text_present_on_page("Rate Type")
    app.verification.text_present_on_page("Project Business Unit")
    app.verification.text_present_on_page("Pay Rates Setup")
    app.verification.text_present_on_page("Add Notes to Finance")

    app.ac_project.payment.fill_out_fields({"PROJECT WORKDAY TASK ID": "P12345",
                                            # "TASK CODE": '123345',
                                            "Rate Type": "By Task",
                                            "Project Business Unit": "CR",
                                            "Add Notes to Finance": "1",
                                            "Notes to Finance": "Test Notes to Finance"})
    app.navigation.click_btn('Save')

    app.navigation.click_btn("Add Pay Rate")
    app.ac_project.payment.fill_out_fields({"Custom Pay Rates": "1"})

    #verifying the fields present on Custom pay rate window.
    app.verification.text_present_on_page("Hiring Target")
    app.verification.text_present_on_page("Spoken Fluency")
    app.verification.text_present_on_page("Written Fluency")
    app.verification.text_present_on_page("Require certified fluency")
    app.verification.text_present_on_page("User Group")
    app.verification.text_present_on_page("Task Type")
    app.verification.text_present_on_page("WORKDAY TASK ID (OPTIONAL)")
    app.verification.text_present_on_page("Rate")

    app.ac_project.payment.select_custom_pay_rates('English (Canada)', 'Canada')

    #Entering the details on custom page
    app.ac_project.payment.fill_out_fields({"Spoken Fluency": "Native or Bilingual",
                                            "Written Fluency": "Native or Bilingual",
                                            "User Group": "All users",
                                            "Task Type": "Annotation",
                                            "Rate": 123
                                            }, action='Save')


    app.navigation.click_btn("Set Template")
    app.verification.wait_untill_text_present_on_the_page("Invoice Template Setup", max_time=15)
    app.verification.text_present_on_page("Invoice Template Setup")
    app.ac_project.payment.fill_out_fields({"Invoice Type":'User self-reported'}, action='Save')


    app.ac_project.payment.load_project({"PROJECT WORKDAY TASK ID": 'P12345',
                                         "Rate Type": "By Task",
                                         "Project Business Unit": "CR",
                                         "Notes to Finance": "Test Notes to Finance"})

    app.ac_project.payment.verify_pay_rate_is_present_on_page(hiring_target='English (Canada)',
                                                              input_fluency='Native or Bilingual', input_grp='All users',
                                                              input_work='.', input_taskid='.',
                                                              input_rate='$1.23')

    app.navigation.click_btn('Save')
    app.navigation.click_btn('Next: Project Tools')
    # assert app.ac_project.project_setup_status() == '58%'


@pytest.mark.ac_ui_uat
@pytest.mark.dependency(depends=["test_payment_page"])
def test_tools_page(app, login):
    app.verification.text_present_on_page("Project Tools")
    app.verification.text_present_on_page("External System")
    app.verification.text_present_on_page("Secure IP Access")
    app.verification.text_present_on_page("If checked, vendors will need to acquire tasks from an external source "
                                          "that is not part of our task platform.")
    app.verification.text_present_on_page("If checked, only selected IPs will be allowed access")
    # app.verification.text_present_on_page("If checked, it will be used for prompting the user to enter task timings "
    #                                       "for the task types in the data file.")

    app.ac_project.tools.fill_out_fields(data={
        # "External System checkbox": "1",
        "External System": "ADAP"
        # "Secure IP Access": "1",
        # "Allowed IPs": "107.3.166.36"
    })

    # app.ac_project.tools.add_allowed_ip("107.3.166.00")
    # app.ac_project.tools.add_allowed_ip("107.3.166.01")
    app.navigation.click_btn('Save')
    # app.ac_project.tools.load_project(data={"External System": "ADAP"})
    app.ac_project.tools.fill_out_fields(data={
        "External System checkbox": "1"
    })
    # app.navigation.click_btn("Next: Project Access")
    app.navigation.click_btn("Next: User Project Page")
    # assert app.ac_project.project_setup_status() == '72%'


@pytest.mark.ac_ui_uat
@pytest.mark.dependency(depends=["test_tools_page"])
def test_user_project_page_create(app, login):
    app.verification.text_present_on_page("User Project Page")
    app.verification.text_present_on_page("Default Page Task")
    app.verification.text_present_on_page("Available Skill Review")
    app.verification.text_present_on_page("ACAN Project")

    app.ac_project.user_project.fill_out_fields({"Default Page Task": "Tasks",
                                                 "Available Skill Review": '1',
                                                 "ACAN Project": "1"
                                                 })
    app.navigation.click_btn('Save')
    app.ac_project.user_project.load_project(data={"Default Page Task": "Tasks"})

    #project resources
    app.navigation.click_btn("Add Resource")
    app.ac_project.user_project.select_resource_type("Academy")

    app.ac_project.user_project.fill_out_fields({
        "Academy": "Needs Met Academy",
        "Allow Active Users Access": 1
    })
    app.ac_project.user_project.save_project_resource()

    #Data Collection Consent Form Template
    app.navigation.click_btn("Set Template")
    app.ac_project.user_project.fill_out_fields({
        "Project Contact Email": "test@test.com",
        "Appen Entity": "Appen Butler Hill Inc.",
        "PII Data collected": "Genetic information"
    })
    app.ac_project.user_project.select_pii_data("Select PII data")

    app.ac_project.user_project.fill_out_fields({
        "Countries collecting data": "United States of America"
    })
    app.ac_project.user_project.select_pii_data("Select Countries")

    app.ac_project.user_project.fill_out_fields({
        "Program DPO contact email": "test1@test.com",
        "Program full legal name": "full name",
        "Program country": "United States of America",
        "PII Third party": 1
    })
    app.ac_project.user_project.select_data_from_third_party("Both")

    app.ac_project.user_project.save_consent_form_template()

    app.navigation.click_btn("Next: Support Team")
    # assert app.ac_project.project_setup_status() == '86%'


@pytest.mark.ac_ui_uat
@pytest.mark.dependency(depends=["test_user_project_page_create"])
def test_support_page(app, login):
    app.ac_project.support.fill_out_fields({"Support User Role": "Quality",
                                            "Member Name": "Support (Ac)"})

    app.navigation.click_btn('Save')
    app.verification.text_present_on_page("Quality")
    app.verification.text_present_on_page("Support (Ac)")

    app.navigation.click_btn("Next: Preview")
    assert app.ac_project.project_setup_status() == '100%'


@pytest.mark.ac_ui_uat
@pytest.mark.dependency(depends=["test_support_page"])
def test_preview_page_project(app, login):
    global project_name

    app.verification.text_present_on_page("Project Overview")

    app.ac_project.verify_project_info({
        "Project Name": "Appen SMOKE_" + project_name[0],
        "Project Alias": "ST_" + project_name[1],
        # "Project Description": "New Project Description SMOKE_TEST_",
        "Type of Project": "Express",
        "Type of Task": "Transcription",
        "Task Volume": "Very Low"
    })


@pytest.mark.ac_ui_uat
@pytest.mark.dependency(depends=["test_preview_page_project"])
def test_preview_page_reg_qua(app, login):
    app.verification.text_present_on_page("Registration and Qualification")

    if pytest.env == "prod":
        app.ac_project.verify_project_info({
            "Registration Process": "A Simple Registration Process",
            "Qualification Process": "A Simple Qualification Process"})
    else:
        app.ac_project.verify_project_info({
            "Registration Process": "A Simple Registration Process",
            "Qualification Process": "A Simple Qualification Process"
    })


@pytest.mark.ac_ui_uat
@pytest.mark.dependency(depends=["test_preview_page_reg_qua"])
def test_preview_page_recruitment(app, login):
    app.verification.text_present_on_page("Recruitment")

    app.verification.text_present_on_page("Locale Tenants")
    app.verification.text_present_on_page("COUNTRY")
    app.verification.text_present_on_page("TENANT")
    app.verification.text_present_on_page("TENANT TYPE")
    app.verification.text_present_on_page("Canada")
    app.verification.text_present_on_page("Appen Ltd.")
    app.verification.text_present_on_page("Contractor")

    app.verification.text_present_on_page("LOC. LANGUAGE")
    app.verification.text_present_on_page("LOC. DIALECT")
    app.verification.text_present_on_page("REST. TO COUNTRY")
    app.verification.text_present_on_page("HIRING DEADLINE")
    app.verification.text_present_on_page("TARGET")
    app.verification.text_present_on_page("English")
    app.verification.text_present_on_page("Canada")
    # app.verification.text_present_on_page("Italy")
    app.verification.text_present_on_page("12")

    app.ac_project.verify_project_info({
        "Blocking Rules": "Project NameQATest (Permanent)",
        "Linked Projects": "Figure-Eight Testing",
        "Notes to Recruiting Team": "Test Notes to Recruiting Team"
    })


@pytest.mark.ac_ui_uat
@pytest.mark.dependency(depends=["test_preview_page_recruitment"])
def test_preview_page_invoice_payment(app, login):
    app.verification.text_present_on_page("Invoice & Payment")

    app.ac_project.verify_project_info({
        "PROJECT WORKDAY TASK ID": "Task Code: P12345",
        "Rate Type": "By Task",
        "Project Business Unit": "CR"
    })

    app.verification.text_present_on_page("Pay Rates Setup")
    app.verification.text_present_on_page("HIRING TARGET")
    app.verification.text_present_on_page("SPOKEN AND WRITTEN FLUENCY")
    app.verification.text_present_on_page("GROUP")
    app.verification.text_present_on_page("TASK TYPE")
    app.verification.text_present_on_page("WORKDAY TASK Id")
    app.verification.text_present_on_page("RATE")

    app.verification.text_present_on_page("Canada")
    app.verification.text_present_on_page("English (Canada)")
    app.verification.text_present_on_page("Native or Bilingual")
    app.verification.text_present_on_page("All users")
    app.verification.text_present_on_page("Annotation")
    app.verification.text_present_on_page("$1.23")

    app.ac_project.verify_project_info({
        "Productivity Data": "Not enabled",
        "Notes to Finance": "Test Notes to Finance"
    })


@pytest.mark.ac_ui_uat
@pytest.mark.dependency(depends=["test_preview_page_invoice_payment"])
def test_preview_page_project_tools(app, login):
    app.verification.text_present_on_page("Project Tools")

    app.ac_project.verify_project_info({
        "External Project": "-"
    })

    app.verification.text_present_on_page("Secure IP Access")


@pytest.mark.ac_ui_uat
@pytest.mark.dependency(depends=["test_preview_page_project_tools"])
def test_preview_page_user_project_page(app, login):
    app.verification.text_present_on_page("User Project Pages")
    app.verification.text_present_on_page("Default Page Task")

    app.verification.text_present_on_page("Available Skill Review")
    app.verification.text_present_on_page("ACAN Project")


@pytest.mark.ac_ui_uat
@pytest.mark.dependency(depends=["test_preview_page_user_project_page"])
def test_preview_page_user_support_team(app, login):
    app.verification.text_present_on_page("Support Team")

    app.ac_project.verify_project_info({
        "Support User Role": "Quality: Support (Ac)"
    })


@pytest.mark.ac_ui_uat
@pytest.mark.dependency(depends=["test_preview_page_user_support_team"])
def test_finish_page_project(app, login):

    app.verification.text_present_on_page("Finish Project Setup")

    # app.navigation.click_btn("Finish Project Setup")
    #
    # app.verification.text_present_on_page('Your project is ready to be enabled. Until then, all project information '
    #                                       'can be seen and edited on the project page.')
    #
    # app.navigation.click_btn("Go to Project Page")


# @pytest.mark.dependency(depends=["test_finish_page_project"])
# @pytest.mark.skip(reason='Change on Flow')
# def test_load_page(app, login):
#     # app.navigation.open_page("https://connect-stage.appen.com/qrp/core/partners/project/view/3127")
#     app.navigation_old_ui.click_edit('EditClick')
#     app.navigation.click_btn("Resume setup experience")
#
#     app.navigation.switch_to_frame("page-wrapper")
#     app.verification.text_present_on_page("Preview")
#
#     test_preview_page_project(app, login)
#     test_preview_page_reg_qua(app, login)
#     test_preview_page_recruitment(app, login)
#     test_preview_page_invoice_payment(app, login)
#     test_preview_page_project_tools(app, login)
#     test_preview_page_user_project_page(app, login)
#     test_preview_page_user_support_team(app, login)


# @pytest.mark.dependency(depends=["test_finish_page_project"])
# def test_navigate_pages(app, login):
#     global project_name
#
#     # app.ac_project.click_on_step('Project Overview')
#     app.ac_project.overview.load_project(data={
#         "Project Name": "Appen SMOKE_" + project_name[0],
#         "Project Alias": "ST_" + project_name[1],
#         # "Project Description": "New Project Description SMOKE_TEST_",
#         "Customer": "APPEN",
#         "Project Type": "Express",
#         "Task Type": "TRANSCRIPTION",
#         "Task Volume": "VERY_LOW"
#     })
#     app.verification.text_present_on_page("Project Setup")
#     app.verification.text_present_on_page('Project Overview')
#
#
#     app.ac_project.click_on_step('Registration and Qualification')
#     app.verification.text_present_on_page("Registration and Qualification")
#     app.ac_project.registration.load_project(data={
#         "Select Registration process": "A Simple Registration Process",
#         "Select Qualification process": "A Simple Qualification Process"
#     })
#
#     app.ac_project.click_on_step('Recruitment')
#     app.verification.text_present_on_page("Recruitment")
#     app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="Canada", tenant='Appen Ltd.', tenant_type='Contractor')
#
#     formatted_date = (custom_strftime('%b {S}, %Y', (datetime.date.today() + datetime.timedelta(days=30))))
#
#     # Changing this verification because of the defect https://appen.atlassian.net/browse/ACE-8076
#
#
#     app.ac_project.recruitment.verify_regular_hiring_target_row_present_on_page(language='English', region='Canada',
#                                                                                 restrict_country='Canada',
#                                                                                 deadline=formatted_date, target='12', status = 'DRAFT')
#
#     app.ac_project.recruitment.load_project(data={"BLOCK PROJECT": "Project NameQATest",
#                                                   "LINKED PROJECT": "Figure-Eight Testing",
#                                                   "Recruiting Notes": "Test Notes to Recruiting Team"})
#
#     app.ac_project.click_on_step('Invoice & Payment')
#     app.verification.text_present_on_page("Invoice & Payment")
#     app.ac_project.payment.load_project({"PROJECT WORKDAY TASK ID": 'P12345',
#                                          "Rate Type": "By Task",
#                                          "Project Business Unit": "CR",
#                                          "Notes to Finance": "Test Notes to Finance"})
#
#     app.ac_project.payment.verify_pay_rate_is_present_on_page(hiring_target='English (Canada)',
#                                                               input_fluency='Native or Bilingual', input_grp='All users',
#                                                               input_work='.', input_taskid='.',
#                                                               input_rate='$1.23')
#
#     app.ac_project.click_on_step('Project Tools')
#     app.verification.text_present_on_page("Project Tools")
#     app.ac_project.tools.load_project(data={"External System": "ADAP"})
#
#     # app.navigation.click_btn("Next: Project Access")
#     app.navigation.click_btn("Next: User Project Page")
#     app.verification.text_present_on_page("User Project Page")
#     app.ac_project.user_project.load_project(data={"Default Page Task": "Tasks"})
#
#     app.ac_project.click_on_step('Support Team')
#     app.verification.text_present_on_page("Support Team")
#     app.verification.text_present_on_page("Quality")
#     app.verification.text_present_on_page("Support (Ac)")
#
#     app.ac_project.click_on_step('Preview')
#     app.verification.text_present_on_page("Preview")


@pytest.mark.dependency(depends=["test_finish_page_project"])
def test_navigate_back(app, login):
    scroll_to_page_bottom(app.driver)
    # app.ac_project.click_on_step('Preview')
    app.navigation.click_btn('Back')
    app.verification.text_present_on_page("Support Team")
    app.navigation.click_btn('Back')
    app.verification.text_present_on_page("User Project Page")
    app.navigation.click_btn('Back')
    # app.verification.text_present_on_page("Project Access")
    # app.navigation.click_btn('Back')
    app.verification.text_present_on_page("Project Tools")
    app.navigation.click_btn('Back')
    app.verification.text_present_on_page("Invoice & Payment")
    app.navigation.click_btn('Back')
    app.verification.text_present_on_page("Recruitment")
    app.navigation.click_btn('Back')
    app.verification.text_present_on_page("Registration and Qualification")
    app.navigation.click_btn('Back')
    app.verification.text_present_on_page('Project Overview')
    app.ac_project.click_on_step('Preview')


@pytest.mark.dependency(depends=["test_finish_page_project"])
def test_edit_project_overview(app, login):
    global project_name
    app.ac_project.click_on_step('Project Overview')
    app.ac_project.overview.remove_data_from_fields({
        "Project Title": "SMOKE_" + project_name[0],
        "Project Alias": "ST_" + project_name[1],
        "Project Description": "New Project Description SMOKE_TEST_",
    })
    app.ac_project.overview.fill_out_fields(data={
        "Project Title": "EDIT_SMOKE_" + project_name[0],
        "Project Alias": "EDIT_ST_" + project_name[1],
        "Project Description": "EDIT_New Project Description SMOKE_TEST_",
        "Customer": "APPEN",
        # "Project Type": "Regular",
        "Task Type": "Express",
        "Task Volume": "Very High"
    })
    app.navigation.click_btn('Save')
    app.ac_project.overview.load_project(data={
        "Project Title": f"Appen EDIT_SMOKE_{project_name[0]} (EDIT_ST_{project_name[1]})",
        "Project Alias": "EDIT_ST_" + project_name[1],
        "Project Description": "EDIT_New Project Description SMOKE_TEST_",
        # "Project Type": "Regular",
        "Task Type": "Express",
        "Task Volume": "VERY_HIGH"
    })


@pytest.mark.dependency(depends=["test_edit_project_overview"])
def test_edit_registration_and_qualification(app, login):

    app.navigation.click_btn('Next: Registration and Qualification')

    if pytest.env == "prod":
        app.ac_project.registration.fill_out_fields(data={
            "Select Registration process": "Agnew registration",
            "Select Qualification process": "Aliso Qualification"})
    else:
        app.ac_project.registration.fill_out_fields(data={
            "Select Registration process": "A Simple Registration Process 02",
            "Select Qualification process": "A Simple Qualification Process 02"
    })

    app.navigation.click_btn('Save')
    app.ac_project.registration.load_project(data={
        "Select Registration process": "A Simple Registration Process 02",
        "Select Qualification process": "A Simple Qualification Process 02"
    })


@pytest.mark.dependency(depends=["test_edit_registration_and_qualification"])
def test_edit_recruitment(app, login):

    app.navigation.click_btn('Next: Recruitment')
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Norway", tenant='Appen Ltd. (Facility Employee)')

    tomorrow_date = (datetime.date.today() + datetime.timedelta(days=60)).strftime("%m/%d/%Y")
    app.ac_project.recruitment.add_target(language='Norwegian Bokmål', region='Norway', restrict_country='Norway',
                                          deadline=tomorrow_date, target='120')

    app.ac_project.recruitment.fill_out_fields({"Blocking Rules": "0"})

    app.ac_project.recruitment.fill_out_fields({"Linked Projects": "0"})

    app.ac_project.recruitment.fill_out_fields({"Add Notes to Recruiting Team": "0"})

    app.navigation.click_btn('Save')
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="Norway", tenant='Appen Ltd.', tenant_type='Facility Employee')

    formatted_date = (custom_strftime('%b {S}, %Y', (datetime.date.today() + datetime.timedelta(days=60))))

    # Changing this verification because of the defect https://appen.atlassian.net/browse/ACE-8076

    app.ac_project.recruitment.verify_regular_hiring_target_row_present_on_page(language='Norwegian Bokmål', region='Norway',
                                                                                restrict_country='Norway',
                                                                                deadline=formatted_date, target='120', status = 'DRAFT')


@pytest.mark.dependency(depends=["test_edit_recruitment"])
def test_edit_invoice(app, login):
    app.navigation.click_btn("Next: Invoice & Payment")

    app.ac_project.payment.fill_out_fields({"PROJECT WORKDAY TASK ID": "CR12345",
                                            "Rate Type": "Hourly",
                                            "Project Business Unit": "LR",
                                            "Available Productivity Data": "1",
                                            "Add Notes to Finance": "0"})

    app.navigation.click_btn("Add Pay Rate")
    app.ac_project.payment.fill_out_fields({"Custom Pay Rates": "1"})

    app.ac_project.payment.select_custom_pay_rates('Norwegian Bokmål (Norway)', 'Norway')

    app.ac_project.payment.fill_out_fields({"Spoken Fluency": "Near Native",
                                            "Written Fluency": "Near Native",
                                            "User Group": "All users",
                                            "Task Type": "Default",
                                            "Rate": 1234
                                            }, action='Save')

    # app.navigation.click_btn("Set Template")
    # app.verification.text_present_on_page("Invoice Template Setup")
    # assert app.ac_project.payment.get_options_for_dropdown("Invoice type") == [
    #     {'name': 'User self-reported', 'title': ''},
    #     {'name': 'System generated', 'title': 'Enabled only when “Available Productivity Data” is checked.'},
    #     {'name': 'User self-reported and System approved',
    #      'title': 'Enabled only when “Available Productivity Data” is checked.'}]
    #
    # assert app.ac_project.payment.auto_approve_is_disable()
    # app.navigation.click_btn("Cancel")

    app.navigation.click_btn('Save')
    app.ac_project.payment.load_project({"Rate Type": "Hourly",
                                         "Project Business Unit": "LR"})

    app.ac_project.payment.verify_pay_rate_is_present_on_page(hiring_target='Norwegian Bokmål (Norway)',
                                                              input_fluency='Near Native', input_grp='All users',
                                                              input_work='.', input_taskid='.',
                                                              input_rate='$12.34')


@pytest.mark.dependency(depends=["test_edit_invoice"])
def test_edit_project_tools(app, login):
    app.navigation.click_btn('Next: Project Tools')

    app.ac_project.tools.fill_out_fields(data={
        "External System": "ADAP"
        # "Secure IP Access": "1",
        # "Allowed IPs": "107.3.166.36"
    })

    app.navigation.click_btn('Save')
    app.ac_project.tools.load_project(data={"External System": "ADAP"})
                                            # "Allowed IPs": "107.3.166.36"})


@pytest.mark.dependency(depends=["test_edit_project_tools"])
def test_edit_user_project_page(app, login):

    # app.navigation.click_btn("Next: Project Access")
    app.navigation.click_btn("Next: User Project Page")
    app.ac_project.user_project.fill_out_fields({"Default Page Task": "Tasks",
                                                 "Available Skill Review": '0',
                                                 "ACAN Project": "0"
                                                 })
    app.navigation.click_btn('Save')
    app.ac_project.user_project.load_project(data={"Default Page Task": "Tasks"})


@pytest.mark.dependency(depends=["test_edit_user_project_page"])
def test_edit_support_team(app, login):
    app.navigation.click_btn("Next: Support Team")

    app.ac_project.support.fill_out_fields({"Edit Member Name": "Quality Super (Ta)"})

    app.navigation.click_btn('Save')
    app.verification.text_present_on_page("Quality")
    app.verification.text_present_on_page("Quality Super (Ta)")

    app.navigation.click_btn("Next: Preview")


@pytest.mark.dependency(depends=["test_edit_support_team"])
def test_preview_after_edit(app, login):
    global project_name

    app.ac_project.verify_project_info({
        "Project Name": f"Appen EDIT_SMOKE_{project_name[0]} (ST_{project_name[1]})",
        "Project Alias": "EDIT_ST_" + project_name[1],
        "Project Description": "EDIT_New Project Description SMOKE_TEST_",
        # "Type of Project": "Regular",
        "Type of Task": "Express",
        "Task Volume": "Very High"
    })

    # Registration and Qualification
    if pytest.env == "prod":
        app.ac_project.verify_project_info({
            "Registration Process": "Agnew registration",
            "Qualification Process": "Aliso Qualification"})
    else:
        app.ac_project.verify_project_info({
            "Registration Process": "A Simple Registration Process 02",
            "Qualification Process": "A Simple Qualification Process 02"
    })

    # Recruitment
    app.verification.text_present_on_page("Norway")
    app.verification.text_present_on_page("Appen Ltd.")
    app.verification.text_present_on_page("Facility Employee")

    app.verification.text_present_on_page("Norwegian Bokmål")
    app.verification.text_present_on_page("Norway")
    app.verification.text_present_on_page("120")

    app.ac_project.verify_project_info({
        "Demographic Requirements": "Not available"
    })

    # Invoice & Payment
    app.ac_project.verify_project_info({
        "Rate Type": "Hourly",
        "Project Business Unit": "LR",
        "Productivity Data": "Available"
    })

    app.verification.text_present_on_page("Norwegian Bokmål (Norway)")
    app.verification.text_present_on_page("Near Native")
    app.verification.text_present_on_page("All users")
    app.verification.text_present_on_page("Default")
    app.verification.text_present_on_page("$12.34")

    # Project Tools
    app.ac_project.verify_project_info({
        "External Project": "ADAP"
        # "Secure IP Access": "Allowed IPs: 107.3.166.36",
    })

    # User Project Pages
    app.ac_project.verify_project_info({
        "Default Page Task": "Tasks"
    })

    # Support Team
    app.ac_project.verify_project_info({
        "Support User Role": "Quality: Quality Super (Ta)"
    })


@pytest.mark.dependency(depends=["test_preview_after_edit"])
def test_resend_partner_data(app, login):
    app.navigation.click_btn("Finish Project Setup")
    app.navigation.click_btn("Go to Project Page")
    # app.navigation.open_page("https://connect-stage.appen.com/qrp/core/partners/project_setup/view/4778")
    app.navigation.switch_to_frame("page-wrapper")
    app.ac_project.click_on_step('Invoice & Payment')
    app.verification.text_present_on_page("Manually reload partner data from ADAP.")
    app.navigation.click_btn("Resend Partner Data")
    app.verification.text_present_on_page("No jobs with this project_id")
