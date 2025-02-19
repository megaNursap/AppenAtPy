import time

import allure
from allure_commons.types import AttachmentType

from adap.ui_automation.utils.selenium_utils import find_elements, find_element, find_elements_by_css_selector, \
    sleep_for_seconds
from adap.ui_automation.utils.utils import convert_to_snake_case


class Judgements:

    def __init__(self, job):
        self.job = job
        self.driver = self.job.app.driver
        self.app = job.app

    def get_num_completed_tasks(self):
        with allure.step('Get number of completed tasks'):
            el = find_elements(self.driver, "//h4[.//small[text()=' tasks completed' or text()=' task completed']]")
            assert el[0], "Completed tasks have not been found"
            return el[0].text.strip()

    def select_option_answers(self, answers):
        el = find_elements(self.driver, "//*[@id='job_units']/*[@class='cml jsawesome']")
        for i in range(1, len(el) + 1):
            with allure.step(f'Select answers for questions {answers[i - 1]}'):
                option = find_element(self.driver, f"//*[@id='job_units']/*[@class='cml jsawesome'][{i}]//*[@value='{convert_to_snake_case(answers[i - 1])}']")
                self.driver.execute_script("arguments[0].click();", option)

    def click_submit_judgements(self):
        with allure.step('Find submit button'):
            xpath = "//div[@class='form-actions']//input[@value='Submit & Continue']"
            submit_btn = find_elements(self.app.driver, xpath)
            submit_btn[0].click()
            time.sleep(7)

    def get_collected_judgments(self):
        with allure.step('Get collected judgements info'):
            el = find_element(self.app.driver, "//div[contains(text(), 'Judgments Collected')]/..")
            return el.text

    def create_random_judgments_answer(self, var_numbers=3, wait_time=2):
        with allure.step("Create judgments answers"):
            print("Judgments answers will be created")

            time.sleep(3)
            elements = find_elements(self.app.driver, "//input[@type='radio']/..")

            for elem in elements[::var_numbers]:
                elem.click()

            time.sleep(wait_time)

            self.click_submit_judgements()

