import os
import time
import allure
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

from adap.perf_platform.utils.logging import get_logger
from adap.ui_automation.utils.js_utils import is_enabled_js
from adap.ui_automation.utils.pandas_utils import dataframe_equals
from adap.ui_automation.utils.selenium_utils import find_elements, find_element, find_elements_by_css_selector

log = get_logger(__name__)


class GeneralVerification:
    def __init__(self, app):
        self.app = app

    def current_url_contains(self, appendix):
        with allure.step('Verify current URL contains "%s"' % appendix):
            current_url = self.app.driver.current_url
            if appendix not in current_url:
                 assert False, (
                        'Redirection went wrong. {' + appendix + '} not reached. Current url is {' + current_url + '}')

    def logo_is_displayed_on_page(self):
        with allure.step('Verify F8 logo is displayed on page'):
            # customer page
            if '/welcome' in self.app.driver.current_url:
                logo = self.app.driver.find_elements('xpath',"//a[@class='b-welcome-logo']")
            else:
                # contributors or tasks page
                logo = self.app.driver.find_elements("id", "Logo")
            assert len(logo) > 0, " Logo is not  displayed on the page"

    def text_present_on_page(self, page_text, is_not=True):
        with allure.step('Verify the text "%s" is present= %s on the page' % (page_text, is_not)):
            if is_not:
                try:
                    element = find_elements(self.app.driver, "//*[text()[contains(.,\"%s\")]]" % page_text)
                except:
                    element = find_elements(self.app.driver, "//*[text()[contains(.,\'%s\')]]" % page_text)

                if not element: #find text, case insensitive
                    element = find_elements(self.app.driver, '//*[contains(translate(text(),"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"),"%s")]' % page_text.lower())

                if element:
                    print("\n The text %s is displayed on the page" % page_text)
                    return True
                else:
                    assert False, ("\n The text %s is NOT displayed on the page" % page_text)
            if not is_not:
                element = find_elements(self.app.driver, "//*[contains(text(),'%s')]" % page_text)
                if not element:
                    log.debug("\n The text %s is NOT displayed on the page (as expected!)" % page_text)
                    return True
                else:
                    assert False, ("\n The text %s IS displayed on the page (but it must not!)" % page_text)

    def texts_present_on_page(self, page_texts, is_not=True):
        return all(self.text_present_on_page(text, is_not) for text in page_texts)

    def verify_error_is_visible_on_the_page(self):
        with allure.step('Verify error is visible on the page'):
            element = find_elements_by_css_selector(self.app.driver, "[type='error']")
            if len(element) > 0:
                return True
            else:
                return False

    def wait_untill_text_present_on_the_page(self, text, max_time=20):
        wait = WebDriverWait(self.app.driver, max_time)
        try:
            wait.until(ec.visibility_of_any_elements_located((By.XPATH, f"//*[contains(text(),'{text}')]")))
            return True
        except:
            return False

    def tab_with_columns_present_on_page(self, columns):
        with allure.step('Verify the table with columns is present on the page: %s' % (columns)):
            expected_columns = columns.split(",")
            actual_columns = [x.text.upper() for x in find_elements(self.app.driver, "//th[not(text()=' ') and text()]")]
            assert sorted(expected_columns) == sorted(actual_columns), "Expected columns: %s \n Actual columns: %s" % (expected_columns, actual_columns)

    def assert_data_frame_equals(self, data_fr_expected, data_fr_actual):
        with allure.step('Verify data frame equals' ):
            assert dataframe_equals(data_fr_expected,data_fr_actual), "Data doesn't match"

    def verify_file_present_in_dir(self, file_name, dir_name, contains=False):
        with allure.step('Verify file %s exists in dir %s' %(file_name, dir_name)):
            files = os.listdir(dir_name)
            if contains:
                for f in files:
                    if file_name in f:
                        return True
            assert file_name in files, "File %s has not been found in %s" % (file_name, dir_name)

    def element_is_visible_on_the_page(self, xpath, is_not=True):
        with allure.step('Element with XPATH is visible on the page %s' % xpath):
            element = find_elements(self.app.driver, xpath)
            if is_not:
                assert len(element), ("\n The element %s is NOT displayed on the page" % xpath)
                assert element[0].is_displayed(),  ("\n The element %s is NOT displayed on the page" % xpath)
            else:
                assert len(element)==0, ("\n The element %s is displayed on the page" % xpath)

    def element_is(self, param, tab_name, is_not=False):
        with allure.step('Element %s is %s' % (tab_name,param)):
            time.sleep(1)
            tab_el = self.app.driver.find_elements('xpath',"//a[text()='%s']" % tab_name)
            assert tab_el, "Tab %s has not been found" % tab_name
            _class = tab_el[0].get_attribute('class')
            active = _class.find(param)

            if is_not:
                assert active==-1, "param %s is active" % tab_el
            else:
                assert active, "param %s is not active" % tab_el

    def input_field_is_readonly(self, name):
        with allure.step('Element %s is readonly' % name):
            time.sleep(1)
            tab_el = self.app.driver.find_elements('xpath',"//input[@name='%s']" % name)
            assert tab_el, "Field %s has not been found" % name
            _param = tab_el[0].get_attribute('readonly')
            return _param

    def pagination_is_displayed(self, is_not=False):
        with allure.step('Verify pagination is displayed on the page(%s)' % is_not):
            el = find_elements(self.app.driver, "//span[text()='Page']")
            if is_not:
                assert not el, "Pagination is displayed"
            else:
                assert len(el)>0, "Pagination is not displayed"

    def switch_to_window_and_verify_link(self, expected_link):
        with allure.step("verify link for new window '%s'" % expected_link):
            self.app.driver.switch_to.window(self.app.driver.window_handles[-1])
            new_window = self.app.driver.current_url
            if new_window not in expected_link:
                assert False, (
                        'Redirection went wrong. {' + new_window + '} not reached. Current url is {' + expected_link + '}')
            job_window = self.app.driver.window_handles[0]
            self.app.navigation.switch_to_window(job_window)

    def scrollbar_is_visible(self, element):
        scroll_height = element.get_attribute('scrollHeight')
        offset_height = element.get_attribute('offsetHeight')
        if int(scroll_height) > int(offset_height): return True
        return False

    def checkbox_by_text_is_selected(self, name, index=0):
        with allure.step('Get checkbox status by text: %s' % name):
            el = find_elements(self.app.driver, "//label[text()='%s']/..//input" % name)
            if len(el) > 0:
                return el[index].is_selected()
            else:
                assert False, "Checkbox with text - %s has not been found" % name

    def checkbox_by_text_background_color(self, name, index=0):
        with allure.step('Get background color of check/uncheck checkbox status by text: %s' % name):
            el = find_elements(self.app.driver, "//label[text()='%s']/..//label" % name)
            if len(el) > 0:
                return el[index].value_of_css_property('background-color')
            else:
                assert False, "Checkbox with text - %s has not been found" % name

    def button_is_disable(self, btn_name):
        with allure.step('Button %s is displayed' % btn_name):
            # btn = find_elements(self.app.driver, "//button[.//*[text()='%s'] or text()='%s']" % (btn_name, btn_name))
            btn = find_elements(self.app.driver,
                                "//*[(contains(@class,'btn') or contains(@class,'Button')) and contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'%s')]" % btn_name.lower())
            if len(btn) == 0:
                btn = find_elements(self.app.driver,
                                    "//button[.='%s']" % btn_name)
            assert len(btn) > 0, "Button has not been found"
            # el_class = btn[0].get_attribute('class')
            return not btn[0].is_enabled()
            # return (True, False)[el_class.find('disabled') == -1]

    def link_is_disable(self, btn_name, method='selenium'):
        with allure.step('Button %s is displayed' % btn_name):
            btn = find_elements(self.app.driver,
                                "//a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'%s')]" % btn_name.lower())
            if len(btn) == 0:
                btn = find_elements(self.app.driver,
                                    "//a[text()='%s']" % btn_name)
            assert len(btn) > 0, "Button has not been found"

            if method == 'selenium':
                return not btn[0].is_enabled()

            if method == 'cursor_property':
                return btn[0].value_of_css_property('cursor') == 'not-allowed'

    def button_is_displayed(self, btn_name, is_not=True):
        with allure.step('Verify button is displayed: %s' % btn_name):
            btn = find_elements(self.app.driver,
                                "//*[(contains(@class,'btn') or contains(@class,'Button')) and contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'%s')]" % btn_name.lower())
            if len(btn) == 0:
                btn = find_elements(self.app.driver,
                                    "//button[text()='%s']" % btn_name)

            if is_not:
                assert len(btn) > 0, "Button %s is not displayed on the page" % btn_name
            else:
                assert len(btn) == 0, "Button %s is displayed on the page" % btn_name

    def link_is_displayed(self, link_name, is_not=True):
        with allure.step('Verify link is displayed: %s' % link_name):
            link = find_elements(self.app.driver,
                                 "//a[(normalize-space(text())='%s') or ./span[contains(text(),'%s')]]" % (
                                    link_name, link_name))
            if is_not:
                assert len(link) > 0, "Link %s is not displayed on the page" % link_name
            else:
                assert len(link) == 0, "Link %s is displayed on the page" % link_name

    def count_text_present_on_page(self, page_text):
        with allure.step('Count the number of text "%s" present on the page' % page_text):
            element = find_elements(self.app.driver, "//*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'%s')]" % page_text.lower())
            return len(element)

    def verify_mode_text_is(self, mode_text):
        with allure.step(f"Verify mode text is '{mode_text}'"):
            mode_text_element = find_element(self.app.driver, f"//h4[contains(text(), '{mode_text}')]")
            assert mode_text_element, f"Mode text is not '{mode_text}', elements - '{mode_text_element}'"

    def wait_until_text_disappear_on_the_page(self, text, max_time):
        wait = WebDriverWait(self.app.driver, max_time)
        try:
            wait.until_not(ec.visibility_of_any_elements_located((By.XPATH, "//*[contains(text(),'%s')]" % text)))
            return True
        except:
            return False

    def verify_validation_status(self, validation_status='validation-succeeded'):
        with allure.step(f"Verify if {validation_status} status appeared on page"):
            validation_status_el = find_elements(self.app.driver, "//div[contains(@class, '%s')]" % validation_status)
            assert validation_status_el, "The status element NOT present"
            display = validation_status_el[0].get_attribute('style').split(' ')
            if 'block;' in display:
                log.debug(f"\n The status {validation_status} is displayed on the page (as expected!)")
                return True
            else:
                assert False, f"The {validation_status} status NOT present on page"

    def verify_link_redirects_to(self, link_name, target_url, new_window=False, index=0):
        with allure.step(f"Verify that {link_name} redirects to {target_url}"):
            if new_window:
                current_window = self.app.driver.window_handles[0+index]

            self.app.navigation.click_link(link_name)

            time.sleep(2)
            if new_window:
                new_window = self.app.driver.window_handles[1]
                self.app.navigation.switch_to_window(new_window)

            self.current_url_contains(target_url)

            if new_window:
                self.app.navigation.switch_to_window(current_window)





