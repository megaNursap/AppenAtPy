import time
import allure
from selenium.webdriver import Keys

from adap.ui_automation.utils.selenium_utils import (
    find_element, find_elements, iframe_context
)


class TeamFunds:
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def delete_saved_card(self):
        with allure.step('Remove Saved Card'):
            el = find_elements(self.driver, "//*[local-name() = 'svg' and @title='Remove Saved Card']")
            if len(el) > 0:
                el[0].click()
                time.sleep(3)
            else:
                print("No Saved Card present")

    def get_iframes_pay_with_card(self) -> dict:
        """ Get list of iframes under Pay with card block """
        iframes = find_elements(self.driver, "//div[@data-braintree-id='card']//iframe")
        assert len(iframes) == 5, f"Expected 5 iframes in Pay with card block, got {len(iframes)}"
        iframes_dict = {}
        for iframe in iframes:
            iframe_name = iframe.get_attribute('name').split('-')[-1]
            iframes_dict[iframe_name] = iframe
        expected_iframes = ['cardholderName', 'number', 'expirationDate', 'cvv', 'postalCode']
        assert all([i in iframes_dict.keys() for i in expected_iframes]), ''\
            f"Expected {expected_iframes}, got {list(iframes_dict.keys())}"
        return iframes_dict


    def make_purchase_by_entering_card_info(self, amount, card_number, name, expiration_date, cvv, zipcode, automatic_payment=False, remember_card=False):
        with allure.step('enter card information'):
            amount_field = find_element(self.driver, "//input[@name='amount']")
            amount_field.send_keys(amount, Keys.RETURN)
            iframes = self.get_iframes_pay_with_card()
            with iframe_context(self.app, iframes['number']):
                number_field = find_element(self.driver, "//input[@name='credit-card-number']")
                number_field.send_keys(card_number)
            with iframe_context(self.app, iframes['cardholderName']):
                name_field = find_element(self.driver, "//input[@name='cardholder-name']")
                name_field.send_keys(name)
            with iframe_context(self.app, iframes['expirationDate']):
                expiry_field = find_element(self.driver, "//input[@name='expiration']")
                expiry_field.send_keys(expiration_date)
            with iframe_context(self.app, iframes['cvv']):
                cvv_field = find_element(self.driver, "//input[@name='cvv']")
                cvv_field.send_keys(cvv)
            with iframe_context(self.app, iframes['postalCode']):
                zipcode_field = find_element(self.driver, "//input[@name='postal-code']")
                zipcode_field.send_keys(zipcode)
            if remember_card:
                self.app.navigation.click_checkbox_by_text('Remember card')
            if automatic_payment:
                self.app.navigation.click_checkbox_by_text('Automatic Payments')
            self.app.navigation.click_link('Make Purchase')
            time.sleep(2)

    def button_is_disable(self, btn_name):
        with allure.step('Check if button %s is disabled' % btn_name):
            btn = find_elements(self.driver,
                                "//*[(contains(@class,'btn') or contains(@class,'Button')) and contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'%s')]" % btn_name.lower())
            if len(btn) == 0:
                btn = find_elements(self.driver,
                                    "//button[text()='%s']" % btn_name)
            el_class = btn[0].get_attribute('class')
            return (True, False)[el_class.find('disabled') == -1]

    def get_purchase_history(self):
        with allure.step('Get purchase history'):
            purchase_histories = []
            history_rows = find_elements(self.driver, "//table[.//thead//*[text()='Transaction ID']]//tbody//tr")
            for row in history_rows:
                purchase_history = {}
                cells = row.find_elements('xpath',".//td")
                purchase_history['purchase_date'] = cells[0].text
                purchase_history['transaction_id'] = cells[1].text
                purchase_history['buyer_name'] = cells[2].text
                purchase_history['last_4'] = cells[3].text
                purchase_history['total'] = cells[4].text
                purchase_histories.append(purchase_history)
            return purchase_histories

    def is_cc_active(self, last4digits) -> bool:
        """ Check if credit card ending in 'last4digits' is active """
        time.sleep(3)
        xpath = f"//div[@data-braintree-id='methods-container'][//*[contains(text(), 'Ending in {last4digits}')]]"
        ele = find_elements(self.driver, xpath)
        assert ele, "Saved Credit Card block not found"
        cc_box = ele[0]
        return cc_box.get_attribute('class').endswith('active')

    def get_automatic_payments_ele(self):
        ele = find_elements(self.driver, "//*[contains(text(),\'Automatic Payments\')]/..")
        assert len(ele) == 1, "Automatic Payments block not found"
        return ele[0]

    def get_automatic_payments_status(self):
        label = self.get_automatic_payments_ele().text
        status = label.split()[-1]
        return status

    def get_edit_automatic_payments_ele(self):
        ele = self.get_automatic_payments_ele().find_elements('xpath',"./following-sibling::*")
        assert len(ele) == 1, "Automatic Payments Edit icon not found"
        return ele[0]
