"""
If all cases failed, that means project is not created succesesfully, please rerun it.
This test cover Appen Connect new UI experience view and edit functionality.
As we need to create the whole project firstly, then check view and edit,
so all the cases are leveraging the same project created and in one file. There are lots of cases.
Basically, it covers:
1. Create a whole project.
2. View header and action information
3. View and edit 'OVERVIEW & TOOLS' page (including highlight information, external system, secure IP)
4. View and edit 'REGISTRATION & QUALIFICATION' page (including registration process and qualification process)
5. View and edit 'RECRUITMENT' page (including locale  tenants, hiring target, blocking rules,linked project, notes, custom demographic requirements etc)
6. View and edit 'INVOICE & PAYMENT' page
7. View and edit 'USER PROJECT PAGE' page
8. View and edit 'SUPPORT TEAM' page
9. Check project status transfer, from ready to enabled, to disabled
"""

import datetime
import time
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name, tomorrow_date
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.selenium_utils import find_elements
from faker import Faker

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

# pytestmark = [pytest.mark.regression_ac]


faker = Faker()
IP_ADDR = faker.ipv4()
URL = 'https://connect-stage.appen.com/qrp/core/partners/projects'
NEW_URL = 'https://connect-stage.appen.com'


@pytest.fixture(scope="module")
def create_project_for_view_and_edit(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    project_name = generate_project_name()
    app.ac_project.create_new_project()

    app.ac_project.overview.fill_out_fields(data={
        "Project Title": project_name[0],
        "Project Alias": "test " + project_name[0],
        "Project Description": "new experience test description",
        "Customer": app.ac_project.identify_customer(pytest.env),
        "Project Type": "Express",
        "Task Type": "Express",
        "Task Volume": "Very Low"
    })

    app.navigation.click_btn('Next: Registration and Qualification')
    if pytest.env == "prod":
        app.ac_project.registration.fill_out_fields(data={
            "Select Registration process": "Agnew registration",
            "Select Qualification process": "Aliso Qualification"})
    else:
        app.ac_project.registration.fill_out_fields(data={
            "Select Registration process": "Acac Register",
            "Select Qualification process": "Apple NDA"
        })

    app.navigation.click_btn('Next: Recruitment')
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Algeria", tenant='Appen Ltd. (Facility Employee)')
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Albania", tenant='Appen Ltd. (Facility Employee)')
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="United States of America", tenant='Appen Ltd. (Contractor)')
    tomorrow_date = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%m/%d/%Y")
    app.ac_project.recruitment.add_target(language='English', region='Algeria', restrict_country='Albania',
                                          deadline=tomorrow_date, target='12')
    app.ac_project.recruitment.fill_out_fields({"Blocking Rules": "1"})

    if pytest.env == 'prod':
        app.ac_project.recruitment.add_block_project("Name error api")
        app.ac_project.recruitment.click_permanent_btn("Name error api")
    else:
        app.ac_project.recruitment.add_block_project("Project NameQATest")
        app.ac_project.recruitment.click_permanent_btn("Project NameQATest")
    app.ac_project.recruitment.fill_out_fields({"Linked Projects": "1"})
    app.ac_project.recruitment.add_linked_project("Figure-Eight Testing")
    app.navigation.click_btn('Save')

    app.navigation.click_btn("Next: Invoice & Payment")
    app.ac_project.payment.fill_out_fields({
        "PROJECT WORKDAY TASK ID": "P23345",
        # "TASK CODE": 'P23345',
        "Rate Type": "By Task",
        "Project Business Unit": "CR",
        "Add Notes to Finance": "1",
        "Notes to Finance": "Test Notes to Finance"})
    app.navigation.click_btn("Add Pay Rate")
    app.ac_project.payment.fill_out_fields({"Custom Pay Rates": "1"})
    app.ac_project.payment.select_custom_pay_rates('English (Algeria)', 'Albania')
    app.ac_project.payment.fill_out_fields({"Spoken Fluency": "Fluent",
                                            "Written Fluency": "Fluent",
                                            "User Group": "All users",
                                            "Task Type": "Default",
                                            "Rate": 123
                                            }, action='Save')

    app.navigation.click_btn('Set Template')
    app.ac_project.payment.fill_out_fields({"Check PM Approve Level": "1"})
    app.ac_project.payment.choose_invoice_type('User self-reported', action='Save')
    app.navigation.click_btn('Save')

    app.navigation.click_btn('Next: Project Tools')
    app.ac_project.tools.fill_out_fields(data={
        "External System": "SWFH",
        "SWFH URL": "https://connect-stage.appen.com/qrp/core/partners/projects"
    })

    app.ac_project.tools.fill_out_fields(data={
        "Secure IP Access": "1",
        "Allowed IPs": IP_ADDR
    })
    app.navigation.click_btn('Save')

    # app.navigation.click_btn("Next: Project Access")
    # use default value on this page and click next
    app.navigation.click_btn("Next: User Project Page")

    app.ac_project.user_project.fill_out_fields({"Default Page Task": "Tasks",
                                                 "Available Skill Review": '1',
                                                 "ACAN Project": "1"
                                                 })
    app.navigation.click_btn('Save')

    app.navigation.click_btn("Next: Support Team")
    app.ac_project.support.fill_out_fields({"Support User Role": "Quality",
                                            "Member Name": "Support (Ac)"})

    app.navigation.click_btn('Save')

    app.navigation.click_btn("Next: Preview")
    app.navigation.click_btn("Finish Project Setup")
    app.navigation.click_btn("Go to Project Page")
    time.sleep(5)
    app.driver.switch_to.default_content()
    app.navigation.click_link('Projects')
    app.navigation.switch_to_frame("page-wrapper")
    app.project_list.filter_project_list_by(name=project_name[0])
    app.project_list.open_project_by_name(project_name[0])
    app.driver.switch_to.default_content()
    try:
        app.navigation.click_btn("View new experience")
        time.sleep(2)
    except:
        print("new UI")
    app.navigation.switch_to_frame("page-wrapper")
    return project_name


