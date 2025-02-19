import time

import pytest
from faker import Faker
from adap.api_automation.utils.data_util import *
from appen_connect.api_automation.services_config.ac_api import AC_API
from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project

pytestmark = [pytest.mark.regression_ac_core, pytest.mark.regression_ac, pytest.mark.ac_user_project_mapping]

faker = Faker()

USER_NAME = get_test_data('test_ui_account', 'email')
PASSWORD = get_test_data('test_ui_account', 'password')
VENDOR = get_test_data('test_project_mapping_vendor', 'email')
VENDOR_ID = get_test_data('test_project_mapping_vendor', 'id')


@pytest.fixture(scope="function")
def login(app_test):
    app_test.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)


# TODO find ui alias from api
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
    "qualificationProcessTemplateId": 1386,
    "registrationProcessTemplateId": 764,
    "locale": {
        "country": _country
    },
    "hiring_target": {
        "language": _lan,
        "languageCountry": _lan_country,
        "restrictToCountry": _country
    },
    "pay_rates": {
        "spokenFluency": _fluency.upper().replace(" ","_"),
        "writtenFluency": _fluency.upper().replace(" ","_"),
        "rateValue": _pay_rate,
        "taskType": "DEFAULT",
        "language": _lan,
        "languageCountry": "*",
        "restrictToCountry": _country
    },
    "invoice":"default",
    "update_status":"READY"
}

def test_e2e_project_mapping(app_test, login):
    app_test.navigation.click_link('Partner Home')
    # app_test.navigation.click_link('View previous list page')
    # app_test.ac_user.select_customer('Appen Internal')
    time.sleep(2)
    ac_api_cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in app_test.driver.get_cookies()}

    _new_group = "Test group "+faker.zipcode()

    # 1. create new group
    app_test.navigation.click_link('Groups')
    app_test.partner_home.create_group(group_name=_new_group, group_description="Group Description")
    print("--new group--", _new_group)
    time.sleep(5)

    # 2. add group to customer
    app_test.navigation.click_link('Programs')
    app_test.partner_home.open_customer('Appen Internal')
    app_test.partner_home.add_group_to_customer(_new_group)
    print("--added to customer--")

    # 3. add group to vendor
    time.sleep(2)
    app_test.navigation.click_link('Internal Home')
    time.sleep(2)
    app_test.navigation.click_link('Vendors')
    app_test.vendor_pages.open_vendor_profile_by(VENDOR, search_type='name')
    app_test.vendor_pages.add_group_to_vendor(_new_group)
    print("--added to vendor--")

    # 4. add locale to vendor (optional, depends on project)
    app_test.navigation.click_link("Locales & Groups")
    actual_locale = app_test.vendor_pages.get_locale()
    print("--locale: ", actual_locale)

    if {'locale': _locale,
        'translate_locale': '',
        'spoken_fluency': _fluency,
        'written_fluency': _fluency} not in actual_locale:

        print("--add new locale--")
        app_test.vendor_pages.add_locale_to_vendor({
            "selectedLocaleId": _locale,
            "spokenFluency": _fluency,
            "writtenFluency": _fluency
        })
        print("--add new locale-- done")

    # 5. create project - enabled
    _project = api_create_simple_project(new_config=project_config, cookies=ac_api_cookie)
    status_payload = {
        "status": "ENABLED"
    }
    api = AC_API(ac_api_cookie)
    status = api.update_project_status(_project['id'], status_payload)
    status.assert_response_status(200)

    print("--project--", _project)

    # 6. add project to experiment list
    app_test.navigation.click_link('Partner Home')
    app_test.navigation.click_link('Experiment List')

    app_test.partner_home.open_experiment_for_project(_project['name'])
    # assert False
    # app_test.partner_home.add_experiment_group(_new_group)
    # print("--added to experimental list--")

    # 7. add pay rate to project for new group (??? do this by api)
    time.sleep(3)
    app_test.navigation.click_link('Projects')
    time.sleep(3)
    app_test.navigation.switch_to_frame("page-wrapper")
    app_test.project_list.filter_project_list_by(_project['name'])
    app_test.project_list.open_project_by_name(_project['name'])
    app_test.driver.switch_to.default_content()
    try:
        app_test.navigation.click_btn("View new experience")
        time.sleep(2)
    except:
        print("new UI")
    # app_test.project_old_ui.add_pay_rate(data={
    #     "localeLang": _lan_ui,
    #     "localeCountry": _country_ui,
    #     "group.id": "ALL USERS",
    #     "country": _country_ui,
    #     # "state": "",
    #     "spokenFluency": _fluency,
    #     "writtenFluency": _fluency,
    #     # "requireCertified": "",
    #     # "workdayId": "",
    #     # "disabled": "",
    #     "payRate": _pay_rate
    # })
    # app_test.project_old_ui.add_pay_rate(data={
    #     "localeLang": _lan_ui,
    #     "localeCountry": _country_ui,
    #     "group.id": _new_group,
    #     "country": _country_ui,
    #     "spokenFluency": _fluency,
    #     "writtenFluency": _fluency,
    #
    #     "payRate": _pay_rate
    # })
    # print("--added pay rate--")

    # 8. verification
    app_test.navigation.click_link('Internal Home')
    time.sleep(2)
    app_test.navigation.click_link('Vendors')

    # app_test.vendor_pages.open_vendor_profile_by(VENDOR, search_type='name')   # system is not stable
    # app_test.navigation.open_page("https://connect-stage.appen.com/qrp/core/vendor/view/%s" % VENDOR_ID)
    # app_test.navigation.click_link("Impersonate")
    # time.sleep(120)
    # app_test.navigation.click_link('All Projects')
    # app_test.vendor_pages.all_projects_vendor()
    # app_test.verification.text_present_on_page(_project["alias"])
