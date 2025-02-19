import datetime
import logging
import random
import time

import allure
from selenium.webdriver.common.keys import Keys

from adap.api_automation.utils.data_util import get_test_data
from adap.ui_automation.utils.js_utils import mouse_over_element, open_new_tab, open_url_in_new_tab, scroll_to_element
from adap.ui_automation.utils.selenium_utils import find_elements, go_to_page, find_element, create_screenshot, \
    send_keys_by_xpath, click_element_by_xpath

LOGGER = logging.getLogger(__name__)

URL = {
    'stage': 'https://connect-stage.integration.cf3.us/qrp/core/login',
    'qa': 'https://connect-qa.sandbox.cf3.us/qrp/core/login',
    'prod': 'https://connect.appen.com/qrp/core/login',
    'integration': 'https://connect.integration.cf3.us/qrp/core/login'
}


def new_vendor(app, pr="pb", verification_code="4266E5", language=None, region='United States of America', open_sign_up_page=True, state='Alabama', **kwargs):
    _today = datetime.datetime.today()
    prefix = pr + _today.strftime("%Y%m%d") + "_" + str(random.randint(1000, 9999))
    vendor_name = "sandbox+" + prefix + "@figure-eight.com"
    password = get_test_data('test_ui_account', 'password')

    app.ac_user.register_new_vendor(vendor_name=vendor_name,
                                    vendor_password=password,
                                    vendor_first_name=kwargs.get('vendor_first_name', None),
                                    user_last_name=kwargs.get('user_last_name', None),
                                    verification_code=verification_code,
                                    open_sign_up_page=open_sign_up_page,
                                    residence_value=region,
                                    state=state)

    app.navigation.click_btn('Go to Login page')

    if language and region:
        app.ac_user.login_as(user_name=vendor_name, password=password)

        app.navigation.switch_to_frame("page-wrapper")
        app.vendor_profile.registration_flow.fill_out_fields({"YOUR PRIMARY LANGUAGE": language,
                                                                      "YOUR LANGUAGE REGION": region})

        time.sleep(1)
        app.navigation.click_btn("Continue")

    time.sleep(2)
    return {"vendor": vendor_name,
            "password": password}


