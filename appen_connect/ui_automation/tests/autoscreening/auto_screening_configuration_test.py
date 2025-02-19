import time

import pytest

from adap.api_automation.utils.data_util import get_user_email, get_user_password, generate_random_string
from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name

pytestmark = [pytest.mark.regression_ac_autoscreening, pytest.mark.regression_ac, pytest.mark.ac_autoscreening]

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

_project_name = "Autoscreening config test " + generate_project_name()[0]
_alias = "Autoscreening config test " + generate_random_string(5)

_country = "*"
_country_ui = "United States of America"
_locale = "English (United States)"
_fluency = "Native or Bilingual"
_lan = "eng"
_lan_ui = "English"
_lan_country = "*"
_pay_rate = 6




@pytest.fixture(scope="module")
def create_project(app):
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
        }
    }

    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.navigation.click_link('Partner Home')
    # app.navigation.click_link('View previous list page')
    # app.ac_user.select_customer('Appen Internal')
    time.sleep(2)
    try:
        app.driver.accept_alert()
    except:
        print('no alerts')

    time.sleep(2)
    global ac_api_cookie
    ac_api_cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                     app.driver.get_cookies()}

    _project = api_create_simple_project(new_config = project_config, cookies=ac_api_cookie)

    return _project


@pytest.mark.dependency()
def test_autoscreen_access(app, create_project):
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

    app.verification.text_present_on_page("Auto-screening Configuration")
    app.verification.text_present_on_page("Auto-screening configuration entries at the project level by locale.")
    app.verification.text_present_on_page("Only required if the project has a registration/qualification process defined for it.")

    app.ac_project.recruitment.fill_out_fields({
        "Auto-screening Configuration": 1
    })
    app.verification.text_present_on_page("Add Configuration")

    app.ac_project.recruitment.fill_out_fields({
        "Auto-screening Configuration": 1
    })
    app.verification.text_present_on_page("Add Configuration", is_not=False)


@pytest.mark.dependency(depends=["test_autoscreen_access"])
def test_add_new_config(app, create_project):
    # pass
    app.ac_project.recruitment.fill_out_fields({
        "Auto-screening Configuration":1
    })

    app.navigation.click_btn("Add Configuration")

    app.verification.text_present_on_page("Add Auto-screening Configuration")

    app.ac_project.recruitment.fill_out_fields({
        "Locale": "French (France)",
        "Max users per day": 10,
        "Max active users":20
    })

    app.ac_project.recruitment.click_save_auto_screening()

    res = app.ac_project.recruitment.get_autoscfreening_table_details()
    assert res == [{'locale': 'French (France)', 'users_per_day': '10', 'users_total': '20'}]

    app.navigation.click_btn("Add Configuration")
    app.ac_project.recruitment.fill_out_fields({
        "Locale": "English (United States)",
        "Max users per day": 2,
        "Max active users": 3
    })

    app.ac_project.recruitment.click_save_auto_screening()

    app.ac_project.recruitment.fill_out_fields({"Target Screening and Data Requirements": "1"})
    app.verification.text_present_on_page("Use existing target group")
    app.verification.text_present_on_page("Create new target Group")
    app.verification.text_present_on_page("Select target audience group")

    app.ac_project.recruitment.fill_out_fields(data={
        "Select target audience group": "test"})

    res = app.ac_project.recruitment.get_autoscfreening_table_details()
    assert res == [{'locale': 'French (France)', 'users_per_day': '10', 'users_total': '20'},
                   {'locale': 'English (United States)', 'users_per_day': '2', 'users_total': '3'}]


@pytest.mark.dependency(depends=["test_add_new_config"])
def test_edit_users_autoscreen(app, create_project):
    app.ac_project.recruitment.edit_autoscreen_locale('English (United States)')
    app.ac_project.recruitment.fill_out_fields({
        "Max users per day": 10,
        "Max active users": 30
    })
    app.ac_project.recruitment.click_save_auto_screening()

    res = app.ac_project.recruitment.get_autoscfreening_table_details()
    assert res == [{'locale': 'French (France)', 'users_per_day': '10', 'users_total': '20'},
                   {'locale': 'English (United States)', 'users_per_day': '10', 'users_total': '30'}]


@pytest.mark.dependency(depends=["test_edit_users_autoscreen"])
def test_delete_locale_from_autoscreen(app, create_project):
    app.ac_project.recruitment.delete_autoscreen_locale('French (France)')
    res = app.ac_project.recruitment.get_autoscfreening_table_details()
    assert res == [{'locale': 'English (United States)', 'users_per_day': '10', 'users_total': '30'}]

    app.navigation.click_btn("Save")
    # app.ac_project.click_on_step('Project Access')
    # app.navigation.click_btn("Save")
    app.ac_project.click_on_step('Preview')

    app.navigation.click_btn('Finish Project Setup')
    assert app.verification.count_text_present_on_page('Error') == 0,'Unexpected error displayed'


@pytest.mark.dependency(depends=["test_delete_locale_from_autoscreen"])
def test_project_view_set_up_autoscreen(app_test):
    app_test.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app_test.navigation.click_link('Partner Home')

    app_test.navigation.click_link('Projects')
    app_test.navigation.switch_to_frame("page-wrapper")
    app_test.project_list.filter_project_list_by(_project_name)
    app_test.project_list.open_project_by_name(_project_name)

    app_test.driver.switch_to.default_content()
    try:
        app_test.navigation.click_btn("View new experience")
        time.sleep(2)
    except:
        print("new UI")

    app_test.navigation.switch_to_frame("page-wrapper")
    time.sleep(3)
    app_test.ac_project.click_on_step('Recruitment')
    app_test.navigation.click_btn('Edit')

    app_test.navigation.click_btn("Add Configuration")

    # add new locale
    app_test.ac_project.recruitment.fill_out_fields({
        "Locale": "French (France)",
        "Max users per day": 10,
        "Max active users":20
    })

    app_test.ac_project.recruitment.click_save_auto_screening()

    res = app_test.ac_project.recruitment.get_autoscfreening_table_details()
    assert {'locale': 'French (France)', 'users_per_day': '10', 'users_total': '20'} in res

    # edit config
    app_test.ac_project.recruitment.edit_autoscreen_locale('French (France)')
    app_test.ac_project.recruitment.fill_out_fields({
        "Max users per day": 12,
        "Max active users": 12
    })
    app_test.ac_project.recruitment.click_save_auto_screening()

    res = app_test.ac_project.recruitment.get_autoscfreening_table_details()
    assert {'locale': 'French (France)', 'users_per_day': '12', 'users_total': '12'} in res

    # delete locale
    app_test.ac_project.recruitment.delete_autoscreen_locale('French (France)')
    res = app_test.ac_project.recruitment.get_autoscfreening_table_details()
    assert {'locale': 'French (France)', 'users_per_day': '12', 'users_total': '12'}  not in res
