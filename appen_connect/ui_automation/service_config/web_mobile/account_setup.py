import time

import allure
from selenium.webdriver import ActionChains, Keys

from adap.ui_automation.utils.js_utils import scroll_to_page_bottom
from adap.ui_automation.utils.selenium_utils import click_element_by_xpath, scroll_to_element_by_action, find_elements, \
    send_keys_by_xpath, get_attribute_by_xpath, send_keys_and_select_by_xpath


class AccountSetupPage:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    ADULT_CERTIFY_CHECKBOX = "//input[@name='adultCertify']/../span"
    TAX_DOCUMENTATION_CHECKBOX = "//input[@name='taxDocumentation']/../span"
    BACK_BUTTON = "//div[text()='Back']/.."
    DECLINE_POPUP_TEXT = "//div[contains(@class, 'styles__DeclineModalContainer')]//p"

    @allure.step("Click on adult certify checkbox")
    def confirm_adult_certify(self):
        click_element_by_xpath(self.driver, self.ADULT_CERTIFY_CHECKBOX)

    @allure.step("Click on tax documentation checkbox")
    def confirm_tax_documentation(self):
        click_element_by_xpath(self.driver, self.TAX_DOCUMENTATION_CHECKBOX)

    @allure.step("Get state of back button")
    def get_element_state(self, element):
        back_btn = find_elements(self.driver, element)
        return back_btn[0]

    @allure.step("Get text from Decline Modal ")
    def get_text_from_decline_modal(self):
        text_els = find_elements(self.driver, self.DECLINE_POPUP_TEXT)
        return text_els


class AboutYouPage:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.action = ActionChains(self.driver)

    PRIMARY_LANGUAGE = "//input[@id='primaryLanguage']"
    LANGUAGE_REGION = "//input[@id='languageRegion']"
    SOCIAL_MEDIA_CHOICE = "//div[@class='collapsibleFieldContainer']//input[contains(@name,'%s')]/../span"
    BUSINESS_NAME_CHOICE = "//div[@class='collapsibleFieldContainer']//input[@name='hasBusinessName']/../div"
    OPTIONAL_INPUT = "//input[contains(@name,'%s')]"
    LANGUAGE_REGION_TEXT = LANGUAGE_REGION + "/../../div"
    ERROR_MSG = "//div[contains(@class, 'styles__ErrorContainer')]/p"

    @allure.step("Set primary language")
    def set_primary_language(self, pr_language, index=0):
        primary_lan = find_elements(self.driver, self.PRIMARY_LANGUAGE)
        assert primary_lan, f'Input for select primary language absent: {primary_lan}'
        self.action.click(primary_lan[index]).send_keys(pr_language).send_keys(Keys.ENTER).perform()
        time.sleep(1)

    @allure.step("Set region language")
    def set_region_language(self, rg_language):
        region_lan = find_elements(self.driver, self.LANGUAGE_REGION)
        assert region_lan, 'Input for select region language absent'
        self.action.click(region_lan[0]).send_keys(rg_language).send_keys(Keys.ENTER).perform()
        time.sleep(1)


    @allure.step("Check optional choice")
    def check_social_media(self, social_media_choice):
        click_element_by_xpath(self.driver, self.SOCIAL_MEDIA_CHOICE % social_media_choice)

    @allure.step("Check business name")
    def check_business_name(self):
        click_element_by_xpath(self.driver, self.BUSINESS_NAME_CHOICE)

    @allure.step("Set info for optional choice")
    def set_optional_info(self, optional_choice_input, optional_info):
        send_keys_by_xpath(self.driver, self.OPTIONAL_INPUT % optional_choice_input, optional_info)

    @allure.step("Get language region value")
    def get_region_language_text(self):
        rg_language_text = find_elements(self.driver, self.LANGUAGE_REGION_TEXT)
        assert rg_language_text, "The value for language region Not present"
        return rg_language_text[0].text

    @allure.step("Get error message")
    def get_error_message(self):
        error_ms_els = find_elements(self.driver, self.ERROR_MSG)
        assert error_ms_els, "Error message not present on page"
        return error_ms_els

    @allure.step("Get optional field (social media, business name)")
    def get_optional_field(self, optional_choice_name):
        optional_field = find_elements(self.driver, self.OPTIONAL_INPUT % optional_choice_name)
        return optional_field

    @allure.step("Get value of optional field (social media, business name)")
    def get_optional_field_value(self, optional_choice_name):
        assert self.get_optional_field(optional_choice_name), f"The optional filed for {optional_choice_name} Not present on page"
        return self.get_optional_field(optional_choice_name)[0].get_attribute("value")