class Registration:
    YOUR_PRIMARY_LANGUAGE_LOCATOR= ""
    YOUR_LANGUAGE_REGION_LOCATOR = ""
    # CERTIFY_DATA_PRIVACY = "//label[@data-testid='adult-check']"
    # CERTIFY_SSN = "//label[@data-testid='country-doc-check']"
    CERTIFY_DATA_PRIVACY_LOCATOR = "//input[@name='adultCertify']/..//span"
    CERTIFY_SSN_LOCATOR = "//input[@name='taxDocumentation']/..//span"
    VERIFICATION_CODE_LOCATOR = "//input[@name='verificationCode']"
    DATE_OF_BIRTH_LOCATOR = "//input[@id='birthDate']"
    EMAIL_LOCATOR = "//input[@name='email']"
    PASSWORD_LOCATOR = "//input[@name='password']"
    FIRST_NAME_LOCATOR = "//input[@name='firstName']"
    LAST_NAME_LOCATOR = "//input[@name='lastName']"
    COUNTRY_OF_RESIDENCE_LOCATOR = "//label[text()='COUNTRY OF RESIDENCE']/..//div[contains(@class,'container') and @id='country']"

    elements = {
        "CERTIFY DATA PRIVACY":
            {"xpath": CERTIFY_DATA_PRIVACY_LOCATOR,
             "type": "checkbox"
             },
        "CERTIFY SSN":
            {"xpath": CERTIFY_SSN_LOCATOR,
             "type": "checkbox"
             },
        "YOUR PRIMARY LANGUAGE":
            {"xpath": YOUR_PRIMARY_LANGUAGE_LOCATOR,
             "type": "dropdown"
             },
        "YOUR LANGUAGE REGION":
            {"xpath": YOUR_LANGUAGE_REGION_LOCATOR,
             "type": "dropdown"
             },
        "VERIFICATION CODE":
            {"xpath": VERIFICATION_CODE_LOCATOR,
             "type": "input"
             },
        "DATE OF BIRTH":
            {"xpath": DATE_OF_BIRTH_LOCATOR,
             "type": "calendar"
             },
        "EMAIL":
            {"xpath": EMAIL_LOCATOR,
             "type": "input"
             },
        "PASSWORD":
            {"xpath": PASSWORD_LOCATOR,
             "type": "input"
             },
        "FIRST NAME":
            {"xpath": FIRST_NAME_LOCATOR,
             "type": "input"
             },
        "LAST NAME":
            {"xpath": LAST_NAME_LOCATOR,
             "type": "input"
             },
        "COUNTRY OF RESIDENCE":
            {"xpath":COUNTRY_OF_RESIDENCE_LOCATOR,
             "type": "dropdown"
            }
    }

    def __init__(self, project):
        self.project = project
        self.app = project.app
        self.driver = self.app.driver
        self.url = URL[self.app.env]

    def register_user(self, user_name, user_password, user_first_name, user_last_name, residence_value, state=None, open_sign_up_page=True):
        with allure.step("Register flow"):
            create_screenshot(self.driver, "before0")

            if open_sign_up_page:
                go_to_page(self.driver, self.url)
                self.app.navigation.click_link('Register')
                time.sleep(2)

            time.sleep(4)
            create_screenshot(self.driver, "before")
            btn = find_elements(self.app.driver,
                                "//button[contains(text(),'Cookies')]")
            if len(btn) > 0:
                btn[0].click()

            self.app.navigation.switch_to_frame("page-wrapper")
            self.fill_out_fields({"EMAIL": user_name,
                                  "PASSWORD": user_password,
                                  "FIRST NAME": user_first_name,
                                  "LAST NAME": user_last_name})
            time.sleep(5)
            country_of_residence = find_elements(self.app.driver,
                                                 "//label[text()='COUNTRY OF RESIDENCE']/..//div[contains(@class,'container') and @id='country']")
            assert len(country_of_residence), "Field country of residence has not been found"
            country_of_residence[0].click()
            time.sleep(3)
            option = find_elements(self.driver,
                                   "//div[contains(@id,'react-select')][.//div[text()='%s']]" % residence_value)
            assert len(option), "Value %s has not been found" % residence_value
            option[0].click()
            if state:
                try:
                    state_field = find_elements(self.driver,
                                                         "//label[text()='STATE']/..//div[contains(@class,'container') and @id='state']")
                    assert len(state_field), "Field state has not been found"
                    state_field[0].click()
                    time.sleep(3)
                    option = find_elements(self.driver,
                                           "//div[contains(@id,'react-select')][.//div[text()='%s']]" % state)
                    assert len(option), "Value %s has not been found" % state
                    option[0].click()
                except:
                     print("State is not required!")

    def fill_out_demographic_survey(self, select_value, container_index=0):
        with allure.step("Fill out demographic survey"):
            el = find_elements(self.app.driver,
                               "//label[text()='gender you identify with']/../../..//div[contains(@class,'container')]")
            el[container_index].click()
            time.sleep(2)
            option = find_elements(self.app.driver,
                                   "//div[contains(@id,'react-select')][.//div[text()='%s']]" % select_value)
            option[0].click()
            time.sleep(1)

    def get_start_from_welcome_page(self, text_value):
        with allure.step("Enter verification code for register flow"):
            el = find_elements(self.driver, " //div[contains(text(),'%s')]" % text_value)
            # mouse_over_element(self.driver, el[0])
            el[0].click()

    def fill_out_fields(self, data, action=None):
        with allure.step("Fill out fields"):
            self.app.ac_project.enter_data(data=data, elements=self.elements)
            if action:
                self.app.navigation.click_btn(action)

    def get_user_profile_percentage(self):
        with allure.step("Get user profile percentage"):
            el = find_element(self.driver, "//span[@class='percentage-span']")
            return el.text

    def select_value_for_choice_and_proceed(self, input_type, input_choice):
        with allure.step('Select value for multiple choice'):
            elements = find_elements(self.driver, "//input[@type='%s' and @value='%s']" % (input_type, input_choice))
            return elements

    def select_option_and_proceed(self, input_name, input_choice):
        with allure.step('Select option'):
            elements = find_elements(self.driver, "//select[@name='%s']//option[contains(@value,'%s')]" % (input_name, input_choice))
            assert len(elements), "Element has not been found"
            elements[0].click()

    def select_familiarity_level(self, level):
        with allure.step('Select familiarity level'):
            find_element(self.driver, "//*[@name='profile.computerLiteracy']").click()
            find_element(self.driver, "//*[@value='%s' and text()='%s']" % (level, level)).click()
            time.sleep(1)

    def sign_the_form(self, user_name, user_password, action=None):
        with allure.step('Sign the document form'):
            '''
            email = find_element(self.driver, '//input[@name="email"]')
            email.clear()
            time.sleep(2)
            email.send_keys(user_name)
            password = find_element(self.driver, '//input[@name="password"]')
            password.clear()
            time.sleep(2)
            password.send_keys(user_password)
            '''
            if action:
                find_element(self.driver, '//*[@class="checkbox" and @value =  "true"]').click()
                time.sleep(2)
                btn = find_elements(self.driver, '//input[@value="Continue"]')
                if len(btn):
                    btn[0].click()

            self.app.navigation.refresh_page()


    def accept_the_form(self,action=None):
        if action:
            el = find_elements(self.driver, '//*[input[@type="checkbox"]]/input[@value="true"]')
            if len(el) <1:
                el = find_elements(self.driver, '//label[.//input[@name="signDocument"]]')
            assert len(el), 'Element has not vee found'

            scroll_to_element(self.driver, el[0])
            time.sleep(1)
            el[0].click()
            time.sleep(2)



    def apply_the_project_by_name(self, project_name):
        with allure.step('Apply the project'):
            search_field = find_element(self.driver, "//input[@placeholder='Search by project name']")
            search_field.clear()
            search_field.send_keys(project_name)
            time.sleep(1)
            self.app.navigation.click_btn("Apply")
            time.sleep(12)
            #self.app.navigation.click_btn("Continue To Registration")
            #time.sleep(3)

    def refresh_page_and_wait_until_project_load(self, interval, max_wait_time, text, switchframe=None):
        with allure.step('Wait until text present'):
            _c = 0
            while _c < max_wait_time:
                self.app.navigation.refresh_page()
                if switchframe:
                    self.app.navigation.switch_to_frame(switchframe)
                element = find_elements(self.app.driver, "//*[text()[contains(.,\"%s\")]]" % text)
                if len(element) == 0:
                    break
                else:
                    _c += interval
                    time.sleep(interval)
            else:
                msg = f'Max wait time reached, text still not present'
                raise Exception(msg)

    def remove_data_from_fields(self, data):
        self.project.remove_data(data, self.elements)


    def add_paypal(self, user_name):
        with allure.step('Add Paypal Account'):
            email = find_element(self.driver, '//input[@name="paymentAccount"]')
            email.clear()
            time.sleep(2)
            email.send_keys(user_name)
            email = find_element(self.driver, '//input[@name="confirmPaymentAccount"]')
            email.clear()
            time.sleep(2)
            email.send_keys(user_name)
            find_element(self.driver, '//input[@name="savePaymentAccount" and @value="Save"]').click()
            time.sleep(2)

    def smartphone_verification(self, enable=False):
        with allure.step('Smartphone verification step'):
            if enable:
                self.select_value_for_choice_and_proceed('radio', 'Yes')[0].click()
                link = find_elements(self.driver, "//a[contains(@href,'/smartphone/add/')]")
                assert len(link)>0, "Link has not been found"
                _url = link[0].text

                main_window = self.app.driver.window_handles[0]

                open_new_tab(self.app.driver)

                verification_window = self.app.driver.window_handles[1]

                self.app.navigation.switch_to_window(verification_window)
                self.app.navigation.open_page(_url)
                time.sleep(5)
                self.app.driver.close()

                self.app.navigation.switch_to_window(main_window)

                self.app.verification.wait_untill_text_present_on_the_page('Continue', 20)
                self.select_value_for_choice_and_proceed('submit', 'Continue')[0].click()

            else:
                self.select_value_for_choice_and_proceed('radio', 'No')[0].click()
                self.select_value_for_choice_and_proceed('submit', 'Continue')[0].click()


    def provide_yukon_info(self, google_id, level_ai, action=None):
        with allure.step('provide data for Yukon project'):
            send_keys_by_xpath(self.driver, "//td[text()='Google ID']/..//input", google_id)
            send_keys_by_xpath(self.driver, "//td[text()='Type Levle IA Data']/..//input", level_ai)
            if action:
               self.app.navigation_old_ui.click_input_btn(action)

    def provide_demographics(self, age, gender, action):
        with allure.step('provide demographics data'):
            click_element_by_xpath(self.driver, "//h3[text()='Estimated Demographics']/..//a[text()='Change']")
            click_element_by_xpath(self.driver, f"//select[@name='estimatedAge']//option[@value='{age}']" )
            click_element_by_xpath(self.driver, f"//input[@name='estimatedGender' and @value='{gender}']")
            click_element_by_xpath(self.driver, f"//a[@id='save-estimated-demographics' and text()='{action}']")
            time.sleep(3)






