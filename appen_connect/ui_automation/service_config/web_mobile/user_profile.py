import time

import allure

from adap.ui_automation.utils.js_utils import scroll_to_element, scroll_to_page_bottom
from adap.ui_automation.utils.selenium_utils import find_elements, click_element_by_xpath, find_element, \
    send_keys_by_xpath, get_text_by_xpath, get_attribute_by_xpath, click_and_send_keys_by_xpath, \
    send_keys_and_select_by_xpath
from appen_connect.ui_automation.service_config.web_mobile.ui_components import select_dropdown_option


class ContributorExperienceProfile:
    TAB = "//div[@id and text()='{}']"

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.languages = Languages(self)
        self.more_about_me = MoreAboutMe(self)
        self.personal_info = PersonalInfo(self)
        self.settings = Setting(self)

    def open_tab(self, tab_name):
        with allure.step("Open Profile tab"):
            click_element_by_xpath(self.driver, self.TAB.format(tab_name))
            time.sleep(3)

    def get_user_info(self):
        with allure.step("Get user info"):
            full_name = get_text_by_xpath(self.driver, "//div[contains(@class, 'styles__PrimaryHeaderContaine')]//h2")
            email = get_text_by_xpath(self.driver,
                                      "//div[contains(@class, 'styles__PrimaryHeaderContaine')]//div[text()]")
            region = get_text_by_xpath(self.driver,
                                       "//div[contains(@class, 'styles__SecondaryHeaderContainer')]//div[text()][1]")
            locale = get_text_by_xpath(self.driver,
                                       "//div[contains(@class, 'styles__SecondaryHeaderContainer')]//div[text()][2]")

            return {
                "full_name": full_name,
                "email": email,
                "region": region,
                "locale": locale
            }


