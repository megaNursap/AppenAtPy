import time

from adap.api_automation.utils.data_util import *
from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project
from appen_connect.ui_automation.service_config.application import AC
from appen_connect.ui_automation.service_config.vendor_profile.registration_flow import new_vendor
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name

pytestmark = [pytest.mark.regression_ac_profile_builder, pytest.mark.regression_ac]


def get_valid_cookies():
    app = AC(pytest.env)
    USER_NAME = get_user_email('test_ui_account')
    PASSWORD = get_user_password('test_ui_account')
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.navigation.click_link('Partner Home')
    # app.navigation.click_link('View previous list page')
    # app.ac_user.select_customer('Appen Internal')
    time.sleep(2)
    global ac_api_cookie
    ac_api_cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                     app.driver.get_cookies()}
    app.driver.close()
    # app.destroy()
    return ac_api_cookie


def new_project_vendor_profile(api_cookies):
    """
    Profile target:
        AUTOMATION VENDOR PROFILE
            1 - Skin tone
            How would you describe your skin tone/ complexion?
            Pass: Deep, Dark/ Rich, Tan/Olive
    """

    _country = "*"
    _country_ui = "United States of America"
    _locale = "English (United States)"
    _fluency = "Native or Bilingual"
    _lan = "eng"
    _lan_ui = "English"
    _lan_country = "*"
    _pay_rate = 6

    _project_name = "E2E Vendor Profile " + generate_project_name()[0]
    _alias = "E2E Vendor Profile  " + generate_random_string(10)

    profile_target = {
        "stage": 295,
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
            "taskType": "DEFAULT",
            "language": _lan,
            "languageCountry": "*",
            "restrictToCountry": _country,
            "defaultRate": False
        },
        "all_users": True,
        "update_status": "ENABLED"
    }

    _project = api_create_simple_project(new_config=project_config, cookies=api_cookies)
    print(f"PROJECT_ID: {_project['id']}")

    return _project


@pytest.mark.dependency()
def test_create_new_vendor_for_profile(app_test):
    global vendor
    vendor = new_vendor(app_test,
                        pr='profile',
                        verification_code={'stage':'816160',
                                            'qa':'A3B76E'}[pytest.env],
                        language='English',
                        region='United States of America')

    print(f'LOGINNAME {vendor["vendor"]}')
    app_test.navigation.switch_to_frame("page-wrapper")
    assert app_test.verification.text_present_on_page('Welcome')
    # assert app_test.verification.text_present_on_page('Get started now!')



@pytest.mark.dependency(depends=["test_create_new_vendor_for_profile"])
def test_vendor_profile_questionary_access(app):
    app.ac_user.login_as(user_name=vendor["vendor"], password=vendor["password"])
    # app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_link('Profile')
    current_url = app.driver.current_url
    app.navigation.open_page(current_url+'?pb=true')

    app.navigation.switch_to_frame("page-wrapper")
    app.verification.text_present_on_page('MORE ABOUT ME')
    app.vendor_profile.open_tab('MORE ABOUT ME')
    app.vendor_profile.confirm_consent_form()
    time.sleep(5)
    assert app.vendor_profile.get_category_of_questions() == ['Tell us more about yourself!', 'Family & Me', 'Health & Medical', 'Home & Income', 'Social', 'Technologies & Communications', 'Transport', 'Work & Education', 'Entertainment & Activities', 'Politics']

    category_details = app.vendor_profile.get_category_details('Health & Medical')
    assert category_details['no_answers']
    assert category_details['edit_btn_status'] == 'disabled'


@pytest.mark.dependency(depends=["test_vendor_profile_questionary_access"])
def test_vendor_profile_start_answering(app):
    category_details = app.vendor_profile.get_category_details('Social')
    assert category_details['no_answers']
    assert category_details['edit_btn_status'] == 'disabled'

    app.vendor_profile.click_start_answering_category('Social')

    app.verification.text_present_on_page('Do you use any social apps / messenger accounts?')

    app.vendor_profile.answer_question(
        question="Do you use any social apps / messenger accounts?",
        answers=["Yes"],
        question_type='radio_btn',
        action="Submit")

    category_details = app.vendor_profile.get_category_details('Social')
    assert not category_details['no_answers']
    assert category_details['edit_btn_status'] == 'enabled'
    assert not category_details['all_answered']
    assert category_details['unanswered_questions'] == 2
    assert category_details['answers'] == {
        "Do you use any social apps / messenger accounts?": "Yes"
    }
    # verify that answers are saved
    app.navigation.refresh_page()

    app.navigation.switch_to_frame("page-wrapper")
    app.vendor_profile.open_tab('MORE ABOUT ME')

    category_details = app.vendor_profile.get_category_details('Social')
    assert not category_details['no_answers']
    assert category_details['edit_btn_status'] == 'enabled'
    assert not category_details['all_answered']
    assert category_details['unanswered_questions'] == 2
    assert category_details['answers'] == {
        "Do you use any social apps / messenger accounts?": "Yes"
    }


