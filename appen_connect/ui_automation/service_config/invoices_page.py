import time

import allure
from selenium.webdriver import Keys

from adap.ui_automation.utils.selenium_utils import click_element_by_xpath, send_keys_by_xpath, get_text_by_xpath, \
    find_elements, find_element


class InvoicesPage:
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.navigation = self.app.navigation

    _SUBMIT_BUTTON_LOCATOR = "//input[@id='submit-filters']"
    _INVOICE_ROW_LOCATOR = "//td[contains(text(),'%s')]/.."

    @allure.step('Click go button')
    def click_on_go_button(self):
        click_element_by_xpath(self.driver, self._SUBMIT_BUTTON_LOCATOR)
        time.sleep(5)

        return self

    @allure.step('Get current status')
    def get_current_status_by_text_in_row(self, text):
        invoice_row_we = find_element(self.app.driver, self._INVOICE_ROW_LOCATOR % text)
        tds_we = find_elements(invoice_row_we, './/td')

        return tds_we[-2].text

    @allure.step('Get amount')
    def get_amount(self, text):
        invoice_row_we = find_element(self.app.driver, self._INVOICE_ROW_LOCATOR % text)
        tds_we = find_elements(invoice_row_we, './/td')

        return tds_we[-1].text