class Languages:
    LOCALE_LANGUAGE = "//input[contains(@name,'language_')]/.."
    LANGUAGE_REGION = "//input[contains(@name,'region_')]/.."
    SPOKEN_FLUENCY = "//input[contains(@name,'spokenFluency_')]/.."
    WRITTEN_FLUENCY = "//input[contains(@name,'writtenFluency_')]/.."
    EDIT = "//h4[text()='{}']/..//a[text()='Edit']"
    FROM_LANGUAGE = "//input[contains(@name,'fromLanguage_')]/.."
    TO_LANGUAGE = "//input[contains(@name,'toLanguage_')]/.."
    REVERSE = "//input[contains(@name,'reversePair_')]/.."

    def __init__(self, profile):
        self.app = profile.app
        self.driver = self.app.driver

    def _enter_language_data(self,
                             locale_lang=None,
                             lang_region=None,
                             spoken_fluency=None,
                             writen_fluency=None,
                             index=0):

        if locale_lang:
            select_dropdown_option(self.driver, self.LOCALE_LANGUAGE, locale_lang, index=index)
        if lang_region:
            select_dropdown_option(self.driver, self.LANGUAGE_REGION, lang_region, index=index)
        if spoken_fluency:
            select_dropdown_option(self.driver, self.SPOKEN_FLUENCY, spoken_fluency, index=index)
        if writen_fluency:
            select_dropdown_option(self.driver, self.WRITTEN_FLUENCY, writen_fluency, index=index)

    def add_additional_language(self, locale_lang=None,
                                lang_region=None,
                                spoken_fluency=None,
                                writen_fluency=None,
                                action=None):
        with allure.step("Add additional Language"):
            # find index
            count_existing_languages = len(find_elements(self.driver, "//h4[contains(text(),'Language')]"))
            self.app.navigation.click_btn('New Language')
            time.sleep(1)
            scroll_to_page_bottom(self.driver)

            self._enter_language_data(locale_lang, lang_region, spoken_fluency, writen_fluency,
                                      count_existing_languages)

            if action:
                self.app.navigation.click_btn(action)

    def get_additional_languages(self):
        with allure.step("Get additional Languages"):
            languages = find_elements(self.driver,
                                      "//h4[text()='Additional Languages']/..//div[contains(@class,'styles__ItemContainer')]")
            result = {}
            for lang in languages:
                title = lang.find_element('xpath', ".//h5").text
                lang_data = lang.find_elements('xpath', './/div[@data-baseweb]')
                language = lang_data[0].text
                spoken = lang_data[1].text
                written = lang_data[2].text

                result[title] = {
                    "locale_language": language,
                    "spoken": spoken,
                    "written": written
                }

            return result

    def click_edit_section(self, section):
        with allure.step(f"Click Edit {section}"):
            click_element_by_xpath(self.driver, self.EDIT.format(section))

    def delete_additional_language(self, index):
        with allure.step("Delete additional language"):
            delete_icon = '//h4[contains(text(), "Language")]/..//img'
            click_element_by_xpath(self.driver, delete_icon, index=index - 1)

    def edit_additional_language(self, index,
                                 locale_lang=None,
                                 lang_region=None,
                                 spoken_fluency=None,
                                 writen_fluency=None,
                                 action=None):
        with allure.step("Edit additional lang info"):
            self._enter_language_data(locale_lang, lang_region, spoken_fluency, writen_fluency, index - 1)

            if action:
                self.app.navigation.click_btn(action)

    def add_translation_experience(self, from_lang=None, to_lang=None, reverse=False, action=None):
        with allure.step("Add translation experience"):
            count_existing_experience = len(find_elements(self.driver, "//h4[contains(text(),'Translation Pair ')]"))
            self.app.navigation.click_btn('Translation Pair')

            self._enter_translation_experience(from_lang=from_lang, to_lang=to_lang, reverse=reverse,
                                               index=count_existing_experience)
            if action:
                self.app.navigation.click_btn(action)

    def get_translation_experience(self):
        with allure.step("Get translation experience"):
            experiences = find_elements(self.driver,
                                        "//h4[text()='Translation Experience']/..//div[contains(@class,'styles__ItemContainer')]")
            result = {}
            for ex in experiences:
                title = ex.find_element('xpath', ".//h5").text
                tr_ex_data = ex.find_elements('xpath', './/div[@data-baseweb]')
                from_tr_ex = tr_ex_data[0].text
                to_tr_ex = tr_ex_data[1].text
                # reverse - TBD
                result[title] = {
                    "from_language": from_tr_ex,
                    "to_language": to_tr_ex
                }
            return result

    def delete_translation_experience(self, index):
        with allure.step("Delete translation experience"):
            delete_icon = '//h4[contains(text(), "Translation Pair")]/..//img'
            click_element_by_xpath(self.driver, delete_icon, index=index - 1)

    def _enter_translation_experience(self, from_lang=None, to_lang=None, reverse=False, index=0):
        if from_lang:
            select_dropdown_option(self.driver, self.FROM_LANGUAGE, from_lang, index=index)

        if to_lang:
            select_dropdown_option(self.driver, self.TO_LANGUAGE, to_lang, index=index)

        if reverse:
            click_element_by_xpath(self.driver, self.REVERSE)

    def edit_translation_experience(self, from_lang=None, to_lang=None, reverse=False, index=0, action=None):
        with allure.step("Edit translation experience"):
            self._enter_translation_experience(from_lang, to_lang, reverse, index - 1)
            if action:
                self.app.navigation.click_btn(action)


class MoreAboutMe:

    def __init__(self, profile):
        self.app = profile.app
        self.driver = self.app.driver

    def click_edit_answers_for_category(self, category):
        with allure.step(f"Click Edit for category: {category}"):
            click_element_by_xpath(self.driver, f"//h4[text()='{category}']/..//a[text()='Edit']")

    def get_progress_for_category(self, category):
        with allure.step(f"Get progress for category:{category}"):
            el_category = find_elements(self.driver, f'//h4[text()="{category}"]/..')
            data = el_category[0].find_elements('xpath', ".//div[text()]")
            return {"questions": data[0].text,
                    'progress': data[1].text}

    def get_all_questions_for_category(self):
        with allure.step(f"Get all questions for category "):
            result = []
            questions = find_elements(self.driver, "//div[./label and contains(@class, 'styles__Container')]")
            for q in questions:
                title = q.find_elements('xpath', './/label')
                result.append(title[0].text)

            return result

    def answer_question(self, question, answers, question_type='radio_btn', action=None):
        with allure.step('Answer Profile question: %s' % question):
            q_el = find_elements(self.driver,
                                 '//div[contains(@class,"styles__Container")]//label[contains(text(),"%s")]/..' % question)
            assert len(q_el) > 0, "Question %s has not been found"

            scroll_to_element(self.driver, q_el[0])
            time.sleep(1)

            if question_type == 'radio_btn':
                for ans in answers:
                    _answ = q_el[0].find_elements('xpath', ".//div[contains(text(),'%s')]" % ans)
                    assert len(_answ) > 0, "Answer %s has not been found" % ans
                    _answ[0].click()

            if question_type == 'checkbox':
                for ans in answers:
                    _answ = q_el[0].find_elements('xpath', ".//h5[text()='%s']" % ans)
                    assert len(_answ) > 0, "Answer %s has not been found" % ans
                    _answ[0].click()

            if question_type == 'input_field':
                _answ = q_el[0].find_elements('xpath', ".//input")
                assert len(_answ) > 0, "Answer %s has not been found" % ans
                _answ[0].clear()
                _answ[0].send_keys(answers)

            if question_type == 'date_picker':
                pass

            if question_type == 'dropdown':
                select_dropdown_option(self.driver,
                                       "//div[contains(@class,'styles__Container')]//label[text()='%s']/..//input/.." % question,
                                       answers)

            if action:
                self.app.navigation.click_btn(action)
            time.sleep(1)

    def get_all_categories(self):
        with allure.step("Get all categories"):
            els = find_elements(self.driver, '//h4')
            return [x.text for x in els]


