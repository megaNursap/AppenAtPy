"""
Create an External project with specific "External project - SWFH" configuration using API
and the tests validates the Project SWFH and Secure IP configuration when newly created project is being viewed and editing
"""
import datetime
import time

import pytest

from adap.api_automation.utils.data_util import *
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name, tomorrow_date

from adap.ui_automation.utils.selenium_utils import find_elements

pytestmark = [pytest.mark.regression_ac_project_view, pytest.mark.regression_ac, pytest.mark.ac_ui_project_view_n_edit,
              pytest.mark.ac_ui_project_swfh]

USER_NAME = get_user_name('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

faker = Faker()
IP_ADDR = faker.ipv4()
URL = "https://connect-stage.appen.com/qrp/core/partners/projects"
NEW_URL = 'https://connect-stage.appen.com'


# generating project name
PROJECT_NAME = generate_project_name()


@pytest.fixture(scope="module")
def login(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)


# creating the project by selecting APPEN
@pytest.mark.dependency()
def test_secureIP_enable_disable_swift(app, login):
    app.ac_project.create_new_project()
    customer = app.ac_project.identify_customer(pytest.env)

    # filling out the details on the project overview page
    app.ac_project.overview.fill_out_fields(data={
        "Project Title": "Secure_ip_" + PROJECT_NAME[0],
        "Project Alias": "Secure_ip_" + PROJECT_NAME[1],
        "Project Description": "Secure IP New Project Description",
        "Customer":customer,
        "Project Type": "Express",
        "Task Type": "Transcription",
        "Task Volume": "Very Low"
    })

    app.navigation.click_btn('Next: Registration and Qualification')

    # filling out details on registration page
    if pytest.env == "prod":
        app.ac_project.registration.fill_out_fields(data={
            "Select Registration process": "Agnew registration",
            "Select Qualification process": "Aliso Qualification"})
    else:
        app.ac_project.registration.fill_out_fields(data={
            "Select Registration process": "Acac Register",
            "Select Qualification process": "Apple NDA"
        })

    # Case1: When there is no tenant on the recruitment page
    app.navigation.click_btn('Next: Recruitment')

    app.navigation.click_btn("Next: Invoice & Payment")

    # Filling out details on payment page
    app.ac_project.payment.fill_out_fields({"PROJECT WORKDAY TASK ID": "P12345",
                                            "Rate Type": "By Task",
                                            "Project Business Unit": "CR",
                                            "Add Notes to Finance": "1",
                                            "Notes to Finance": "Test notes"})

    app.navigation.click_btn('Next: Project Tools')

    # checking if secure IP Access is disabled
    assert app.ac_project.secure_ip_disable(), "Secure IP Acess is not disabled"

    # CASE2: when there is tenant but tenant type is not FACILITY
    # navigating back to recuritment page to add tenant
    app.ac_project.navigate_pages("Recruitment")
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Albania", tenant='Appen Ltd. (Contractor)')
    app.navigation.click_btn("Next: Invoice & Payment")

    app.navigation.click_btn("Next: Project Tools")

    # Secure IP should be disabled
    assert app.ac_project.secure_ip_disable(), "Secure IP Acess is not disabled"

    # CASE3: when FACILITY tenant type is added
    # navigating back to recruitment page to add tenant
    app.ac_project.navigate_pages("Recruitment")
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="All Countries", tenant='Appen Ltd. (Facility Employee)')
    app.navigation.click_btn("Next: Invoice & Payment")

    app.navigation.click_btn("Next: Project Tools")

    # Secure IP access should be enabled
    assert not app.ac_project.secure_ip_disable(), "Secure IP Access is enabled."

    # filling the details for secure IP
    app.ac_project.tools.fill_out_fields(data={
        "External System": "SWFH",
        "SWFH URL": URL,
        "Secure IP Access": "1",
        "Allowed IPs": "107.3.166.36"
    })
    app.navigation.click_btn('Save')

    # Finish complete filling required fields to complete creating project 1. Hiring Target and 2. Pay rate and Invoice setup
    app.ac_project.navigate_pages("Recruitment")
    app.ac_project.recruitment.add_target(language='English', region='Algeria', restrict_country='Albania',
                                          deadline=tomorrow_date(days=30), target='12')

    app.navigation.click_btn("Next: Invoice & Payment")
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

    app.navigation.click_btn("Next: Project Tools")

    # app.navigation.click_btn("Next: Project Access")

    app.navigation.click_btn("Next: User Project Page")

    # filling the details for user project page
    app.ac_project.user_project.fill_out_fields({"Default Page Task": "Tasks",
                                                 "Available Skill Review": '1',
                                                 "ACAN Project": "1"
                                                 })

    app.navigation.click_btn("Next: Support Team")

    # filling the details for support team page
    app.ac_project.support.fill_out_fields({"Support User Role": "Support",
                                            "Member Name": "Support (Ac)"})

    app.navigation.click_btn("Next: Preview")

    # Verifying the preview page with all the data entered
    app.ac_project.verify_project_info({
        "Project Name": "Secure_ip_" + PROJECT_NAME[0],
        "Project Alias": "Secure_ip_" + PROJECT_NAME[1],
        "Project Description": "Secure IP New Project Description",
        "Type of Project": "Express",
        "Type of Task": "Transcription",
        "Task Volume": "Very Low",
        "Secure IP Access": "Allowed IPs: 107.3.166.36"
    })


