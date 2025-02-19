import time

import allure
from selenium.webdriver import ActionChains

from adap.ui_automation.utils.js_utils import mouse_click_element, mouse_over_element, element_to_the_middle
from adap.ui_automation.utils.selenium_utils import find_elements


class UserProject:
    # XPATH
    DEFAULT_PAGE_TASK = "//input[contains(@name,'defaultPageTask')]"
    SKILL_REVIEW = "//input[@name='hasSkillReview']/..//span[@class='overlay']"
    ACAN = "//input[@name='isACANProject']/..//span[@class='overlay']"
    ACADEMY = "//input[@name='resourceId']"
    APPLICANTS_ACCESS = "//input[@name='allowQualifyingApplicantAccess']/..//span[@class='overlay']"
    USER_ACCESS = "//input[@name='allowActiveUserAccess']/..//span[@class='overlay']"


    UPSKILLING = "//span[@role='radio'][.//label[text()='Upskilling']]"
    GUIDELINE = "//span[@role='radio'][.//label[text()='Guideline']]"
    DOCUMENT = ""
    ACKNOWLEDGEMENT = "//input[@name='requireAcknowledgement']"
    NOTES_RATERS = "//input[@name='hasNotesToRaters']/..//span[@class='overlay']"
    CONSENT_FORM = "//input[@name='hasDataCollectionConsentForm']/..//span[@class='overlay']"


    QUIZ = ""
    QUESTIONS_SHUFFLED = "//input[@name='questionsShuffled']/..//span[@class='overlay']"
    QUESTIONS_FEEDBACK = "//input[@name='showFeedback']/..//span[@class='overlay']"
    UNLIMITED = "//input[@name='unlimited']/.."
    ALL_QUESTIONS = "//input[@name='allQuestions']/.."
    MAX_QUIZ_ATTEMPTS = "//input[@name='maxQuizAttempts']"
    SUBSET_SIZE = "//input[@name='subsetSize']"
    PASSING_SCORE = "//input[@name='passingScore']"
    CONSENT_FORM_CONTACT_EMAIL = "//input[@name='projectContactEmail']"
    APPEN_ENTITY = ''
    PII_DATA_COLLECTED = ''
    COUNTRY_COLLECT_DATA = ''
    PII_THIRD_PARTY = "//input[@name='collectThirdPartyPII']/.."
    DPO_CONTACT_EMAIL = "//input[@name='customerDPOEmail']"
    LEGAL_NAME = "//input[@name='customerFullLegalName']"
    CUSTOMER_COUNTRY = ''

    SURVEY=''
    FILTER_RESOURCES = ''
    FIRST_NAME = "//input[@placeholder='Enter first name']"
    LAST_NAME = "//input[@placeholder='Enter last name']"
    AGE = "//input[@placeholder='Enter age']"
    EMAIL_ADDRESS = "//input[@placeholder='Enter email address']"
    GENDER = ''

    elements = {
        "Filter resources":
            {"xpath": FILTER_RESOURCES,
             "type": "dropdown"
             },
        "Survey":
            {"xpath": SURVEY,
             "type": "dropdown"
             },
        "Quiz":
            {"xpath": QUIZ,
             "type": "dropdown"
             },
        "Shuffle Questions":
            {"xpath": QUESTIONS_SHUFFLED,
             "type": "checkbox"
             },
        "Show Question Feedback":
            {"xpath": QUESTIONS_FEEDBACK,
             "type": "checkbox"
             },
        "UNLIMITED":
            {"xpath": UNLIMITED,
             "type": "checkbox"
             },
        "ALL QUESTIONS":
            {"xpath": ALL_QUESTIONS,
             "type": "checkbox"
             },
        "Maximum Attempts":
            {"xpath": MAX_QUIZ_ATTEMPTS,
             "type": "input"
             },
        "Subset Size":
            {"xpath": SUBSET_SIZE,
             "type": "input"
             },
        "Passing Score":
            {"xpath": PASSING_SCORE,
             "type": "input"
             },
        "Document":
            {"xpath": DOCUMENT,
             "type": "dropdown"
             },
        "Upskilling":
            {"xpath": UPSKILLING,
             "type": "checkbox"
             },
        "Guideline":
            {"xpath": GUIDELINE,
             "type": "checkbox"
             },
        "REQUIRE ACKNOWLEDGEMENT":
            {"xpath": ACKNOWLEDGEMENT,
             "type": "checkbox"
             },
        "Default Page Task":
            {"xpath": DEFAULT_PAGE_TASK,
             "type": "dropdown"
             },
        "Available Skill Review":
            {"xpath": SKILL_REVIEW,
             "type": "checkbox"
             },
        "ACAN Project":
            {"xpath": ACAN,
             "type": "checkbox"
             },
        "Academy":
            {"xpath": ACADEMY,
             "type": "dropdown"
             },
        "Allow Qualifying Applicants Access":
            {"xpath": APPLICANTS_ACCESS,
             "type": "checkbox"
             },
        "Allow Active Users Access":
            {"xpath": USER_ACCESS,
             "type": "checkbox"
             },
        "Add Notes To Raters":
            {"xpath": NOTES_RATERS,
             "type": "checkbox"
             },
        "Project Contact Email":
            {"xpath": CONSENT_FORM_CONTACT_EMAIL,
             "type": "input"
             },
        "Appen Entity":
            {"xpath": APPEN_ENTITY,
             "type": "dropdown"
             },
        "PII Data collected":
            {"xpath": PII_DATA_COLLECTED,
             "type": "dropdown"
             },
        "Countries collecting data":
            {"xpath": COUNTRY_COLLECT_DATA,
             "type": "dropdown"
             },
        "PII Third party":
            {"xpath": PII_THIRD_PARTY,
             "type": "checkbox"
             },
        "Program DPO contact email":
            {"xpath": DPO_CONTACT_EMAIL,
             "type": "input"
             },
        "Program full legal name":
            {"xpath": LEGAL_NAME,
             "type": "input"
             },
        "Program country":
            {"xpath": CUSTOMER_COUNTRY,
             "type": "dropdown"
             },
        "First name":
            {"xpath": FIRST_NAME,
             "type": "input"
             },
        "Last name":
            {"xpath": LAST_NAME,
             "type": "input"
             },
        "Age":
            {"xpath": AGE,
             "type": "input"
             },
        "Email address":
            {"xpath": EMAIL_ADDRESS,
             "type": "input"
             },
        "Gender":
            {"xpath": GENDER,
             "type": "dropdown"
             },
        "Data Collection Consent Form Template":
            {"xpath": CONSENT_FORM,
             "type": "checkbox"
             },
    }

    def __init__(self, project):
        self.project = project
        self.app = project.app

    def fill_out_fields(self, data, index=0):
        self.project.enter_data(data=data, elements=self.elements, index=index)

    def load_project(self, data):
        self.project.load_project(data=data, elements=self.elements)

    def select_resource_type(self, name):
        with allure.step('Select resource type: %s' % name):
            el = find_elements(self.app.driver, "//button[.//span[text()='%s']]" % name)
            assert len(el) > 0, "Button %s has not been found" % name
            el[0].click()

    def save_project_resource(self, is_not=True):
        with allure.step('Click Save project resource'):
            if is_not:
                el = find_elements(self.app.driver, "//div[contains(@class, 'styles_modal')]//button[text()='Save']")
            else:
                el = find_elements(self.app.driver, "//div[contains(@class, 'styles_modal')]//button[text()='Cancel']")

            assert len(el) > 0, "Button Save/Cancel has not been found"
            el[0].click()
            time.sleep(2)

    def get_project_resources(self):
        with allure.step('Get project resources'):
            resources = find_elements(self.app.driver, "//button[text()='Add Resource']/preceding-sibling::div[1]/*")

            result = []
            for resource in resources:
                _resource = resource.find_elements('xpath',".//div")
                _name = _resource[0].find_element('xpath',".//label").text
                _access = _resource[1].text
                result.append({"name": _name, "access":_access})

            return result

    def __find_project_resource(self, project_type, project_name):
        # _res = find_elements(self.app.driver, "//button[text()='Add Resource']/preceding-sibling::div[1]//div["
        #                                       ".//span[text()='%s'] and .//label[contains(text(),'%s')]]" % (
        #     project_type, project_name))
        _res = find_elements(self.app.driver, "//label[contains(., '%s')][.//span[text()='%s']]/../.." %(project_name, project_type))
        if len(_res) == 0:
            _res = find_elements(self.app.driver,f"//label[text()[1]=' | ' and contains(text()[2],'{project_name}')][.//span[text()='{str(project_type).upper()}']]/../..")

        assert len(_res)>0, "Resource %s %s has not been found" % (project_type, project_name)
        return _res[0]

    def click_context_menu_project_resource(self, project_type, project_name, menu):
        _res = self.__find_project_resource(project_type, project_name)
        element_to_the_middle(self.app.driver, _res)
        time.sleep(1)
        action = ActionChains(self.app.driver)
        action.move_to_element(_res).pause(2).click().perform()
        time.sleep(1)

        _btn = _res.find_element('xpath',".//*[local-name() = 'svg' and @xmlns]")
        _btn.click()
        time.sleep(1)

        _action = _res.find_element('xpath',".//div[@role='button']//div[text()='%s']" % menu)
        _action.click()
        time.sleep(2)

    def click_user_project_page(self):
        with allure.step('Click user project page'):
            link = find_elements(self.app.driver, "//div[@data-testid and text()='User Project Page']")
            if len(link) > 0:
                link[0].click()
            assert len(link) > 0, "Link user project page not found"
            time.sleep(4)

    def save_consent_form_template(self):
        with allure.step('Save consent form template'):
            find_elements(self.app.driver, "//h2[text()='Data Collection Consent Form Template']/../..//button[text()='Save']")[0].click()

    def select_pii_data(self, span):
        with allure.step('Select pii data'):
            el = find_elements(self.app.driver, "//span[text()='%s']/..//div" % span)
            assert len(el), "span has not been found"
            el[0].click()
            time.sleep(1)

    def select_data_from_third_party(self, label):
        with allure.step('Select data from third party'):
            el = find_elements(self.app.driver, "//label[text()='%s']/..//div//div" % label)
            assert len(el), "Field 1 has not been found"
            el[0].click()
            time.sleep(2)