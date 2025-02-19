"""
https://appen.atlassian.net/browse/QED-2281
https://appen.atlassian.net/browse/QED-2507
https://appen.atlassian.net/browse/QED-2284
This test covers end to end for 3rd party consent form.
1. Create a new project via api with Express type
2. Call invoice configure api
3. Finish Data Collection Consent Form Template Configuration on UI
4. Enable project
5. Vendor apply the project created above, sign the consent form, finish smartphone questionnaire
6. Internal user go to vendor page to complete the project
"""
import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.js_utils import scroll_to_page_bottom, scroll_to_element
from appen_connect.api_automation.services_config.ac_api import AC_API
from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name

pytestmark = [pytest.mark.regression_ac_consent_form, pytest.mark.regression_ac, pytest.mark.consent_form]

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
VENDOR_USER_NAME = get_user_email('test_consent_form_vendor')
VENDOR_PASSWORD = get_user_password('test_consent_form_vendor')
VENDOR_ID = get_test_data('test_consent_form_vendor', "id")

_project_name = "3rd party consent form automation " + generate_project_name()[0]
_alias = "3rd party consent form automation " + generate_random_string(8)

_country = "*"
_country_ui = "United States of America"
_locale = "English (United States)"
_fluency = "Native or Bilingual"
_lan = "eng"
_lan_ui = "English"
_lan_country = "*"
_pay_rate = 6

