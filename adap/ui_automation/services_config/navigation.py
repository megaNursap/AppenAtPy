import time

import allure
from allure_commons.types import AttachmentType
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from adap.ui_automation.utils.selenium_utils import find_elements, go_to_page, find_element
from adap.ui_automation.utils.page_element_utils import click_rebrand_popover


class Navigation:
    def __init__(self, app):
        self.app = app

    def open_page(self, url):
        with allure.step('Open page: %s' % url):
            go_to_page(self.app.driver, url)
            time.sleep(2)

    @allure.step('Refresh page')
    def refresh_page(self):
        with allure.step('Refresh page'):
            self.app.driver.refresh()
            time.sleep(5)

    @allure.step('Browser back')
    def browser_back(self):
        with allure.step('Browser back'):
            self.app.driver.back()
            time.sleep(2)

    def click_btn(self, btn_name, timeout=2):
        with allure.step('Click button: %s' % btn_name):
            btn = find_elements(self.app.driver,
                                '//*[(contains(@class,"btn") or contains(@class,"rebrand-Button")) and contains(translate(text(),"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"),"%s")]' % btn_name.lower())
            if len(btn) == 0:
                btn = find_elements(self.app.driver,
                                    '//button[text()="%s"]' % btn_name)

            if len(btn) == 0:
                btn = find_elements(self.app.driver,
                                    '//button[contains(.,"%s")]' % btn_name)

            if len(btn) == 0:
                btn = find_elements(self.app.driver,
                                    f"//div[contains(@class,'buttons')]//input[@value='{btn_name}']")

            if len(btn) == 0:
                btn = find_elements(self.app.driver,
                                    "//a[.//div[text()='%s']]" % btn_name)

            if len(btn) == 0:
                btn = find_elements(self.app.driver,
                                    "//a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'%s')]" % btn_name.lower())
            assert len(btn) > 0, "Button %s has not been found" % btn_name
            btn[0].click()
            time.sleep(timeout)
            self.app.navigation.accept_alert()

    def click_btn_by_text(self, text):
        with allure.step('Click button: %s' % text):
            btn = find_element(self.app.driver, "//*[text()='%s']" % text)
            btn.click()

    def click_link(self, link_name, index=0):
        with allure.step('Click link: %s' % link_name):
            link = find_elements(self.app.driver,
                                 "//a[(normalize-space(text())='%s') or ./span[contains(text(),'%s')] or .='%s']" % (
                                     link_name, link_name, link_name))

            if len(link) == 0:
                link = find_elements(self.app.driver,
                                     "//a[contains(text(),'%s')]" % (link_name))
            if len(link) == 0:
                link = find_elements(self.app.driver,
                                     "//div[(normalize-space(text())='%s')]" % (link_name))

            assert len(link) >= index + 1, "Link %s has not been found" % link_name
            link[index].click()
            time.sleep(2)

    def click_link_by_href(self, href, index=0):
        with allure.step('Click link by href: %s' % href):
            link = find_elements(self.app.driver, f"//a[@href='{href}']")
            assert len(link) >= index + 1, "Link %s has not been found" % href
            link[index].click()
            time.sleep(2)

    def hover_over_meta_tag(self):
        with allure.step('hover over a web element'):
            info_element = find_elements(self.app.driver, "(//h5[@data-baseweb='block']/following-sibling::span)[1]")
            hover = ActionChains(self.app.driver).move_to_element(info_element[0])
            hover.perform()

    def click_checkbox_by_text(self, name, index=0):
        with allure.step('Click checkbox by text: %s' % name):
            time.sleep(2)
            el = find_elements(self.app.driver, "//li[.//*[text()='%s']]" % name)

            if len(el) == 0:
                el = find_elements(self.app.driver,
                                   "//label[text()='%s']/preceding-sibling::label" % name)

            # delete when all checkboxed will be changed
            if len(el) == 0:
                el = find_elements(self.app.driver,
                                   "//label[text()='%s']/..//label[contains(@class,'rebrand-Checkbox__icon')]" % name)

            if len(el) > 0:
                el[index].click()
            else:
                assert False, "Checkbox with text - %s has not been found" % name

    def click_checkbox_by_id(self, name):
        with allure.step('Click checkbox by id: %s' % name):
            el = find_elements(self.app.driver, "//input[@id='%s']" % name)
            if len(el) > 0:
                el[0].click()
            else:
                assert False, "Checkbox with id - %s has not been found" % name

    def get_checkbox_status_by_text(self, name):
        with allure.step('Get checkbox status by text: %s' % name):
            el = find_elements(self.app.driver, "//li[.//*[text()='%s']]//input" % name)
            if len(el) == 0:  # sandbox
                el = find_elements(self.app.driver, "//label[text()='%s']/preceding-sibling::input" % name)
            if len(el) > 0:
                if el[0].get_attribute('checked'):
                    return True
            else:
                assert False, "Checkbox with text - %s has not been found" % name

            return False

    def switch_to_window(self, _window):
        self.app.driver.switch_to.window(_window)

    def close_modal_window(self):
        with allure.step('Close modal window'):
            el = find_elements(self.app.driver, "//div[@id='js-modal-overlay']//*[local-name() = 'svg']")
            assert len(el) > 0, "Modal window has not been found"
            el[0].click()
            time.sleep(1)

    def close_tour_guide_popup(self):
        with allure.step('Close Tour Guide popup window'):
            xpath = "//*[local-name() = 'svg' and contains(@class, 'TourStep__closeIcon')]"
            elements = find_elements(self.app.driver, xpath)
            for ele in elements:
                ele.click()
                time.sleep(1)

            click_rebrand_popover(self.app.driver)

    def get_title(self):
        with allure.step('Get page title'):
            return self.app.driver.title

    def switch_to_frame(self, _iframe):
        self.accept_alert()
        self.app.driver.switch_to.frame(_iframe)
        time.sleep(2)

    def deactivate_iframe(self):
        self.app.driver.switch_to.default_content()

    def fill_out_input_by_name(self, name, value):
        with allure.step('Type into field: %s, value: %s' % (name, value)):
            el = find_elements(self.app.driver, "//input[@name='%s']" % name)
            assert len(el) > 0, "Input field %s has not been found" % name
            el[0].clear()
            el[0].send_keys(value)

    def undo_shortcut(self):
        ac = ActionChains(self.app.driver)
        ac.key_down(Keys.COMMAND).send_keys('z').key_up(Keys.COMMAND).perform()
        time.sleep(3)

    def combine_hotkey(self, key, character):
        with allure.step('Hotkey character'):
            ac = ActionChains(self.app.driver)
            ac.key_down(key).send_keys(character).key_up(key).perform()
            time.sleep(3)

    def hotkey(self, key):
        with allure.step('Hotkey character'):
            ac = ActionChains(self.app.driver)
            ac.send_keys(key).perform()
            time.sleep(3)

    def accept_alert(self):
        try:
            alert = self.app.driver.switch_to.alert
            alert.accept()
        except:
            pass

    def cancel_alert(self):
        try:
            alert = self.app.driver.switch_to.alert
            alert.dismiss()
        except:
            pass

    def maximize_window(self):
        self.app.driver.maximize_window()

    def accept_cookies(self):
        try:
            self.app.navigation.click_btn("Accept Cookies")
        except:
            print("no Accept Cookies button")

    def click_bytext(self, text):
        el = find_elements(self.app.driver, "//*[contains(text(), '%s')]" % text)
        assert len(el) > 0, "The text %s not present on page" % text
        el[0].click()
        time.sleep(3)

    def click_on_element_by_attribute_value(self, attribute, value):
        with allure.step(f"Click on element by attribute and it value: {attribute}: {value}"):
            el = find_elements(self.app.driver, f"//*[@{attribute}='{value}']")
            if len(el) > 0:
                el[0].click()
            else:
                assert False, f"Element with attribute: {attribute} and value: {value} has not been found"

    def wait_for_element_to_be_clickable(self,driver, xpath, timeout=20):
        wait = WebDriverWait(driver, timeout)
        return wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

    def click_element_by_xpath(self,driver, xpath):
        element = driver.find_element(By.XPATH, xpath)
        element.click()

    def click_checkbox_by_xpath(self,driver, xpath):
        element = driver.find_element(By.XPATH, xpath)
        element.click()