# ---------- View and edit 'OVERVIEW & TOOLS' page ---------
@pytest.mark.dependency()
def test_view_overview_and_tools_page_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Overview & tools')
    app.verification.current_url_contains('/project_setup/view')
    app.verification.text_present_on_page('Overview & Tools')
    app.verification.text_present_on_page('Project Setup')
    app.verification.text_present_on_page('Project Tools')
    original_secure_ip = app.ac_project.get_project_info_for_section('Secure IP Access')
    app.ac_project.verify_project_info({
        "Project Description": "new experience test description",
        "Type of Project": "Express",
        "Type of Task": "Express",
        "Task Volume": "Very Low",
        "External Project": "SWFH",
        "SWFH Url": URL,
        "Secure IP Access": original_secure_ip
    })


def test_view_highlight_information_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Overview & tools')
    assert app.ac_project.get_project_info_for_section('Status') == 'Ready'
    assert app.verification.text_present_on_page(
        'Your project is ready to be enabled. Click on “Enable Project” to start recruitment.')
    type_of_task = 'Express'
    type_of_project = 'Express'
    task_volume = 'Very Low'
    task = app.ac_project.get_project_info_for_section(type_of_task)
    assert type_of_project + ' project' in task
    assert task_volume + ' task volume' in task

    customer = app.ac_project.get_project_info_for_section('Customer')
    assert app.ac_project.identify_customer(pytest.env) in customer

    formatted_date = custom_strftime('%B %d, %Y', datetime.date.today())
    app.verification.text_present_on_page(formatted_date)
    app.verification.text_present_on_page('Appen Connect')
    app.navigation.click_link('Appen Connect')
    assert '/qrp/core/vendor/view/' in app.driver.current_url
    # need go back to new experience page for other test  cases
    app.navigation.click_link('Partner Home')
    app.navigation.switch_to_frame("page-wrapper")
    app.project_list.filter_project_list_by(name=create_project_for_view_and_edit[0])
    app.project_list.open_project_by_name(create_project_for_view_and_edit[0])
    app.driver.switch_to.default_content()
    try:
        app.navigation.click_btn("View new experience")
        time.sleep(2)
    except:
        print("new UI")
    app.navigation.switch_to_frame("page-wrapper")


@pytest.mark.dependency(depends=["test_view_overview_and_tools_page_new_ui"])
def test_view_info_in_edit_mode_new_ui(app, create_project_for_view_and_edit):
    original_secure_ip = app.ac_project.get_project_info_for_section('Secure IP Access')
    app.navigation.click_btn('Edit')
    assert app.ac_project.checkbox_by_text_is_selected_ac('Secure IP Access')
    assert app.ac_project.checkbox_by_text_is_selected_ac('External System')

    app.ac_project.overview.load_project(data={
        "Project Title": create_project_for_view_and_edit[0],
        "Project Alias": "test " + create_project_for_view_and_edit[0],
        "Project Description": "new experience test description",
        "Project Type": "Express",
        "Task Type": "Express",
        "Task Volume": "Very Low"
    })
    app.ac_project.tools.load_project(data={
        "External System": "SWFH",
        "SWFH URL": URL,
        "Allowed IPs": IP_ADDR
    })
    app.navigation.click_btn('Cancel')
    app.ac_project.verify_project_info({
        "Project Description": "new experience test description",
        "Type of Project": "Express",
        "Type of Task": "Express",
        "Task Volume": "Very Low",
        "External Project": "SWFH",
        "SWFH Url": URL,
        "Secure IP Access": original_secure_ip
    })


@pytest.mark.dependency(depends=["test_view_info_in_edit_mode_new_ui"])
def test_remove_swfh_url_new_ui(app, create_project_for_view_and_edit):
    app.navigation.click_btn('Edit')
    assert app.ac_project.checkbox_by_text_is_selected_ac('External System')
    app.ac_project.tools.remove_data_from_fields({
        "SWFH URL": URL
    })
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page(
        'Secure Work From Home Project External URL must be configured for SWFH project')
    app.ac_project.close_error_msg()


@pytest.mark.dependency(depends=["test_remove_swfh_url_new_ui"])
def test_uncheck_external_system_new_ui(app, create_project_for_view_and_edit):
    # uncheck external system checkbox and save the data
    app.ac_project.tools.fill_out_fields(data={
        "External System checkbox": "1"
    })
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page('Cannot set a project to non-external while it has external experiments.')
    app.ac_project.close_error_msg()


@pytest.mark.dependency(depends=["test_uncheck_external_system_new_ui"])
def test_edit_save_external_system_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.tools.fill_out_fields(data={
        "External System checkbox": "1",
        "SWFH URL": NEW_URL
    })
    app.navigation.click_btn('Save Changes')
    time.sleep(2)
    app.ac_project.verify_project_info({
        "External Project": "SWFH",
        "SWFH Url": NEW_URL,
    })


@pytest.mark.dependency(depends=["test_edit_save_external_system_new_ui"])
def test_add_secure_ip(app, create_project_for_view_and_edit):
    original_secure_ip = app.ac_project.get_project_info_for_section('Secure IP Access')
    ip_being_added = faker.ipv4()
    new_secure_ip = original_secure_ip + ", " + ip_being_added
    app.navigation.click_btn('Edit')
    app.navigation.click_btn('Add Other IP')
    # save change without input ip, will show error message
    app.navigation.click_btn('Save Changes')
    app.ac_project.close_error_msg()
    app.verification.text_present_on_page('If "Secure IP Access" is checked this is a required field.')

    el = find_elements(app.driver, "//input[contains(@name, 'ipAddress')]")
    el[-1].send_keys(ip_being_added)
    time.sleep(1)
    app.navigation.click_btn('Save Changes')
    app.ac_project.verify_project_info({
        "Secure IP Access": new_secure_ip
    })


@pytest.mark.dependency(depends=["test_add_secure_ip"])
def test_add_multiple_secure_ip_new_ui(app, create_project_for_view_and_edit):
    secure_ip = app.ac_project.get_project_info_for_section('Secure IP Access')
    app.navigation.click_btn('Edit')
    for i in range(5):
        ip_being_added = faker.ipv4()
        secure_ip = secure_ip + ", " + ip_being_added
        app.ac_project.tools.add_allowed_ip(ip_being_added)
    app.navigation.click_btn('Save Changes')
    app.ac_project.verify_project_info({
        "Secure IP Access": secure_ip
    })


