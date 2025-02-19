import datetime
import time

import pytest

from adap.api_automation.utils.data_util import get_test_data, get_secret
from adap.ui_automation.utils.js_utils import scroll_to_page_bottom
from appen_connect.api_automation.services_config.ac_api import AC_API
from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project
from appen_connect.ui_automation.service_config.application import AC
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name, tomorrow_date
from conftest import ac_api_cookie

pytest.appen = 'true'
pytest.env = 'stage'
env = 'stage'
key = get_secret()
USER_NAME = get_test_data('test_ui_account', 'email', env=env)
PASSWORD = get_test_data('test_ui_account', 'password', env=env, key=key)
customer = 'Appen Internal'
project_type = 'Regular'


def create_new_project_ui():
    app = AC(env)
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)

    project_name = generate_project_name()

    app.ac_project.create_new_project()
    # Project overview
    app.ac_project.overview.fill_out_fields(data={
        "Project Title": "NEW_" + project_name[0],
        "Project Alias": "ST_" + project_name[1],
        "Project Description": "Question|Option1|Option2|Option3",
        "Customer": customer,
        "Project Type": project_type,
        "Task Type": "Data Collection",
        "Task Volume": "Average"
    })

    app.navigation.click_btn('Save')
    app.navigation.click_btn('Next: Registration and Qualification')

    # Registration and qualification process
    app.ac_project.registration.fill_out_fields(data={
        "Select Registration process": "Tracy AC 2.0 ",
        "Select Qualification process": " test 123"
    })

    app.navigation.click_btn('Save')
    app.navigation.click_btn('Next: Recruitment')

    # Recruitment
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="All Countries", tenant='Appen Ltd. (Contractor)')

    tomorrows_date = tomorrow_date()
    app.ac_project.recruitment.add_target(language='English',
                                          region='All Countries',
                                          restrict_country='All Countries',
                                          owner='Yu (Tracy)',
                                          deadline=tomorrows_date,
                                          target='100',
                                          target_hours='100')

    app.ac_project.recruitment.add_target(language='French',
                                          region='All Countries',
                                          restrict_country='All Countries',
                                          owner='Yu (Tracy)',
                                          deadline=tomorrows_date,
                                          target='100',
                                          target_hours='100')

    app.navigation.switch_to_frame("intelligent-attr-iframe")
    app.ac_project.recruitment.add_intelligent_attributes(value='Rural or Urban')
    app.navigation.deactivate_iframe()

    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn("Next: Invoice & Payment")

    # Invoice page
    app.ac_project.payment.fill_out_fields({"PROJECT WORKDAY TASK ID": "P12345",
                                            "Rate Type": "Hourly",
                                            "Project Business Unit": "CR"})

    app.navigation.click_btn("Add Pay Rate")
    app.ac_project.payment.fill_out_fields({"Custom Pay Rates": "1"})
    time.sleep(1)
    app.ac_project.payment.select_custom_pay_rates('English (All Countries)', 'All Countries')
    app.ac_project.payment.fill_out_fields({"Spoken Fluency": "Native or Bilingual",
                                            "Written Fluency": "Native or Bilingual",
                                            "User Group": "All users",
                                            "Task Type": "Default",
                                            "Rate": 100
                                            }, action='Save')

    app.navigation.click_btn("Add Pay Rate")
    app.ac_project.payment.fill_out_fields({"Custom Pay Rates": "1"})
    app.ac_project.payment.select_custom_pay_rates('French (All Countries)', 'All Countries')
    app.ac_project.payment.fill_out_fields({"Spoken Fluency": "Native or Bilingual",
                                            "Written Fluency": "Native or Bilingual",
                                            "User Group": "All users",
                                            "Task Type": "Default",
                                            "Rate": 150
                                            }, action='Save')

    app.navigation.click_btn("Set Template")
    time.sleep(3)
    app.ac_project.payment.fill_out_fields({"Invoice Type": 'User self-reported'}, action='Save')
    app.navigation.click_btn('Next: Project Tools')

    # project tools
    app.ac_project.tools.fill_out_fields(data={
        "External System": "ADAP"
    })

    app.navigation.click_btn("Next: User Project Page")

    app.ac_project.user_project.fill_out_fields({"Default Page Task": "Tasks"})

    app.navigation.click_btn("Add Resource")
    app.ac_project.user_project.select_resource_type("Academy")

    app.ac_project.user_project.fill_out_fields({
        "Academy": "Project Nile Academy"
    })
    app.ac_project.user_project.save_project_resource()

    # app.ac_project.user_project.fill_out_fields({
    #     "Data Collection Consent Form Template": 1
    # })
    #
    # app.navigation.click_btn("Set Template")
    # app.ac_project.user_project.fill_out_fields({
    #     "Project Contact Email": "test@test.com",
    #     "Appen Entity": "Appen Butler Hill Inc.",
    #     "PII Data collected": "Genetic information",
    #     "Countries collecting data": "All countries"
    # })
    #
    # app.ac_project.user_project.fill_out_fields({
    #     "Customer DPO contact email": "test1@test.com",
    #     "Customer full legal name": "full name",
    #     "Customer country": "United States of America",
    #     "PII Third party": 1
    # })
    # app.ac_project.user_project.save_consent_form_template()
    app.navigation.click_btn('Save')

    app.navigation.click_btn("Next: Support Team")

    # Support team
    app.ac_project.support.fill_out_fields({"Support User Role": "Quality",
                                            "Member Name": "Support (Ac)"})

    app.navigation.click_btn('Save')
    app.navigation.click_btn("Next: Preview")

    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn('Finish Project Setup')

    app.navigation.click_btn('Go to Project Page')

    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn("Enable Project")
    # time.sleep(60)

    app.navigation.deactivate_iframe()

    app.navigation.click_link('Experiment List')

    app.ac_user.select_customer('Appen Internal')
    app.partner_home.open_experiment_for_project("Appen NEW_" + project_name[0])

    app.partner_home.add_experiment_group('ALL USERS')
    time.sleep(20)
    app.driver.quit()
    print("Done! Project created:")
    print("name:", "NEW_" + project_name[0])
    print("alias:", "ST_" + project_name[1])




