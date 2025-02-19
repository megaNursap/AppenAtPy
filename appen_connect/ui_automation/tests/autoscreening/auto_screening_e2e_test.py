import datetime
import time

import pytest

from adap.api_automation.utils.data_util import get_user_email, get_user_password, generate_random_string, get_test_data
from appen_connect.api_automation.services_config.ac_api import AC_API
from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name

pytestmark = [pytest.mark.regression_ac_autoscreening, pytest.mark.regression_ac, pytest.mark.ac_autoscreening]

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

_project_name = "E2E Autoscreening test " + generate_project_name()[0]
_alias = "E2E Autoscreening test " + generate_random_string(8)

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
    "registrationProcessTemplateId": 5145,
    "qualificationProcessTemplateId": 1926,
    "invoice": "default",
    "profileTargetId": 114,
    'targetAudienceBuilderId':114,
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
        "restrictToCountry": _country,
        "create": True
    }
}


def vendor_login(user, password, app_test):
    app_test.ac_user.login_as(user_name=user, password=password)
    time.sleep(60)
    app_test.navigation.click_link('Projects')
    app_test.navigation.switch_to_frame("page-wrapper")
    app_test.vendor_pages.open_projects_tab("All projects")

    app_test.vendor_pages.search_project_by_name(_alias)
    # app_test.vendor_pages.click_action_for_project(_alias, 'Apply')
    app_test.navigation.click_btn('Apply')

    app_test.verification.wait_untill_text_present_on_the_page(text="Thank you for your answers. You are a project match!",max_time=20)
    app_test.navigation.click_btn("Continue To Registration")

    try:
        app_test.vendor_pages.answer_the_question_radio_btn("Do you own an internet enabled smartphone?", "No")
        app_test.vendor_profile.registration_flow.select_value_for_choice_and_proceed('submit', 'Continue')[0].click()
    except:
        pass


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

    _project = api_create_simple_project(new_config=project_config, cookies=ac_api_cookie)
    # _project = {"id":7609,
    #             "name": "E2E Autoscreening test Ramirez Ltd07/16/2021",
    #             "alias":"E2E Autoscreening test ningf"
    #             }

    #   add hiring target
    api = AC_API(ac_api_cookie)

    tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1)).isoformat()
    hiring_target_payload = {
        "deadline": tomorrow,
        "language": "fra",
        "languageCountry": "FRA",
        "languageCountryTo": "",
        "languageTo": "",
        "ownerId": 0,
        "priority": 0,
        "projectId": _project["id"],
        "restrictToCountry": _country,
        "target": 1,
        "targetHours": 4
    }
    hir_target = api.add_hiring_target(hiring_target_payload)
    hir_target.assert_response_status(201)

    pay_rates_payload = {
        "projectId": _project["id"],
        "writtenFluency": "NATIVE_OR_BILINGUAL",
        "spokenFluency": "NATIVE_OR_BILINGUAL",
        "rateValue": 5,
        # "disabled": false,
        "language": "fra",
        "languageCountry": "FRA",
        "languageTo": "",
        "languageCountryTo": "",
        "restrictToCountry": "FRA",
        "groupId": 1,
        "taskType": "DEFAULT",
        "defaultRate": 'true',
        "countryPayRateId": 9
    }
    pay_rates = api.create_pay_rate(pay_rates_payload)
    pay_rates.assert_response_status(201)

    return _project