@pytest.mark.dependency(depends=["test_add_multiple_secure_ip_new_ui"])
def test_remove_secure_ip_access_new_ui(app, create_project_for_view_and_edit):
    app.navigation.click_btn('Edit')
    # while 'Secure IP Access' checkbox is checked, remove the ip and click save, error message will show on the page
    app.ac_project.tools.remove_data_from_fields({
        "Allowed IPs": IP_ADDR
    })
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page('If "Secure IP Access" is checked this is a required field.')
    app.ac_project.close_error_msg()
    # uncheck checkbox and save the data
    app.ac_project.tools.fill_out_fields(data={
        "Secure IP Access": "1"
    })
    app.navigation.click_btn('Save Changes')
    # due to bug https://appen.atlassian.net/browse/ACE-6063, comment out below code until bug is fixed
    # app.ac_project.verify_project_info({
    #     "Secure IP Access": "Not enabled"
    # })


# ---------- View project header and action information ---------
@pytest.mark.dependency()
def test_view_header_information_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Overview & tools')
    app.verification.text_present_on_page(create_project_for_view_and_edit[0])
    current_url = app.driver.current_url
    index = current_url.find('view')
    global project_id
    project_id = current_url[index + 5:]
    header_info = app.ac_project.get_header_info()
    assert 'ID' in header_info
    assert ("test " + create_project_for_view_and_edit[0]).lower() in header_info.lower()
    assert project_id in header_info


@pytest.mark.dependency(depends=["test_view_header_information_new_ui"])
def test_view_actions_in_header_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Overview & tools')
    app.ac_project.get_action_in_header_info('Clone Project')
    app.ac_project.get_action_in_header_info('Delete')
    user_project = app.ac_project.get_action_in_header_info('User Project Page')
    user_project.click()
    time.sleep(2)
    current_url = app.driver.current_url
    assert '/qrp/core/vendors/project_site/' + project_id in current_url
    # need go back to new experience page for other test  cases
    app.navigation.click_link('Partner Home')
    app.navigation.switch_to_frame("page-wrapper")
    app.project_list.filter_project_list_by(name=create_project_for_view_and_edit[0])
    app.project_list.open_project_by_name(create_project_for_view_and_edit[0])
    app.driver.switch_to.default_content()
    try:
        app.navigation.click_btn("View new experience")
        time.sleep(2)
    except:
        print("new UI")
    app.navigation.switch_to_frame("page-wrapper")


# ---------- View and edit 'REGISTRATION & QUALIFICATION' page ---------
@pytest.mark.dependency()
def test_view_registration_and_qualification_page_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Registration & Qualification')
    app.verification.text_present_on_page('Registration & Qualification')
    app.verification.text_present_on_page('Registration Process')
    app.verification.text_present_on_page('Qualification Process')
    if pytest.env == "prod":
        app.ac_project.verify_project_info({
            "Agnew registration": "1 - Sign Document",
            "Aliso Qualification": "1 - Sign Document"})
    else:
        app.ac_project.verify_project_info({
            "Acac Register": "1 - Sign Document",
            "Apple NDA": "1 - Sign Document"})


def test_view_metrics_registration_and_qualification_page_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Registration & Qualification')
    app.verification.text_present_on_page('Registered')
    app.verification.text_present_on_page('% passed per step')
    app.verification.text_present_on_page('Qualified')
    app.verification.text_present_on_page('In Progress')
    app.verification.text_present_on_page('Rejected')
    app.verification.text_present_on_page('Abandoned')


@pytest.mark.dependency(depends=["test_view_registration_and_qualification_page_new_ui"])
def test_click_project_qualifications_link_new_ui(app, create_project_for_view_and_edit):
    app.navigation.click_link('Project Qualifications')
    app.verification.text_present_on_page('Project Qualifications')
    app.verification.current_url_contains('/recruiting/project_qualifications')
    app.navigation.click_link('Waiting to be screened +')
    # need go back to new experience page for other test  cases
    app.navigation.click_link('Partner Home')
    app.navigation.switch_to_frame("page-wrapper")
    app.project_list.filter_project_list_by(name=create_project_for_view_and_edit[0])
    app.project_list.open_project_by_name(create_project_for_view_and_edit[0])
    app.driver.switch_to.default_content()
    try:
        app.navigation.click_btn("View new experience")
        time.sleep(2)
    except:
        print("new UI")
    app.navigation.switch_to_frame("page-wrapper")


@pytest.mark.dependency(depends=["test_click_project_qualifications_link_new_ui"])
def test_edit_registration_and_qualification_page_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Registration & Qualification')
    app.navigation.click_btn('Edit')
    app.verification.button_is_displayed('Cancel')
    app.verification.button_is_displayed('Save Changes')
    app.verification.link_is_displayed('Project Qualifications', is_not=False)
    app.ac_project.registration.fill_out_fields(data={
        "Select Registration process": "Apple NDA",
        "Select Qualification process": "CC Qualification"
    })
    app.navigation.click_btn('Save Changes')
    app.ac_project.verify_project_info({
        "Apple NDA": "1 - Complete Additional Attributes",
        "CC Qualification": "1 - Sign Document"})


# ---------- View and edit 'RECRUITMENT' page ---------
def test_view_recruitment_page_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.verification.text_present_on_page('Recruitment')
    app.verification.text_present_on_page('Locale Tenants')
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="Albania", tenant='Appen Ltd.',
                                                                 tenant_type='Facility Employee', is_view_mode=True)
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="Algeria", tenant='Appen Ltd.',
                                                                 tenant_type='Facility Employee', is_view_mode=True)

    app.verification.text_present_on_page('Hiring Targets')
    formatted_date = (custom_strftime('%b {S}, %Y', (datetime.date.today() + datetime.timedelta(days=30))))
    app.ac_project.recruitment.verify_regular_hiring_target_row_present_on_page(language='English',
                                                                                region='Algeria',
                                                                                restrict_country='Albania',
                                                                                assigned_owner='.',
                                                                                deadline=formatted_date, target='12')

    app.verification.text_present_on_page('Custom Demographic Requirements')
    app.ac_project.verify_project_info({
        "Blocking Rules": "Project NameQATest (Permanent)",
        "Linked Projects": "Figure-Eight Testing"
    })


