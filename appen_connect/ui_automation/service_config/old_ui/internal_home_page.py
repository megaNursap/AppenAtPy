import time
import allure

from adap.ui_automation.utils.selenium_utils import find_element, find_elements


class InternalHome:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.navigation = self.app.navigation

    CATEGORY = "//select[@id='template-category']"
    NAME = "//input[@name='templateName']"
    STATEMENT = "//textarea[@name='templateStatement']"
    DESCRIPTION = "//iframe[@class='cke_wysiwyg_frame cke_reset']"
    VIEW_ROLES = ""
    EDIT_ROLES = "//body/div[@id='main']/div[@class='content clear']/form/fieldset[" \
                 "@class='standard-form']/table/tbody/tr[7]/td[1]/span[1]/span[1]/span[1] "

    elements_sql_report = {
        "Category":
            {"xpath": CATEGORY,
             "type": "dropdown"
             },
        "Name":
            {
                "xpath": NAME,
                "type": "input"
            },
        "Statement":
            {
                "xpath": STATEMENT,
                "type": "textarea"
            }
    }

    def fill_out_fields(self, data={}):
        with allure.step('Fill out fields. %s' % data):
          self.app.navigation_old_ui.enter_data_v1(data, self.elements_sql_report)

    def fill_description(self, description):
        with allure.step('Fill in the description - %s' % description):
            self.driver.switch_to.frame(0)
            el = find_elements(self.driver,
                               "//body[@class='cke_editable cke_editable_themed cke_contents_ltr cke_show_borders']")
            if len(el) > 0:
                el[0].send_keys(description)
            time.sleep(3)
            self.driver.switch_to.default_content()

    def search_vendor(self, vendor_id):
        with allure.step('Enter your vendor ID - for your SQL report %s' % vendor_id):
            el = find_elements(self.driver, "//input[@id='search']")
            assert len(el), "Vendor %s has not been found" % vendor_id
            if len(el) > 0:
                el[0].send_keys(vendor_id)
            time.sleep(2)


    def select_vendor_status(self, status):
        with allure.step('Enter your vendor ID - for your SQL report %s' % status):
            el = find_elements(self.driver, "//select[@id='status']")
            assert len(el), "Vendor %s has not been found" % status
            if len(el) > 0:
                el[0].send_keys(status)
            time.sleep(2)

    def click_work_on_project(self, project_name):
        with allure.step('Click "Work This!" for project %s' % project_name):
            el = find_elements(self.driver, "//tr[@data-track-content][.//a[@href and text()='%s']]//a[@onClick]" % project_name)
            assert len(el), "Project %s has not been found" % project_name
            el[0].click()
            time.sleep(2)
            window_after = self.driver.window_handles[1]
            self.app.navigation.switch_to_window(window_after)

    def click_on_adap_task_by_id(self, job_id):
        with allure.step('Open ADAP task by job Id %s' % job_id):
            el = find_elements(self.driver, "//tbody//a[contains(@href, '%s')]" % job_id)
            assert len(el), "Job %s has not been found" % job_id
            el[0].click()
            time.sleep(10)
            window_after = self.driver.window_handles[1]
            self.app.navigation.switch_to_window(window_after)


