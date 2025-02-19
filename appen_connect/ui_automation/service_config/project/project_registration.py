import allure

from appen_connect.ui_automation.service_config.project.process import Process, element_to_the_middle
from adap.ui_automation.utils.selenium_utils import *


class Registration(Process):
    # XPATH
    REGISTRATION_PROCESS = "//input[@name='registrationProcessTemplate']"
    QUALIFICATION_PROCESS = "//input[@name='qualificationProcessTemplate']"

    elements = {
        "Select Registration process":
            {"xpath": REGISTRATION_PROCESS,
             "type": "dropdown"
             },
        "Select Qualification process":
            {"xpath": QUALIFICATION_PROCESS,
             "type": "dropdown"
             }
    }

    def __init__(self, project):
        super().__init__(project)
        self.project = project
        self.app = project.app

    def fill_out_fields(self, data):
        self.project.enter_data(data=data, elements=self.elements)

    def load_project(self, data):
        self.project.load_project(data=data, elements=self.elements)

    def _get_current_process_name(self, process_type):
        process = find_elements(self.app.driver, "//label[text()='Select %s process']/..//div[text()]"  %process_type)
        assert len(process), "Process has not been found"
        process_name = process[0].text

        modules = find_elements(self.app.driver, "//label[text()='%s']/..//div[text() and @data-testid]" % process_name)
        _modules = [m.text for m in modules]

        created = find_elements(self.app.driver,
                                "//label[text()='%s']/..//div[text() and not (@data-testid)]" % process_name)
        _created_by = created[0].text

        return {"name": process_name,
                "modules": _modules,
                "created": _created_by}

    def get_current_registration_process_info(self):
        with allure.step('Get info about current registration process'):
            return self._get_current_process_name("Registration")

    def get_current_qualification_process_info(self):
        with allure.step('Get info about current qualification process'):
            return self._get_current_process_name("Qualification")

    def click_gear_menu_item_for_process(self, process_name, process_type, menu_action):
        with allure.step('Click gear menu for process'):
            process = find_elements(self.app.driver, "//div[text()='%s']/..//label[text()='%s']/.."% (process_type, process_name))
            element_to_the_middle(self.app.driver, process[0])
            action = ActionChains(self.app.driver)
            action.click(process[0]).pause(2).perform()

            gear = process[0].find_elements('xpath',
                ".//div[contains(@class, 'registration_and_qualification_process_steps_actions')]//*[local-name() = 'svg']/..")

            # element_to_the_middle(self.app.driver, gear)
            assert len(gear)
            action.click(gear[0]).perform()
            action.pause(2).perform()
            time.sleep(2)
            print(process[0].get_attribute('innerHTML'))
            menu = process[0].find_elements('xpath',".//div[@role='button'][.//div[text()='%s']]" % menu_action)
            assert len(menu) > 0, "%s button has not been found" % menu_action
            action.click(menu[0]).perform()
            action.pause(2).perform()
            time.sleep(2)

            try:
                self.app.navigation.click_btn('Proceed')
            except:
                print("No Proceed btn")


    def click_preview_process(self, process_type):
        process = find_elements(self.app.driver, "//label[text()='Select %s process']/..//div[text()]" % process_type)
        assert len(process), "Process has not been found"
        process_name = process[0].text

        el = find_elements(self.app.driver, "//label[text()='%s']/..//button[text()='Preview Process']" % process_name)
        assert len(el) > 0, "Button %s has not been found"
        el[0].click()