# Local Tenants
def test_add_tenant_required_fields_in_edit_mode_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    # see error message, maybe a bug on stage env
    app.ac_project.close_error_msg()
    app.navigation.click_btn('Add Tenant')
    app.verification.text_present_on_page("Country is a required field.", is_not=False)
    app.verification.text_present_on_page("Tenant is a required field.", is_not=False)
    app.ac_project.recruitment.click_save_add_tenant()
    app.verification.text_present_on_page("Country is a required field.")
    app.verification.text_present_on_page("Tenant is a required field.")
    app.ac_project.recruitment.click_cancel_add_tenant()


def test_add_local_tenant_cancel_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Andorra", tenant='Appen Ltd. (Contractor)', action=None)
    app.ac_project.recruitment.click_cancel_add_tenant()
    app.ac_project.recruitment.verify_locale_tenant_is_displayed("Andorra", "Appen Ltd.", "Contractor",
                                                                 is_not=False)


def test_add_multiple_local_tenants_save_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Andorra", tenant='Appen Ltd. (Facility Employee)')
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Anguilla", tenant='Appen Ltd. (Facility Employee)')
    app.navigation.click_btn('Save Changes')
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="Andorra", tenant='Appen Ltd.',
                                                                 tenant_type='Facility Employee', is_view_mode=True)
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="Anguilla", tenant='Appen Ltd.',
                                                                 tenant_type='Facility Employee', is_view_mode=True)


@pytest.mark.dependency()
def test_add_tenant_all_countries_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="All Countries", tenant='Appen Ltd. (Facility Employee)')
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="All Countries", tenant='Appen Ltd.',
                                                                 tenant_type='Facility Employee', is_view_mode=True)


@pytest.mark.dependency(depends=["test_add_tenant_all_countries_new_ui"])
def test_fail_edit_tenant_all_countries_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.edit_tenant("All Countries", "Appen Ltd.", "Facility Employee",
                                           "Bulgaria", 'Appen Ltd. (Contractor)')
    app.verification.text_present_on_page('Failed to save Locale Tenant')
    app.verification.text_present_on_page(
        'You cannot change a Locale Tenant from a project for a Country that still has Hiring Targets specified for the Restrict to Country.  You must first remove the Hiring Targets for this Restrict to Country.')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.click_cancel_add_tenant()
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="All Countries", tenant='Appen Ltd.',
                                                                 tenant_type='Facility Employee')


def test_fail_edit_tenant_with_hiring_target_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    # see error message, close it if any
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.edit_tenant("Albania", "Appen Ltd.", "Facility Employee", "Albania",
                                           'Appen Ltd. (Contractor)')
    app.verification.text_present_on_page('Failed to save Locale Tenant')
    app.verification.text_present_on_page(
        'You cannot change a Locale Tenant from a project for a Country that still has Hiring Targets specified for the Restrict to Country.  You must first remove the Hiring Targets for this Restrict to Country.')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.click_cancel_add_tenant()
    app.ac_project.recruitment.verify_locale_tenant_is_displayed("Albania", "Appen Ltd.", "Facility Employee")


def test_edit_tenant_successfully_without_hiring_target_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Bahrain", tenant='Appen Ltd. (Facility Employee)')
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="Bahrain", tenant='Appen Ltd.',
                                                                 tenant_type='Facility Employee')
    app.ac_project.recruitment.edit_tenant("Bahrain", "Appen Ltd.", "Facility Employee", "Bulgaria",
                                           'Appen Ltd. (Contractor)')
    app.ac_project.recruitment.verify_locale_tenant_is_displayed("Bulgaria", "Appen Ltd.", "Contractor")
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="Bahrain", tenant='Appen Ltd.',
                                                                 tenant_type='Facility Employee', is_not=False)


@pytest.mark.dependency(depends=["test_add_tenant_all_countries_new_ui"])
def test_fail_delete_tenant_all_countries_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.delete_tenant("All Countries", "Appen Ltd.", "Facility Employee")
    app.verification.text_present_on_page('Error')
    app.verification.text_present_on_page(
        'You cannot delete a Locale Tenant from a project for a Country that still has Hiring Targets specified for the Restrict to Country.  You must first remove the Hiring Targets for this Restrict to Country.')
    app.ac_project.close_error_msg()


def test_delete_tenant_successfully_without_hiring_target_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Argentina", tenant='Appen Ltd. (Facility Employee)')
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="Argentina", tenant='Appen Ltd.',
                                                                 tenant_type='Facility Employee')
    app.ac_project.recruitment.delete_tenant("Argentina", "Appen Ltd.", "Facility Employee")
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="Argentina", tenant='Appen Ltd.',
                                                                 tenant_type='Facility Employee', is_not=False)


# Hiring Targets
def test_add_hiring_target_required_field_in_edit_mode_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.navigation.click_btn('Add Target')
    app.ac_project.recruitment.click_save_ht()
    app.verification.text_present_on_page("Locale Language is a required field.")
    app.verification.text_present_on_page("Locale Region is a required field.")
    app.verification.text_present_on_page("Restrict to Country is a required field.")
    app.verification.text_present_on_page("Hiring Deadline is a required field.")
    app.verification.text_present_on_page("Target is a required field.")
    app.ac_project.recruitment.click_cancel_hiring_target()


@pytest.mark.dependency()
def test_add_hiring_target_in_edit_mode_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    formatted_date = (custom_strftime('%b {S}, %Y', (datetime.date.today() + datetime.timedelta(days=1))))
    app.ac_project.recruitment.add_target(language='Achinese', region='All Countries',
                                          restrict_country='All Countries',
                                          deadline=tomorrow_date(), target='12')
    app.navigation.click_btn('Save Changes')
    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='Achinese',
                                                                        loc_dialect_from='All Countries',
                                                                        rest_to_country='All Countries',
                                                                        deadline=formatted_date, target='12')


