"""
[AC] Profile Builder
https://appen.atlassian.net/browse/QED-2509
"""

import random
import datetime
import time

import pytest

from adap.api_automation.utils.data_util import get_test_data
from appen_connect.api_automation.services_config.ac_api_v1 import AC_API_V1
from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project
from appen_connect.ui_automation.service_config.vendor_profile.registration_flow import new_vendor
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name


pytestmark = [pytest.mark.regression_ac_profile_builder, pytest.mark.regression_ac]


USER_NAME = get_test_data('test_ui_account', 'email')
PASSWORD = get_test_data('test_ui_account', 'password')

_project = generate_project_name()

_country = "*"
_country_ui = "United States of America"
_locale = "English (United States)"
_fluency = "Native or Bilingual"
_lan = "eng"
_lan_ui = "English"
_lan_country = "*"
_pay_rate = 6

project_config = {
    "projectType": 'Express',
    "workType": "LINGUISTICS",
    "externalSystemId": 15,
    "qualificationProcessTemplateId": 85,
    "registrationProcessTemplateId": 1977,
    "profileTargetId": 45,
    "customerId": 53,
    "rateType": "HOURLY",
    "businessUnit": "CR",
    "defaultPageId": 11976,
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
    "invoice": "default",
    "update_status": "ENABLED"
}


def vendor_open_project(current_app, vendor, project_alias):
    current_app.ac_user.login_as(user_name=vendor["vendor"], password=vendor["password"])

    try:
        current_app.navigation.switch_to_frame("page-wrapper")
        current_app.vendor_profile.registration_flow.fill_out_fields({"YOUR PRIMARY LANGUAGE": "English",
                                                                     "YOUR LANGUAGE REGION": "United States of America"})

        current_app.navigation.click_btn("Continue")

        current_app.navigation.switch_to_frame("page-wrapper")
        current_app.vendor_profile.registration_flow.get_start_from_welcome_page("Browse jobs")
    except:
        print("Vendor logged in")


    try:
        # current_app.navigation.switch_to_frame("page-wrapper")
        current_app.navigation.click_btn('Skip')
    except:
        pass

    # current_app.navigation.switch_to_frame("page-wrapper")
    # current_app.ac_project.click_header_info('All Projects')

    try:
        current_app.navigation.switch_to_frame("page-wrapper")
        current_app.navigation.click_btn('Skip')
    except:
        pass

    max_time = 60*10
    # TODO add wait until function based on api
    wait = 10
    running_time = 0
    found = False
    while not found and (running_time < max_time):
        print("while")
        current_app.navigation.refresh_page()
        current_app.navigation.switch_to_frame("page-wrapper")
        time.sleep(1)
        current_app.vendor_pages.open_projects_tab("All projects")
        name_input = current_app.driver.find_element('xpath',"//input[@placeholder='Search Projects' or @placeholder='Search by project name']")
        name_input.clear()
        name_input.send_keys(project_alias)
        found = True if len(current_app.driver.find_elements('xpath',"//table//h2[contains(text(),'%s')]" % project_alias)) > 0 else False
        running_time += wait
        time.sleep(wait)

    assert found, "Project %s has not been found" %  project_alias

    current_app.vendor_pages.click_action_for_project(project_alias, 'Apply')


@pytest.fixture(scope="module")
def access_cookie(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.navigation.click_link('Partner Home')
    # app.navigation.click_link('View previous list page')
    # app.ac_user.select_customer('Appen Internal')
    time.sleep(2)
    ac_api_cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                     app.driver.get_cookies()}

    return ac_api_cookie


@pytest.mark.dependency()
def test_vendor_match_project_checkbox_question(app_test, access_cookie):
    # "profileTargetId": 45,
    # --- [DO NOT DELETE] AUTOMATION - LAPTOP
    # 1 - PC/ Laptop ownership
    # What brand of desktop and/or laptop device do you own or have access to?
    # Pass: Acer, Apple, Asus

    global vendor
    vendor = new_vendor(app_test, 'pb')

    project_config["profileTargetId"] = 45
    _project = api_create_simple_project(project_config, access_cookie)

    vendor_open_project(app_test, vendor, _project["alias"])
    # app_test.vendor_pages.click_action_for_project(project_alias, 'Apply')
    app_test.verification.wait_untill_text_present_on_the_page(
        text="Thank you for your answers. You are a project match!", max_time=20)
    app_test.verification.text_present_on_page('Thank you for your answers. You are a project match!')
    app_test.navigation.click_btn("Continue To Registration")
    try:
        app_test.vendor_pages.answer_the_question_radio_btn("Do you own an internet enabled smartphone?", "No")
        app_test.vendor_profile.registration_flow.select_value_for_choice_and_proceed('submit', 'Continue')[0].click()
    except:
        pass


@pytest.mark.dependency(depends=["test_vendor_match_project_checkbox_question"])
def test_vendor_not_match_project_checkbox_question(app_test, access_cookie):
    # "profileTargetId": 46,
    # [DO NOT DELETE] AUTOMATION - RESIDENCE
    # 1 - Residence
    # What type of residence do you currently live in?
    # Pass: Detached home, Unit/ Apartment

    project_config["profileTargetId"] = 46
    _project = api_create_simple_project(project_config, access_cookie)

    vendor_open_project(app_test, vendor, _project["alias"])

    app_test.vendor_profile.answer_question(question="What type of residence do you currently live in?",
                                            answers=["Townhouse"],
                                            question_type='radio_btn',
                                            action="Submit")

    app_test.verification.text_present_on_page("We’re sorry, you are not a project match.")
    app_test.navigation.click_btn('Close')

