import datetime
import time

import pytest
import datetime as ds
from faker import Faker

from adap.api_automation.utils.data_util import get_test_data
from adap.ui_automation.utils.js_utils import scroll_to_page_bottom
from appen_connect.ui_automation.service_config.vendor_profile.registration_flow import new_vendor


pytestmark = [pytest.mark.regression_ac_yukon]

verification_code = {
    "stage": "20AB81"
}


@pytest.mark.dependency()
def test_yukon_create_new_account(app):
    global yukon_vendor
    yukon_vendor = new_vendor(app,
                              pr='yukon_',
                              verification_code=verification_code[pytest.env],
                              language='English',
                              region='United States of America',
                              state='Alaska',
                              vendor_first_name='Yukon',
                              user_last_name='Test',
                              open_sign_up_page=True)

    print(yukon_vendor)
    app.navigation.switch_to_frame("page-wrapper")
    assert app.verification.text_present_on_page('Welcome')
    app.navigation.click_btn('Skip')
    app.navigation.deactivate_iframe()


@pytest.mark.dependency(depends=["test_yukon_create_new_account"])
def test_yukon_complete_profile(app):
    fake = Faker()
    app.navigation.click_link('Profile')
    app.navigation.switch_to_frame("page-wrapper")
    time.sleep(2)

    app.navigation.click_link('Complete Profile')
    app.navigation.switch_to_frame("page-wrapper")

    app.vendor_profile.open_tab('Location')
    residency_history_date = (ds.date.today() - ds.timedelta(days=4800)).strftime("%Y/%m/%d")
    app.vendor_profile.location.fill_out_fields({"Street Address": "12529 State Road 535",
                                                 "CITY": "City City",
                                                 "ZIP CODE": "90090",
                                                 "Residency History": residency_history_date
                                                 })

    app.navigation.click_btn("Next: Education")

    app.vendor_profile.open_tab('Education')
    app.vendor_profile.education.fill_out_fields(
        {
            "HIGHEST LEVEL OF EDUCATION": "Master\'s degree or equivalent",
            "LINGUISTICS QUALIFICATION (optional)": "Master’s degree – Studying"
        }
    )
    app.navigation.click_btn("Next: Work Experience")

    app.vendor_profile.open_tab('Phone Number')
    app.vendor_profile.phone.fill_out_fields({"Mobile Phone Number": fake.phone_number()})
    app.navigation.click_btn("Next: Preview")

    app.vendor_profile.open_tab('Preview')
    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn("Save and Submit Profile")
    time.sleep(3)
    app.navigation.click_btn("Continue")

    app.navigation.deactivate_iframe()

    app.verification.text_present_on_page('Smartphone Information')


@pytest.mark.dependency(depends=["test_yukon_complete_profile"])
def test_yukon_additional_profile(app):
    app.verification.current_url_contains("/complete_profile/smartphone")
    app.vendor_profile.registration_flow.smartphone_verification(enable=True)
    time.sleep(3)

    app.verification.current_url_contains("/complete_profile/view")
    additional_info_elements = app.vendor_profile.registration_flow.select_value_for_choice_and_proceed('radio',
                                                                                                        'true')
    additional_info_elements[0].click()

    additional_info_elements = app.vendor_profile.registration_flow.select_value_for_choice_and_proceed(
        'radio',
        'false')
    for i in range(0, 3):
        additional_info_elements[i].click()

    app.vendor_profile.registration_flow.select_familiarity_level('Expert')
    app.vendor_profile.registration_flow.select_value_for_choice_and_proceed('submit', 'Submit')[0].click()
    app.verification.current_url_contains("/process_resolution")


@pytest.mark.dependency(depends=["test_yukon_additional_profile"])
def test_yukon_project_apply(app):
    app.navigation.switch_to_frame("page-wrapper")

    project_name = 'Yukon'
    app.vendor_pages.click_action_for_project(project_name, 'Apply Now')

    app.verification.text_present_on_page('Profile Requirements')

    app.vendor_profile.answer_question(
        question="Which gender do you identify with?",
        answers=["Woman"],
        question_type='radio_btn',
        action="Submit")

    app.verification.text_present_on_page("Thank you for your answers. You are a project match!")
    app.navigation.click_btn("Continue To Registration")

    app.navigation.deactivate_iframe()
    app.navigation.click_btn('Proceed')
    app.verification.current_url_contains('raterlabs')

    app.navigation.switch_to_frame("page-wrapper")
    app.verification.text_present_on_page('Welcome to Yukon')


@pytest.mark.dependency(depends=["test_yukon_project_apply"])
def test_yukon_start_project_application(app):
    app.navigation.click_btn('Next: Sign Rater Agreement')

    time.sleep(3)
    app.verification.text_present_on_page('Sign Rater Agreement')
    app.verification.text_present_on_page('PERSONALIZED RATER AGREEMENT')
    app.verification.text_present_on_page('By participating in this type of rating, I understand and agree that')
    app.verification.text_present_on_page('Create Yukon Support Ticket')

    app.vendor_profile.registration_flow.accept_the_form(action='I understand and agree')
    app.navigation.click_btn('Next: Provide required information')
    time.sleep(2)

#     TODO  verify 'Create Yukon Support Ticket link