@pytest.mark.dependency(depends=["test_secureIP_enable_disable_swift"])
def test_remove_swfh_url(app, login):
    app.navigation.click_btn("Finish Project Setup")
    app.navigation.click_btn("Go to Project Page")
    time.sleep(5)
    app.driver.switch_to.default_content()
    app.navigation.click_link('Projects')
    app.navigation.switch_to_frame("page-wrapper")
    app.project_list.filter_project_list_by(name="Secure_ip_" + PROJECT_NAME[0])
    app.project_list.open_project_by_name("Secure_ip_" + PROJECT_NAME[0])
    app.driver.switch_to.default_content()
    try:
        app.navigation.click_btn("View new experience")
        time.sleep(2)
    except:
        print("new UI")
    app.navigation.switch_to_frame("page-wrapper")
    app.ac_project.click_on_step('Overview & tools')
    app.verification.current_url_contains('/project_setup/view')
    app.verification.text_present_on_page('Overview & Tools')
    app.verification.text_present_on_page('Project Setup')
    app.verification.text_present_on_page('Project Tools')
    app.navigation.click_btn('Edit')
    assert app.ac_project.checkbox_by_text_is_selected_ac('External System')
    app.ac_project.tools.remove_data_from_fields({
        "SWFH URL": URL
    })
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page(
        'Secure Work From Home Project External URL must be configured for SWFH project')
    app.ac_project.close_error_msg()


# @pytest.mark.dependency(depends=["test_remove_swfh_url"])
# def test_uncheck_external_system_swift(app, login):
#     # uncheck external system checkbox and save the data
#     app.ac_project.tools.fill_out_fields(data={
#         "External System checkbox": "1"
#     })
#     app.navigation.click_btn('Save Changes')
#     # app.verification.text_present_on_page('Cannot set a project to non-external while it has external experiments.')
#     # app.ac_project.close_error_msg()


@pytest.mark.dependency(depends=["test_remove_swfh_url"])
def test_edit_save_external_system_swift(app, login):
    app.ac_project.tools.fill_out_fields(data={
        # "External System checkbox": "1",
        "SWFH URL": NEW_URL
    })
    app.navigation.click_btn('Save Changes')
    time.sleep(2)
    app.ac_project.verify_project_info({
        "External Project": "SWFH",
        "SWFH Project URL": 'Go to external system',
    })


@pytest.mark.dependency(depends=["test_edit_save_external_system_swift"])
def test_add_secure_ip_swift(app, login):
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
    app.ac_project.close_error_msg()
    app.navigation.click_btn('Save Changes')
    app.ac_project.verify_project_info({
        "Secure IP Access": new_secure_ip
    })


@pytest.mark.dependency(depends=["test_add_secure_ip_swift"])
def test_add_multiple_secure_ip(app, login):
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


@pytest.mark.dependency(depends=["test_add_multiple_secure_ip"])
def test_remove_secure_ip_access(app, login):
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
