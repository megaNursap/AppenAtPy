import time

import allure
from adap.ui_automation.utils.selenium_utils import find_elements


class MfaProfile:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def select_multi_factor_authentication(self, title_name):
        with allure.step('Select title name %s' % title_name):
            title_elements = find_elements(self.driver, f"//span[(contains(@class,'title') and text()='{title_name}')]")
            assert title_elements, "Title elements have not been found"
            title_elements[0].click()
            time.sleep(1)
