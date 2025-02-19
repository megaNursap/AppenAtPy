"""
create 1 vendor
create 2 projects with the same target profile question
vendor match the 1st project
vendor change answer and does not match 2nd project
"""

import time


from adap.api_automation.utils.data_util import *
from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project
from appen_connect.ui_automation.service_config.application import AC
from appen_connect.ui_automation.service_config.vendor_profile.registration_flow import new_vendor
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name

pytestmark = [pytest.mark.regression_ac_profile_builder, pytest.mark.regression_ac]

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')


_country = "*"
_country_ui = "United States of America"
_locale = "English (United States)"
_fluency = "Native or Bilingual"
_lan = "eng"
_lan_ui = "English"
_lan_country = "*"
_pay_rate = 6


@pytest.fixture(scope="module", autouse=True)
def get_valid_cookies(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.navigation.click_link('Partner Home')
    # app.navigation.click_link('View previous list page')
    # app.ac_user.select_customer('Appen Internal')
    time.sleep(2)
    global ac_api_cookie
    ac_api_cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                     app.driver.get_cookies()}
    return ac_api_cookie


@pytest.fixture(scope="module")
def first_project():
    """
    Profile target:
        AUTOMATION LEVEL OF EDUCATION
          1 - Highest level of education
          What is your highest level of education achieved?
          Pass: Primary/ Elementary or equivalent, Middle/ Junior school or equivalent,
                High school/secondary school or equivalent, Undergraduate or equivalent,
                Post-secondary diploma or equivalent, Graduate degree or equivalent,
                Master's degree or equivalent, Doctorate degree or equivalent
    """
    _project_name = "E2E UI vendor match project " + generate_project_name()[0]
    _alias = "E2E vendor UI match project  " + generate_random_string(10)

    profile_target = {
        "stage": 4,
        "qa": 1
    }
    project_config = {
        "name": _project_name,
        "alias": _alias,
        "projectType": 'Express',
        "workType": "LINGUISTICS",
        "externalSystemId": 15,
        "registrationProcessTemplateId": 1977,
        "qualificationProcessTemplateId": 1926,
        "invoice": "default",
        "profileTargetId": profile_target[pytest.env],
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
        "all_users": True,
        "update_status": "ENABLED"
    }

    _project = api_create_simple_project(new_config=project_config, cookies=ac_api_cookie)

    return _project


@pytest.fixture(scope="module")
def second_project():
    """
    Profile target:
        AUTOMATION LEVEL OF EDUCATION (REJECT)
                1 - Highest level of education
                What is your highest level of education achieved?
                Pass: Primary/ Elementary or equivalent, Doctorate degree or equivalent , Other
    """
    _project_name = "E2E vendor not match project " + generate_project_name()[0]
    _alias = "E2E vendor not match project  " + generate_random_string(10)

    profile_target = {
        "stage": 20,
        "qa": 2
    }

    project_config = {
        "name": _project_name,
        "alias": _alias,
        "projectType": 'Express',
        "workType": "LINGUISTICS",
        "externalSystemId": 15,
        "registrationProcessTemplateId": 1977,
        "qualificationProcessTemplateId": 1926,
        "invoice": "default",
        "profileTargetId": profile_target[pytest.env],
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
        "all_users": True,
        "update_status": "ENABLED"
    }

    _project = api_create_simple_project(new_config=project_config, cookies=ac_api_cookie)

    return _project


@pytest.fixture(scope="module")
def vendor1():
    _app = AC(pytest.env)
    vendor = new_vendor(_app, language='English', region='United States of America')
    # _app.destroy()
    return vendor


@pytest.mark.dependency()
def test_vendor1_match_project(app_test, vendor1, first_project):
    print("----1 ------")
    app_test.ac_user.login_as(user_name=vendor1["vendor"], password=vendor1["password"])

    app_test.navigation.click_link("Projects")

    max_time = 60 * 10
    wait = 10
    running_time = 0
    found = False
    while not found and (running_time < max_time):
        app_test.navigation.refresh_page()
        app_test.navigation.switch_to_frame("page-wrapper")
        time.sleep(1)
        app_test.vendor_pages.open_projects_tab("All projects")
        app_test.vendor_pages.search_project_by_name(first_project['alias'])
        found = app_test.vendor_pages.project_found_on_page(first_project['alias'])
        running_time += wait
        time.sleep(wait)

    assert found, "Project %s has not been found" % first_project['alias']

    app_test.vendor_pages.click_action_for_project(first_project['alias'], 'Apply')

    app_test.vendor_profile.answer_question(
                                question="What is your highest level of education achieved?",
                                answers=["Undergraduate or equivalent"],
                                question_type='radio_btn',
                                action="Submit")

    app_test.verification.text_present_on_page("Thank you for your answers. You are a project match!")
    app_test.navigation.click_btn("Continue To Registration")


@pytest.mark.dependency(depends=["test_vendor1_match_project"])
def test_vendor2_not_match_project(app_test, vendor1, second_project):
    app_test.ac_user.login_as(user_name=vendor1["vendor"], password=vendor1["password"])

    app_test.navigation.click_link("Projects")

    max_time = 60 * 10
    wait = 10
    running_time = 0
    found = False
    while not found and (running_time < max_time):
        app_test.navigation.refresh_page()
        app_test.navigation.switch_to_frame("page-wrapper")
        time.sleep(1)
        app_test.vendor_pages.open_projects_tab("All projects")
        app_test.vendor_pages.search_project_by_name(second_project['alias'])
        found = app_test.vendor_pages.project_found_on_page(second_project['alias'])
        running_time += wait
        time.sleep(wait)

    assert found, "Project %s has not been found" % second_project['alias']

    app_test.vendor_pages.click_action_for_project(second_project['alias'], 'Apply')

    assert app_test.vendor_profile.get_current_answer('What is your highest level of education achieved?') == "Undergraduate or equivalent"

    app_test.vendor_profile.answer_question(
        question="What is your highest level of education achieved?",
        answers=["Post-secondary diploma or equivalent"],
        question_type='radio_btn',
        action="Submit")

    app_test.verification.text_present_on_page("We’re sorry, you are not a project match.")
