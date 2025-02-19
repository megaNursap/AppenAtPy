"""
[AC] Profile Builder + Crowd Submission
https://appen.atlassian.net/browse/QED-2348
"""

import time

import pytest

from adap.api_automation.utils.data_util import get_user_email, get_user_password, generate_random_string
from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name

pytestmark = [pytest.mark.regression_ac_profile_builder, pytest.mark.regression_ac, pytest.mark.ac_profile_builder]

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

_project_name = "Profile builder config test " + generate_project_name()[0]
_alias = "Profile builder config test " + generate_random_string(5)

_country = "*"
_country_ui = "United States of America"
_locale = "English (United States)"
_fluency = "Native or Bilingual"
_lan = "eng"
_lan_ui = "English"
_lan_country = "*"
_pay_rate = 6

project_config_profile_builder = {
    "name": _project_name,
    "alias": _alias,
    "projectType": 'Express',
    "workType": "LINGUISTICS",
    "externalSystemId": 15,
    "registrationProcessTemplateId": 1977,
    "qualificationProcessTemplateId": 1926,
    "invoice": "default",
    # "profileTargetId": 151,
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

    _project = api_create_simple_project(new_config=project_config_profile_builder, cookies=ac_api_cookie)

    return _project


@pytest.mark.dependency()
def test_profile_builder_access(app, create_project):
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

    time.sleep(2)
    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn('Resume Setup')
    time.sleep(1)
    app.navigation.switch_to_frame("page-wrapper")
    app.ac_project.click_on_step('Recruitment')

    app.verification.text_present_on_page("Target Screening and Data Requirements")

    app.ac_project.recruitment.fill_out_fields({
        "Target Screening and Data Requirements": "1"
    })

    app.verification.text_present_on_page("Select target audience group")
    app.verification.text_present_on_page("Create new target Group")

    app.ac_project.recruitment.fill_out_fields({
        "Target Screening and Data Requirements": "1"
    })

    app.verification.text_present_on_page("Select target audience group", is_not=False)
    app.verification.text_present_on_page("Create new target Group", is_not=False)


@pytest.mark.dependency(depends=["test_profile_builder_access"])
def test_add_new_target_group(app, create_project):
    app.ac_project.recruitment.fill_out_fields({
        "Target Screening and Data Requirements": "1"
    })

    app.ac_project.recruitment.click_create_new_target_group()
    app.verification.text_present_on_page("Configure Target Audience")

    app.navigation.click_btn("Configure Target Audience")

    app.verification.text_present_on_page("Create Target Audience Group")
    app.verification.text_present_on_page("Group Name")
    app.verification.text_present_on_page("Group Description")


@pytest.mark.dependency(depends=["test_add_new_target_group"])
def test_target_group_required_fields(app, create_project):
    app.ac_project.recruitment.modal_window_action("Save")
    app.verification.text_present_on_page("Group name is a required field.")
    app.verification.text_present_on_page("Group description is a required field.")

    app.ac_project.recruitment.modal_window_action("Cancel")


@pytest.mark.dependency(depends=["test_target_group_required_fields"])
def test_target_group_details(app, create_project):
    app.navigation.click_btn("Configure Target Audience")

    app.ac_project.recruitment.new_target_group_details({"Group Name": _alias,
                                                         "Group Description": " test description"
                                                         })

    app.ac_project.recruitment.modal_window_action("Save")

    app.verification.text_present_on_page(_alias)
    app.verification.text_present_on_page("Target Audience Builder")
    app.verification.text_present_on_page("Profile Questions")


@pytest.mark.dependency(depends=["test_target_group_details"])
def test_target_group_edit_details(app, create_project):
    app.ac_project.recruitment.click_edit_target_group_details()

    app.ac_project.recruitment.new_target_group_details({"Group Name": _project_name,
                                                         "Group Description": " test description updated"
                                                         })

    app.ac_project.recruitment.modal_window_action("Save")

    app.verification.text_present_on_page(_project_name)
    app.verification.text_present_on_page("Target Audience Builder")


@pytest.mark.dependency(depends=["test_target_group_edit_details"])
def test_target_group_transport_required_fields(app, create_project):
    app.ac_project.recruitment.open_question_group("Transport")

    app.ac_project.recruitment.add_question_to_builder("Transport", "Modes of transport")
    app.ac_project.recruitment.save_question_in_builder('Modes of transport')

    app.verification.text_present_on_page("Checkbox Group is a required field.")
    app.verification.text_present_on_page("Action is a required field.")


@pytest.mark.dependency(depends=["test_target_group_transport_required_fields"])
def test_add_question_transport(app, create_project):
    app.ac_project.recruitment.set_up_answers_for_question(q_type='checkbox',
                                                           question='Modes of transport',
                                                           answers=['Car', 'Boat'],
                                                           action_checked='Pass Through'
                                                           # action_unchecked='Reject'
                                                           )

    app.ac_project.recruitment.save_question_in_builder('Modes of transport')

    app.verification.text_present_on_page("Checkbox Group is a required field.", is_not=False)
    app.verification.text_present_on_page("Action is a required field.", is_not=False)

    app.navigation.click_btn('Create Target Audience')


@pytest.mark.dependency(depends=["test_add_question_transport"])
def test_project_view_target_group(app, create_project):
    app.navigation.click_btn('Exit')
    app.verification.text_present_on_page('Target Screening and Data Requirements')

    app.ac_project.recruitment.load_project({"Select target audience group": _project_name})

    app.verification.text_present_on_page('Modes of transport')
    app.verification.text_present_on_page('Do you own any of the following modes of transport?')
    app.verification.text_present_on_page('Pass: Car, Boat')
    app.verification.text_present_on_page('Created by')


# #     TODO created by -  current user

@pytest.mark.dependency(depends=["test_project_view_target_group"])
def test_edit_target_group(app, create_project):
    app.ac_project.recruitment.target_group_edit()

    app.verification.text_present_on_page('Target Audience Builder')

    app.ac_project.recruitment.edit_question_in_builder('Modes of transport')

    app.ac_project.recruitment.set_up_answers_for_question(q_type='checkbox',
                                                           question='Modes of transport',
                                                           answers=['Motorbike']
                                                           )

    app.ac_project.recruitment.save_question_in_builder('Modes of transport')

    app.navigation.click_btn('Save Updates')
    app.navigation.click_btn('Exit')

    time.sleep(6)
    app.verification.text_present_on_page('Pass: Car, Motorbike, Boat')


@pytest.mark.dependency(depends=["test_edit_target_group"])
def test_add_2nd_question(app, create_project):
    app.ac_project.recruitment.target_group_edit()
    app.verification.text_present_on_page('Target Audience Builder')

    app.ac_project.recruitment.open_question_group("Work & Education")

    app.ac_project.recruitment.add_question_to_builder("Work & Education", "Highest level of education")
    app.ac_project.recruitment.save_question_in_builder('Highest level of education')

    app.ac_project.recruitment.set_up_answers_for_question(q_type='checkbox',
                                                           question='Highest level of education',
                                                           answers=['Graduate degree or equivalent'],
                                                           action_checked='Pass Through'
                                                           )

    time.sleep(1)
    app.ac_project.recruitment.save_question_in_builder('Highest level of education')

    app.navigation.click_btn('Save Updates')
    app.navigation.click_btn('Exit')

    time.sleep(4)
    app.verification.text_present_on_page('Pass: Car, Motorbike, Boat')
    app.verification.text_present_on_page('Pass: Graduate degree or equivalent')


@pytest.mark.dependency(depends=["test_add_2nd_question"])
def test_remove_question_from_group(app, create_project):
    app.ac_project.recruitment.target_group_edit()

    app.ac_project.recruitment.remove_question_from_builder('Highest level of education')
    app.navigation.click_btn('Save Updates')
    app.navigation.click_btn('Exit')

    time.sleep(2)
    app.verification.text_present_on_page('Pass: Car, Motorbike, Boat')
    app.verification.text_present_on_page('Pass: Graduate degree or equivalent', is_not=False)


@pytest.mark.dependency(depends=["test_remove_question_from_group"])
def test_target_group_duplicate_not_allowed(app, create_project):
    app.ac_project.recruitment.click_create_new_target_group()

    app.navigation.click_btn("Configure Target Audience")

    app.ac_project.recruitment.new_target_group_details({"Group Name": _project_name,
                                                         "Group Description": " test description"
                                                         })

    app.ac_project.recruitment.modal_window_action("Save")

    app.ac_project.recruitment.open_question_group("Transport")

    app.ac_project.recruitment.add_question_to_builder("Transport", "Modes of transport")

    app.ac_project.recruitment.set_up_answers_for_question(q_type='checkbox',
                                                           question='Modes of transport',
                                                           answers=['Car'],
                                                           action_checked='Pass Through',
                                                           action_unchecked='Reject'
                                                           )

    app.ac_project.recruitment.save_question_in_builder('Modes of transport')

    app.navigation.click_btn('Create Target Audience')

    app.verification.text_present_on_page('Name Already Exists For This Profile Target.')


@pytest.mark.dependency(depends=["test_target_group_duplicate_not_allowed"])
def test_no_access_edit_target(app_test, create_project):
    user_name = get_user_email('ac_internal_user')
    password = get_user_password('ac_internal_user')

    app_test.ac_user.login_as(user_name=user_name, password=password)
    app_test.navigation.click_link('Partner Home')
    # app_test.navigation.click_link('View previous list page')
    # app_test.ac_user.select_customer('Appen Internal')

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

    time.sleep(2)
    app_test.navigation.switch_to_frame("page-wrapper")
    app_test.navigation.click_btn('Resume Setup')
    time.sleep(1)
    app_test.navigation.switch_to_frame("page-wrapper")
    app_test.ac_project.click_on_step('Recruitment')

    assert app_test.ac_project.recruitment.edit_target_group_button_is_disable()

    # clear target group
    app_test.verification.text_present_on_page('No group selected', is_not=False)
    app_test.ac_project.recruitment.target_group_clear()
    app_test.verification.text_present_on_page('No group selected')
