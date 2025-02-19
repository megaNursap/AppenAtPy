import time

from adap.api_automation.utils.data_util import get_test_data
from adap.api_automation.utils.judgments_util import create_screenshot
from adap.ui_automation.utils.js_utils import scroll_to_page_bottom
from appen_connect.ui_automation.service_config.vendor_profile.registration_flow import new_vendor
import pytest
import datetime as ds
from appen_connect.ui_automation.tests.yukon_project.yukon_landing_page_test import URL
from faker import Faker

pytestmark = [pytest.mark.regression_ac_yukon]


@pytest.mark.dependency()
def test_yukon_create_new_account_landing_page(app_test):
    fake = Faker()
    app_test.navigation.open_page(URL[pytest.env])
    time.sleep(7)

    try:
        app_test.navigation.click_btn("Cookies")
    except:
        print("no Accept Cookies button")

    app_test.navigation.switch_to_frame("page-wrapper")
    create_screenshot(app_test.driver, "before1")

    app_test.ac_user.shasta_click_btn("Start now! Apply to Yukon.")
    create_screenshot(app_test.driver, "before2")

    app_test.ac_user.shasta_click_btn("Create an Account")
    create_screenshot(app_test.driver, "before3")

    verification_code = '4CD90D'

    global yukon_vendor
    yukon_vendor = new_vendor(app_test, pr='yukon_', verification_code=verification_code,
                               language='English', state='Alaska',
                              region='United States of America', open_sign_up_page=False)

    app_test.navigation.switch_to_frame("page-wrapper")
    app_test.navigation.click_btn('Fill & Submit Profile')

    app_test.navigation.switch_to_frame("page-wrapper")
    app_test.vendor_profile.open_tab('Location')
    #residency_history_date = (ds.date.today() - ds.timedelta(days=1800)).strftime("%Y/%m/%d")
    residency_history_years = "2 years"
    app_test.vendor_profile.location.fill_out_fields({"Street Address": "12529 State Road 535",
                                                      "CITY": "City City",
                                                      "ZIP CODE": "90090"
                                                      })

    app_test.vendor_profile.location.residence_history_of_worker(residency_history_years)
    app_test.navigation.click_btn("Next: Education")

    app_test.vendor_profile.open_tab('Education')
    app_test.vendor_profile.education.fill_out_fields(
        {
            "HIGHEST LEVEL OF EDUCATION": "Master\'s degree or equivalent",
            "LINGUISTICS QUALIFICATION": "Master’s degree – Studying"
        }
    )
    app_test.navigation.click_btn("Next: Work Experience")

    app_test.vendor_profile.open_tab('Phone Number')
    app_test.vendor_profile.phone.fill_out_fields({"Mobile Phone Number": fake.phone_number()})
    app_test.navigation.click_btn("Next: Preview")

    app_test.vendor_profile.open_tab('Preview')
    scroll_to_page_bottom(app_test.driver)
    app_test.navigation.click_btn("Save and Submit Profile")
    time.sleep(3)
    app_test.navigation.click_btn("Continue")

    app_test.verification.current_url_contains("/complete_profile/smartphone")
    app_test.vendor_profile.registration_flow.smartphone_verification(enable=True)
    time.sleep(3)

    app_test.verification.current_url_contains("/complete_profile/view")
    additional_info_elements = app_test.vendor_profile.registration_flow.select_value_for_choice_and_proceed('radio',
                                                                                                             'true')
    additional_info_elements[0].click()

    additional_info_elements = app_test.vendor_profile.registration_flow.select_value_for_choice_and_proceed(
        'radio',
        'false')
    for i in range(0, 3):
        additional_info_elements[i].click()

    app_test.vendor_profile.registration_flow.select_familiarity_level('Expert')
    app_test.vendor_profile.registration_flow.select_value_for_choice_and_proceed('submit', 'Submit')[0].click()
    app_test.verification.current_url_contains("/process_resolution")
    app_test.navigation.click_link("Logout")

    print("------", yukon_vendor)


@pytest.mark.dependency(depends=["test_yukon_create_new_account_landing_page"])
def test_yukon_project_qualify_vendor(app_test):
    PASSWORD = get_test_data('test_ui_account', 'password')
    INTERNAL_USER_NAME = get_test_data('test_ui_account', 'email')

    app_test.ac_user.login_as(user_name=INTERNAL_USER_NAME, password=PASSWORD)

    app_test.navigation.click_link("Vendors")
    app_test.vendor_pages.open_vendor_profile_by(yukon_vendor['vendor'], search_type='name', status='Any Status')

    app_test.vendor_pages.vendor_qualification_action("Completed")
    app_test.vendor_profile.registration_flow.select_option_and_proceed('complete-reason', 'ADDRESS')
    app_test.navigation.click_btn('Complete')
    time.sleep(6)

    # app_test.vendor_profile.registration_flow.provide_demographics('35-44 years', 'Male', 'Save')

    app_test.verification.text_present_on_page('SCREENED')
    app_test.navigation.click_link("Logout")

@pytest.mark.dependency(depends=["test_yukon_project_qualify_vendor"])
def test_yukon_vendor_sign_up_docs(app_test):
    app_test.navigation.open_page(URL[pytest.env])
    time.sleep(7)

    try:
        app_test.navigation.click_btn("Cookies")
    except:
        print("no Accept Cookies button")

    app_test.navigation.switch_to_frame("page-wrapper")

    app_test.ac_user.shasta_click_btn("Start now! Apply to Yukon.")
    app_test.ac_user.shasta_click_btn("Sign In")

    app_test.ac_user.login_as(user_name=yukon_vendor['vendor'], password=yukon_vendor['password'])

    electronic_signature = True
    while electronic_signature:
        try:
            app_test.vendor_profile.registration_flow.sign_the_form(user_name=yukon_vendor['vendor'],
                                                                    user_password=yukon_vendor['password'],
                                                                    action="I Agree")
        except:
            electronic_signature = False

    app_test.verification.current_url_contains('raterlabs')
    app_test.verification.text_present_on_page('Free Gmail Address Required')

    app_test.navigation.click_link("Logout")


@pytest.mark.dependency(depends=["test_yukon_vendor_sign_up_docs"])
def test_yukon_vendor_is_registered(app_test):
    PASSWORD = get_test_data('test_ui_account', 'password')
    INTERNAL_USER_NAME = get_test_data('test_ui_account', 'email')

    app_test.ac_user.login_as_raterlabs_user(user_name=INTERNAL_USER_NAME, password=PASSWORD)

    app_test.navigation.click_link("Employees")
    app_test.vendor_pages.open_vendor_profile_by(yukon_vendor['vendor'], search_type='name', status='Any Status')
    time.sleep(2)

    actual_projects = app_test.vendor_pages.get_project_mapping_for_current_vendor()

    assert actual_projects.get('Aztec Aztec Google Yukon (Yukon) (Yukon)', False)
    assert actual_projects['Aztec Aztec Google Yukon (Yukon) (Yukon)']['status'] == 'REGISTERED'
