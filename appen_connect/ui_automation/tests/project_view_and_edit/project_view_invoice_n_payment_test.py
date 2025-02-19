"""
Create a project with specific "Hiring Targets & Metrics" configuration using API
and the tests validates the Project Hiring Target configuration when newly created project is being viewed and tests while editing the configuration
"""
import datetime
import time

from adap.ui_automation.utils.selenium_utils import find_elements
from appen_connect.api_automation.services_config.ac_api import AC_API
from appen_connect.api_automation.services_config.endpoints.ac_api import URL_BASE
from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project
from appen_connect.ui_automation.service_config.project.project_helper import tomorrow_date
from adap.api_automation.utils.data_util import *
from conftest import ac_api_cookie

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

pytestmark = [pytest.mark.regression_ac_project_view, pytest.mark.regression_ac, pytest.mark.ac_ui_project_invoice_n_payment,
              pytest.mark.ac_ui_project_view_n_edit,pytest.mark.ac_ui_project_view_n_test ]

_country = "DZA"
_country_ui = "Algeria"
_locale = "English (Algeria)"
_fluency = "Native or Bilingual"
_toCountry = 'Albania'
_lan = "eng"
_lan_ui = "English"
_lan_country = "DZA"
_pay_rate = 1.23
_pay_rate2 = 500
_tomorrow_date = tomorrow_date(days=30)
tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1)).isoformat()
http_url = URL_BASE(env=pytest.env)

project_config = {
    "acanProject": 'true',
    "projectType": 'Regular',
    "workType": "LINGUISTICS",
    "externalSystemId": 15,
    "rateType": "PIECERATE",
    "financeNotes": "Test Notes to Finance",
    "qualificationProcessTemplateId": 1386,
    "registrationProcessTemplateId": 764,
    "locale": {
        "country": _country
    },
    "hiring_target": {
        "language": _lan,
        "languageCountry": _lan_country,
        "restrictToCountry": _country,
        "target": 10
    },
    "pay_rates": {
        "spokenFluency": _fluency.upper().replace(" ", "_"),
        "writtenFluency": _fluency.upper().replace(" ", "_"),
        "rateValue": _pay_rate,
        "taskType": "Default",
        "language": _lan,
        "languageCountry": "DZA",
        "restrictToCountry": _country,
        "defaultRate": 'false' # to overwrite default if rate is custom
    },
    "invoice": "default",
    "update_status": "READY"
}


@pytest.fixture(scope="module")
def create_project(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.navigation.click_link('Partner Home')
    # app.navigation.click_link('View previous list page')
    # app.ac_user.select_customer('Appen Internal')
    time.sleep(2)

    ac_api_cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                     app.driver.get_cookies()}

    global _project
    _project = api_create_simple_project(project_config, ac_api_cookie)
    print(_project)

    status_payload = {
        "status": "ENABLED"
    }
    project_id = _project['id']
    api = AC_API(ac_api_cookie)
    local_tenant_payload = {"country": "ALB", "projectId": project_id, "tenantId": 1}
    resp = api.create_locale_tenant(local_tenant_payload)
    print("RESP", resp)
    resp.assert_response_status(201)

    hiring_target_2 = {
        "deadline": tomorrow,
        "language": "eng",
        "languageCountry": "DZA",
        "projectId": project_id,
        "restrictToCountry": "ALB",
        "target": 12,
        "targetHoursTasks": "2"
    }

    resp2 = api.add_hiring_target(hiring_target_2)
    print("RESP", resp2)
    resp2.assert_response_status(201)

    #### workaround add pay rate via ui
    app.navigation.open_page(f"{http_url}/qrp/core/partners/project_setup/view/{project_id}")
    app.navigation.switch_to_frame("page-wrapper")
    app.ac_project.click_on_step("Invoice & Payment", on_bottom=False)
    app.navigation.click_btn('Edit')
    app.navigation.click_btn("Add Pay Rate")
    app.verification.wait_untill_text_present_on_the_page("Hiring Target", max_time=20)
    app.ac_project.payment.fill_out_fields({"Custom Pay Rates": "1"})
    app.ac_project.payment.select_custom_pay_rates("English (Algeria)",  "Albania")
    app.ac_project.payment.fill_out_fields({"Spoken Fluency": "Native or Bilingual",
                                            "Written Fluency": "Native or Bilingual",
                                            "User Group": "All users",
                                            "Task Type": "Annotation",
                                            "Rate": _pay_rate
                                            }, action='Save')

    app.navigation.click_btn("Add Pay Rate")
    app.ac_project.payment.fill_out_fields({"Custom Pay Rates": "1"})
    app.ac_project.payment.select_custom_pay_rates("English (Algeria)", "Algeria")
    app.ac_project.payment.fill_out_fields({"Spoken Fluency": "Native or Bilingual",
                                            "Written Fluency": "Native or Bilingual",
                                            "User Group": "All users",
                                            "Task Type": "Annotation",
                                            "Rate": _pay_rate2
                                            }, action='Save')


    # do not remove. uncomment for pay rate via api
    # pay_rates = api.create_pay_rate(pay_rates_payload)
    #
    # pay_rates.assert_response_status(201)

    status = api.update_project_status(project_id, status_payload)
    status.assert_response_status(200)

    project_status = status.json_response['status']
    _project['status'] = project_status
    app.driver.switch_to.default_content()
    return _project


