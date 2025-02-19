import time
import pytest
import allure

from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from adap.ui_automation.utils.js_utils import element_to_the_middle
from adap.ui_automation.utils.selenium_utils import find_elements
from adap.ui_automation.services_config.annotation import Annotation
from adap.api_automation.services_config.builder import Builder


def copy_with_tq_and_launch_job(api_key, job_id):
    copied_job = Builder(api_key)
    copied_job_resp = copied_job.copy_job(job_id, "all_units")
    copied_job_resp.assert_response_status(200)
    # copied_job_resp.assert_job_message({'notice': 'Job copied. Units will be copied over shortly.'})
    copied_job.launch_job()
    copied_job.wait_until_status('running', 340)
    res = copied_job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")
    return copied_job.job_id


class TextAnnotation(Annotation):
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def activate_iframe_by_index(self, index):
        with allure.step('Activate iframe'):
            time.sleep(3)
            first_image = self.driver.find_elements('xpath',"//div[@class='cml jsawesome']")[index]
            element_to_the_middle(self.driver, first_image)
            iframe = first_image.find_element('xpath',".//iframe")
            self.iframe = iframe
            self.driver.switch_to.frame(iframe)
            time.sleep(2)

    def full_screen(self):
        with allure.step('Make full screen'):
            find_elements(self.driver, "//button[contains(@class, 'b-Button__fullscreen')]")[0].click()
            time.sleep(2)

    def find_word_with_text_token(self, value, word_index=0):
        with allure.step('Find word by text token'):
            els = find_elements(self.driver,
                                "//div[contains(@class,'b-TextGridSpan-TextToken') and text()='%s']/.." % value)

            assert len(els) > 0, "Word %s has not been found" % value
            if word_index:
                assert len(els) >= word_index + 1, "Word %s, index %s has not been found" % (value, word_index)
            return els[word_index]

    def get_word_count_with_label(self, label, value):
        with allure.step('Get word counts with label'):
            els = find_elements(self.driver,
                                "//div[contains(@class, 'b-TextGridSpan')][.//div[@class='b-TextGridSpan-TextSpan__label' "
                                "and text()='%s']]//div[contains(@class,'b-TextGridSpan-TextToken') and text()='%s']/.." % (
                                    label, value))
            return len(els)

    def click_token(self, value, word_index=0):
        with allure.step('Click token'):
            el = self.find_word_with_text_token(value, word_index)
            el.click()
            time.sleep(2)

    def click_span(self, span):
        with allure.step('Click span'):
            self.driver.find_element('xpath',
                "//div[@class='b-Sidebar__category-header' and text()='%s']" % span).click()
            time.sleep(2)

    def delete_span(self):
        with allure.step('Delete span'):
            self.driver.find_element('xpath',"//button[@class='b-Button b-ButtonDelete']//*[local-name() = 'svg']").click()
            time.sleep(2)

    def get_inactive_span_line_counts(self):
        with allure.step('Get inactive span line'):
            inactive_span = find_elements(self.driver,
                                          "//div[@class='b-NestedCanvas-InactiveSpan-SpanLine b-NestedCanvas-InactiveSpan__span-line']")
            return len(inactive_span)

    def get_gray_span_line_counts(self):
        with allure.step('Get gray span line'):
            gray_span = find_elements(self.driver,
                                      "//div[contains(@class,'b-NestedCanvas-InactiveSpan__empty-span-line')]")
            return len(gray_span)

    def select_gray_span(self, index):
        with allure.step('Get gray span line'):
            gray_span = find_elements(self.driver,
                                      "//div[contains(@class,'b-NestedCanvas-InactiveSpan__empty-span-line')]")
            if len(gray_span) >= index:
                gray_span[index].click()

    def merge_token(self, tokens):
        with allure.step('Merge token'):
            ac = ActionChains(self.driver)
            for token in tokens:
                ac.key_down(Keys.SHIFT).perform()
                self.click_token(token)

    def merge_nested_token(self, gray_line_index, token):
        with allure.step('Merge token'):
            ac = ActionChains(self.driver)
            ac.key_down(Keys.SHIFT).perform()
            self.select_gray_span(gray_line_index)
            ac.key_down(Keys.SHIFT).perform()
            self.click_token(token)
