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
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name
from conftest import ac_api_cookie

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

pytestmark = [pytest.mark.regression_ac_project_view, pytest.mark.regression_ac, pytest.mark.ac_ui_project_support_user_access,
              pytest.mark.ac_ui_project_view_n_edit, pytest.mark.ac_ui_project_view_n_test]

#_project = generate_project_name()

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
    "businessUnit": "CR",
    "workdayTaskId": "CR99912",
    "customerId": 53, # Appen Internal
    # "defaultPageId": 0,
    #"description": "Test Project" + _project[1],
    #"name": _project[0],
    "projectType": "Regular",
    "workType": "LINGUISTICS",
    "qualificationProcessTemplateId": 1386,
    "rateType": "PIECERATE",
    "registrationProcessTemplateId": 764,
    "externalSystemId": 15,
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
    "defaultPageId": 9895,
    "skillsReview": 'true',
    "acanProject": 'true',
    "supportTeam": [
        {
            "userId": 1294202,
            "role": "SUPPORT"
        }
    ],
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

    global _project_generated
    _project_generated = api_create_simple_project(project_config, ac_api_cookie)
    print(_project_generated)
    """
    status_payload = {
        "status": "ENABLED"
    }
    project_id = _project['id']
    api = AC_API(ac_api_cookie)
    status = api.update_project_status(project_id, status_payload)
    status.assert_response_status(200)
    project_status = status.json_response['status']
    _project['status'] = project_status
    """
    return _project_generated


# ---------- View and edit 'USER PROJECT PAGE' page ---------
@pytest.mark.dependency()
def test_user_project_page_support(app, create_project):
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
    app.ac_project.user_project.click_user_project_page()
    app.verification.text_present_on_page('User Project Page')
    app.ac_project.verify_project_info({
        "Default Page Task": "Tasks"
    })
    #These 2 values are not being set using API payload, will ask Developer.
    app.verification.text_present_on_page('Not available')
    app.verification.text_present_on_page('No')


@pytest.mark.dependency(depends=["test_user_project_page_support"])
def test_edit_user_project_page_support(app, create_project):
    app.ac_project.user_project.click_user_project_page()
    app.verification.text_present_on_page('User Project Page')
    app.navigation.click_btn('Edit')
    app.ac_project.user_project.fill_out_fields(data={
        "Available Skill Review": "1",
        "ACAN Project": "1"
    })
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page('Available')
    app.verification.text_present_on_page('Yes')


# ---------- View and edit 'SUPPORT TEAM' page ---------
def test_view_support_team_page(app, create_project):
    app.ac_project.click_on_step('Support Team')
    app.verification.text_present_on_page('Support Team')
    app.ac_project.support.verify_support_team_information_is_displayed(user_role='Support',
                                                                        member_name='Support (Ac)',
                                                                        phone_number='+11111111111',
                                                                        email='acsupport@appen.com')


# https://appen.atlassian.net/browse/QED-1821
def test_add_team_member(app, create_project):
    app.ac_project.click_on_step('Support Team')
    app.navigation.click_btn('Edit')
    app.navigation.click_btn('Add Member')
    # click save without select user role and member name
    app.navigation.click_btn('Save Changes')
    app.verification.text_present_on_page('User Role is a required field.')
    app.verification.text_present_on_page('Member name is a required field.')
    app.ac_project.close_error_msg()
    # select user role and member name and save info
    app.ac_project.support.fill_out_fields(data={"Support User Role": "Finance",
                                                 "Member Name": "Support (Ac)"},
                                           add_more_members=True
                                           )
    app.navigation.click_btn('Save Changes')
    app.ac_project.support.verify_support_team_information_is_displayed(user_role='Finance',
                                                                        member_name='Support (Ac)',
                                                                        phone_number='+11111111111',
                                                                        email='acsupport@appen.com')


def test_add_multiple_team_members(app, create_project):
    app.ac_project.click_on_step('Support Team')
    app.navigation.click_btn('Edit')
    user_roles = ['Human Resources', 'Support', 'Engineering']
    for i in range(3):
        app.navigation.click_btn('Add Member')
        app.ac_project.support.fill_out_fields(data={"Support User Role": user_roles[i],
                                                     "Member Name": "Support (Ac)"},
                                               add_more_members=True
                                               )
    app.navigation.click_btn('Save Changes')
    app.ac_project.support.verify_support_team_information_is_displayed(user_role='Human Resources',
                                                                        member_name='Support (Ac)',
                                                                        phone_number='+11111111111',
                                                                        email='acsupport@appen.com')
    app.ac_project.support.verify_support_team_information_is_displayed(user_role='Support',
                                                                        member_name='Support (Ac)',
                                                                        phone_number='+11111111111',
                                                                        email='acsupport@appen.com')
    app.ac_project.support.verify_support_team_information_is_displayed(user_role='Engineering',
                                                                        member_name='Support (Ac)',
                                                                        phone_number='+11111111111',
                                                                        email='acsupport@appen.com')


def test_delete_team_member(app, create_project):
    app.ac_project.click_on_step('Support Team')
    app.navigation.click_btn('Edit')
    app.navigation.click_btn('Add Member')
    app.ac_project.support.fill_out_fields(data={"Support User Role": 'Project Manager',
                                                 "Member Name": "Support (Ac)"},
                                           add_more_members=True
                                           )
    app.ac_project.support.delete_support_team_member()
    app.navigation.click_btn('Save Changes')
    time.sleep(2)
    app.ac_project.support.verify_support_team_information_is_displayed(user_role='Project Manager',
                                                                        member_name='Support (Ac)',
                                                                        phone_number='+11111111111',
                                                                        email='acsupport@appen.com', is_not=False)


# ---------- Test project status change ---------
# https://appen.atlassian.net/browse/QED-1805
@pytest.mark.dependency()
def test_status_change_from_ready_to_enabled(app, create_project):
    app.ac_project.click_on_step('Overview & tools')
    assert app.ac_project.get_project_info_for_section('Status') == 'Ready'
    app.verification.text_present_on_page('Your project is ready to be enabled. '
                                          'Click on “Enable Project” to start recruitment.')
    app.navigation.click_btn('Enable Project')
    assert app.ac_project.get_project_info_for_section('Status') == 'Enabled'
    app.verification.text_present_on_page('Your project is now running and recruitment is in progress.')


@pytest.mark.dependency(depends=["test_status_change_from_ready_to_enabled"])
def test_status_change_from_enabled_to_disabled(app, create_project):
    app.navigation.click_btn('Disable Project')
    assert app.ac_project.get_project_info_for_section('Status') == 'Disabled'
    app.verification.text_present_on_page('Your project is currently disabled. '
                                          'Click on “Enable Project” to resume recruitment.')


@pytest.mark.dependency(depends=["test_status_change_from_enabled_to_disabled"])
def test_status_change_from_disabled_to_enabled(app, create_project):
    app.navigation.click_btn('Enable Project')
    assert app.ac_project.get_project_info_for_section('Status') == 'Enabled'


def test_resume_setup_draft_status_project(app, create_project):
    app.driver.switch_to.default_content()
    app.navigation.click_link('Projects')
    app.navigation.switch_to_frame("page-wrapper")
    app.project_list.filter_project_list_by(status='Draft')
    random_project = random.choice(app.project_list.get_projects_on_page())
    app.project_list.open_project_by_id(random_project['id'])
    app.driver.switch_to.default_content()
    app.navigation.click_btn("View new experience")
    time.sleep(2)
    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn('Resume Setup')
    time.sleep(1)
    app.verification.current_url_contains('/editNewProject')