@pytest.mark.dependency(depends=["test_vendor_profile_start_answering"])
def test_vendor_profile_edit_answer(app):
    app.vendor_profile.click_edit_answers('Social')

    app.verification.text_present_on_page('Do you use any social apps / messenger accounts?')
    app.vendor_profile.answer_question(
        question="Do you use any social apps / messenger accounts?",
        answers=["No"],
        question_type='radio_btn',
        action="Submit")


    category_details = app.vendor_profile.get_category_details('Social')
    assert not category_details['no_answers']
    assert category_details['edit_btn_status'] == 'enabled'
    assert not category_details['all_answered']
    assert category_details['unanswered_questions'] == 1
    assert category_details['answers'] == {
        "Do you use any social apps / messenger accounts?": "No"
    }

    # verify that answers are saved
    app.navigation.refresh_page()

    app.navigation.switch_to_frame("page-wrapper")
    app.vendor_profile.open_tab('MORE ABOUT ME')

    category_details = app.vendor_profile.get_category_details('Social')
    assert not category_details['no_answers']
    assert category_details['edit_btn_status'] == 'enabled'
    assert not category_details['all_answered']
    assert category_details['unanswered_questions'] == 1
    assert category_details['answers'] == {
        "Do you use any social apps / messenger accounts?": "No"
    }


@pytest.mark.dependency(depends=["test_vendor_profile_edit_answer"])
def test_vendor_profile_cancel_edit_answer(app):
    app.vendor_profile.click_edit_answers('Social')

    app.vendor_profile.answer_question(
        question="Do you use any social apps / messenger accounts?",
        answers=["Yes"],
        question_type='radio_btn',
        action="Cancel")

    category_details = app.vendor_profile.get_category_details('Social')
    assert not category_details['no_answers']
    assert category_details['edit_btn_status'] == 'enabled'
    assert not category_details['all_answered']
    assert category_details['unanswered_questions'] == 1
    assert category_details['answers'] == {
        "Do you use any social apps / messenger accounts?": "No"
    }


@pytest.mark.dependency(depends=["test_vendor_profile_edit_answer"])
def test_vendor_profile_family_category_less_more_btn(app):
    app.verification.text_present_on_page('The following category of questions relates to demographic information '
                                          'about yourself and your family. Training data from diverse populations of '
                                          'contributors is needed to train AI to perform equally well for everyone. '
                                          'To provide training data that supports inclusive AI, and to ensure all '
                                          'groups are fully represented in the data that we collect, we are asking '
                                          'you to complete these questions. All questions in this category are '
                                          'optional, and, as in all Appen projects, you can opt out at any time.')

    app.vendor_profile.click_less_more_link_for_category('Family & Me', 'Less')

    app.verification.text_present_on_page('The following category of questions relates to demographic information about yourself and your famil...')


@pytest.mark.dependency(depends=["test_vendor_profile_family_category_less_more_btn"])
def test_vendor_profile_family_sensitive_questions(app):
    # app.vendor_profile.click_start_answering_category('Family & Me')  #commented since Family&Me category already partially completed
    app.vendor_profile.click_edit_answers("Family & Me")

    app.verification.text_present_on_page('Please note that this question is asked to target the scope and/or '
                                          'collection of views from different demographic profiles. To provide '
                                          'training data that supports inclusive AI, and to ensure all groups are '
                                          'fully represented in the data that we collect, we are asking you this '
                                          'question.')

    app.verification.text_present_on_page('Below is a question about your skin tone. Images of many different skin '
                                          'tone are needed to train image-based AI to perform equally well for '
                                          'everyone. To provide training data that supports inclusive AI, '
                                          'and to ensure all groups are fully represented in the data that we '
                                          'collect, we are asking you this question. Please note that it is optional, '
                                          'and, as in all Appen projects, you can opt out at any time.')

def test_vendor_apply_to_project_and_answer_question(app_test):
    cookies = get_valid_cookies()
    _project = new_project_vendor_profile(api_cookies=cookies)
    project_alias = _project['alias']
    print(f"Line 263 PROJECT_ALIAS {project_alias}")
    app_test.ac_user.login_as(user_name=vendor["vendor"], password=vendor["password"])

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
        app_test.vendor_pages.search_project_by_name(project_alias)
        found = app_test.vendor_pages.project_found_on_page(project_alias)
        running_time += wait
        time.sleep(wait)

    assert found, "Project %s has not been found" % project_alias

    app_test.vendor_pages.click_action_for_project(project_alias, 'Apply')
    app_test.vendor_profile.answer_question(
        question="How would you describe your skin tone/ complexion?",
        answers=["Deep"],
        question_type='radio_btn',
        action="Submit")

    app_test.verification.text_present_on_page("Thank you for your answers. You are a project match!")
    app_test.navigation.click_btn("Continue To Registration")


def test_vendor_profile_question_answered_in_project(app_test):
    app_test.ac_user.login_as(user_name=vendor["vendor"], password=vendor["password"])
    app_test.navigation.click_link('Profile')
    current_url = app_test.driver.current_url
    app_test.navigation.open_page(current_url+'?pb=true')

    app_test.navigation.switch_to_frame("page-wrapper")
    app_test.vendor_profile.open_tab('MORE ABOUT ME')
    app_test.vendor_profile.confirm_consent_form()
    time.sleep(5)

    category_details = app_test.vendor_profile.get_category_details('Family & Me')
    assert not category_details['no_answers']
    assert category_details['edit_btn_status'] == 'enabled'
    assert not category_details['all_answered']
    assert category_details['unanswered_questions'] == 17
    assert category_details['answers'] == {'How would you describe your skin tone/ complexion? (optional)': 'Deep'}


# TODO vendor provides answer in profile and change it by project
# TODO complex questions with dependencies
# TODO answer all type of questions: date; dropdown; input
# TODO answers for sensitive/system questions