class PersonalInfo:
    EDIT = "//h4[text()='{}']/..//a[text()='Edit']"
    PHONE = "//input[@id='primaryPhone']"

    def __init__(self, profile):
        self.app = profile.app
        self.driver = self.app.driver

    def get_user_personal_info(self):
        with allure.step("Get user personal info"):
            result = {}
            contact_section = find_element(self.driver, "//h4[text()='Contact']/..")
            elements = [x.text for x in contact_section.find_elements("xpath", ".//div[@data-baseweb]")]
            result['contact'] = elements

            social_media_section = find_element(self.driver, "//h4[text()='Social Media']/..")
            elements_social = social_media_section.find_elements("xpath", ".//div[@data-baseweb]")
            facebook = elements_social[0].text
            instagram = elements_social[1].text
            twitter = elements_social[2].text
            linkedin = elements_social[3].text
            result['social_media'] = {
                'facebook': facebook,
                'instagram': instagram,
                'twitter': twitter,
                'linkedin': linkedin,
            }

            return result

    def click_edit_section(self, section):
        with allure.step(f"Click Edit {section}"):
            click_element_by_xpath(self.driver, self.EDIT.format(section))

    def enter_phone_number(self, number, action=None):
        with allure.step("Enter phone number"):
            print("enter ", number)
            send_keys_by_xpath(self.driver, self.PHONE, number, clear_current=True, mode='keys')
            if action:
                self.app.navigation.click_btn(action)

    def get_phone_number(self):
        with allure.step("Get phone number"):
            return get_attribute_by_xpath(self.driver, self.PHONE, 'value')

    def get_home_address(self):
        with allure.step("Get home address"):
            results = {}
            # home_address_section = find_element(self.driver, "//h4[text()='Home Address']/..")
            field_xpath = "//input[@id='{}']/../preceding-sibling::div"
            fields = ['country', 'state', 'address', 'city', 'zip']

            for field in fields:
                if field in ['country', 'state']:
                    value = find_element(self.driver, field_xpath.format(field)).text
                else:
                    value = find_element(self.driver, "//input[@id='{}']".format(field)).get_attribute('value')

                results[field] = value

            return results

    def enter_social_media(self, data, action=None):
        with allure.step("Enter social media"):
            for key, value in data.items():
                send_keys_by_xpath(self.driver, f"//input[@id='{key}']", value)

            if action:
                self.app.navigation.click_btn(action)


class Setting:
    def __init__(self, profile):
        self.app = profile.app
        self.driver = self.app.driver

    def get_notifications(self):
        with allure.step("Get current Notifications"):
            notifications = find_elements(self.driver,
                                          "//h4[text()='Notifications']/..//h5")
            result = {}
            for row in notifications:
                title = row.text
                value = row.find_element('xpath', './following-sibling::div').text
                result[title] = value

            return result

    def enable_notification(self, recruitment=None, community_updates=None, action=None):
        with allure.step("Enable notification"):
            if recruitment:
                click_element_by_xpath(self.driver, "//input[@name='recruitment.email']/..")

            if community_updates:
                click_element_by_xpath(self.driver, "//input[@name='community.email']/..")

            if action:
                self.app.navigation.click_btn(action)




