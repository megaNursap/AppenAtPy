import time

import allure
from selenium.webdriver.common.keys import Keys
from adap.ui_automation.utils.js_utils import get_text_excluding_children
from adap.ui_automation.utils.selenium_utils import find_elements, find_element
from appen_connect.ui_automation.service_config.vendor_profile.basic_information import BasicInformation
from appen_connect.ui_automation.service_config.vendor_profile.education import Education
from appen_connect.ui_automation.service_config.vendor_profile.languages import Languages
from appen_connect.ui_automation.service_config.vendor_profile.location import Location
from appen_connect.ui_automation.service_config.vendor_profile.phone import Phone
from appen_connect.ui_automation.service_config.vendor_profile.preview import Preview
from appen_connect.ui_automation.service_config.vendor_profile.prior_experience import PriorExperience
from appen_connect.ui_automation.service_config.vendor_profile.project_application import ProjectApplication
from appen_connect.ui_automation.service_config.vendor_profile.registration_flow import Registration


class VendorProfile:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

        self.basic_information = BasicInformation(self)
        self.education = Education(self)
        self.languages = Languages(self)
        self.location = Location(self)
        self.phone = Phone(self)
        self.preview = Preview(self)
        self.prior_experience = PriorExperience(self)
        self.registration_flow = Registration(self)
        self.project_application = ProjectApplication(self)

    def open_tab(self, tab_name):
        with allure.step('Open tab %s' % tab_name):
            tab = find_elements(self.driver, "//div[./h3 and ./span[text()='%s']]" % tab_name)
            if not tab:
                tab = find_elements(self.driver, "//div[text()='%s']" % tab_name)
            assert len(tab), "Tab %s has not been found" % tab_name
            tab[0].click()
            time.sleep(1)

    def get_information_from_page(self):
        with allure.step('Get information from the page'):
            fields = find_elements(self.driver, "//div[./label]")
            businessnamefield=find_elements(self.driver,"//div/span[./label]/..")
            if len(businessnamefield) :
                fields.append(businessnamefield[0])
            result = {}
            for field in fields:
                name = field.find_element('xpath',".//label").text
                try:
                    value = get_text_excluding_children(self.driver, field)
                    if value == '': raise Exception("Not Found")
                except:
                    if len(field.find_elements('xpath',".//p")) > 0:
                        value = field.find_element('xpath',".//p").text
                    elif len(field.find_elements('xpath',".//input")) > 0:
                        input_field = field.find_element('xpath',".//input")
                        if input_field.get_attribute('type') == 'checkbox':
                            value = input_field.get_attribute('checked')
                        else:
                            value = field.find_element('xpath',".//input").get_attribute('value')
                            if value == '':
                                value = field.find_element('xpath',".//div").get_attribute('textContent')
                result[name] = value
            return result

    def get_table_content(self, tab_name):
        with allure.step('Grab info from table %s' % tab_name):
            table = find_elements(self.driver, "//div[text()='%s']/../../..//table" % tab_name)
            if len(table) == 0:  return []
            headers = [x.text for x in table[0].find_elements('xpath',".//thead//th")]

            _result = []

            for row in table[0].find_elements('xpath',".//tbody//tr"):
                columns = row.find_elements('xpath',".//td")
                index = 0
                _data = {}
                for column in columns:
                    _data[headers[index]] = column.text
                    index += 1
                _result.append(_data)

            return _result


    def confirm_consent_form(self):
        with allure.step('Accept Consent Form if displayed'):
            time.sleep(5)
            prompt = find_elements(self.driver, "//div[contains(text(),'I agree to the Terms of Service')]")
            if len(prompt) > 0:
                prompt[0].click()
                self.app.navigation.click_btn("Submit")


    def click_drop(self, inp_name):
        with allure.step('Click input: %s' % inp_name):
            el = find_elements(self.app.driver, "//label[text()='%s']//..//div[contains(text(),'Select')]" % inp_name)
            if len(el) > 0:
                el[0].click()
                assert len(el) > 0, ("Input %s has not been found" % inp_name)
                time.sleep(4)

    def click_out(self, inp_name):
        with allure.step('Click input: %s' % inp_name):
            el = find_elements(self.app.driver, "//label[text()='%s']" % inp_name)
            if len(el) > 0:
                el[0].click()
                assert len(el) > 0, ("Input %s has not been found" % inp_name)
                time.sleep(4)

    def remove_data(self, data, elements):
        with allure.step('Remove data: %s' % data):
            for field in data:
                el = find_elements(self.app.driver, elements[field]['xpath'])
                assert len(el), "Field %s has not been found" % field
                current_value = el[0].get_attribute('value')
                for i in range(len(current_value)):
                    el[0].send_keys(Keys.BACK_SPACE)

    def answer_question(self, question, answers, question_type='radio_btn', action=None):
        with allure.step('Answer Profile Builder question: %s' % question):
            if question_type == 'radio_btn':
                q_el = find_elements(self.driver,
                                     "//div[contains(@class,'styles_modal')]//label[text()='%s']/.." % question)
                assert len(q_el) > 0, "Question %s has not been found"

                for ans in answers:
                    _answ = q_el[0].find_elements('xpath',".//div[text()='%s']" % ans)
                    assert len(_answ) > 0, "Answer %s has not been found"
                    _answ[0].click()

            if action:
               self.app.navigation.click_btn(action)
            time.sleep(1)

    def get_current_answer(self, question):
        with allure.step('Get Answer for question: %s' % question):
            el = find_elements(self.driver, "//label[text()='%s']/..//input[@checked]/..//div[text()]" % question)
            assert len(el), "Question %s has not been found"
            return el[0].text

    def get_category_of_questions(self):
        with allure.step('Get category of questions from MORE ABOUT ME page'):
            el = find_elements(self.driver, "//h3[@data-baseweb]")
            return [x.text for x in el]

    def _find_category(self, name):
        with allure.step('Find category: %s' % name):
            el = find_elements(self.driver, "//h3[@data-baseweb and text()='%s']/../../.." % name)
            assert len(el) > 0, 'Category %s has not been found' % name
            return el[0]

    def click_start_answering_category(self, name):
        with allure.step('Start answering questions for category: %s' % name):
            category = self._find_category(name)
            btn = category.find_elements('xpath',".//button/*[text()='Start Answering']" )
            assert len(btn) > 0, 'Button Start Answering has not been found'
            btn[0].click()

    def click_edit_answers(self, name):
        with allure.step('Edit answers for category: %s' % name):
            category = self._find_category(name)
            btn = category.find_elements('xpath',".//a[text()='Edit']" )
            assert len(btn) > 0, 'Button Edit has not been found'
            btn[0].click()

    def click_less_more_link_for_category(self, name, btn_name):
        with allure.step('Less button for category: %s' % name):
            category = self._find_category(name)
            btn = category.find_elements('xpath',".//span[text()='%s']" % btn_name)
            assert len(btn) > 0, 'Button %s has not been found' %btn_name
            btn[0].click()

    def get_category_details(self, name):
        with allure.step('Get status for category: %s' % name):
            category = self._find_category(name)

            _edit_btn_status = ''
            _unanswered = 0
            _answers = {}

            _no_answers = True if len(category.find_elements('xpath',".//h5[text()='no answers']"))>0 else False
            _all_answered = True if category.find_elements('xpath',".//span[text()='All questions Answered']")  else False

            edit_btn = category.find_elements('xpath',".//a[text()='Edit']")
            if not edit_btn:
                _edit_btn_status = 'not found'
            else:
                _edit_btn_status = 'disabled' if edit_btn[0].get_attribute('disabled') else 'enabled'

            _unanswered_details = category.find_elements('xpath',".//div[contains(.,' questions unanswered') or contains(.,' question unanswered')]")
            if len(_unanswered_details) >0:
                _unanswered = _unanswered_details[-1].text.split(" ")[0]

            if _all_answered or _unanswered:
                questions = category.find_elements('xpath',".//div[@data-baseweb='block']/..")
                for q in questions:
                    _details = [x.text for x in q.find_elements('xpath',".//div")]
                    _answers[_details[0]] = _details[1]

            details = {
                "no_answers": _no_answers,
                "edit_btn_status": _edit_btn_status,
                "all_answered": _all_answered,
                "unanswered_questions": int(_unanswered),
                "answers":_answers
            }

            return details