@pytest.mark.dependency(depends=["test_yukon_start_project_application"])
@pytest.mark.dependency()
def test_yukon_gmail_verification(app):
    faker = Faker()
    prefix = datetime.datetime.now().strftime("%Y_%m_%d") + faker.zipcode()
    email = f'qateam_{prefix}@gmail.com'
    app.vendor_profile.project_application.input_required_info(gmail=email,
                                                               retype_gmail=email,
                                                               do_you_use_gmail_with_family='Yes',
                                                               web_history_enabled='Yes',
                                                               how_often_do_you_use_gmail='Once per week')

    app.navigation.click_btn('Next')

    app.verification.text_present_on_page('Gmail Verification')
    app.verification.text_present_on_page(
        'We have sent a verification link to your provided gmail. Please retype the code here.')

    app.vendor_profile.project_application.input_gmail_verification_code('999999', action='Submit')

    app.verification.text_present_on_page('Please complete the following required information for project Yukon')
    app.verification.text_present_on_page('Provide required information')

    app.vendor_profile.project_application.input_additional_info(how_long_do_you_live_in_country='More than 5 years',
                                                                 translation_exp='Yes',
                                                                 current_company='N/A')

    app.navigation.click_btn('Next: Waiting to be qualified')
    time.sleep(3)


@pytest.mark.dependency(depends=["test_yukon_gmail_verification"])
def test_yukon_wait_to_be_qualified(app):
    app.verification.text_present_on_page('Waiting to be qualified')
    app.verification.text_present_on_page('STATUS:')
    app.verification.text_present_on_page('In Progress')
    app.verification.text_present_on_page("Your application is under review. This process takes about 2 business days "
                                          "for review. If you're a fit, you will then be scheduled for a "
                                          "qualification exam. Check back here for an updated status or watch your "
                                          "email for next steps!")

    app.verification.text_present_on_page('Additional Resources & Support')
    app.verification.text_present_on_page('Appen Learning Center')
    app.verification.text_present_on_page('Yukon microsoft teams group')

    app.verification.verify_link_redirects_to('Create Yukon Support Ticket',
                                              'https://crowdsupport.appen.com/hc/en-us/requests/new',
                                              new_window=True)

    # TODO verify Go to Learning Center and Join Yukon MS Teams links


@pytest.mark.dependency(depends=["test_yukon_wait_to_be_qualified"])
def test_yukon_vendor_screening(app_test):
    PASSWORD = get_test_data('test_ui_account', 'password')
    INTERNAL_USER_NAME = get_test_data('test_ui_account', 'email')

    app_test.ac_user.login_as_raterlabs_user(user_name=INTERNAL_USER_NAME, password=PASSWORD)

    app_test.navigation.click_link("Employees")
    app_test.vendor_pages.open_vendor_profile_by(yukon_vendor['vendor'], search_type='name', status='Any Status')

    app_test.vendor_pages.vendor_qualification_action("Completed")
    app_test.vendor_profile.registration_flow.select_option_and_proceed('complete-reason', 'ADDRESS')
    app_test.navigation.click_btn('Complete')
    time.sleep(6)

    app_test.navigation.click_link('Projects')
    time.sleep(2)
    app_test.vendor_pages.screen_user_take_action_on_project('Aztec Aztec Google Yukon (Yukon) (Yukon)', "Completed")
    app_test.navigation.click_btn('Confirm')
    time.sleep(2)

    for i in range(2):
        app_test.navigation.click_link('Projects')
        app_test.vendor_pages.screen_user_take_action_on_project('Aztec Aztec Google Yukon (Yukon) (Yukon)',
                                                                 "Completed")
        time.sleep(2)

    app_test.navigation.click_link('Logout')


@pytest.mark.dependency(depends=["test_yukon_vendor_screening"])
def test_yukon_vendor_complete_exam_page(app):
    app.navigation.refresh_page()
    for i in range(3):
        app.vendor_profile.registration_flow.accept_the_form(action='I understand and agree')
        app.navigation.click_btn("Continue")

    time.sleep(4)
    app.navigation.switch_to_frame("page-wrapper")

    app.verification.text_present_on_page('Complete Exam')
    app.verification.text_present_on_page('Exam Deadline:')
    app.verification.text_present_on_page('System Requirements')
    app.verification.text_present_on_page('Exam Tracker')
    app.verification.text_present_on_page('In Progress')
    app.verification.text_present_on_page('We are processing your results and might take a few hours')


@pytest.mark.dependency(depends=["test_yukon_vendor_complete_exam_page"])
def test_yukon_complete_exam(app_test):
    PASSWORD = get_test_data('test_ui_account', 'password')
    INTERNAL_USER_NAME = get_test_data('test_ui_account', 'email')
    app_test.ac_user.login_as_raterlabs_user(user_name=INTERNAL_USER_NAME, password=PASSWORD)

    app_test.navigation.click_link("Employees")
    app_test.vendor_pages.open_vendor_profile_by(yukon_vendor['vendor'], search_type='name', status='Any Status')

    app_test.navigation.click_link('Projects')
    app_test.vendor_pages.screen_user_take_action_on_project('Aztec Aztec Google Yukon (Yukon) (Yukon)',
                                                             "Completed")
    time.sleep(2)
    app_test.navigation.click_link('Logout')


@pytest.mark.dependency(depends=["test_yukon_complete_exam"])
def test_yukon_start_activation_process(app):
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")

    app.verification.text_present_on_page('Start Activation Process')
    app.verification.text_present_on_page('At this point, your application will be reviewed by our team and you will '
                                          'receive instructions via email for next steps. This process takes about '
                                          '7-9 days to be completed. In the meantime, you may continue with the '
                                          'activation process!')

    app.navigation.click_link('Proceed')
    app.verification.current_url_contains('/vendors/activation/view')