# ---------- View and edit 'INVOICE & PAYMENT' page ---------
@pytest.mark.dependency()
def test_view_invoice_and_payment_page(app, create_project):
    # print(f"USERNAME {USER_NAME}, PWD {PASSWORD}") ##used for triaging, do not remove
    print(f"PROJECTID: {create_project['id']}")

    app.navigation.click_link('Projects')
    app.navigation.switch_to_frame("page-wrapper")

    app.project_list.filter_project_list_by(create_project['name'])
    app.project_list.open_project_by_name(create_project['name'])

    app.driver.switch_to.default_content()
    try:
        app.navigation.click_btn("View new experience")
        time.sleep(2)
    except:
        print("new UI")

    app.navigation.switch_to_frame("page-wrapper")
    app.ac_project.click_on_step('Invoice & Payment')
    app.verification.text_present_on_page('Invoice & Payment')
    app.verification.text_present_on_page('Pay Rates Setup')
    app.ac_project.verify_project_info({
        "PROJECT WORKDAY TASK ID": "Task Code: CR99912",
        "Rate Type": "By Task",
        "Project Business Unit": "CR",
        "Productivity Data": "Not enabled"
    })
    app.ac_project.payment.verify_pay_rate_is_present_on_page(hiring_target='English (Algeria)Algeria',
                                                              input_fluency='Native or Bilingual', input_grp='All users',
                                                              input_work='.', input_taskid='.',
                                                              input_rate='$5.00')



@pytest.mark.dependency(depends=["test_view_invoice_and_payment_page"])
def test_invoice_and_payment_required_fields_in_edit_mode(app, create_project):
    # Adding required information from UI and verify that if removed gives error
    app.ac_project.click_on_step('Invoice & Payment')
    app.navigation.click_btn('Edit')
    time.sleep(2)
    app.ac_project.payment.fill_out_fields({
        "PROJECT WORKDAY TASK ID": 'P23345',
        "Add Notes to Finance": "1",
        "Notes to Finance": 'Test Notes to Finance'
    })
    app.navigation.click_btn('Save Changes')

    app.ac_project.click_on_step('Invoice & Payment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.payment.remove_data_from_fields({
        "PROJECT WORKDAY TASK ID": 'P23345',
        "Notes to Finance": 'Test Notes to Finance'
    })
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page('When "Add Notes to Finance" is checked this is a required field.')
    app.verification.text_present_on_page('Workday Task Id is a required field.')


@pytest.mark.dependency(depends=["test_invoice_and_payment_required_fields_in_edit_mode"])
def test_edit_invoice_and_payment(app, create_project):

    app.ac_project.payment.fill_out_fields({"PROJECT WORKDAY TASK ID": 'P23333',
                                            "Project Business Unit": "LR",
                                            "Available Productivity Data": "1",
                                            "Notes to Finance": "Updated notes"})
    app.ac_project.close_error_msg()
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page('When "Add Notes to Finance" is checked this is a required field.',
                                          is_not=False)
    app.ac_project.verify_project_info({
        "PROJECT WORKDAY TASK ID": "Task Code: P23333",
        "Project Business Unit": "LR",
        "Productivity Data": "Available",
        "Notes to Finance": "Updated notes"
    })


