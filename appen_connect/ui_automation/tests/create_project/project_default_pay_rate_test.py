"""
create Default Payrates for USA and Regular Payrate for BR-PT;
Verify Project is saved in Draft Status
Finish project setup and create/edit default payrate in view mode
"""
import datetime
import time
import pytest

from adap.api_automation.utils.data_util import *
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name, tomorrow_date

pytestmark = [pytest.mark.regression_ac_project_config, pytest.mark.regression_ac, pytest.mark.ac_ui_new_project, pytest.mark.ac_ui_pay_rate]

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')



@pytest.fixture(scope="module")
def login(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)


@pytest.mark.dependency()
def test_default_pay_rate(app, login):
    global project_name
    project_name = generate_project_name()
    app.ac_project.create_new_project()

    app.ac_project.overview.fill_out_fields(data={
        "Project Title": "Default_" + project_name[0],
        "Project Alias": "Default_" + project_name[1],
        "Project Description": "Default Pay Rates New Project Description",
        "Customer": app.ac_project.identify_customer(pytest.env),
        "Project Type": "Regular",
        "Task Type": "Transcription",
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

    # Adding first tenant
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Brazil", tenant='Appen Ltd. (Contractor)')

    # Adding second tenant
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="United States of America", tenant='Appen Ltd. (Contractor)')

    tomorrows_date = tomorrow_date()
    # Adding first hiring target
    app.ac_project.recruitment.add_target(language='Portuguese', region='Brazil', restrict_country='United States of America',
                                          deadline=tomorrows_date, target='12')

    # Adding first second target
    app.ac_project.recruitment.add_target(language='English', region='United States of America', restrict_country='United States of America',
                                          deadline=tomorrows_date, target='12')

    app.navigation.click_btn("Next: Invoice & Payment")

    app.ac_project.payment.fill_out_fields({"PROJECT WORKDAY TASK ID": "P12345",
                                            "Rate Type": "Hourly",
                                            "Project Business Unit": "CR",
                                            "Available Productivity Data": "1"
                                            })

    app.navigation.click_btn("Add Pay Rate")

    # Adding default pay rate for 1st country
    app.ac_project.payment.select_default_pay_rates('Portuguese (Brazil)', 'U.S.A.')
    app.ac_project.payment.select_pay_rate('Contractor', 'CR', 'Hourly', '$9.00', action='Save')

    app.navigation.click_btn("Add Pay Rate")

    # Adding default pay rates for 2nd country and saving at the end
    app.ac_project.payment.select_default_pay_rates('English (U.S.A.)', 'U.S.A.')
    app.ac_project.payment.select_pay_rate('Contractor', 'CR', 'Hourly', '$12.00', 'AK')
    app.ac_project.payment.select_pay_rate('Contractor', 'CR', 'Hourly', '$9.00', 'AL')
    app.ac_project.payment.select_pay_rate('Contractor', 'CR', 'Hourly', '$10.00', 'AR', action='Save')

    # verifying the final number of rows in table after adding the pay rates
    assert app.ac_project.payment.payrate_setup_table_num_of_rows() == 4, "number of pay rates rows are not matching with table total number of rows"

    # verifying the data added in the row
    app.ac_project.payment.verify_pay_rate_is_present_on_page("Portuguese (Brazil)U.S.A.", "Native or Bilingual", ".", ".", ".", "$9.00", ".", )
    app.ac_project.payment.verify_pay_rate_is_present_on_page("English (U.S.A.)U.S.A.", "Native or Bilingual", ".", ".", ".", "$12.00", "AK")
    app.ac_project.payment.verify_pay_rate_is_present_on_page("English (U.S.A.)U.S.A.", "Native or Bilingual", ".", ".", ".", "$9.00", "AL")
    app.ac_project.payment.verify_pay_rate_is_present_on_page("English (U.S.A.)U.S.A.", "Native or Bilingual", ".", ".", ".", "$10.00", "AR")
    app.navigation.click_btn('Save')


@pytest.mark.dependency(depends=["test_default_pay_rate"])
def test_verify_status_draft(app, login):
    app.driver.switch_to.default_content()
    # app.navigation.refresh_page()
    # app.driver.switch_to.alert.accept()
    app.navigation.click_link('Projects')
    time.sleep(2)

    app.navigation.switch_to_frame("page-wrapper")
    app.project_list.filter_project_list_by("Default_" + project_name[1])
    app.project_list.open_project_by_name("Default_" + project_name[0])
    app.driver.switch_to.default_content()
    try:
        app.navigation.click_btn("View new experience")
        time.sleep(2)
    except:
        print("new UI")
    app.navigation.switch_to_frame("page-wrapper")

    app.ac_project.click_on_step('Overview & tools')
    assert app.ac_project.get_project_info_for_section('Status') == 'Draft'
    app.verification.text_present_on_page('Finish project setup to start recruiting workers for this project.')


@pytest.mark.dependency(depends=["test_verify_status_draft"])
def test_finish_project_creation_for_view_and_edit(app, login):
    app.navigation.click_btn('Resume Setup')
    app.navigation.switch_to_frame("page-wrapper")
    app.ac_project.click_on_step('Project Tools')
    app.ac_project.tools.fill_out_fields(data={
        # "External System checkbox": "1",
        "External System": "SWFH",
        "SWFH URL": "https://connect-stage.appen.com/qrp/core/partners/projects"
    })
    app.navigation.click_btn('Save')
    # app.navigation.click_btn("Next: Project Access")
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


@pytest.mark.dependency(depends=["test_finish_project_creation_for_view_and_edit"])
def test_default_pay_rate_required_fields_in_view_mode(app, login):
    app.navigation.switch_to_frame("page-wrapper")
    app.ac_project.click_on_step('Invoice & Payment')
    app.navigation.click_btn('Edit')
    app.navigation.click_btn("Add Pay Rate")
    app.navigation.click_btn('Save')
    app.verification.text_present_on_page('Hiring Target is a required field.')


@pytest.mark.dependency(depends=["test_default_pay_rate_required_fields_in_view_mode"])
def test_add_default_pay_rate_already_exist(app, login):
    app.ac_project.payment.select_default_pay_rates('English (U.S.A.)', 'U.S.A.')
    app.ac_project.payment.select_pay_rate('Contractor', 'CR', 'Hourly', '$10.00', 'AR', action='Save')
    app.verification.text_present_on_page('Project Pay Rate already exists')
    app.ac_project.close_error_msg()



@pytest.mark.dependency(depends=["test_add_default_pay_rate_already_exist"])
def test_add_new_default_pay_rate_in_view_mode(app, login):
    # Deselect AR and select CA
    app.ac_project.payment.select_pay_rate('Contractor', 'CR', 'Hourly', '$10.00', 'AR')
    app.ac_project.payment.select_pay_rate('Contractor', 'CR', 'Hourly', '$13.00', 'CA', action='Save')
    app.ac_project.payment.verify_pay_rate_is_present_on_page("English (U.S.A.)U.S.A.", "Native or Bilingual", ".",
                                                                ".", ".", "$13.00", "CA")
    app.navigation.click_btn('Save Changes')


'''
####Below Tests are commented as they are not valid scenarios now####
@pytest.mark.skip(reason='not a valid test, default payrate is not available to select and copy')
@pytest.mark.dependency(depends=["test_finish_project_creation_for_view_and_edit"])
def test_copy_default_payrates_already_exist(app, login):
    app.ac_project.click_on_step('Invoice & Payment')
    app.navigation.click_btn('Edit')
    app.ac_project.payment.click_copy_pay_rate(hiring_target='English (U.S.A.)U.S.A.',
                                               input_fluency='Native or Bilingual', input_grp='All users',
                                               input_work='Default', input_taskid='.',
                                               input_rate='$12.00', custom_pay_rate=False, state='AK')
    app.ac_project.payment.fill_out_fields({"Default Pay Rates": "1"})
    # Bug https://appen.atlassian.net/browse/ACE-8868
    # app.ac_project.payment.select_pay_rate('Contractor', 'CR', 'Hourly', '$12.00', 'AK')
    # app.navigation.click_btn('Save')
    # app.verification.text_present_on_page('Project Pay Rate already exists')
    # app.ac_project.close_error_msg()

@pytest.mark.skip(reason='not a valid test, default payrate is not available to select and add')
@pytest.mark.dependency(depends=["test_copy_default_payrates_already_exist"])
def test_copy_default_payrates_successfully(app, login):
    app.ac_project.payment.select_pay_rate('Contractor', 'CR', 'Hourly', '$12.00', 'AK')
    app.ac_project.payment.select_pay_rate('Contractor', 'CR', 'Hourly', '$12.00', 'CO', action='Save')
    app.navigation.click_btn('Save')
    app.navigation.click_btn('Save Changes')
    app.ac_project.payment.verify_pay_rate_is_present_on_page("English (U.S.A.)U.S.A.", "Native or Bilingual", "All users",
                                                              "Default", ".", "$12.00", "CO")


@pytest.mark.skip(reason='not a valid test, default payrate is not allowed to delete')
@pytest.mark.dependency(depends=["test_finish_project_creation_for_view_and_edit"])
def test_delete_default_payrates(app, login):
    app.ac_project.click_on_step('Invoice & Payment')
    app.navigation.click_btn('Edit')
    app.ac_project.payment.delete_pay_rate(hiring_target='English (U.S.A.)U.S.A.',
                                           input_fluency='Native or Bilingual', input_grp='All users',
                                           input_work='Default', input_taskid='.',
                                           input_rate='$12.00', custom_pay_rate=False, state='AK')
    app.navigation.click_btn('Save Changes')
    app.ac_project.payment.verify_pay_rate_is_present_on_page(hiring_target='English (U.S.A.)U.S.A.',
                                                              input_fluency='Native or Bilingual', input_grp='All users',
                                                              input_work='Default', input_taskid='.', input_rate='$12.00', state='AK', is_not=False)
'''