@pytest.mark.dependency(depends=["test_add_hiring_target_in_edit_mode_new_ui"])
def test_copy_hiring_target_error_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.click_copy_target("Achinese", "All Countries", "All Countries")
    app.ac_project.recruitment.click_save_ht()
    app.verification.text_present_on_page(
        "You have a very similar target already included. If you need to increase a target, consider editing it.")
    app.ac_project.recruitment.close_error_msg()


@pytest.mark.dependency(depends=["test_copy_hiring_target_error_new_ui"])
def test_edit_hiring_target_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.recruitment.fill_out_fields({"Locale Language": "Kashmiri",
                                                "Language Region": "India"})
    app.ac_project.recruitment.click_save_ht()
    app.navigation.click_btn('Save Changes')
    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='Kashmiri',
                                                                        loc_dialect_from='India',
                                                                        rest_to_country='All Countries', target='12')


@pytest.mark.dependency(depends=["test_edit_hiring_target_new_ui"])
def test_delete_hiring_target_new_ui(app, create_project_for_view_and_edit):
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.delete_target("Kashmiri", "India", "All Countries")
    formatted_date = (custom_strftime('%b {S}, %Y', (datetime.date.today() + datetime.timedelta(days=1))))
    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='Kashmiri',
                                                                        loc_dialect_from='India',
                                                                        rest_to_country='All Countries',
                                                                        deadline=formatted_date,
                                                                        target='12', row_is_present=False)


# Blocking Rules
@pytest.mark.dependency()
def test_add_blocking_rules_required_fields_in_edit_mode_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.navigation.click_btn('Add Other Project')
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page('Project is a required field.')


@pytest.mark.dependency(depends=["test_add_blocking_rules_required_fields_in_edit_mode_new_ui"])
def test_add_multiple_blocking_rules_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.recruitment.add_block_project("A A Quiz", multiple_projects=True)
    app.ac_project.recruitment.click_permanent_btn("A A Quiz")
    app.navigation.click_btn('Add Other Project')
    app.ac_project.recruitment.add_block_project("Acac Test", multiple_projects=True)
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page('A A Quiz')
    app.verification.text_present_on_page('Acac Test')


def test_delete_blocking_rules_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.navigation.click_btn('Add Other Project')
    app.ac_project.recruitment.add_block_project("Action Beans", multiple_projects=True)
    app.ac_project.recruitment.delete_block_project("Action Beans")
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page("Action Beans", is_not=False)


# Linked Projects
@pytest.mark.dependency()
def test_linked_projects_required_fields_in_edit_mode_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()

    el = find_elements(app.driver, "//button[text()='Add Other Project']")
    el[1].click()
    time.sleep(1)
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page('Project is a required field.')


@pytest.mark.dependency(depends=["test_linked_projects_required_fields_in_edit_mode_new_ui"])
def test_add_multiple_linked_projects_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.recruitment.add_linked_project("Apple Test", multiple_projects=True, is_edit_mode=True)
    app.ac_project.recruitment.add_linked_project("Automation", multiple_projects=True, is_edit_mode=True)
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page('Apple Test')
    app.verification.text_present_on_page('Automation')


def test_delete_linked_projects_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.add_linked_project("A A Transcription", multiple_projects=True, is_edit_mode=True)
    app.ac_project.recruitment.delete_linked_project("A A Transcription")
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page("A A Transcription", is_not=False)


# Add Notes to Recruiting Team
@pytest.mark.dependency()
def test_recruiting_team_notes_required_field_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.fill_out_fields({"Add Notes to Recruiting Team": "1"})
    app.navigation.click_btn("Save Changes")
    app.verification.text_present_on_page('When \"Add Notes to Recruiting Team\" is checked this is a required field.')


@pytest.mark.dependency(depends=["test_recruiting_team_notes_required_field_new_ui"])
def test_add_recruiting_team_notes_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.recruitment.fill_out_fields({"Recruiting Notes": "Test Notes to Recruiting Team"})
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page('When \"Add Notes to Recruiting Team\" is checked this is a required field.',
                                          is_not=False)
    app.ac_project.verify_project_info({
        "Notes to Recruiting Team": "Test Notes to Recruiting Team"
    })


# https://appen.atlassian.net/browse/QED-1816
# Edit Custom Demographic Requirements
@pytest.mark.dependency()
def test_demographics_required_fields_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    assert not app.ac_project.checkbox_by_text_is_selected_ac('Add Custom Demographic Requirements')
    app.ac_project.recruitment.fill_out_fields(data={
        "Add Custom Demographic Requirements": "1"
    })
    app.navigation.click_btn('Set Demographics')
    app.verification.text_present_on_page('Demographic Requirements Setup')
    app.verification.text_present_on_page('DEMOGRAPHICS TYPE')
    app.verification.text_present_on_page('VIEW AS')
    app.verification.text_present_on_page('SELECT PARAMETERS')
    app.verification.text_present_on_page('Requirements by group')
    app.verification.text_present_on_page('Aggregated requirements', is_not=False)

    params_selected = app.ac_project.recruitment.get_current_num_of_selected_params_demographic()
    assert params_selected == '0'
    app.navigation.click_btn('Next: Distribution')
    app.verification.text_present_on_page('Select at least one requirement')


@pytest.mark.dependency(depends=["test_demographics_required_fields_new_ui"])
def test_demographics_requirements_by_group_percentage_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.recruitment.set_up_demographic_requirements(params=['Gender', 'Device'])
    assert app.ac_project.recruitment.get_current_num_of_selected_params_demographic() == '2'
    assert app.ac_project.recruitment.get_current_selected_params_demographic() == ['Gender', 'Device']

    app.ac_project.recruitment.delete_selected_demographic_param('Device')
    assert app.ac_project.recruitment.get_current_num_of_selected_params_demographic() == '1'
    assert app.ac_project.recruitment.get_current_selected_params_demographic() == ['Gender']
    app.navigation.click_btn('Next: Distribution')
    app.ac_project.recruitment.distribute_demograph({'Female': 60, 'Male': 40})
    app.navigation.click_btn('Save Requirements')
    assert app.ac_project.recruitment.get_saved_requirements() == 'Gender'
    app.navigation.click_btn('Save Changes')