def create_new_project_api():
    # get cookies for api
    app = AC(env)
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    flat_cookie_dict = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                        app.driver.get_cookies()}

    api = AC_API(cookies=flat_cookie_dict, env=env)

    # generate project name
    project_name = generate_project_name()
    _project_name = "Appen NEW_" + project_name[0]
    _alias = "ST_" + project_name[1]

    # api: create new project
    print("Setting up: name and processes")
    #     create new project
    _payload = {
        "name": f"{_project_name} ({_alias})",
        "alias": _alias,
        "title": f"{_project_name} ({_alias})",
        "businessUnit": "CR",
        "workdayTaskId": "CR99912",
        "customerId": 53,  # Appen Internal
        # "defaultPageId": 0,
        "description": "Question|Option1|Option2|Option3",
        "projectType": project_type,
        "qualificationProcessTemplateId": 3963,
        "rateType": "HOURLY",
        "registrationProcessTemplateId": 5000,
        "status": "DRAFT",
        "externalSystemId": 15,
        "profileTargetId": "",
        "supportTeam": [
            {
                "userId": 1294202,
                "role": "QUALITY"
            }
        ],
        "taskVolume": "AVERAGE",
        "workType": "DATA_COLLECTION_IA"
    }

    res = api.create_project(payload=_payload)
    res.assert_response_status(201)
    print("done!! project name", _project_name)

    # ----------- locales ------------
    # api: add locale
    print("Setting up: locales")
    project_id = res.json_response['id']

    locale_payload = {
        "country": "*",
        "projectId": "{project_id}".format(project_id=project_id),
        "tenantId": 1
    }

    locale = api.create_locale_tenant(payload=locale_payload)
    locale.assert_response_status(201)
    print("done!!")

    #  -------- Hiring target -----------
    # api: add hiring targets
    print("Setting up: hiring targets")
    future_day = (datetime.datetime.today() + datetime.timedelta(days=20)).isoformat()
    hiring_target_payload_eng = {
        "deadline": future_day,
        "language": "eng",
        "languageCountry": "*",
        "ownerId": 1294896,
        "projectId": project_id,
        "restrictToCountry": "*",
        "target": 100,
        "targetHoursTasks": 100
    }

    hiring_target_payload_french = {
        "deadline": future_day,
        "language": "fra",
        "languageCountry": "*",
        "ownerId": 1294896,
        "projectId": project_id,
        "restrictToCountry": "*",
        "target": 100,
        "targetHoursTasks": 100
    }
    hir_target = api.add_hiring_target(hiring_target_payload_eng)
    hir_target.assert_response_status(201)
    hir_target = api.add_hiring_target(hiring_target_payload_french)
    hir_target.assert_response_status(201)
    print('Done!!')

    # ----- Pay rates ------------
    # api: add pay rates
    print("Setting up: hiring targets")
    pay_rates_payload_eng = {
        "projectId": project_id,
        "writtenFluency": "NATIVE_OR_BILINGUAL",
        "spokenFluency": "NATIVE_OR_BILINGUAL",
        "disabled": 'false',
        "language": "eng",
        "languageCountry": "*",
        "languageTo": "",
        "languageCountryTo": "",
        "restrictToCountry": "*",
        "groupId": 1,
        "taskType": "DEFAULT",
        "defaultRate": 'false',
        "countryPayRateId": 9,
        "rateValue": 15.00,
        "workdayTaskId": " CR21212"
    }

    pay_rates_payload_fra = {
        "projectId": project_id,
        "writtenFluency": "NATIVE_OR_BILINGUAL",
        "spokenFluency": "NATIVE_OR_BILINGUAL",
        "disabled": 'false',
        "language": "fra",
        "languageCountry": "*",
        "languageTo": "",
        "languageCountryTo": "",
        "restrictToCountry": "*",
        "groupId": 1,
        "taskType": "DEFAULT",
        "defaultRate": 'false',
        "countryPayRateId": 9,
        "rateValue": 15.00,
        "workdayTaskId": " CR21212"
    }
    pay_rates = api.create_pay_rate(pay_rates_payload_eng)
    pay_rates.assert_response_status(201)
    pay_rates = api.create_pay_rate(pay_rates_payload_fra)
    pay_rates.assert_response_status(201)

    # ------ Invoice ----
    # api: add invoice
    print("Setting up: invoice")
    invoice_payload = {
        "disableUserReportTime": 'false',
        "autoApproveInvoice": 'false',
        "autoGenerateInvoice": 'false',
        "invoiceLineItemApproval": 'false',
        "requiresPMApproval": 'false',
        "autoRejectInvoice": 'false',
        "configuredInvoice": 'true'
    }
    invoice = api.update_invoice_configuration(project_id, invoice_payload)
    invoice.assert_response_status(200)
    print("Done!!")

    # api: add experiment group
    print("Setting up: experiment group")
    res = api.get_experiments_for_project(project_id)
    res.assert_response_status(200)

    experiment_info = res.json_response[0]["id"]
    payload = [{"experimentId": experiment_info, "groupId": 1}]

    res = api.update_experiment_group(experiment_info, payload)
    res.assert_response_status(200)
    print("Done!!")

    # api: enable project
    print("Setting up: enable project")
    status_payload = {
        "status": "READY"
    }
    status = api.update_project_status(project_id, status_payload)
    status.assert_response_status(200)

    status_payload = {
        "status": "ENABLED"
    }
    status = api.update_project_status(project_id, status_payload)
    status.assert_response_status(200)
    print("Done!!")
    app.driver.quit()
    print("Done! Project created:")
    print("name:", _project_name)
    print("alias:", _alias)


if __name__ == '__main__':

    mode = input("What mode to use? (api or ui): ")

    if mode == 'ui':
        create_new_project_ui()
    elif mode == 'api':
        create_new_project_api()
    else:
        print(f"not supported param: {mode}")
