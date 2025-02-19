"""
Create a project with specific "Hiring Targets & Metrics" configuration using API
and the tests validates the Project Hiring Target configuration when newly created project is being viewed and tests while editing the configuration
"""
import datetime
import time

from adap.ui_automation.utils.selenium_utils import find_elements
from appen_connect.api_automation.services_config.ac_api import AC_API
from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project
from adap.api_automation.utils.data_util import *
from appen_connect.ui_automation.service_config.project.project_helper import tomorrow_date
from conftest import ac_api_cookie

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

pytestmark = [pytest.mark.regression_ac_project_view, pytest.mark.regression_ac, pytest.mark.ac_ui_project_hiring_targets, pytest.mark.ac_ui_project_view_n_edit]

_country = "*"
_country_ui = "United States of America"
_locale = "English (United States)"
_fluency = "Native or Bilingual"
_lan = "eng"
_lan_ui = "English"
_lan_country = "*"
_pay_rate = 6
_tomorrow_date = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%m/%d/%Y")

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
def hiring_target_project(app):
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
    status = api.update_project_status(project_id, status_payload)
    status.assert_response_status(200)

    project_status = status.json_response['status']
    _project['status'] = project_status
    return _project



@pytest.mark.dependency()
def test_hiring_targets_metrics(app,hiring_target_project):

    app.navigation.click_link('Projects')
    app.navigation.switch_to_frame("page-wrapper")

    app.project_list.filter_project_list_by(hiring_target_project['name'])
    app.project_list.open_project_by_name(hiring_target_project['name'])

    app.driver.switch_to.default_content()
    try:
        app.navigation.click_btn("View new experience")
        time.sleep(2)
    except:
        print("new UI")

    app.navigation.switch_to_frame("page-wrapper")
    app.ac_project.click_on_step('Recruitment', on_bottom=False)
    app.verification.text_present_on_page('Recruitment')
    app.verification.text_present_on_page('Locale Tenants')
    app.ac_project.recruitment.verify_locale_tenant_is_displayed(country="All Countries", tenant='Appen Ltd.',
                                                                 tenant_type='Contractor', is_view_mode=True)

    app.verification.text_present_on_page('Hiring Targets')
    formatted_date = (custom_strftime('%b {S}, %Y', (datetime.date.today() + datetime.timedelta(days=1))))

    app.ac_project.recruitment.verify_regular_hiring_target_row_present_on_page(language='English',
                                                                                region='All Countries',
                                                                                restrict_country='All Countries',
                                                                                assigned_owner='.',
                                                                                deadline=formatted_date, target='10',
                                                                                qualifying='0', active='0',
                                                                                progress='0', status=hiring_target_project['status'])

    hiring_progress = app.ac_project.recruitment.get_hiring_progress()
    assert (hiring_progress == '0%')
    app.verification.text_present_on_page('Custom Demographic Requirements')


@pytest.mark.dependency()
def test_add_hiring_target_required_field_in_edit_mode(app):
    app.ac_project.click_on_step('Recruitment', on_bottom=False)
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.navigation.click_btn('Add Target')
    app.ac_project.recruitment.click_save_ht()
    app.verification.text_present_on_page("Locale Language is a required field.")
    app.verification.text_present_on_page("Locale Region is a required field.")
    app.verification.text_present_on_page("Restrict to Country is a required field.")
    app.verification.text_present_on_page("Hiring Deadline is a required field.")
    app.verification.text_present_on_page("Target Contributors is a required field.")
    app.verification.text_present_on_page("Target Hours/Tasks is a required field.")
    app.ac_project.recruitment.click_cancel_hiring_target()


@pytest.mark.dependency(depends=["test_add_hiring_target_required_field_in_edit_mode"])
def test_add_hiring_target_in_edit_mode(app):
    formatted_date = (custom_strftime('%b {S}, %Y', (datetime.date.today() + datetime.timedelta(days=1))))
    app.ac_project.recruitment.add_target(language='Achinese', region='All Countries',
                                          restrict_country='All Countries',
                                          deadline=tomorrow_date(), target='12')
    app.navigation.click_btn('Save Changes')
    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='Achinese',
                                                                        loc_dialect_from='All Countries',
                                                                        rest_to_country='All Countries',
                                                                        deadline=formatted_date, target='12')


@pytest.mark.dependency(depends=["test_add_hiring_target_in_edit_mode"])
def test_copy_hiring_target_error(app):
    app.ac_project.click_on_step('Recruitment', on_bottom=False)
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.click_copy_target("Achinese", "All Countries", "All Countries")
    app.ac_project.recruitment.click_save_ht()
    app.verification.text_present_on_page(
        "You have a very similar target already included. If you need to increase a target, consider editing it.")
    app.ac_project.recruitment.close_error_msg()


@pytest.mark.dependency(depends=["test_copy_hiring_target_error"])
def test_edit_hiring_target(app):
    app.ac_project.recruitment.fill_out_fields({"Locale Language": "Kashmiri",
                                                "Language Region": "India"})
    app.ac_project.recruitment.click_save_ht()
    app.navigation.click_btn('Save Changes')
    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='Kashmiri',
                                                                        loc_dialect_from='India',
                                                                        rest_to_country='All Countries', target='12')

#test deprecated per https://appen.atlassian.net/browse/ACE-16503
# @pytest.mark.dependency(depends=["test_edit_hiring_target"])
# def test_delete_hiring_target_metrics(app):
#     app.navigation.click_btn('Edit')
#     app.ac_project.close_error_msg()
#     app.ac_project.recruitment.delete_target("Kashmiri", "India", "All Countries")
#     formatted_date = (custom_strftime('%b {S}, %Y', (datetime.date.today() + datetime.timedelta(days=1))))
#     app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='Kashmiri',
#                                                                         loc_dialect_from='India',
#                                                                         rest_to_country='All Countries',
#                                                                         deadline=formatted_date,
#                                                                         target='12', row_is_present=False)


@pytest.mark.dependency(depends=["test_edit_hiring_target"])
def test_pause_hiring_target_metrics(app):
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()

    deadline = (custom_strftime('%b {S}, %Y', (datetime.date.today() + datetime.timedelta(days=1))))
    loc_lang = 'Kashmiri'
    loc_dialect = 'India'
    rest_to_country = 'All Countries'
    target = '12'

    initial_status = 'Paused'
    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from=loc_lang,
                                                                        loc_dialect_from=loc_dialect,
                                                                        rest_to_country=rest_to_country,
                                                                        deadline=deadline,
                                                                        target=target, status=initial_status)

    change_status_to = 'Activate'
    expected_status = 'Active'
    app.ac_project.recruitment.target_activate_pause(loc_lang, loc_dialect, rest_to_country,option=change_status_to)

    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from=loc_lang,
                                                                        loc_dialect_from=loc_dialect,
                                                                        rest_to_country=rest_to_country,
                                                                        deadline=deadline,
                                                                        target=target, status=expected_status)

    change_status_to = 'Pause'
    expected_status = 'Paused'
    app.ac_project.recruitment.target_activate_pause(loc_lang, loc_dialect, rest_to_country, option=change_status_to)

    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from=loc_lang,
                                                                        loc_dialect_from=loc_dialect,
                                                                        rest_to_country=rest_to_country,
                                                                        deadline=deadline,
                                                                        target=target, status=expected_status)