@pytest.mark.dependency(depends=["test_demographics_requirements_by_group_percentage_new_ui"])
def test_demographics_requirements_by_group_number_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.click_clear_saved_req()
    app.navigation.click_btn('Set Demographics')
    app.ac_project.recruitment.set_up_demographic_requirements(d_type='Requirements by group', view='NUMBER',
                                                               params=['Gender'])
    assert app.ac_project.recruitment.get_current_num_of_selected_params_demographic() == '1'
    assert app.ac_project.recruitment.get_current_selected_params_demographic() == ['Gender']
    app.navigation.click_btn('Next: Distribution')
    app.ac_project.recruitment.click_distribute_evenly()
    app.navigation.click_btn('Save Requirements')
    assert app.ac_project.recruitment.get_saved_requirements() == 'Gender'
    app.navigation.click_btn('Save Changes')


@pytest.mark.dependency(depends=["test_demographics_requirements_by_group_number_new_ui"])
def test_demographics_aggregated_requirements_percentage_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.click_clear_saved_req()
    app.navigation.click_btn('Set Demographics')
    app.ac_project.recruitment.set_up_demographic_requirements(d_type='Aggregated requirements', view='PERCENTAGE',
                                                               params=['Gender'])
    assert app.ac_project.recruitment.get_current_num_of_selected_params_demographic() == '1'
    assert app.ac_project.recruitment.get_current_selected_params_demographic() == ['Gender']
    app.navigation.click_btn('Next: Distribution')
    app.ac_project.recruitment.distribute_demograph({'Female': 60, 'Male': 40})
    app.navigation.click_btn('Save Requirements')
    # seems bug here, it does not show aggregated requirement, https://appen.atlassian.net/browse/ACE-6158
    # assert app.ac_project.recruitment.get_saved_requirements(demographics_type='AGGREGATED REQUIREMENTS') == 'Gender'
    app.navigation.click_btn('Save Changes')


@pytest.mark.dependency(depends=["test_demographics_aggregated_requirements_percentage_new_ui"])
def test_demographics_aggregated_requirements_number_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.click_clear_saved_req()
    app.navigation.click_btn('Set Demographics')
    app.ac_project.recruitment.set_up_demographic_requirements(d_type='Aggregated requirements', view='NUMBER',
                                                               params=['Gender'])
    assert app.ac_project.recruitment.get_current_num_of_selected_params_demographic() == '1'
    assert app.ac_project.recruitment.get_current_selected_params_demographic() == ['Gender']
    app.navigation.click_btn('Next: Distribution')
    app.ac_project.recruitment.click_distribute_evenly()
    app.navigation.click_btn('Save Requirements')
    # bug https://appen.atlassian.net/browse/ACE-6158
    # assert app.ac_project.recruitment.get_saved_requirements(demographics_type='AGGREGATED REQUIREMENTS') == 'Gender'
    app.navigation.click_btn('Save Changes')


@pytest.mark.dependency(depends=["test_demographics_aggregated_requirements_number_new_ui"])
def test_edit_demographics_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.click_edit_saved_req()
    app.verification.text_present_on_page('Demographic Requirements Setup')
    app.verification.text_present_on_page('Save Requirements')

    app.ac_project.recruitment.distribute_demograph({'Female': 2, 'Male': 6})
    app.navigation.click_btn('Save Requirements')

    app.ac_project.recruitment.click_edit_saved_req()
    assert app.ac_project.recruitment.get_current_distribution() == {'GENDER': {'Female': '2', 'Male': '6'}}
    app.navigation.click_btn('Save Requirements')
    app.navigation.click_btn('Save Changes')


# comment it out due to https://appen.atlassian.net/browse/ACE-7318
@pytest.mark.skip(reason='bug ACE-7318')
@pytest.mark.dependency(depends=["test_edit_demographics_new_ui"])
def test_view_demographics_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Demographic Distribution')
    app.verification.text_present_on_page('Demographic Distribution')
    app.verification.text_present_on_page('Requirements by group (Gender)')
    app.verification.text_present_on_page('CUSTOM DEMOGRAPHICS')
    app.verification.text_present_on_page('TOTAL BY CATEGORY')
    app.ac_project.recruitment.verify_demografics_header_view(type="Gender", target='ALL > ACE (ALL)',
                                                              engaged='(0% of 100%)')
    app.ac_project.recruitment.verify_demografics_row_view(type="Female", engaged='0% of 2%')
    app.ac_project.recruitment.verify_demografics_row_view(type="Male", engaged='0% of 6%')
    app.ac_project.recruitment.verify_demographics_select_view(view="TOTAL BY CATEGORY")

    app.ac_project.recruitment.verify_demografics_header_view(type="Gender", target='ALL > ACE (ALL)',
                                                              engaged='(0 of 12)')
    app.ac_project.recruitment.verify_demografics_row_view(type="Female", engaged='0%')
    app.ac_project.recruitment.verify_demografics_row_view(type="Male", engaged='0%')

    app.ac_project.recruitment.verify_demografics_header_view(type="Age Range", target='ALL > ACE (ALL)',
                                                              engaged='(0 of 12)')
    app.ac_project.recruitment.verify_demografics_row_view(type="18-24", engaged='0%')
    app.ac_project.recruitment.verify_demografics_row_view(type="25-34", engaged='0%')
    app.ac_project.recruitment.verify_demografics_row_view(type="35-44", engaged='0%')
    app.ac_project.recruitment.verify_demografics_row_view(type="45-54", engaged='0%')
    app.ac_project.recruitment.verify_demografics_row_view(type="55+", engaged='0%')

    app.ac_project.recruitment.verify_demografics_header_view(type="Device", target='ALL > ACE (ALL)',
                                                              engaged='(0 of 12)')
    app.ac_project.recruitment.verify_demografics_row_view(type="Android", engaged='0%')
    app.ac_project.recruitment.verify_demografics_row_view(type="iOS", engaged='0%')

    app.ac_project.recruitment.verify_demographics_select_view(view="CUSTOM DEMOGRAPHICS")
    app.verification.text_present_on_page('Demographic Distribution')
    app.ac_project.recruitment.close_modal_window()


