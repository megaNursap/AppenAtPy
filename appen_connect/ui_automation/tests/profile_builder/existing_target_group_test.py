"""
Project Configuration. Target Group

"""
import time
from adap.api_automation.utils.data_util import *
from appen_connect.api_automation.services_config.ac_api import AC_API
from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name

pytestmark = [pytest.mark.regression_ac_profile_builder, pytest.mark.regression_ac, pytest.mark.consent_form]

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

_project_name = "Master Profile Automation e2e " + generate_project_name()[0]
_alias = "Master Profile Automation e2e " + generate_random_string(5)

_country = "*"
_country_ui = "Canada"
_locale = "French (Canada)"
_fluency = "Native or Bilingual"
_lan = "fra"
_lan_ui = "French"
_lan_country = "*"
_pay_rate = 6

project_config = {
    "name": _project_name,
    "alias": _alias,
    "projectType": 'Express',
    "workType": "LINGUISTICS",
    "externalSystemId": 15,
    "registrationProcessTemplateId": 1977,
    "qualificationProcessTemplateId": 1926,
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
        "spokenFluency": _fluency.upper().replace(" ","_"),
        "writtenFluency": _fluency.upper().replace(" ","_"),
        "rateValue": _pay_rate,
        "taskType": "Default",
        "language": _lan,
        "languageCountry": "*",
        "restrictToCountry": _country
    }
}


@pytest.fixture(scope="module")
def create_project(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.navigation.click_link('Partner Home')
    # app.navigation.click_link('View previous list page')
    # app.ac_user.select_customer('Appen Internal')
    time.sleep(2)
    global ac_api_cookie
    ac_api_cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                     app.driver.get_cookies()}

    global _project
    _project = api_create_simple_project(project_config, ac_api_cookie)
    project_id = _project['id']

    # step c from https://appen.atlassian.net/browse/QED-2281, call invoice configure api
    ac_api = AC_API(ac_api_cookie)
    payload = {
        "autoApproveInvoice": 'false',
        "autoApproveInvoiceBasedon": "TIME_SPENT",
        "autoGenerateInvoice": 'true',
        "autoGenerateInvoiceBasedon": "TIME_SPENT",
        "autoRejectInvoice": 'true',
        "configuredInvoice": 'true',
        "disableUserReportTime": 'true',
        "invoiceLineItemApproval": 'true',
        "projectInvoiceVarianceThreshold": 0,
        "requiresPMApproval": 'true'
    }
    res = ac_api.update_invoice_configuration(id=project_id, payload=payload)
    res.assert_response_status(200)
    return _project


@pytest.mark.dependency()
def test_configure_project_access(app, create_project):
    app.navigation.click_link('Projects')
    app.navigation.switch_to_frame("page-wrapper")
    app.project_list.filter_project_list_by(_project_name)
    app.project_list.open_project_by_name(_project_name)
    app.driver.switch_to.default_content()
    try:
        app.navigation.click_btn("View new experience")
        time.sleep(2)
    except:
        print("new UI")
    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn('Resume Setup')
    time.sleep(1)
    app.navigation.switch_to_frame("page-wrapper")
    # app.ac_project.click_on_step('Project Access')
    # app.navigation.click_btn('Save')


@pytest.mark.dependency(depends=["test_configure_project_access"])
def test_configure_target_group_before_finish_project(app, create_project):
    app.ac_project.click_on_step('Preview')
    app.navigation.click_btn("Finish Project Setup")
    app.verification.text_present_on_page("Configure Target Groups and/or Intelligent Attributes to finish setting up your project.")


@pytest.mark.dependency(depends=["test_configure_project_access"])
def test_configure_target_group(app):

    app.ac_project.click_on_step("Recruitment")
    app.verification.text_present_on_page("Target Screening and Data Requirements")
    app.verification.text_present_on_page("Important")
    app.verification.text_present_on_page('There is a "Complete Additional Attributes" module added to this project')
    app.ac_project.recruitment.fill_out_fields({"Target Screening and Data Requirements": "1"})

    app.verification.text_present_on_page("Use existing target group")
    app.verification.text_present_on_page("Create new target Group")
    app.verification.text_present_on_page("Select target audience group")

    app.ac_project.recruitment.fill_out_fields(data={
        "Select target audience group": "Audience Group Demo for automation test"})
    app.verification.text_present_on_page("What brand of desktop and/or laptop device do you own or have access to?")
    app.verification.text_present_on_page("Pass: Acer, Apple, Dell")
    app.navigation.click_btn("Save")


@pytest.mark.dependency(depends=["test_configure_target_group"])
def test_configure_target_group_preview_and_finish(app):
    app.ac_project.click_on_step('Preview')

    app.ac_project.verify_project_info({
        "Target Screening and Data Requirements": "Audience Group Demo for automation test"
    })

    app.navigation.click_btn("Finish Project Setup")
    app.navigation.click_btn("Go to Project Page")
    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn('Enable Project')

    app.ac_project.click_on_step("Recruitment")
    app.verification.text_present_on_page("Audience Group Demo for automation test")
