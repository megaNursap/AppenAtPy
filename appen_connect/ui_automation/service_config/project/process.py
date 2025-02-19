import time

import allure
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from adap.ui_automation.utils.js_utils import *
from adap.ui_automation.utils.selenium_utils import *


class Process:
    PROJECT_NAME = "//input[@name='processName']"
    PROJECT_DESCRIPTION = "//textarea[@name='processDescription']"
    COPY_PROCESS = "//input[@name='showCopyFromProcessSelect']/../span[@class='overlay']"
    COPY_MODULES = "//input[@name='copyModulesFrom']"
    SELECT_ACADEMY_COURSE = "//input[@name='SELECT ACADEMY COURSE']"
    Quiz = "//input[@name='Quiz']"
    MAXATTEMPTS = "//input[@id='maximumAttemps']"
    SUBSETSIZE = "//input[@id='subsetSize']"
    PASSINGSCORE = "//input[@id='passingScore']"
    RATE_TYPE = "//input[@name='rateType']"
    PROJECT_BUSINESS_UNIT = "//input[@name='businessUnit']"

    elements = {
        "Process Name":
            {"xpath": PROJECT_NAME,
             "type": "input"
             },
        "Process Description":
            {"xpath": PROJECT_DESCRIPTION,
             "type": "input"
             },
        "Copy Modules From an Existing Process": {
            "xpath": COPY_PROCESS,
            "type": "checkbox"
        },
        "Copy modules from": {
            "xpath": COPY_MODULES,
            "type": "dropdown"
        },
        "Quiz": {
            "xpath": Quiz,
            "type": "dropdown"
        },
        "Rate Type":
            {"xpath": RATE_TYPE,
             "type": "dropdown"
             },
        "Project Business Unit":
            {"xpath": PROJECT_BUSINESS_UNIT,
             "type": "dropdown"
             }
    }

    def __init__(self, project):
        self.project = project
        self.app = project.app
        self.sign_document = SignDocument(self)
        self.take_exam = TakeExam(self)
        self.take_quize = TakeQuiz(self)
        self.take_academy = TakeAcademyCourse(self)


    def load_project_pay_type(self, data):
        with allure.step('select pay rate for project'):
            time.sleep(2)
            self.project.enter_data(data=data, elements=self.elements)

    def new_process(self, process_type):
        with allure.step('Create new %s' % process_type):
            time.sleep(2)
            new_process_btn = find_element(self.app.driver,
                                           "//div[text()='%s']/..//div[text()='Create new process']" % process_type)
            new_process_btn.click()
            time.sleep(2)
            crete_btn = find_element(self.app.driver,
                                     "//div[text()='%s']/..//button[text()='Create Process']" % process_type)
            crete_btn.click()


    def new_process_details(self, data):
        with allure.step('Fill out new process details'):
            self.project.enter_data(data=data, elements=self.elements)

    def cancel_process_creation(self):
        with allure.step('Cancel process creation'):
            btn = find_elements(self.app.driver, "//button[text()='Start']/../..//button[text()='Cancel']")
            assert len(btn), "Cancel btn has not been found"
            btn[0].click()

    def copy_modules_from_process(self, process_name):
        with allure.step('Copy modules from process: %s' % process_name):
            self.project.enter_data(data={"Copy Modules From an Existing Process": "1",
                                          "Copy modules from": process_name}, elements=self.elements)

    def _find_module_by_name(self, module_name):
        return self._find_modules_by_name(module_name)[0]

    def _find_modules_by_name(self, module_name):
        gear = find_elements(self.app.driver, "//div[contains(text(),'%s')]/../.." % module_name)
        assert len(gear) > 0, "Modules %s has not been found" % module_name
        return gear

    def _click_module_action(self, module, module_action):
        gear = module.find_element('xpath',
            ".//div[contains(@class, 'process_builder__card__actions')]//*[local-name() = 'svg']/..")
        action = ActionChains(self.app.driver)
        self.app.driver.execute_script("window.scrollTo(0, window.scrollY + 100)")
        action.click(gear).pause(5).perform()
        time.sleep(5)
        btn = module.find_elements('xpath',".//div[text()='%s']" % module_action)
        assert len(btn) > 0, "%s button has not been found" % module_action
        btn[0].click()
        time.sleep(2)


    def preview_module_from_process(self, module_name, index=0):
        with allure.step('Click preview module %s' % module_name):
            module = self._find_modules_by_name(module_name)
            self._click_module_action(module[index], 'Preview')

    def remove_module_from_process(self, module_name):
        with allure.step('Remove module %s' % module_name):
            module = self._find_module_by_name(module_name)
            self._click_module_action(module, "Remove")

    def edit_module_in_process(self, module_name, index=0):
        with allure.step('Edit module %s' % module_name):
            module = self._find_modules_by_name(module_name)
            self._click_module_action(module[index], "Edit")


    def get_modal_window_header(self):
        with allure.step('Get modal window header'):
            el = find_elements(self.app.driver, "//div[@role='dialog']//h2")
            assert len(el) > 0, "Header has not been found"
            return el[0].text

    def verify_module_name_in_preview_window(self, module_name, is_not=True):
        with allure.step('Verify module name in preview window'):
            element = find_elements(self.app.driver, "//div[@role='dialog']//div[text()='%s']" % module_name)
            if is_not:
                assert len(element) > 0, "Actual Module name is not %s" % module_name
            if not is_not:
                assert len(element) == 0, "%s is present on the page, but not should not"
            time.sleep(5)

    def carousel_preview_process_click(self, btn_name):
        with allure.step('Click caroucel button %s' % btn_name):
            btns = find_elements(self.app.driver, "//div[contains(@class,'carousel-slider')]//span")
            if btn_name == 'Next': btns[1].click()
            if btn_name == "Previous": btns[0].click()

    def get_current_process_modules(self):
        with allure.step('Get current modules'):
            modules = find_elements(self.app.driver,
                                    "//div[@title and contains(@class, 'card__index')]/../child::div[2]/child::div[1]")
            return [x.text for x in modules]

    def switch_to_process_preview_iframe(self):
        iframe = find_elements(self.app.driver, "//iframe[@title= 'Process Preview']")
        self.app.driver.switch_to.frame(iframe[0])

    def _click_process_builder_action(self, menu_action):
        print(self.app.driver.page_source)
        process = find_element(self.app.driver, "//h2[contains(.,'Process Builder')]/../..")

        action = ActionChains(self.app.driver)
        # action.move_to_element(process).perform()
        # time.sleep(2)

        gear = process.find_element('xpath',".//*[local-name() = 'svg']")
        action.click(gear).perform()

        menu = process.find_elements('xpath',".//div[@role='button'][.//div[text()='%s']]" % menu_action)
        assert len(menu) > 0, "%s button has not been found" % menu_action
        action.click(menu[0]).perform()
        time.sleep(2)

    def click_edit_process_details(self):
        with allure.step('Click Edit Process Details'):
            self._click_process_builder_action('Edit Details')

    def click_cancel_process_creation(self):
        with allure.step('Click Cancel Process Details'):
            self._click_process_builder_action('Cancel')