# ---------- View and edit 'INVOICE & PAYMENT' page ---------
@pytest.mark.dependency()
def test_view_invoice_and_payment_page_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Invoice & Payment')
    app.verification.text_present_on_page('Invoice & Payment')
    app.verification.text_present_on_page('Pay Rates Setup')
    app.ac_project.verify_project_info({
        "PROJECT WORKDAY TASK ID": "Task Code: P23345",
        "Rate Type": "By Task",
        "Project Business Unit": "CR",
        "Productivity Data": "Not enabled",
        "Notes to Finance": "Test Notes to Finance"
    })
    app.ac_project.payment.verify_pay_rate_is_present_on_page(hiring_target='English (Algeria)',
                                                              input_fluency='Fluent', input_grp='All users',
                                                              input_work='Default', input_taskid='.',
                                                              input_rate='$1.23')


@pytest.mark.dependency(depends=["test_view_invoice_and_payment_page_new_ui"])
def test_invoice_and_payment_required_fields_in_edit_mode_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Invoice & Payment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.payment.remove_data_from_fields({
        "TASK CODE": 'P23345',
        "Notes to Finance": 'Test Notes to Finance'
    })
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page('When "Add Notes to Finance" is checked this is a required field.')
    app.verification.text_present_on_page('Workday Task Id is a required field.')


@pytest.mark.dependency(depends=["test_invoice_and_payment_required_fields_in_edit_mode_new_ui"])
def test_edit_invoice_and_payment_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.payment.fill_out_fields({"TASK CODE": 'P23333',
                                            "Rate Type": "Hourly",
                                            "Project Business Unit": "LR",
                                            "Available Productivity Data": "1",
                                            "Notes to Finance": "Updated notes"})
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page('When "Add Notes to Finance" is checked this is a required field.',
                                          is_not=False)
    app.ac_project.verify_project_info({
        "PROJECT WORKDAY TASK ID": "Task Code: P23333",
        "Rate Type": "Hourly",
        "Project Business Unit": "LR",
        "Productivity Data": "Available",
        "Notes to Finance": "Updated notes"
    })


@pytest.mark.dependency()
def test_add_custom_pay_rates_required_fields_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Invoice & Payment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.navigation.click_btn("Add Pay Rate")
    app.ac_project.payment.fill_out_fields({"Custom Pay Rates": "1"})
    app.navigation.click_btn('Save')
    app.verification.text_present_on_page('Hiring Target is a required field.')


@pytest.mark.dependency(depends=["test_add_custom_pay_rates_required_fields_new_ui"])
def test_add_new_custom_pay_rates_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.payment.select_custom_pay_rates('English (Algeria)', 'Albania')
    app.ac_project.payment.fill_out_fields({"Spoken Fluency": "Beginner",
                                            "Written Fluency": "Beginner",
                                            "User Group": "Aqa novatics",
                                            "Task Type": "Default",
                                            "Rate": 333
                                            }, action='Save')
    app.navigation.click_btn('Save Changes')
    app.ac_project.payment.verify_pay_rate_is_present_on_page(hiring_target='English (Algeria)',
                                                              input_fluency='Beginner', input_grp='Aqa novatics',
                                                              input_work='Default', input_taskid='.',
                                                              input_rate='$3.33')


@pytest.mark.dependency()
def test_copy_customer_payrates_already_exist_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Invoice & Payment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.payment.click_copy_pay_rate(hiring_target='English (Algeria)Albania',
                                               input_fluency='Fluent', input_grp='All users',
                                               input_work='Default', input_taskid='.',
                                               input_rate='$1.23')
    app.ac_project.payment.fill_out_fields({"Spoken Fluency": "Near Native",
                                            "Written Fluency": "Near Native",
                                            "Rate": 188
                                            }, action='Save')
    app.verification.text_present_on_page('Project Pay Rate already exists')
    app.ac_project.close_error_msg()
    app.ac_project.payment.click_cancel_copy_pay_rate()
    app.navigation.click_btn('Cancel')


@pytest.mark.skip(reason='no task type judgement available, only default task type')
@pytest.mark.dependency(depends=["test_copy_customer_payrates_already_exist_new_ui"])
def test_copy_customer_payrates_successfully_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.payment.fill_out_fields({"Task Type": "Judgement",
                                            }, action='Save')
    app.verification.text_present_on_page('Project Pay Rate already exists', is_not=False)
    app.navigation.click_btn('Save Changes')
    app.ac_project.payment.verify_pay_rate_is_present_on_page(hiring_target='English (Algeria)',
                                                              input_fluency='Near Native', input_grp='All users',
                                                              input_work='Judgement',
                                                              input_taskid='.',
                                                              input_rate='$1.88')


@pytest.mark.dependency()
def test_edit_customer_payrates_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Invoice & Payment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.payment.click_edit_pay_rate(hiring_target='English (Algeria)Albania',
                                               input_fluency='Fluent', input_grp='All users',
                                               input_work='Default', input_taskid='.',
                                               input_rate='$1.23')
    app.ac_project.payment.fill_out_fields({"Rate": 155}, action='Save')
    app.navigation.click_btn('Save Changes')
    app.ac_project.payment.verify_pay_rate_is_present_on_page(hiring_target='English (Algeria)',
                                                              input_fluency='Fluent', input_grp='All users',
                                                              input_work='Default', input_taskid='.',
                                                              input_rate='$1.55')


@pytest.mark.dependency(depends=["test_copy_customer_payrates_successfully_new_ui"])
def test_delete_customer_payrates_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Invoice & Payment')
    app.navigation.click_btn('Edit')
    app.ac_project.payment.delete_pay_rate(hiring_target='English (Algeria)Albania',
                                           input_fluency='Fluent', input_grp='All users',
                                           input_work='Default', input_taskid='.',
                                           input_rate='$1.55')
    app.verification.text_present_on_page(
        "You cannot delete the rate for the system ALL USERS group while there are still rates defined for other groups in the same locale.")
    app.navigation.click_btn("Cancel")


