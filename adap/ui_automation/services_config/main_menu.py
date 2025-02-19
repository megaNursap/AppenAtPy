import time

import allure
from allure_commons.types import AttachmentType

from adap.ui_automation.utils.js_utils import mouse_click_element
from adap.ui_automation.utils.selenium_utils import find_element, find_elements, get_console_log, create_screenshot


class MainMenu:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def open_menu_item(self, item):
        with allure.step('Open menu item: %s' % item):
            # check if there is a tooltip which overlay the menu and close it
            tooltip_locator = \
                "//*[contains(text(),'Choose a job template based on your use case.')]/../../div/a"
            tooltip_we = self.driver.find_elements('xpath',tooltip_locator)
            tooltip_we[0].click() if len(tooltip_we) else None

            find_element(self.driver,
                         "//li//a[contains(@href,'/%s') and not(text())]" % item).click()

            get_console_log(driver=self.driver, method_name="open_menu")
            create_screenshot(self.driver, "open_menu")

    def menu_item_is_disabled(self, item, is_not=False):
        with allure.step('Menu item: %s is disable %s' % (item, is_not)):
            # menu = find_elements(self.driver,
            #                      "//ul[@data-test-id='global-nav']//a[contains(@href,'/%s') and not(text())]" % item)

            menu = find_elements(self.driver,
                                 "//a[contains(@href,'/%s') and not(text())]" % item)

            if not is_not:
                assert len(menu) == 0, "Menu item %s is enabled" % item
            else:
                assert len(menu) > 0, "Menu item %s is disabled" % item

    def home_page(self):
        self.open_menu_item("welcome")

    def jobs_page(self):
        allure.attach(self.app.driver.get_screenshot_as_png(), name="Job Page", attachment_type=AttachmentType.PNG)
        self.app.verification.wait_untill_text_present_on_the_page("Options", 30)
        self.open_menu_item("jobs")
        time.sleep(2)

    def workflows_page(self):
        self.open_menu_item("workflows")

    def models_page(self):
        self.open_menu_item("models")

    def hostedchannels_page(self):
        self.open_menu_item("hosted_channels")

    def analytics_page(self):
        pass

    def scripts_page(self):
        self.open_menu_item("scripts")

    def quality_flow_page(self):
        self.open_menu_item("quality")
        time.sleep(5)

    def account_menu(self, submenu=None):
        with allure.step('Open account menu item: %s' % submenu):
            # el = find_element(self.app.driver, "//div[@data-test-id='account-link']")
            el = find_element(self.app.driver, "//li[.//a[text()='Your Jobs']]/../..")
            # mouse_click_element(self.app.driver, el)
            el.click()
            time.sleep(1)
            if submenu:
                menu_items = find_elements(self.app.driver, "//li[.//a[text()='Your Jobs']]/../..//a[text()='%s']" % submenu)
                if len(menu_items) > 0:
                    menu_items[0].click()
                else:
                    assert False, "Menu %s has not been found" % submenu
            time.sleep(2)

    def sign_out(self):
        with allure.step('Sign Out'):
            find_element(self.app.driver, "//a[text()='Sign Out']").click()