@pytest.mark.dependency()
def test_set_up_project(app, create_project):
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
    app.ac_project.click_on_step('Recruitment')

    app.ac_project.recruitment.fill_out_fields({
        "Auto-screening Configuration": 1
    })

    app.navigation.click_btn("Add Configuration")
    app.ac_project.recruitment.fill_out_fields({
        "Locale": "French (France)",
        "Max users per day": 1,
        "Max active users": 1
    })
    app.ac_project.recruitment.click_save_auto_screening()

    app.navigation.click_btn("Add Configuration")
    app.ac_project.recruitment.fill_out_fields({
        "Locale": "English (United States)",
        "Max users per day": 1,
        "Max active users": 1
    })
    app.ac_project.recruitment.click_save_auto_screening()

    app.ac_project.recruitment.fill_out_fields({"Target Screening and Data Requirements": "1"})

    app.ac_project.recruitment.fill_out_fields(data={
        "Select target audience group": "autoscreening test"})

    app.navigation.click_btn('Save')

    app.ac_project.click_on_step('Invoice & Payment')
    app.navigation.click_btn("Add Pay Rate")
    app.ac_project.payment.fill_out_fields({"Custom Pay Rates": "1"})

    app.ac_project.payment.select_custom_pay_rates('English (All Countries)', 'All Countries')

    # Entering the details on custom page
    app.ac_project.payment.fill_out_fields({"Spoken Fluency": "Native or Bilingual",
                                            "Written Fluency": "Native or Bilingual",
                                            "User Group": "All users",
                                            "Task Type": "Default",
                                            "Rate": _pay_rate
                                            }, action='Save')

    app.navigation.click_btn("Add Pay Rate")
    app.ac_project.payment.fill_out_fields({"Custom Pay Rates": "1"})

    app.ac_project.payment.select_custom_pay_rates('French (France)', 'All Countries')

    app.ac_project.payment.fill_out_fields({"Spoken Fluency": "Native or Bilingual",
                                            "Written Fluency": "Native or Bilingual",
                                            "User Group": "All users",
                                            "Task Type": "Default",
                                            "Rate": _pay_rate
                                            }, action='Save')

    # app.ac_project.click_on_step('Project Access')
    # app.navigation.click_btn("Save")
    app.ac_project.click_on_step('Preview')

    app.navigation.click_btn('Finish Project Setup')

    app.navigation.click_btn('Go to Project Page')

    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn("Enable Project")
    time.sleep(120)

    app.ac_project.click_on_step('Registration & Qualification')

    assert app.ac_project.get_count_registered_vendors() == '0'
    assert app.ac_project.get_count_qualified_vendors() == '0'


@pytest.mark.dependency(depends=["test_set_up_project"])
def test_auto_screening_vendor_eng(app_test, app):
    vendor = get_test_data('autoscreening_eng_1', 'user_name')
    password = get_test_data('autoscreening_eng_1', 'password')

    vendor_login(vendor, password, app_test)

    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")

    app.ac_project.click_on_step('Registration & Qualification')

    assert app.ac_project.get_count_registered_vendors() == '1 (of 1)'
    assert app.ac_project.get_count_qualified_vendors() == '1 (of 1)'


@pytest.mark.dependency(depends=["test_auto_screening_vendor_eng"])
def test_auto_screening_vendor_fra(app_test, app):
    vendor = get_test_data('autoscreening_fra', 'user_name')
    password = get_test_data('autoscreening_fra', 'password')

    vendor_login(vendor, password, app_test)

    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")

    app.ac_project.click_on_step('Registration & Qualification')

    assert app.ac_project.get_count_registered_vendors() == '2 (of 2)'
    assert app.ac_project.get_count_qualified_vendors() == '2 (of 2)'


@pytest.mark.dependency(depends=["test_auto_screening_vendor_fra"])
def test_not_auto_screening_vendor_but_match(app_test, app):
    vendor = get_test_data('autoscreening_eng_2', 'user_name')
    password = get_test_data('autoscreening_eng_2', 'password')
    time.sleep(120)
    vendor_login(vendor, password, app_test)
    app_test.verification.text_present_on_page("Depending on our current business opportunities and your "
                                               "submitted information, you may be invited to continue the "
                                               "qualification process.")

    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")

    app.ac_project.click_on_step('Registration & Qualification')

    assert app.ac_project.get_count_registered_vendors() == '2 (of 3)'
    assert app.ac_project.get_count_qualified_vendors() == '2 (of 2)'