@pytest.mark.dependency()
def test_add_custom_pay_rates_required_fields(app, create_project):
    app.ac_project.click_on_step('Invoice & Payment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.navigation.click_btn("Add Pay Rate")
    app.ac_project.payment.fill_out_fields({"Custom Pay Rates": "1"})
    app.navigation.click_btn('Save')
    app.verification.text_present_on_page('Hiring Target is a required field.')
    app.ac_project.payment.click_cancel_add_pay_rate()


# @pytest.mark.skip(reason="https://appen.atlassian.net/browse/ACE-10289")
# @pytest.mark.dependency(depends=["test_add_custom_pay_rates_required_fields"])
# def test_add_new_custom_pay_rates(app, create_project):
#     app.navigation.click_btn("Add Pay Rate")
#     app.ac_project.payment.fill_out_fields({"Custom Pay Rates": "1"})
#     app.ac_project.payment.select_custom_pay_rates('English (Algeria)', 'Albania')
#     app.ac_project.payment.fill_out_fields({"Spoken Fluency": "Beginner",
#                                             "Written Fluency": "Beginner",
#                                             "User Group": "Hc group for appen internal",
#                                             "Task Type": "Default",
#                                             "Rate": 333
#                                             }, action='Save')
#     app.navigation.click_btn('Save Changes')
#     app.ac_project.payment.verify_pay_rate_is_present_on_page(hiring_target='English (Algeria)',
#                                                               input_fluency='Beginner',
#                                                               input_grp='Hc group for appen internal',
#                                                               input_work='Default', input_taskid='.',
#                                                               input_rate='$3.33')


def test_copy_customer_payrates_already_exist(app, create_project):
    app.ac_project.click_on_step('Invoice & Payment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.payment.click_copy_pay_rate(hiring_target='English (Algeria)Algeria',
                                               input_fluency='Native or Bilingual', input_grp='All users',
                                               input_work='.', input_taskid='.',
                                               input_rate='$5.00')

    app.ac_project.payment.fill_out_fields({"Spoken Fluency": "Native or Bilingual",
                                            "Written Fluency": "Native or Bilingual",
                                            "Rate": 500
                                            }, action='Save')
    app.verification.text_present_on_page('Project Pay Rate already exists')
    app.ac_project.close_error_msg()
    app.ac_project.payment.click_cancel_copy_pay_rate()


def test_new_default_payrate_with_new_fluency(app, create_project):
    app.ac_project.click_on_step('Invoice & Payment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.payment.click_copy_pay_rate(hiring_target='English (Algeria)Algeria',
                                               input_fluency='Native or Bilingual', input_grp='All users',
                                               input_work='.', input_taskid='.',
                                               input_rate='$5.00')
    app.ac_project.payment.fill_out_fields({"Spoken Fluency": "Near Native",
                                            "Written Fluency": "Near Native",
                                            "Rate": 188
                                            }, action='Save')
    app.navigation.click_btn('Save Changes')


# @pytest.mark.skip(reason='no task type judgement available, only default task type')
# @pytest.mark.dependency(depends=["test_copy_customer_payrates_already_exist"])
# def test_copy_customer_payrates_successfully(app, create_project):
#     app.ac_project.payment.fill_out_fields({"Task Type": "Judgement",
#                                             }, action='Save')
#     app.verification.text_present_on_page('Project Pay Rate already exists', is_not=False)
#     app.navigation.click_btn('Save Changes')
#     app.ac_project.payment.verify_pay_rate_is_present_on_page(hiring_target='English (Algeria)',
#                                                               input_fluency='Near Native', input_grp='All users',
#                                                               input_work='Judgement',
#                                                               input_taskid='.',
#                                                               input_rate='$1.88')
#
#
# @pytest.mark.skip(reason='This is not valid use case now, user cannot edit the pay rate')
# def test_edit_customer_payrates(app, create_project):
#     app.ac_project.click_on_step('Invoice & Payment')
#     app.navigation.click_btn('Edit')
#     app.ac_project.close_error_msg()
#     app.ac_project.payment.click_edit_pay_rate(hiring_target='English (Algeria)Algeria',
#                                                input_fluency='Native or Bilingual', input_grp='All users',
#                                                input_work='.', input_taskid='.',
#                                                input_rate='$5.00')
#     app.ac_project.payment.fill_out_fields({"Rate": 155}, action='Save')
#     app.navigation.click_btn('Save Changes')
#     app.ac_project.payment.verify_pay_rate_is_present_on_page(hiring_target='English (Algeria)Algeria',
#                                                               input_fluency='Native or Bilingual', input_grp='All users',
#                                                               input_work='.', input_taskid='.',
#                                                               input_rate='$1.55')
#
#
# @pytest.mark.skip(reason="https://appen.atlassian.net/browse/ACE-10295")
# def test_delete_customer_payrates(app, create_project):
#     app.ac_project.click_on_step('Invoice & Payment')
#     app.navigation.click_btn('Edit')
#     app.ac_project.payment.delete_pay_rate(hiring_target='English (Algeria)Albania',
#                                            input_work='.', input_taskid='.',
#                                            input_rate='$1.55')
#     app.verification.text_present_on_page(
#         "You cannot delete the rate for the system ALL USERS group while there are still rates defined for other "
#         "groups in the same locale.")
#     app.navigation.click_btn("Cancel")