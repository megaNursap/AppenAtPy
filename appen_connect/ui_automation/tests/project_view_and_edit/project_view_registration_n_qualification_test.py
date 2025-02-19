import time

"""
Create a project with specific "Registration and Qualification" configuration using API
and the tests validates the Project Registration and Qualification configuration when newly created project is being viewed and tests while editing the configuration
"""

from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project
from adap.api_automation.utils.data_util import *
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

pytestmark = [pytest.mark.regression_ac_project_view, pytest.mark.regression_ac, pytest.mark.ac_ui_project_registration_n_qualification, pytest.mark.ac_ui_project_view_n_edit]


config = {}

_project = generate_project_name()

_country = "*"
_country_ui = "United States of America"
_locale  = "English (United States)"
_fluency = "Native or Bilingual"
_lan = "eng"
_lan_ui = "English"
_lan_country = "*"
_pay_rate = 6

project_config = {
    "projectType": 'Regular',
    "workType": "LINGUISTICS",
    "externalSystemId": 15,
    "qualificationProcessTemplateId": 85,
    "registrationProcessTemplateId": 315,
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
        "languageCountry": "*",
        "restrictToCountry": _country
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
    _cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                     app.driver.get_cookies()}

    global _project
    _project = api_create_simple_project(project_config, _cookie)

    return _project

@pytest.mark.dependency()
def test_view_registration_and_qualification_page(app, create_project):
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
    app.ac_project.click_on_step('Registration & Qualification')
    app.verification.text_present_on_page('Registration & Qualification')
    app.verification.text_present_on_page('Registration Process')
    app.verification.text_present_on_page('Qualification Process')
    app.ac_project.verify_project_info({
            "Acac Register": "1 - Sign Document",
            "Apple NDA": "1 - Sign Document"})

def test_view_metrics_registration_and_qualification_page(app, create_project):
    app.ac_project.click_on_step('Registration & Qualification')
    app.verification.text_present_on_page('Registered')
    app.verification.text_present_on_page('% passed per step')
    app.verification.text_present_on_page('Qualified')
    app.verification.text_present_on_page('In Progress')
    app.verification.text_present_on_page('Rejected')
    app.verification.text_present_on_page('Abandoned')


@pytest.mark.dependency(depends=["test_view_registration_and_qualification_page"])
def test_click_project_qualifications_link(app, create_project):
    app.navigation.click_link('Project Qualifications')
    app.verification.text_present_on_page('Project Qualifications')
    app.verification.current_url_contains('/recruiting/project_qualifications')
    app.navigation.click_link('Waiting to be screened +')
    # need go back to new experience page for other test  cases
    app.navigation.click_link('Partner Home')
    app.navigation.switch_to_frame("page-wrapper")
    app.project_list.filter_project_list_by(name=create_project['name'])
    app.project_list.open_project_by_name(create_project['name'])
    app.driver.switch_to.default_content()
    try:
        app.navigation.click_btn("View new experience")
        time.sleep(2)
    except:
        print("new UI")
    app.navigation.switch_to_frame("page-wrapper")


@pytest.mark.dependency(depends=["test_click_project_qualifications_link"])
def test_edit_registration_and_qualification_page(app, create_project):
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

