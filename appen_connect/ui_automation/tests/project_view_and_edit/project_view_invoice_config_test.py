"""
Create a project with specific "Invoice" configuration using API
and the tests validates the Project Invoice configuration when newly created project is being viewed and tests while editing the configuration
"""
import time

from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project
from adap.api_automation.utils.data_util import *

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

pytestmark = [pytest.mark.regression_ac_project_view, pytest.mark.regression_ac,
              pytest.mark.ac_ui_project_invoice_config, pytest.mark.ac_ui_project_view_n_edit]

_country = "*"
_country_ui = "United States of America"
_locale = "English (United States)"
_fluency = "Native or Bilingual"
_lan = "eng"
_lan_ui = "English"
_lan_country = "*"
_pay_rate = 6

project_config = {
    "projectType": 'Regular',
    "workType": "LINGUISTICS",
    "externalSystemId": 15,
    "qualificationProcessTemplateId": 1386,
    "registrationProcessTemplateId": 764,
    "locale": {
        "country": _country
    },
    "hiring_target": {
        "language": _lan,
        "languageCountry": _lan_country,
        "restrictToCountry": _country
    },
    "pay_rates": {
        "create": False
    }
}


@pytest.fixture(scope="module")
def invoice_project(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.navigation.click_link('Partner Home')
    # app.navigation.click_link('View previous list page')
    # app.ac_user.select_customer('Appen Internal')
    time.sleep(2)
    ac_api_cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                     app.driver.get_cookies()}

    global _project
    _project = api_create_simple_project(project_config, ac_api_cookie)
    return _project


@pytest.mark.dependency()
def test_access_control_invoice_config_default_view(app, invoice_project):
    app.navigation.click_link('Projects')
    app.navigation.switch_to_frame("page-wrapper")

    app.project_list.filter_project_list_by(invoice_project['name'])
    app.project_list.open_project_by_name(invoice_project['name'])

    app.driver.switch_to.default_content()
    try:
        app.navigation.click_btn("View new experience")
        time.sleep(2)
    except:
        print("new UI")

    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn("Resume Setup")

    app.navigation.switch_to_frame("page-wrapper")
    app.ac_project.click_on_step('Invoice & Payment')

    app.verification.text_present_on_page("Available Productivity Data")
    app.verification.text_present_on_page("If checked, it will be used for prompting the user to enter task timings "
                                          "for the task types in the data file.")

    app.ac_project.payment.load_project({"Available Productivity Data": 0})

    app.navigation.click_btn("Set Template")
    app.verification.text_present_on_page("Invoice Template Setup")
    assert app.ac_project.payment.get_options_for_dropdown("Invoice type") == [
        {'name': 'User self-reported', 'title': ''},
        {'name': 'System generated', 'title': 'Enabled only when “Available Productivity Data” is checked.'},
        {'name': 'User self-reported and System approved',
         'title': 'Enabled only when “Available Productivity Data” is checked.'}]

    assert app.ac_project.payment.auto_approve_is_disable()
    app.navigation.click_btn("Cancel")


@pytest.mark.dependency(depends=["test_access_control_invoice_config_default_view"])
def test_access_control_invoice_config_productivity_data_view(app, invoice_project):
    app.ac_project.payment.fill_out_fields({"Available Productivity Data": 1})
    app.navigation.click_btn("Save")

    app.navigation.click_btn("Set Template")
    assert app.ac_project.payment.get_options_for_dropdown("Invoice type") == [
        {'name': 'User self-reported', 'title': ''},
        {'name': 'System generated', 'title': ''},
        {'name': 'User self-reported and System approved', 'title': ''}]

    assert not app.ac_project.payment.auto_approve_is_disable()
    app.navigation.click_btn("Cancel")


