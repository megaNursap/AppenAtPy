import time

import allure

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from adap.ui_automation.utils.selenium_utils import find_element, find_elements


class Quizzes:
    # XPATH
    QUIZ_TYPE = "//*[@id='quiz-type']"
    STATUS = "//select[@name='quiz.status']"

    elements = {
        "Quiz Type":
            {"xpath": QUIZ_TYPE,
             "type": "dropdown"
             },
        "Quiz Status":
            {"xpath": STATUS,
             "type": "dropdown"
             }

    }

    def __init__(self, app_test):
        self.app_test = app_test
        self.driver = self.app_test.driver

    def quiz_title(self, quiz_title):
        with allure.step('Enter your quiz title. %s' % quiz_title):
            title = find_element(self.driver, '//input[@name="quiz.title"]')
            title.send_keys(quiz_title)

    def fill_out_fields(self, data):
        with allure.step('Select drop down fields. Quizzes page. %s' % data):
            for field, value in data.items():
                if value:
                    if self.elements[field]['type'] == 'dropdown':
                        el = find_elements(self.app_test.driver, self.elements[field]['xpath'])
                        assert len(el), "Field %s has not been found" % field
                        Select(el[0]).select_by_visible_text(value)
                        time.sleep(1)

    def quiz_instructions(self, quiz_instructions):
        with allure.step('Fill in Quizzes instructions. %s' % quiz_instructions):
            el = find_element(self.driver, '//textarea[@name="quiz.instructions"]')
            el.send_keys(quiz_instructions)

    def search_for_quiz_created(self, quiz_name):
        with allure.step('Fill in Quizz name. %s' % quiz_name):
            el = find_element(self.app_test.driver, "//input[@id='search']")
            el.send_keys(quiz_name)