# ---------- View and edit 'USER PROJECT PAGE' page ---------
@pytest.mark.dependency()
def test_user_project_page_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.user_project.click_user_project_page()
    app.verification.text_present_on_page('User Project Page')
    app.ac_project.verify_project_info({
        "Default Page Task": "Tasks"
    })
    app.verification.text_present_on_page('Available')
    app.verification.text_present_on_page('Yes')


@pytest.mark.dependency(depends=["test_user_project_page_new_ui"])
def test_edit_user_project_page_new_ui(app):
    app.ac_project.user_project.click_user_project_page()
    app.verification.text_present_on_page('User Project Page')
    app.navigation.click_btn('Edit')
    assert app.ac_project.checkbox_by_text_is_selected_ac('Available Skill Review')
    assert app.ac_project.checkbox_by_text_is_selected_ac('ACAN Project')
    app.ac_project.user_project.fill_out_fields(data={
        "Available Skill Review": "1",
        "ACAN Project": "1"
    })
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page('Not available')
    app.verification.text_present_on_page('No')


# ---------- View and edit 'SUPPORT TEAM' page ---------
def test_view_support_team_page_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Support Team')
    app.verification.text_present_on_page('Support Team')
    app.ac_project.support.verify_support_team_information_is_displayed(user_role='Quality',
                                                                        member_name='Support (Ac)',
                                                                        phone_number='+11111111111',
                                                                        email='acsupport@appen.com')


# https://appen.atlassian.net/browse/QED-1821
def test_add_team_member_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Support Team')
    app.navigation.click_btn('Edit')
    app.navigation.click_btn('Add Member')
    # click save without select user role and member name
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page('User Role is a required field.')
    app.verification.text_present_on_page('Member name is a required field.')
    app.ac_project.close_error_msg()
    # select user role and member name and save info
    app.ac_project.support.fill_out_fields(data={"Support User Role": "Finance",
                                                 "Member Name": "Support (Ac)"},
                                           add_more_members=True
                                           )
    app.navigation.click_btn('Save Changes')
    app.ac_project.support.verify_support_team_information_is_displayed(user_role='Finance',
                                                                        member_name='Support (Ac)',
                                                                        phone_number='+11111111111',
                                                                        email='acsupport@appen.com')


def test_add_multiple_team_members_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Support Team')
    app.navigation.click_btn('Edit')
    user_roles = ['Human Resources', 'Support', 'Engineering']
    for i in range(3):
        app.navigation.click_btn('Add Member')
        app.ac_project.support.fill_out_fields(data={"Support User Role": user_roles[i],
                                                     "Member Name": "Support (Ac)"},
                                               add_more_members=True
                                               )
    app.navigation.click_btn('Save Changes')
    app.ac_project.support.verify_support_team_information_is_displayed(user_role='Human Resources',
                                                                        member_name='Support (Ac)',
                                                                        phone_number='+11111111111',
                                                                        email='acsupport@appen.com')
    app.ac_project.support.verify_support_team_information_is_displayed(user_role='Support',
                                                                        member_name='Support (Ac)',
                                                                        phone_number='+11111111111',
                                                                        email='acsupport@appen.com')
    app.ac_project.support.verify_support_team_information_is_displayed(user_role='Engineering',
                                                                        member_name='Support (Ac)',
                                                                        phone_number='+11111111111',
                                                                        email='acsupport@appen.com')


def test_delete_team_member_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Support Team')
    app.navigation.click_btn('Edit')
    app.navigation.click_btn('Add Member')
    app.ac_project.support.fill_out_fields(data={"Support User Role": 'Project Manager',
                                                 "Member Name": "Support (Ac)"},
                                           add_more_members=True
                                           )
    app.ac_project.support.delete_support_team_member()
    app.navigation.click_btn('Save Changes')
    time.sleep(2)
    app.ac_project.support.verify_support_team_information_is_displayed(user_role='Project Manager',
                                                                        member_name='Support (Ac)',
                                                                        phone_number='+11111111111',
                                                                        email='acsupport@appen.com', is_not=False)


# ---------- Test project status change ---------
# https://appen.atlassian.net/browse/QED-1805
@pytest.mark.dependency()
def test_status_change_from_ready_to_enabled_new_ui(app, create_project_for_view_and_edit):
    app.ac_project.click_on_step('Overview & tools')
    assert app.ac_project.get_project_info_for_section('Status') == 'Ready'
    app.verification.text_present_on_page('Your project is ready to be enabled. '
                                          'Click on “Enable Project” to start recruitment.')
    app.navigation.click_btn('Enable Project')
    assert app.ac_project.get_project_info_for_section('Status') == 'Enabled'
    app.verification.text_present_on_page('Your project is now running and recruitment is in progress.')


@pytest.mark.dependency(depends=["test_status_change_from_ready_to_enabled_new_ui"])
def test_status_change_from_enabled_to_disabled_new_ui(app, create_project_for_view_and_edit):
    app.navigation.click_btn('Disable Project')
    assert app.ac_project.get_project_info_for_section('Status') == 'Disabled'
    app.verification.text_present_on_page('Your project is currently disabled. '
                                          'Click on “Enable Project” to resume recruitment.')


@pytest.mark.dependency(depends=["test_status_change_from_enabled_to_disabled_new_ui"])
def test_status_change_from_disabled_to_enabled_new_ui(app, create_project_for_view_and_edit):
    app.navigation.click_btn('Enable Project')
    assert app.ac_project.get_project_info_for_section('Status') == 'Enabled'


def test_resume_setup_draft_status_project_new_ui(app, create_project_for_view_and_edit):
    app.driver.switch_to.default_content()
    app.navigation.click_link('Projects')
    app.navigation.switch_to_frame("page-wrapper")
    app.project_list.filter_project_list_by(status='Draft')
    random_project = random.choice(app.project_list.get_projects_on_page())
    app.project_list.open_project_by_id(random_project['id'])
    app.driver.switch_to.default_content()
    # app.navigation.click_btn("View new experience")
    # time.sleep(2)
    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn('Resume Setup')
    time.sleep(1)
    app.verification.current_url_contains('/editNewProject')
