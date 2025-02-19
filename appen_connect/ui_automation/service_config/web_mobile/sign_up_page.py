import allure
import time

from adap.ui_automation.utils.selenium_utils import send_keys_by_xpath, click_element_by_xpath, \
    clear_text_field_by_xpath, find_elements


class SignUpPage:
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver


    EMAIL = "//input[@id='email']"
    PASSWORD = "//input[@id='password']"
    FIRST_NAME = "//input[@id='firstName']"
    LAST_NAME = "//input[@id='lastName']"
    AGREE_CHECKBOX = "//label[@data-baseweb='checkbox']/span"
    INFO = "//*[text()='Info']/.."
    VERIFICATION_CODE = "//input[@id='verificationCode']"
    MODAL_INFO_TEXT = "//div[contains(@class,'%s')]"

    @allure.step("Enter email")
    def set_email(self, email=None):
        send_keys_by_xpath(self.driver, self.EMAIL, email)

    @allure.step("Enter password")
    def set_password(self, password=None):
        clear_text_field_by_xpath(self.driver, self.PASSWORD)
        send_keys_by_xpath(self.driver, self.PASSWORD, password)

    @allure.step("Enter first name")
    def set_first_name(self, first_name=None):
        send_keys_by_xpath(self.driver, self.FIRST_NAME, first_name)

    @allure.step("Enter last name")
    def set_last_name(self, last_name=None):
        send_keys_by_xpath(self.driver, self.LAST_NAME, last_name)


    @allure.step("Click by agree terms checkbox")
    def click_by_agree_term(self):
        click_element_by_xpath(self.driver, self.AGREE_CHECKBOX)


    @allure.step("Click on read info for password/first name")
    def click_on_read_info(self, index=0):
        click_element_by_xpath(self.driver, self.INFO, index=index)

    @allure.step("Read info from modal box")
    def read_modal_info(self, part_of_text):
        header_modal_el = find_elements(self.driver, self.MODAL_INFO_TEXT % part_of_text)
        return header_modal_el[0].text

    @allure.step("Read info from modal form")
    def read_info(self):
        time.sleep(1)
        return " ".join([self.read_modal_info(part_of_text='styles__ModalHeader'),
                         self.read_modal_info(part_of_text='styles__ModalBody')]).replace('\n', ' ')

    @allure.step("Send verification code")
    def send_verification_code(self, code=None):
        send_keys_by_xpath(self.driver, self.VERIFICATION_CODE, code)


class SignUpWebMobile:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.sign_up_page = SignUpPage(self)

    def create_uses(self, user):
        self.sign_up_page.set_email(user['email'])
        self.sign_up_page.set_password(user['password'])
        self.sign_up_page.set_first_name(user['firstname'])
        self.sign_up_page.set_last_name(user['lastname'])
        self.sign_up_page.click_by_agree_term()

    def read_info_link_page(self, message_on_page):
        self.driver.switch_to.frame(0)
        self.app.verification.text_present_on_page(message_on_page)