@pytest.mark.dependency(depends=["test_access_control_invoice_config_productivity_data_view"])
def test_user_self_reported_view(app, invoice_project):
    app.navigation.click_btn("Set Template")

    app.verification.text_present_on_page("Base auto-approval on", is_not=False)
    app.verification.text_present_on_page("Acceptable Var. Threshold", is_not=False)

    app.ac_project.payment.fill_out_fields({"Auto-approve Invoices": 1})

    app.verification.text_present_on_page("Base auto-approval on")
    app.verification.text_present_on_page("Acceptable Var. Threshold")

    app.ac_project.payment.save_invoice_config()

    app.verification.text_present_on_page('When "Auto-approve Invoices" is checked this is a required field.')

    app.ac_project.payment.choose_invoice_type('User self-reported')

    app.ac_project.payment.fill_out_fields({"Base auto-approval on": 'Units Of Work',
                                            "Acceptable Var. Threshold": 10})

    app.ac_project.payment.save_invoice_config()
    app.verification.text_present_on_page(
        "Project with hourly rate can not have auto approve invoice by units of work.")

    app.ac_project.payment.fill_out_fields({"Base auto-approval on": 'Time Spent'})
    app.ac_project.payment.save_invoice_config()

    app.verification.text_present_on_page("Time Spent")
    app.verification.text_present_on_page("Auto-approval")


@pytest.mark.dependency(depends=["test_user_self_reported_view"])
def test_invoice_system_generated_view(app, invoice_project):
    app.ac_project.payment.click_edit_invoice_config()

    app.ac_project.payment.fill_out_fields({"Auto-approve Invoices": 1})
    app.verification.text_present_on_page("Base auto-approval on", is_not=False)
    app.verification.text_present_on_page("Acceptable Var. Threshold", is_not=False)
    app.verification.text_present_on_page("Base auto-generation on", is_not=False)

    app.ac_project.payment.choose_invoice_type('System generated')
    app.verification.text_present_on_page("Base auto-generation on")

    app.ac_project.payment.save_invoice_config()

    app.verification.text_present_on_page('When "Invoice Type" is not "User self-reported" this is a required field.')

    app.ac_project.payment.fill_out_fields({"Base auto-generation on": 'Units Of Work',
                                            "Auto-approve Invoices": 1,
                                            "Project manager approval at line item level": 1})

    app.ac_project.payment.fill_out_fields({"Base auto-approval on": 'Time Spent',
                                            "Acceptable Var. Threshold": 50})
    app.ac_project.payment.save_invoice_config()
    app.verification.text_present_on_page(
        "Project with hourly rate can not have auto generate invoice by units of work.")

    app.ac_project.payment.fill_out_fields({"Base auto-generation on": 'Time Spent'})
    app.ac_project.payment.save_invoice_config()

    app.verification.text_present_on_page("System generated")
    app.verification.text_present_on_page("PM approval at line item level required")
    app.verification.text_present_on_page("Time Spent")
    app.verification.text_present_on_page("50%")


@pytest.mark.dependency(depends=["test_invoice_system_generated_view"])
def test_invoice_self_report_and_system_generated_view(app, invoice_project):
    app.ac_project.payment.click_edit_invoice_config()

    app.ac_project.payment.fill_out_fields({"Auto-approve Invoices": 1})
    app.verification.text_present_on_page("Base auto-approval on", is_not=False)
    app.verification.text_present_on_page("Acceptable Var. Threshold", is_not=False)

    app.ac_project.payment.choose_invoice_type('User self-reported and System approved ')
    app.verification.text_present_on_page("Base auto-generation on")

    app.ac_project.payment.save_invoice_config()

    app.verification.text_present_on_page(
        'When "Invoice Type" is not "User self-reported" this is a required field.')

    app.ac_project.payment.fill_out_fields({"Base auto-generation on": 'Units Of Work',
                                            "Auto-approve Invoices": 1})

    app.ac_project.payment.fill_out_fields({"Base auto-approval on": 'Time Spent',
                                            "Acceptable Var. Threshold": 10})
    app.ac_project.payment.save_invoice_config()
    app.verification.text_present_on_page(
        "Project with hourly rate can not have auto generate invoice by units of work.")

    app.ac_project.payment.fill_out_fields({"Base auto-generation on": 'Time Spent'})
    app.ac_project.payment.save_invoice_config()

    app.verification.text_present_on_page("User self-reported and System approved ")
    app.verification.text_present_on_page("PM approval at line item level required")
    app.verification.text_present_on_page("Self reporting allowed")
    app.verification.text_present_on_page("Time Spent")
    app.verification.text_present_on_page("10%")


