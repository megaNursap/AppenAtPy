import time

import allure

from adap.ui_automation.utils.js_utils import get_text_excluding_children
from adap.ui_automation.utils.selenium_utils import find_elements


class Scripts:

    def __init__(self, app):
        self.app = app
        self.driver = app.driver

    def open_scripts_tab(self, tab_name):
        with allure.step('Open scripts tab: %s' % tab_name):
            el = find_elements(self.driver, "//li[.//*[text()='%s']]" % tab_name)
            assert len(el), "Tab %s has not been found" % tab_name
            el[0].click()
            time.sleep(1)

    def get_page_header(self):
        with allure.step('Get Scripts page header'):
            el = find_elements(self.driver, "//h3")
            value = get_text_excluding_children(self.driver, el[1])
            if len(el) == 0: return ''
            return value

    def get_scripts(self):
        with allure.step('Get all scripts on the page' ):
            scripts = find_elements(self.driver, "//div[contains(@class=,'b-CatalogPageLayout__cards')]//div[@class='b-ScriptCard']")
            result = []
            for script in scripts:

                name = script.find_element('xpath',".//div[@class='b-ScriptCard__name']").text
                description = script.find_element('xpath',".//div[@class='b-ScriptCard__description']").text
                tag = script.find_element('xpath',".//div[@class='b-ScriptCard__tag']").text

                result.append({
                    "name":name,
                    "description": description,
                    "tag":tag
                })

            return result

    def open_script_by_name(self, script_name):
        with allure.step('Open script by name: %s' %script_name):
            script = find_elements(self.driver, "//div[text()='%s']/.."  % script_name)
            assert len(script)>0, "Script %s has not been found" % script_name
            script[0].click()