class ContactPage:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    COUNTRY_LIVE = "//input[@id='country']"
    STATE = "//input[@id='state']"
    FULL_ADDRESS = "//input[@id='address']"
    CITY = "//input[@id='city']"
    ZIP_CODE = "//input[@id='zip']"
    PHONE = "//input[@id='primaryPhone']"
    EMAIL_NOTIFICATION_BUTTON = "//input[@name='emailNotification']/../div"
    COUNTRY_FLAG = "//div[@class='selected-flag']"
    FINISH_BTN = "//div[text()='Finish']/.."

    @allure.step("Set country in which live")
    def set_country_live(self, country):
        send_keys_and_select_by_xpath(self.driver, self.COUNTRY_LIVE, country)

    @allure.step("Set state/province")
    def set_state(self, state):
        send_keys_and_select_by_xpath(self.driver, self.STATE, state)

    @allure.step("Set full address")
    def set_full_address(self, address):
        send_keys_by_xpath(self.driver, self.FULL_ADDRESS, address)

    @allure.step("Set city")
    def set_city(self, city):
        send_keys_by_xpath(self.driver, self.CITY, city)

    @allure.step("Set zip/postal code")
    def set_zip_code(self, zip_code):
        send_keys_by_xpath(self.driver, self.ZIP_CODE, zip_code)

    @allure.step("Set mobile phone number")
    def set_mobile_phone(self, phone_number):
        send_keys_by_xpath(self.driver, self.PHONE, phone_number)

    @allure.step("Check receive email ")
    def check_receive_email(self):
        click_element_by_xpath(self.driver, self.EMAIL_NOTIFICATION_BUTTON)

    @allure.step("Get phone number value")
    def get_phone_number_value(self):
        return get_attribute_by_xpath(self.driver, self.PHONE, 'value')

    @allure.step("Get mobile phone country flag")
    def get_mobile_phone_flag(self):
        return get_attribute_by_xpath(self.driver, self.COUNTRY_FLAG, 'title')

    @allure.step("Get contact field value")
    def get_contact_field_value(self, field):
        return get_attribute_by_xpath(self.driver, field, 'value')





class ContributorExperienceAccountSetup:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.account_setup_page = AccountSetupPage(self)
        self.about_you_page = AboutYouPage(self)
        self.contact_page = ContactPage(self)

    def accept_consent(self):
        scroll_to_page_bottom(self.app.driver)
        self.account_setup_page.confirm_adult_certify()
        self.account_setup_page.confirm_tax_documentation()
        self.app.navigation.click_btn("Accept & Continue")

    def verify_back_btn_state(self, state="disabled"):
        value = self.account_setup_page.get_element_state(self.account_setup_page.BACK_BUTTON).get_property(state)
        return value

    def grab_text_from_pop_up(self):
        return " ".join(text_el.text for text_el in self.account_setup_page.get_text_from_decline_modal())

    def set_about_you_info(self, primary_lg, region_lg):
        self.about_you_page.set_primary_language(primary_lg)
        self.about_you_page.set_region_language(region_lg)

    def verify_state_of_element(self, state, element):
        value = self.account_setup_page.get_element_state(element).get_property(state)
        return value

    def set_business_name(self, business_name):
        self.about_you_page.check_business_name()
        self.about_you_page.set_optional_info("businessName", business_name)

    def set_social_media(self, social_media, social_media_url):
        self.about_you_page.check_social_media(social_media)
        self.about_you_page.set_optional_info(social_media.lower(), social_media_url)

    def set_contact_info(self, user, receive_mail=False):
        self.contact_page.set_country_live(user['country'])
        self.contact_page.set_state(user['state'])
        self.contact_page.set_full_address(user['address'])
        self.contact_page.set_zip_code(user['zipcode'])
        self.contact_page.set_mobile_phone(user['phone_number'])
        self.contact_page.set_city(user['city'])
        if receive_mail:
            self.contact_page.check_receive_email()





