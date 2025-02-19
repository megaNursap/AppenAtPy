import logging
import time

import allure

from adap.api_automation.utils.data_util import get_test_data
from adap.ui_automation.utils.selenium_utils import go_to_page, click_element_by_xpath, \
    send_keys_by_xpath
from gap.ui_automation.service_config.navigation import Urls

log = logging.getLogger(__name__)


class GUser:
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.current_user = None
        self.current_user_pwd = None
        self.current_user_role = None
        self.current_user_nick_name = None


    def gap_set_current_user(self, user):
        with allure.step("Set current user"):
            user_name = get_test_data(user, 'email')
            log.debug(f"Username: {user_name}")
            assert user_name is not None, "Username not specified"
            user_password = get_test_data(user, 'password')
            assert user_password is not None, "User password not specified"
            user_role = get_test_data(user, 'user_role')
            assert user_role is not None, "User role is not specified"
            user_nick_name = get_test_data(user, 'user_nick_name')
            log.info(f"Nick name: {user_nick_name}")
            assert user_nick_name is not None, "User nick_name is not specified"
            self.current_user_role = user_role
            self.current_user = user_name
            self.current_user_pwd = user_password
            self.current_user_nick_name = user_nick_name


    def gap_login_as(self, user):
        with allure.step('Login user'):
            self.gap_set_current_user(user)
            if not self.app.g_verify.gap_verify_logged_as(self.current_user_nick_name, do_assert=False):
                self.gap_logout()
                self.app.g_nav.open_page_login()
                self.gap_populate_login_form()
                time.sleep(2)
                self.app.g_verify.current_url_contains(Urls.URL_PG_WELCOME)
                self.app.g_verify.gap_verify_logged_as(self.current_user_nick_name)


    def gap_populate_login_form(self):
        with allure.step("Populate login form"):
            send_keys_by_xpath(self.driver, "//input[@id='name']", self.current_user)
            send_keys_by_xpath(self.driver, '//input[@type="password"]', self.current_user_pwd)
            btn = self.driver.find_elements('xpath',"//button[contains(@class,'ant-btn-primary')]")
            assert len(btn) > 0, 'Button Login not present'
            btn[0].click()


    def gap_logout(self):
        with allure.step(f'Logout'):
            if self.app.g_verify.gap_verify_current_url_contain(
                    Urls.URL) and not self.app.g_verify.gap_verify_current_url_contain('user'):
                click_element_by_xpath(self.driver,
                                       "//*[contains(@class,'antd-pro-components-global-header-index-account')]")
                click_element_by_xpath(self.driver, "//*[contains(@data-menu-id,'logout')]")
                time.sleep(1)
                self.app.g_verify.current_url_contains(Urls.URL_USER_LOGIN)
                time.sleep(1)


    def gap_register_user(self, email, name, password):
        with allure.step(f"Register new user {email}"):
            if not self.app.g_verify.gap_verify_current_url_contain(Urls.URL_USER_REGISTER):
                if not self.app.g_verify.gap_verify_current_url_contain("user"):
                    self.gap_logout()
                    click_element_by_xpath(self.driver, "//span[contains(text(),'No account? Create one')]")
                    time.sleep(1)
                else:
                    go_to_page(self.driver, Urls.URL + Urls.URL_USER_REGISTER)

            send_keys_by_xpath(self.driver, "//input[@id='email']", email)
            send_keys_by_xpath(self.driver, "//input[@id='uniqueName']", name)
            send_keys_by_xpath(self.driver, "//input[@id='password']", password)
            send_keys_by_xpath(self.driver, "//input[@id='confirmPassword']", password)
            click_element_by_xpath(self.driver, "//span[@class='ant-checkbox']")
            self.app.g_nav.gap_click_btn("Register")


    def gap_reset_password(self, email):
        pass
