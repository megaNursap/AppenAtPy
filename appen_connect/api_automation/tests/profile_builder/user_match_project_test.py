import time

from adap.api_automation.utils.data_util import *
from appen_connect.api_automation.services_config.gateway import AC_GATEWAY
from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name


pytestmark = [pytest.mark.regression_ac_profile_builder, pytest.mark.regression_ac, pytest.mark.ac_api_gateway, pytest.mark.ac_api_gateway_master_profile, pytest.mark.ac_api]

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')


_country = "*"
_country_ui = "United States of America"
_locale = "Germany (United States)"
_fluency = "Native or Bilingual"
_lan = "deu"
_lan_ui = "Germany"
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
def create_project_match_vendor():
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
    _project_name = "E2E vendor match project " + generate_project_name()[0]
    _alias = "E2E vendor match project  " + generate_random_string(10)

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
def create_project_not_match_vendor():
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


def test_vendor_match_project(app, get_valid_cookies, create_project_match_vendor):
    vendor = get_test_data('autoscreening_eng_1', 'id')

    ac_api = AC_GATEWAY(get_valid_cookies)
    res = ac_api.get_user_match_project(user_id=vendor, project_id=create_project_match_vendor['id'])
    res.assert_response_status(200)

    assert res.json_response == {"userId" :vendor, "match": True}

@allure.issue("https://appen.atlassian.net/browse/ACE-17532", 'Bug: ACE-17532')
def test_vendor_not_match_project(get_valid_cookies, create_project_not_match_vendor):
    vendor = get_test_data('autoscreening_eng_1', 'id')

    ac_api = AC_GATEWAY(get_valid_cookies)
    res = ac_api.get_user_match_project(user_id=vendor, project_id=create_project_not_match_vendor['id'])
    res.assert_response_status(200)

    assert res.json_response == {"userId" :vendor, "match": False}