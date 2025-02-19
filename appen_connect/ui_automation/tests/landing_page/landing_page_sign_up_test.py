import time
import datetime as ds
from adap.api_automation.utils.data_util import get_test_data
from adap.ui_automation.utils.js_utils import scroll_to_page_bottom
import pytest
from faker import Faker

from appen_connect.ui_automation.service_config.vendor_profile.registration_flow import new_vendor
from appen_connect.ui_automation.tests.landing_page.landing_page_test import landing_pages

mark_env = pytest.mark.skipif(not pytest.env in ['stage'], reason="Stage only")
pytestmark = [pytest.mark.regression_ac_landing_page,
              pytest.mark.regression_ac,
              pytest.mark.ac_ui_vendor_registration,
              mark_env]


@pytest.mark.parametrize('name, landing_url, project_name, language, region, vendor, apply_project', landing_pages)
def test_sign_up_project_new_account_landing_page(app_test,
                                                  name,
                                                  landing_url,
                                                  project_name,
                                                  language,
                                                  region,
                                                  vendor,
                                                  apply_project):

    fake = Faker()

    app_test.navigation.open_page(landing_url)
    time.sleep(2)

    app_test.navigation.accept_cookies()

    app_test.navigation.switch_to_frame("page-wrapper")

    app_test.verification.text_present_on_page(project_name)

    app_test.ac_user.shasta_click_btn("Start now! Apply to {name}.".format(name=name))
    app_test.ac_user.shasta_click_btn("Create an Account")

    verification_code = {
        "stage": "4CD90D"
    }

    _vendor = new_vendor(app_test,
                         pr='vendor_landing_page',
                         verification_code=verification_code[pytest.env],
                         vendor_first_name=fake.first_name(),
                         user_last_name=fake.last_name(),
                         language=language,
                         region=region,
                         open_sign_up_page=False,
                         state='Texas')

    print("-=-=", _vendor)

    app_test.navigation.switch_to_frame("page-wrapper")
    app_test.verification.text_present_on_page('You are a project match!')

    app_test.navigation.click_btn('Fill & Submit Profile')

    if apply_project:
        app_test.navigation.switch_to_frame("page-wrapper")
        app_test.vendor_profile.open_tab('Location')
        #residency_history_date = (ds.date.today() - ds.timedelta(days=1800)).strftime("%Y/%m/%d")
        residency_history_years = "2 years"
        app_test.vendor_profile.location.fill_out_fields({"Street Address": "187098 Main Road 2",
                                                          "CITY": "Fenix",
                                                          "ZIP CODE": "213432"
                                                          })
        app_test.vendor_profile.location.residence_history_of_worker(residency_history_years)

        app_test.navigation.click_btn("Next: Education")

        app_test.vendor_profile.open_tab('Education')
        app_test.vendor_profile.education.fill_out_fields(
            {
                "HIGHEST LEVEL OF EDUCATION": "Doctorate degree or equivalent",
                "LINGUISTICS QUALIFICATION": "Doctoral degree – Completed"
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

        app_test.verification.current_url_contains("/complete_profile/view")
        additional_info_elements = app_test.vendor_profile.registration_flow.select_value_for_choice_and_proceed('radio',
                                                                                                                 'true')
        for i in range(0, 3):
            additional_info_elements[i].click()

        app_test.vendor_profile.registration_flow.select_familiarity_level('Expert')
        app_test.vendor_profile.registration_flow.select_value_for_choice_and_proceed('submit', 'Submit')[0].click()
        app_test.verification.current_url_contains("/process_resolution")
        app_test.navigation.click_link("Logout")

        PASSWORD = get_test_data('test_ui_account', 'password')
        INTERNAL_USER_NAME = get_test_data('test_ui_account', 'email')

        app_test.ac_user.login_as(user_name=INTERNAL_USER_NAME, password=PASSWORD)

        app_test.navigation.click_link("Vendors")
        app_test.vendor_pages.open_vendor_profile_by(_vendor['vendor'], search_type='name', status='Any Status')

        app_test.vendor_pages.vendor_qualification_action("Completed")

        app_test.vendor_pages.open_vendor_profile_by(_vendor['vendor'], search_type='name', status='Any Status')

        app_test.navigation.click_link('Impersonate')
        app_test.navigation.click_link('Stop Impersonating')

        app_test.navigation.click_link("Logout")

        app_test.ac_user.login_as(user_name=_vendor['vendor'], password=_vendor['password'])

        electronic_signature = True
        while electronic_signature:
            try:
                app_test.vendor_profile.registration_flow.sign_the_form(user_name=_vendor['vendor'],
                                                                        user_password=_vendor['password'],
                                                                        action="I Agree")
            except:
                electronic_signature = False

        try:
            app_test.vendor_profile.registration_flow.select_option_and_proceed('attributes[0].stringValue', 'Windows')
            app_test.vendor_profile.registration_flow.select_value_for_choice_and_proceed('submit', 'Save')[0].click()
        except:
            pass

        app_test.verification.text_present_on_page(f'REGARDING PROJECT: {name}')
        app_test.navigation.click_btn('Close')

        app_test.navigation.click_link('Projects')
        app_test.navigation.switch_to_frame("page-wrapper")
        app_test.navigation.click_btn('Skip')

        assert app_test.vendor_pages.project_found_on_page(name)

        app_test.driver.switch_to.default_content()

        app_test.navigation.click_link('Stop Impersonating')
        app_test.verification.text_present_on_page(name)