class SignDocument:
    SELECT_DOCUMENT = "//label[text()='Select existing document']/..//input[contains(@id,'react-select')]"
    TITLE = "//input[@id='documentTitle']"
    CONTENT = "//div[@class='DraftEditor-editorContainer']//div[@role='textbox']"
    REQUIRED = "//input[@name='required']/.."
    HAS_NOTES = "//input[@name='hasInternalNotes']/../span[@class='overlay']"
    NOTES = "//textarea[@name='internalNotes']"

    elements = {
        "SELECT DOCUMENT": {
            "xpath": SELECT_DOCUMENT,
            "type": "dropdown"
        },
        "DOCUMENT TITLE":
            {"xpath": TITLE,
             "type": "input"
             },
        "DOCUMENT CONTENT":
            {"xpath": CONTENT,
             "type": "input"
             },
        "REQUIRED":
            {"xpath": REQUIRED,
             "type": "checkbox"
             },
        "Add Internal Notes":
            {"xpath": HAS_NOTES,
             "type": "checkbox"
             },
        "INTERNAL NOTES":
            {"xpath": NOTES,
             "type": "input"
             }
    }

    def __init__(self, process):
        self.app = process.app
        self.project = process.project

    def select_existing_document(self, document_name):
        with allure.step('Select existing document %s' % document_name):
            btn = find_elements(self.app.driver, "//div[text()='USE EXISTING DOCUMENT']")
            assert len(btn) > 0, "USE EXISTING DOCUMENT button has not been found"
            btn[0].click()
            self.project.enter_data(data={"SELECT DOCUMENT": document_name}, elements=self.elements)

    def create_new_document(self, data, action=None):
        with allure.step('Select Create new document '):
            btn = find_elements(self.app.driver, "//div[text()='CREATE NEW DOCUMENT']")
            assert len(btn) > 0, "CREATE NEW DOCUMENT button has not been found"
            btn[0].click()
            self.project.enter_data(data=data, elements=self.elements)
            if action:
                self.app.navigation.click_btn(action)


