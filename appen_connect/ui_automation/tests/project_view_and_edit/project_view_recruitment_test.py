"""
Create a project with specific "Recruitment" configuration using API
and the tests validates the Project Recruitment configuration when newly created project is being viewed and editing
"""
from adap.ui_automation.utils.selenium_utils import find_elements

import datetime

import time

from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project
from adap.api_automation.utils.data_util import *
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

pytestmark = [pytest.mark.regression_ac_project_view, pytest.mark.regression_ac, pytest.mark.ac_ui_project_recruitment, pytest.mark.ac_ui_project_view_n_edit]

config = {}

_project = generate_project_name()

_country1 = "ALB"
_country2 = "ALG"
_country_ui = "Albania"
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
        "country": _country1,
        "tenantId": 3
    },
    "locale":
        {
            "country": _country1,
            "id": 0,
            "tenantId": 3
        },
    "hiring_target": {
        "language": _lan,
        "languageCountry": _lan_country,
        "restrictToCountry": _country1,
        "target": 12
    },
    "blockingRules": [
        {
            "blockedProjectId": 0,
            "permanent": 'true'
        }
    ],
    "linkedProjectsIds": [
        830
    ],
    "pay_rates": {
        "spokenFluency": _fluency.upper().replace(" ", "_"),
        "writtenFluency": _fluency.upper().replace(" ", "_"),
        "rateValue": _pay_rate,
        "taskType": "Default",
        "language": _lan,
        "languageCountry": "*",
        "restrictToCountry": _country1
    },
    "invoice": "default",
    "update_status": "READY"
}


@pytest.fixture(scope="module")
def create_project(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.navigation.click_link('Partner Home')
    app.navigation.click_link('View previous list page')
    app.ac_user.select_customer('Appen Internal')
    time.sleep(2)
    ac_api_cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                     app.driver.get_cookies()}

    global _project
    _project = api_create_simple_project(project_config, ac_api_cookie)

    return _project


def test_view_recruitment_page(app, create_project):
    app.navigation.click_link('Projects')
    app.navigation.switch_to_frame("page-wrapper")
    project_name = create_project['name']

    app.project_list.filter_project_list_by(project_name)
    app.project_list.open_project_by_name(project_name)

    app.driver.switch_to.default_content()
    try:
        app.navigation.click_btn("View new experience")
        time.sleep(2)
    except:
        print("new UI")
    app.navigation.switch_to_frame("page-wrapper")
    app.ac_project.click_on_step('Recruitment')
    app.verification.text_present_on_page('Recruitment')
    app.verification.text_present_on_page('Locale Tenants')
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="Albania", tenant='Appen Ltd.',
                                                                 tenant_type='Facility Employee', is_view_mode=True)

    app.verification.text_present_on_page('Hiring Targets')
    formatted_date = (custom_strftime('%b {S}, %Y', (datetime.date.today() + datetime.timedelta(days=1))))
    app.ac_project.recruitment.verify_regular_hiring_target_row_present_on_page(language='English',
                                                                                region='All Countries',
                                                                                restrict_country='Albania',assigned_owner='.',
                                                                                deadline=formatted_date, target='12')

    app.verification.text_present_on_page('Custom Demographic Requirements')




# Local Tenants
#@pytest.mark.dependency()
def test_add_tenant_required_fields_in_edit_mode(app, create_project):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    # see error message, maybe a bug on stage env
    #app.ac_project.close_error_msg()
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.click_save_add_tenant()
    app.verification.text_present_on_page("Country is a required field.")
    app.verification.text_present_on_page("Tenant is a required field.")
    app.ac_project.recruitment.click_cancel_add_tenant()




#@pytest.mark.dependency(depends=["test_add_tenant_required_fields_in_edit_mode"])
def test_add_local_tenant_cancel(app, create_project):
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Andorra", tenant='Appen Ltd. (Contractor)', action=None)
    app.ac_project.recruitment.click_cancel_add_tenant()
    app.navigation.accept_alert()
    app.ac_project.recruitment.verify_locale_tenant_is_displayed("Andorra", "Appen Ltd.", "Contractor",
                                                                 is_not=False)

#@pytest.mark.dependency(depends=["test_add_local_tenant_cancel"])
def test_add_multiple_local_tenants_save(app, create_project):
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Andorra", tenant='Appen Ltd. (Facility Employee)')
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Anguilla", tenant='Appen Ltd. (Facility Employee)')
    app.navigation.click_btn('Save Changes')
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="Andorra", tenant='Appen Ltd.',
                                                                 tenant_type='Facility Employee', is_view_mode=True)
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="Anguilla", tenant='Appen Ltd.',
                                                                 tenant_type='Facility Employee', is_view_mode=True)


@pytest.mark.dependency()
def test_add_tenant_all_countries_recruitment(app, create_project):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="All Countries", tenant='Appen Ltd. (Facility Employee)')
    app.navigation.click_btn('Save Changes')
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="All Countries", tenant='Appen Ltd.',
                                                                 tenant_type='Facility Employee', is_view_mode=True)


@pytest.mark.dependency(depends=["test_add_tenant_all_countries_recruitment"])
def test_fail_edit_tenant_all_countries(app, create_project):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.recruitment.edit_tenant("All Countries", "Appen Ltd.", "Facility Employee",
                                           "Bulgaria", 'Appen Ltd. (Contractor)')
    app.verification.text_present_on_page('Failed to save Locale Tenant')
    app.verification.text_present_on_page('You can only edit tenants if there are no hiring targets or payrates attached to them.')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.click_cancel_add_tenant()
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="All Countries", tenant='Appen Ltd.',
                                                                 tenant_type='Facility Employee')