@pytest.mark.dependency(depends=["test_invoice_self_report_and_system_generated_view"])
def test_invoice_by_task_config_view(app, invoice_project):
    app.ac_project.payment.fill_out_fields({"Rate Type": "By Task"})

    app.ac_project.payment.click_edit_invoice_config()
    app.ac_project.payment.save_invoice_config()

    app.verification.text_present_on_page(
        "Project with rate type by task must have auto generate invoice by units of work.")

    app.ac_project.payment.fill_out_fields({"Base auto-generation on": 'Units Of Work',
                                            "Base auto-approval on": 'Units Of Work'
                                            })

    app.ac_project.payment.save_invoice_config()


# @pytest.mark.skip  # Skipped due to Idaptive Issue
# def test_invoice_no_access_view(app_test):
#     user_name = get_user_email('test_qa_user')
#     password = get_user_password('test_qa_user')
#
#     app_test.ac_user.login_as(user_name=user_name, password=password)
#     app_test.navigation.click_link('Partner Home')
#     app_test.navigation.switch_to_frame("page-wrapper")
#
#     app_test.project_list.filter_project_list_by(_project['name'])
#     app_test.project_list.open_project_by_name(_project['name'])
#
#     app_test.driver.switch_to.default_content()
#     try:
#         app_test.navigation.click_btn("View new experience")
#         time.sleep(2)
#     except:
#         print("new UI")
#     app_test.navigation.switch_to_frame("page-wrapper")
#     app_test.navigation.click_btn("Resume Setup")
#
#     app_test.navigation.switch_to_frame("page-wrapper")
#     app_test.ac_project.click_on_step('Invoice & Payment')
#
#     try:
#         app_test.ac_project.payment.click_edit_invoice_config()
#         assert False
#     except:
#         assert True, "Edit button is enabled"
#
#
# @pytest.mark.skip  # Skipped due to Idaptive Issue
# def test_create_invoice_config_no_access_view(app_test):
#     user_name = get_user_email('test_qa_user')
#     password = get_user_password('test_qa_user')
#
#     app_test.ac_user.login_as(user_name=user_name, password=password)
#     app_test.navigation.click_link('Partner Home')
#     app_test.navigation.click_link('View previous list page')
#     app_test.ac_user.select_customer('Appen Internal')
#     time.sleep(2)
#     ac_api_cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
#                      app_test.driver.get_cookies()}
#
#     _project_qa = api_create_simple_project(project_config, ac_api_cookie)
#
#     app_test.navigation.click_link('Projects')
#     app_test.navigation.switch_to_frame("page-wrapper")
#
#     app_test.project_list.filter_project_list_by(_project_qa['name'])
#     app_test.project_list.open_project_by_name(_project_qa['name'])
#
#     app_test.driver.switch_to.default_content()
#     try:
#         app_test.navigation.click_btn("View new experience")
#         time.sleep(2)
#     except:
#         print("new UI")
#
#     app_test.navigation.switch_to_frame("page-wrapper")
#     app_test.navigation.click_btn("Resume Setup")
#
#     app_test.navigation.switch_to_frame("page-wrapper")
#     app_test.ac_project.click_on_step('Invoice & Payment')
#
#     assert app_test.ac_project.payment.btn_set_template_is_disabled()