class TakeExam:
    TITLE = "//input[@id='emailTitle']"
    CONTENT = "//div[@class='DraftEditor-editorContainer']//div[@role='textbox']"
    UNLIMITED = "//input[@name='unlimited']/.."
    MAXIMUM_ATTEMPTS = "//input[@id='maximumAttemps']"
    START_EXAM = "//span[@role='radio'][.//label[text()='Start Exam Immediately']]"
    LOAD_USER_INFO = "//span[@role='radio'][.//label[text()='Load the User into Exam Batch']]"

    elements = {
        "EMAIL TITLE": {
            "xpath": TITLE,
            "type": "input"
        },
        "EMAIL CONTENT":
            {"xpath": CONTENT,
             "type": "input"
             },
        "UNLIMITED":
            {"xpath": UNLIMITED,
             "type": "checkbox"
             },
        "MAXIMUM ATTEMPTS":
            {"xpath": MAXIMUM_ATTEMPTS,
             "type": "input"
             },
        "Start Exam Immediately":
            {"xpath": START_EXAM,
             "type": "checkbox"
             },
        "Load the User into Exam Batch":
            {"xpath": LOAD_USER_INFO,
             "type": "checkbox"
             }
    }

    def __init__(self, process):
        self.app = process.app
        self.project = process.project

    def edit_exam(self, data, action=None):
        with allure.step('Edit exam info'):
            self.project.enter_data(data=data, elements=self.elements)
            if action:
                self.app.navigation.click_btn(action)


# Automation Qual Take Internal Quiz
class TakeQuiz:
    QUIZ = "//input[@name='quiz0']"
    LOCALE = "//label[text()='Locale']/..//input"
    LANGUAGE_QUIZ = "//label[text()='Language quiz']/..//input"
    UNLIMITED = "//input[contains(@name,'unlimited')]/.."
    ALL_QUESTIONS = "//input[contains(@name,'allQuestions')]/.."
    MAXIMUM_ATTEMPTS = "//input[@id='maximumAttemps']"
    SUBSET_SIZE = "//input[@id='subsetSize']"
    PASSING_SCORE = "//input[@id='passingScore']"
    TRANSLATE_TO_LOCALE = "//label[text()='TRANSLATE TO LOCALE']/..//input"
    TRANSLATION_QUIZ = "//label[text()='TRANSLATION QUIZ']/..//input"

    elements = {
        "Quiz": {
            "xpath": QUIZ,
            "type": "dropdown"
        },
        "Locale": {
            "xpath": LOCALE,
            "type": "dropdown"
        },
        "LOCALE": {
            "xpath": LOCALE,
            "type": "dropdown"
        },
        "UNLIMITED":
            {"xpath": UNLIMITED,
             "type": "checkbox"
             },
        "ALL QUESTIONS":
            {"xpath": ALL_QUESTIONS,
             "type": "checkbox"
             },
        "Maximum attempts":
            {"xpath": MAXIMUM_ATTEMPTS,
             "type": "input"
             },
        "Subset size":
            {"xpath": SUBSET_SIZE,
             "type": "input"
             },
        "Passing score":
            {"xpath": PASSING_SCORE,
             "type": "input"
             },
        "Language quiz": {
            "xpath": LANGUAGE_QUIZ,
            "type": "dropdown"
        },
        "TRANSLATE TO LOCALE": {
            "xpath": TRANSLATE_TO_LOCALE,
            "type": "dropdown"
        },
        "TRANSLATION QUIZ": {
            "xpath": TRANSLATION_QUIZ,
            "type": "dropdown"
        }
    }

    def __init__(self, process):
        self.app = process.app
        self.project = process.project

    def edit_quiz(self, data, action=None):
        with allure.step('Edit quiz info'):
            self.project.enter_data(data=data, elements=self.elements)
            if action:
                self.app.navigation.click_btn(action)


# Automation Qual Take Academy Course
class TakeAcademyCourse:
    SELECT_ACADEMY_COURSE = "//input[@name='SELECT ACADEMY COURSE']"

    elements = {
        "SELECT ACADEMY COURSE": {
            "xpath": SELECT_ACADEMY_COURSE,
            "type": "dropdown"
        }
    }

    def __init__(self, process):
        self.app = process.app
        self.project = process.project

    def edit_academy_course(self, data, action=None):
        with allure.step('Edit Academy Course info'):
            self.project.enter_data(data=data, elements=self.elements)
            if action:
                self.app.navigation.click_btn(action)
