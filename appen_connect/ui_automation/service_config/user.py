import time
import allure

from adap.ui_automation.utils.selenium_utils import go_to_page, find_element, find_elements, click_element_by_xpath, \
    create_screenshot

URL = {
    'stage': 'https://connect-stage.integration.cf3.us/qrp/core/login',
    'qa': 'https://connect-qa.sandbox.cf3.us/qrp/core/login',
    'prod': 'https://connect.appen.com/qrp/core/login',
    'integration': 'https://connect.integration.cf3.us/qrp/core/login'
}
RL_URL = {'stage': "https://raterlabs-stage.integration.cf3.us/qrp/core",
          'qa': 'https://raterlabs-qa.sandbox.cf3.us/qrp/core',
          'prod': 'https://raterlabs.appen.com/qrp/core',
          'integration':''
          }

FACILITY_URL = {'stage': "https://facility-stage.integration.cf3.us/qrp/core/login",
                'qa': 'https://facility-qa.sandbox.cf3.us/qrp/core/login',
                'prod': 'https://facility.appen.com/qrp/core/login',
                'integration': ''
                }
RQ_URL = "https://rq-{env}.appen.io/qrp/core/login"
AGENCY_URL = "https://agency-{env}.appen.com/qrp/core/login"
CE_URL = "https://contributor-experience.integration.cf3.us"


class User:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.url = URL[self.app.env]

    def login_as(self, user_name=None, password=None, open_login_page=True):
        with allure.step("Login at %s as %s " % (user_name, self.url)):
            if open_login_page:
                create_screenshot(self.driver, 'before_login_open_page')
                go_to_page(self.driver, self.url)
                create_screenshot(self.driver, 'after_open_page')

            email = find_element(self.driver, '//input[@name="username"]')
            email.send_keys(user_name)
            time.sleep(1)
            try:
                password_field = find_element(self.driver, '//input[@name="password"]')
                password_field.send_keys(password)
                find_element(self.driver, '//*[@type="submit"]').click()
                time.sleep(2)
            except:
                find_element(self.driver, "//a[@id='zocial-Idaptive']").click()
                time.sleep(5)

            create_screenshot(self.driver, 'after_login')

    def login_as_raterlabs_user(self, user_name=None, password=None):
        with allure.step("Login at %s as %s " % (user_name, self.url)):
            self.url = RL_URL[self.app.env] + "/login"
            self.login_as(user_name, password)

    def login_as_facility_user(self, user_name=None, password=None):
        with allure.step("Login at %s as %s " % (user_name, self.url)):
            self.url = FACILITY_URL[self.app.env]
            self.login_as(user_name, password)

    def login_as_agency_user(self, user_name=None, password=None):
        with allure.step("Login at %s as %s " % (user_name, self.url)):
            self.url = AGENCY_URL.format(env=self.app.env)
            self.login_as(user_name, password)

    def login_as_rq_user(self, user_name=None, password=None):
        with allure.step("Login at %s as %s " % (user_name, self.url)):
            self.url = RQ_URL.format(env=self.app.env)
            go_to_page(self.driver, self.url)
            email = find_element(self.driver, '//input[@name="username"]')
            email.send_keys(user_name)
            password_field = find_element(self.driver, '//input[@name="password"]')
            password_field.send_keys(password)
            find_element(self.driver, '//*[@type="submit"]').click()
            time.sleep(5)

    def sign_out(self):
        self.app.navigation.click_link('Logout')

    def select_customer(self, customer):
        sel = find_elements(self.driver, "//select[@id='customer-selector']//option[text()='%s']" % customer)
        if len(sel) == 0:
            sel = find_elements(self.driver, "//select[@id='customer-selector']//option[contains(text(),'%s')]" % customer)
        sel[0].click()

    def register_new_vendor(self, vendor_name, vendor_password, verification_code, vendor_first_name="firstname",
                            user_last_name="lastname", residence_value='United States of America', state='Alabama',
                            open_sign_up_page=True):

        create_screenshot(self.driver, "before5")

        self.app.vendor_profile.registration_flow.register_user(user_name=vendor_name, user_password=vendor_password,
                                                                user_first_name=vendor_first_name if vendor_first_name else "firstname",
                                                                user_last_name=user_last_name if user_last_name else "lastname",
                                                                residence_value=residence_value,
                                                                state=state,
                                                                open_sign_up_page=open_sign_up_page)

        self.app.vendor_profile.registration_flow.fill_out_fields({"CERTIFY DATA PRIVACY": 1,
                                                                   "CERTIFY SSN": 1}, action="Create Account")
        time.sleep(10)
        self.app.vendor_profile.registration_flow.fill_out_fields({"VERIFICATION CODE": verification_code},
                                                                  action="Verify Email")

    def shasta_click_btn(self, btn_name):
        with allure.step("Click btn - Create an account"):
            el = find_elements(self.driver, "//*[contains(text(),'%s')]" % btn_name)
            assert len(el) > 0, "Button: %s has not been found " % btn_name
            el[0].click()

    def is_login_page_opened(self):
        els = find_elements(self.driver, "//span[contains(text(),'Login with Appen SSO')]")
        return True if els else False

    def sign_up_contributor_experience(self, endpoint="/sign-up"):
        with allure.step("Sigh up at %s " % self.url):
            self.url = CE_URL + endpoint
            go_to_page(self.driver, self.url, mobile_device=False)