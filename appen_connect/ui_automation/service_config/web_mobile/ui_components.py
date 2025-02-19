import time

from selenium.webdriver import ActionChains, Keys

from adap.ui_automation.utils.selenium_utils import find_elements


def select_dropdown_option(driver, xpath, option, index=0):
    elem = find_elements(driver, xpath)
    assert elem, 'Element has not been found'
    action = ActionChains(driver)
    action.click(elem[index]).send_keys(option).send_keys(Keys.ENTER).perform()
    time.sleep(1)
