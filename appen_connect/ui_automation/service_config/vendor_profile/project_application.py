import time

import allure

from adap.ui_automation.utils.js_utils import mouse_click_element
from adap.ui_automation.utils.selenium_utils import send_keys_by_xpath, click_element_by_xpath, find_elements


class ProjectApplication:
    '''
    created for Yukon project
    '''
    GMAIL_ADDRESS = "//input[@name='gmailAddress']"
    RETYPE_GMAIL_ADDRESS = "//input[@name='retypeGmailAddress']"
    DO_YOU_USE_GMAIL_FOR_FAMILY = "//h5[text()='Is the email address listed above the one you use most often to " \
                                  "communicate with friends and family?']//following-sibling::label[.//div[text()='{" \
                                  "answer}']]"
    DO_YOU_USE_WEB_HISTORY = "//h5[text()='Do you have google web history enabled?']//following-sibling::" \
                             "label[.//div[text()='{answer}']]"

    HOW_OFTEN_USE_GMAIL = "//div[@data-baseweb='select']//*[local-name()='svg']/.."
    GMAIL_VERIFICATION_CODE = "//input[@name='verificationCode']"
    HOW_LONG_HAVE_YOU_LIVE_IN_COUNTRY = "//div[@data-baseweb='select']//*[local-name()='svg']/.."
    DO_YOU_HAVE_TRANSLATION_EXR = "//h5[text()='Do you have any translation experience (professionally or " \
                                  "non-professionally)?']//following-sibling::" \
                                  "label[.//div[text()='{answer}']]"
    CURRENT_COMPANY = "//input[@name='companyName']"


    def __init__(self, project):
        self.project = project
        self.app = project.app
        self.driver = self.app.driver

    def input_required_info(self, gmail=None,
                              retype_gmail=None,
                              do_you_use_gmail_with_family=None,
                              how_often_do_you_use_gmail=None,
                              web_history_enabled=None):
        with allure.step('Provide required data for gmail account'):

            if gmail:
                send_keys_by_xpath(self.driver, self.GMAIL_ADDRESS, gmail)

            if retype_gmail:
                send_keys_by_xpath(self.driver, self.RETYPE_GMAIL_ADDRESS, retype_gmail)

            if do_you_use_gmail_with_family:
                click_element_by_xpath(self.driver,
                                       self.DO_YOU_USE_GMAIL_FOR_FAMILY.format(answer=do_you_use_gmail_with_family))

            if web_history_enabled:
                click_element_by_xpath(self.driver,
                                       self.DO_YOU_USE_WEB_HISTORY.format(answer=web_history_enabled))

            if how_often_do_you_use_gmail:
                click_element_by_xpath(self.driver,
                                       self.HOW_OFTEN_USE_GMAIL)

                # time.sleep(1)
                # click_element_by_xpath(self.driver,
                #                        self.HOW_OFTEN_USE_GMAIL)

                el = find_elements(self.driver,f"//div[text()='{how_often_do_you_use_gmail}']")
                mouse_click_element(self.driver, el[0])

    def input_gmail_verification_code(self, code, action=None):
        with allure.step('Provide GMAIL verification code'):
            send_keys_by_xpath(self.driver, self.GMAIL_VERIFICATION_CODE, code)

            if action:
                self.app.navigation.click_btn('Submit')


    def input_additional_info(self,
                              how_long_do_you_live_in_country=None,
                              translation_exp=None,
                              current_company=None):
        with allure.step('Provide additional info'):

            if how_long_do_you_live_in_country:
                click_element_by_xpath(self.driver,
                                       self.HOW_LONG_HAVE_YOU_LIVE_IN_COUNTRY)

                el = find_elements(self.driver, f"//div[text()='{how_long_do_you_live_in_country}']")
                mouse_click_element(self.driver, el[0])

            if translation_exp:
                click_element_by_xpath(self.driver,
                                       self.DO_YOU_HAVE_TRANSLATION_EXR.format(answer=translation_exp))

            if current_company:
                send_keys_by_xpath(self.driver, self.CURRENT_COMPANY, current_company)