def test_fail_edit_tenant_with_hiring_target(app, create_project):
    app.ac_project.recruitment.edit_tenant("Albania", "Appen Ltd.", "Facility Employee", "Albania",
                                           'Appen Ltd. (Contractor)')
    app.verification.text_present_on_page('Failed to save Locale Tenant')
    app.verification.text_present_on_page('You can only edit tenants if there are no hiring targets or payrates attached to them.')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.click_cancel_add_tenant()
    app.ac_project.recruitment.verify_locale_tenant_is_displayed("Albania", "Appen Ltd.", "Facility Employee")


def test_edit_tenant_successfully_without_hiring_target(app, create_project):
    #app.ac_project.click_on_step('Recruitment')
    #app.ac_project.close_error_msg()
    #app.navigation.click_btn('Edit')

    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Bahrain", tenant='Appen Ltd. (Facility Employee)')
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="Bahrain", tenant='Appen Ltd.',
                                                                 tenant_type='Facility Employee')
    app.ac_project.recruitment.edit_tenant("Bahrain", "Appen Ltd.", "Facility Employee", "Bulgaria",
                                           'Appen Ltd. (Contractor)')
    app.ac_project.recruitment.verify_locale_tenant_is_displayed("Bulgaria", "Appen Ltd.", "Contractor")
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="Bahrain", tenant='Appen Ltd.',
                                                                 tenant_type='Facility Employee', is_not=False)


@pytest.mark.dependency(depends=["test_add_tenant_all_countries_recruitment"])
def test_fail_delete_tenant_all_countries(app, create_project):
    app.ac_project.recruitment.delete_tenant("All Countries", "Appen Ltd.", "Facility Employee")
    app.verification.text_present_on_page('Error')
    app.verification.text_present_on_page('There are hiring targets or payrates attached to this tenant. You will be able to delete them once those targets or payrates are removed.')
    app.ac_project.close_error_msg()


def test_delete_tenant_successfully_without_hiring_target(app, create_project):
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Argentina", tenant='Appen Ltd. (Facility Employee)')
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="Argentina", tenant='Appen Ltd.',
                                                                 tenant_type='Facility Employee')
    app.ac_project.recruitment.delete_tenant("Argentina", "Appen Ltd.", "Facility Employee")
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="Argentina", tenant='Appen Ltd.',
                                                                 tenant_type='Facility Employee', is_not=False)
    app.navigation.click_btn('Save Changes')


# Blocking Rules
@pytest.mark.dependency()
def test_add_blocking_rules_required_fields_in_edit_mode(app, create_project):

    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    #seems to be an error showing up without reason, a bug
    app.ac_project.close_error_msg()
    el = find_elements(app.driver, "//input[@name='hasBlockingRules']/../span[@class='overlay']")
    time.sleep(2)
    el[0].click()
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page('Project is a required field.')


@pytest.mark.dependency(depends=["test_add_blocking_rules_required_fields_in_edit_mode"])
def test_add_multiple_blocking_rules(app, create_project):
    app.ac_project.recruitment.add_block_project("A A Quiz", multiple_projects=True)
    app.ac_project.recruitment.click_permanent_btn("A A Quiz")
    app.navigation.click_btn('Add Other Project')
    app.ac_project.recruitment.add_block_project("Acac Test", multiple_projects=True)
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page('A A Quiz')
    app.verification.text_present_on_page('Acac Test')


def test_delete_blocking_rules_recruitment(app, create_project):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.delete_block_project("Acac Test")
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page("Acac Test", is_not=False)


# Linked Projects
@pytest.mark.dependency()
def test_linked_projects_required_fields_in_edit_mode(app, create_project):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    el= find_elements(app.driver, "//input[@name='hasLinkedProjects']/../span[@class='overlay']")
    time.sleep(2)
    el[0].click()
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page('Project is a required field.')


@pytest.mark.dependency(depends=["test_linked_projects_required_fields_in_edit_mode"])
def test_add_multiple_linked_projects(app, create_project):
    app.ac_project.recruitment.add_linked_project("Apple Test", multiple_projects=True, is_edit_mode=True)
    app.ac_project.recruitment.add_linked_project("Automation", multiple_projects=True, is_edit_mode=True)
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page('Apple Test')
    app.verification.text_present_on_page('Automation')


def test_delete_linked_projects(app, create_project):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.add_linked_project("A A Transcription", multiple_projects=True, is_edit_mode=True)
    app.ac_project.recruitment.delete_linked_project("A A Transcription")
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page("A A Transcription", is_not=False)


# Add Notes to Recruiting Team
@pytest.mark.dependency()
def test_recruiting_team_notes_required_field(app, create_project):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.fill_out_fields({"Add Notes to Recruiting Team": "1"})
    app.navigation.click_btn("Save Changes")
    app.verification.text_present_on_page('When \"Add Notes to Recruiting Team\" is checked this is a required field.')



@pytest.mark.dependency(depends=["test_recruiting_team_notes_required_field"])
def test_add_recruiting_team_notes(app, create_project):
    app.ac_project.recruitment.fill_out_fields({"Recruiting Notes": "Test Notes to Recruiting Team"})
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page('When \"Add Notes to Recruiting Team\" is checked this is a required field.',
                                          is_not=False)
    app.ac_project.verify_project_info({
        "Notes to Recruiting Team": "Test Notes to Recruiting Team"
    })


