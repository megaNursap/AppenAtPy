"""
create new project
"""
import datetime
import pytest

from adap.api_automation.utils.data_util import *
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name

pytestmark = [pytest.mark.regression_ac_project_config, pytest.mark.regression_ac,pytest.mark.ac_ui_new_project, pytest.mark.ac_ui_project_swfh]

USER_NAME = get_user_name('test_ui_account')
PASSWORD = get_user_password('test_ui_account')




@pytest.fixture(scope="module")
def login(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)


#creating the project by selecting APPEN
def test_secureIP_enable_disable(app, login):
    app.ac_project.create_new_project()

    customer = app.ac_project.identify_customer(pytest.env)

    #generating project name
    project_name = generate_project_name()

    #filling out the details on the project overview page
    app.ac_project.overview.fill_out_fields(data={
        "Project Title": "Secure_ip_"+project_name[0],
        "Project Alias": "Secure_ip_"+project_name[1],
        "Project Description": "Secure IP New Project Description",
        "Customer": customer,
        "Project Type": "Express",
        "Task Type": "Transcription",
        "Task Volume": "Very Low"
    })

    app.navigation.click_btn('Next: Registration and Qualification')

    #filling out details on registration page
    if pytest.env == "prod":
        app.ac_project.registration.fill_out_fields(data={
            "Select Registration process": "Agnew registration",
            "Select Qualification process": "Aliso Qualification"})
    else:
        app.ac_project.registration.fill_out_fields(data={
            "Select Registration process": "Acac Register",
            "Select Qualification process": "Apple NDA"
        })

    #Case1: When there is no tenant on the recruitment page
    app.navigation.click_btn('Next: Recruitment')

    app.navigation.click_btn("Next: Invoice & Payment")

    #Filling out details on payment page
    app.ac_project.payment.fill_out_fields({"PROJECT WORKDAY TASK ID": "P12345",
                                            "Rate Type": "By Task",
                                            "Project Business Unit": "CR",
                                            "Add Notes to Finance": "1",
                                            "Notes to Finance": "Test notes"})

    app.navigation.click_btn('Next: Project Tools')

    #checking if secure IP Access is disabled
    assert app.ac_project.secure_ip_disable(), "Secure IP Acess is not disabled"


    #CASE2: when there is tenant but tenant type is not FACILITY
    #navigating back to recuritment page to add tenant
    app.ac_project.navigate_pages("Recruitment")
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Albania", tenant='Appen Ltd. (Contractor)')
    app.navigation.click_btn("Next: Invoice & Payment")

    app.navigation.click_btn("Next: Project Tools")

    #Secure IP should be disabled
    assert app.ac_project.secure_ip_disable(), "Secure IP Acess is not disabled"

    # CASE3: when FACILITY tenant type is added
    # navigating back to recruitment page to add tenant
    app.ac_project.navigate_pages("Recruitment")
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="All Countries", tenant='Appen Ltd. (Facility Employee)')
    app.navigation.click_btn("Next: Invoice & Payment")

    app.navigation.click_btn("Next: Project Tools")

    #Secure IP access should be enabled
    assert not app.ac_project.secure_ip_disable(), "Secure IP Access is enabled."

    #filling the details for secure IP
    app.ac_project.tools.fill_out_fields(data={
        "External System": "SWFH",
        "SWFH URL": "https://connect-stage.appen.com/qrp/core/partners/projects",
        "Secure IP Access": "1",
        "Allowed IPs": "107.3.166.36"
    })
    # app.navigation.click_btn("Next: Project Access")
    app.navigation.click_btn("Next: User Project Page")

    #filling the details for user project page
    app.ac_project.user_project.fill_out_fields({"Default Page Task": "Tasks",
                                                 "Available Skill Review": '1',
                                                 "ACAN Project": "1"
                                                 })

    app.navigation.click_btn("Next: Support Team")

    #filling the details for support team page
    app.ac_project.support.fill_out_fields({"Support User Role": "Support",
                                            "Member Name": "Support (Ac)"})

    app.navigation.click_btn("Next: Preview")

    #Verifying the preview page with all the data entered
    app.ac_project.verify_project_info({
        "Project Name": "Appen Secure_ip_"+project_name[0],
        "Project Alias": "Secure_ip_"+project_name[1],
        "Project Description": "Secure IP New Project Description",
        "Type of Project": "Express",
        "Type of Task": "Transcription",
        "Task Volume": "Very Low",
        "Secure IP Access": "Allowed IPs: 107.3.166.36"
    })