import time

import allure

from adap.ui_automation.utils.selenium_utils import find_elements, find_element


class ProjectOldUI:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def get_current_project_info(self):
        with allure.step('Get details for current project'):
            info_inputs = find_elements(self.driver, "//td//input[@name]")
            result = {}
            for el in info_inputs:
                result[el.get_attribute('name')] = el.get_attribute('value')
            return result

    def add_pay_rate(self, data):
        with allure.step('Add Pay Rate: %s' % data):
            self.app.navigation.click_link("Add Rate")
            time.sleep(2)
            for name, value in data.items():
                if name in ["disabled", "requireCertified"]: #  checkbox
                    find_element(self.driver, "//input[contains(@name,'%s']" % name).click()
                elif name in ["workdayId", "payRate"]:#  input
                    el = find_element(self.driver, "//input[contains(@name,'%s')]" % name)
                    el.clear()
                    el.send_keys(value)
                else:
                    time.sleep(1)
                    find_element(self.driver,
                                 "//select[contains(@name,'%s')]//option[text()='%s']" % (name, value)).click()
                time.sleep(1)
            find_element(self.driver, "//td[.//span[@class='add-another-rate'] and @class='currency "
                                      "new-rate-actions']//input[@name='ajaxSetRate']").click()
            time.sleep(3)