project_config = {
    "name": _project_name,
    "alias": _alias,
    "projectType": 'Express',
    "workType": "LINGUISTICS",
    "externalSystemId": 15,
    "qualificationProcessTemplateId": 3963,
    "registrationProcessTemplateId": 1646,
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
def test_data_collection_consent_form_template_configuration(app, create_project):
    # step d from https://appen.atlassian.net/browse/QED-2281, Data Collection Consent Form Template Configuration
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
    app.ac_project.click_on_step('User Project Page')
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
    app.navigation.click_btn('Save')

    app.ac_project.click_on_step('Preview')
    app.navigation.click_btn("Finish Project Setup")
    app.navigation.click_btn("Go to Project Page")
    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn('Enable Project')
    app.driver.switch_to.default_content()

    app.navigation.deactivate_iframe()

    app.navigation.click_link('Experiment List')

    app.ac_user.select_customer('Appen Internal')
    app.partner_home.open_experiment_for_project(_project_name)

    app.partner_home.add_experiment_group('ALL USERS')
    app.navigation.click_link("Logout")

# @pytest.mark.skip(reason='https://appen.atlassian.net/browse/ACE-15658')
@pytest.mark.dependency(depends=["test_data_collection_consent_form_template_configuration"])
def test_apply_project_consent_form(app, create_project):
    time.sleep(60)
    app.ac_user.login_as(user_name=VENDOR_USER_NAME, password=VENDOR_PASSWORD)
    app.navigation.click_link('Projects')
    app.navigation.switch_to_frame("page-wrapper")
    app.ac_project.click_header_info('All projects')
    app.vendor_pages.search_project_by_name(_alias)
    app.vendor_pages.click_action_for_project(_alias, 'Apply')
    try:
        app.verification.text_present_on_page("Thank you for your answers. You are a project match!")
        app.navigation.click_btn("Continue To Registration")
    except:
        print('skipped step')


# @pytest.mark.skip(reason='https://appen.atlassian.net/browse/ACE-15658')
@pytest.mark.dependency(depends=["test_apply_project_consent_form"])
def test_sign_consent_form(app, create_project):
    app.verification.current_url_contains("/data_collection_consent_form_standard_primary_participant")
    app.vendor_profile.registration_flow.sign_the_form(user_name=VENDOR_USER_NAME, user_password=VENDOR_PASSWORD, action="I Agree")
    time.sleep(3)
    app.vendor_profile.registration_flow.select_value_for_choice_and_proceed('radio', 'No')[0].click()
    app.vendor_profile.registration_flow.select_value_for_choice_and_proceed('submit', 'Continue')[0].click()
    app.vendor_pages.close_process_status_popup()
    app.navigation.click_link("Logout")

# @pytest.mark.skip(reason='https://appen.atlassian.net/browse/ACE-15658')
@pytest.mark.dependency(depends=["test_sign_consent_form"])
def test_complete_project(app, create_project):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.navigation.click_link("Vendors")
    url = {
        "stage": "https://connect-stage.integration.cf3.us",
        "qa": "https://connect-qa.sandbox.cf3.us"
    }
    app.navigation.open_page(url[pytest.env]+f"/qrp/core/vendor/view/{VENDOR_ID}")
    # app.vendor_pages.open_vendor_profile_by(VENDOR_USER_NAME, search_type='name', status='Any Status')
    app.navigation.click_link("Projects")
    app.vendor_pages.screen_user_take_action_on_project(_project_name, "Completed")
    app.navigation.click_btn('Confirm')
    time.sleep(10)
    app.navigation.click_link("Logout")


# @pytest.mark.skip(reason='https://appen.atlassian.net/browse/ACE-15658')
@pytest.mark.dependency(depends=["test_complete_project"])
def test_vendor_work_this_project(app, create_project):
    app.ac_user.login_as(user_name=VENDOR_USER_NAME, password=VENDOR_PASSWORD)
    app.navigation.click_link('Projects')
    app.navigation.switch_to_frame("page-wrapper")
    app.ac_project.click_header_info('My projects')

    max_try = 40
    current_try = 0
    while current_try < max_try:
        app.vendor_pages.search_project_by_name(_alias)
        if app.verification.count_text_present_on_page('Options') == 1:
            break
        else:
            time.sleep(5)
            current_try += 1
            app.navigation.refresh_page()
            app.navigation.switch_to_frame("page-wrapper")

    app.vendor_pages.click_action_for_project(_alias, 'Work This')
    # TODO add InAtr answer
    app.verification.current_url_contains("/qrp/core/vendors/task/view")


# @pytest.mark.skip(reason='https://appen.atlassian.net/browse/ACE-15658')
@pytest.mark.dependency(depends=["test_vendor_work_this_project"])
def test_generate_third_party_consent_form_required_fields(app, create_project):
    app.navigation.click_link('Third Party Consent Forms')
    app.verification.current_url_contains("/qrp/core/vendors/third_party_form_list/view")
    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn('Generate Third Party Consent Form')
    app.navigation.click_btn('Submit')
    app.verification.text_present_on_page("First name is a required field.")
    app.verification.text_present_on_page("Last name is a required field.")
    app.verification.text_present_on_page("Age is a required field.")
    app.verification.text_present_on_page("Email is a required field.")
    app.verification.text_present_on_page("Gender is a required field.")
    app.navigation.click_btn('Cancel')

# @pytest.mark.skip(reason='https://appen.atlassian.net/browse/ACE-15658')
@pytest.mark.dependency(depends=["test_generate_third_party_consent_form_required_fields"])
def test_generate_third_party_consent_form(app, create_project):
    app.navigation.click_btn('Generate Third Party Consent Form')
    app.verification.text_present_on_page("Email address")
    app.ac_project.user_project.fill_out_fields({
        "First name": "firstname",
        "Last name": "lastname",
        "Age": 17,
        "Email address": "test+" + str(random.randint(100, 20000)) + "@test.com",
        "Gender": "Male"
    })
    app.verification.text_present_on_page("Parent or Legal Guardian ")
    # add 4 more consent forms
    for i in range(0, 3):
        app.navigation.click_btn('Add Other Form')
        app.ac_project.user_project.fill_out_fields({
            "First name": generate_random_string(5),
            "Last name": generate_random_string(5),
            "Age": random.randint(18, 50),
            "Email address": "test+" + str(random.randint(100, 20000)) + "@test.com",
            "Gender": "Female"
        }, index=-1)
        btn = app.driver.find_element('xpath',"//button[text()='Add Other Form']")
        scroll_to_element(app.driver, btn)

    app.navigation.click_btn('Submit')
    app.verification.text_present_on_page("firstname")
    app.verification.text_present_on_page("lastname")
    app.verification.text_present_on_page("Pending")
    app.verification.button_is_displayed("Resend")
