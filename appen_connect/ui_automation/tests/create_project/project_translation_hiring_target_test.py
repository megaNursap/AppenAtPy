import datetime
import time

import pytest
from datetime import datetime as dt
from adap.api_automation.utils.data_util import *
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name,tomorrow_date

pytestmark = [pytest.mark.regression_ac_project_config, pytest.mark.regression_ac, pytest.mark.ac_ui_new_project, pytest.mark.ac_ui_hiring_target]

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')



@pytest.fixture(scope="module")
def login(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)



def test_translation_process(app, login):
    app.ac_project.create_new_project()
    customer = app.ac_project.identify_customer(pytest.env)
    project_name = generate_project_name()

    app.ac_project.overview.fill_out_fields(data={
        "Project Title": "Translate_" + project_name[0],
        "Project Alias": "Translate_" + project_name[1],
        "Project Description": "New Project Description",
        "Customer": customer,
        "Project Type": "Express",
        "Task Type": "Translation",
        "Task Volume": "Very Low"
    })

    app.navigation.click_btn('Next: Registration and Qualification')
    time.sleep(3)

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
    app.ac_project.recruitment.add_tenant(country="United States of America", tenant='Appen Ltd. (Contractor)')
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Japan", tenant='Appen Ltd. (Contractor)')
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="China", tenant='Appen Ltd. (Contractor)')

    tomorrows_date = tomorrow_date()
    formatted_date= (custom_strftime('%b {S}, %Y', (datetime.date.today() + datetime.timedelta(days=1))))

    app.ac_project.recruitment.add_target(language='English', region='United States of America', language_to='Japanese',
                                          region_to='Japan', restrict_country='Japan', deadline=tomorrows_date, target='1')
    app.ac_project.recruitment.add_target(language='English', region='United States of America', language_to='All Chinese languages',
                                          region_to='China', restrict_country='China', deadline=tomorrows_date, target='6')

    #verifying the translation rows have been added on the page
    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='English', loc_dialect_from='United States of America', loc_lang_to='Japanese',
                                                                        loc_dialect_to='Japan', rest_to_country='Japan', deadline= formatted_date, target='1', row_is_present= True)
    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='English', loc_dialect_from='United States of America', loc_lang_to='All Chinese languages',
                                                                        loc_dialect_to='China', rest_to_country='China', deadline= formatted_date, target='6', row_is_present= True)
    app.navigation.click_btn("Next: Invoice & Payment")

    app.ac_project.payment.fill_out_fields({ "Rate Type": "By Task",
                                            "Project Business Unit": "CR"})

    app.navigation.click_btn("Add Pay Rate")
    app.ac_project.payment.fill_out_fields({"Custom Pay Rates": "1"})
    app.ac_project.payment.select_custom_pay_rates('From English (U.S.A.) to Japanese (Japan)', 'Japan')

    #Entering the details on custom page
    app.ac_project.payment.fill_out_fields({"Spoken Fluency": "Fluent",
                                            "Written Fluency": "Fluent",
                                            "User Group": "All users",
                                            "Task Type": "Default",
                                            "Rate": 123
                                            }, action='Save')

    app.navigation.click_btn("Add Pay Rate")
    app.ac_project.payment.fill_out_fields({"Custom Pay Rates": "1"})
    app.ac_project.payment.select_custom_pay_rates('From English (U.S.A.)  to All Chinese languages (China)', 'China')

    app.ac_project.payment.fill_out_fields({"Spoken Fluency": "Fluent",
                                            "Written Fluency": "Fluent",
                                            "User Group": "All users",
                                            "Task Type": "Default",
                                            "Rate": 124
                                            }, action='Save')

    # verifying custom pay rate rows have been added in  the page
    app.ac_project.payment.verify_pay_rate_is_present_on_page(hiring_target='From English (U.S.A.)  to Japanese (Japan)Japan',
                                                             input_fluency='Fluent', input_grp='All users', input_work='.', input_taskid='.',
                                                             input_rate='$1.23', is_not=True)

    app.ac_project.payment.verify_pay_rate_is_present_on_page(hiring_target='From English (U.S.A.)  to All Chinese languages (China)China',
                                                             input_fluency='Fluent', input_grp='All users', input_work='.', input_taskid='.',
                                                             input_rate='$1.24', is_not=True)
