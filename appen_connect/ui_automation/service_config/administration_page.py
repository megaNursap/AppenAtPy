import allure
from selenium.webdriver import Keys

from adap.ui_automation.utils.selenium_utils import click_element_by_xpath, send_keys_by_xpath


class AdministrationPage:
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.navigation = self.app.navigation

    _BATCH_USER_TERMINATION_LOCATOR = "//a[contains(text(), 'Batch User Termination')]"
    _USER_IDS_LOCATOR = "//textarea[@name='userIds']"
    _TERMINATION_NOTE_LOCATOR = "//textarea[@name='terminationNote']"
    _TERMINATION_DATE_LOCATOR = "//input[@name='terminationDate']"
    _TERMINATE_BUTTON_LOCATOR = "//input[@id='terminate-button']"
    _REASON_LOCATOR = "//select[@name='terminationReason']"

    @allure.step('Open batch user termination link')
    def open_batch_user_termination(self):
        click_element_by_xpath(self.driver, self._BATCH_USER_TERMINATION_LOCATOR)

        return self

    @allure.step('Type user ids intended to be terminated')
    def set_user_ids(self, ids):
        send_keys_by_xpath(self.driver, self._USER_IDS_LOCATOR, ','.join(ids))

        return self

    @allure.step('Termination note')
    def set_termination_note(self, note):
        send_keys_by_xpath(self.driver, self._TERMINATION_NOTE_LOCATOR, note)

        return self

    @allure.step('Set termination date')
    def set_termination_date(self, date):
        send_keys_by_xpath(self.driver, self._TERMINATION_DATE_LOCATOR, (date, Keys.ENTER))

        return self

    @allure.step('Click on terminate button')
    def terminate(self):
        click_element_by_xpath(self.driver, self._TERMINATE_BUTTON_LOCATOR)

        return self

    @allure.step('Select termination "{reason}" reason')
    def select_reason(self, reason):
        click_element_by_xpath(self.driver, self._REASON_LOCATOR)
        click_element_by_xpath(self.driver, f'//*[contains(text(), "{reason}")]')

        return self
