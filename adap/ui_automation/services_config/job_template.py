import time
import allure
from adap.ui_automation.utils.selenium_utils import find_element, find_elements
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys


class JobTemplate:
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def create_new_template(self, title, description, source_job_id, data_file, invalid_source_job_id=False, input_optional=None, out_optional=None, use_cases_optional=None, tags_optional=None):
        with allure.step('Create new template'):
            self.app.navigation.click_btn('Create New Template')
            time.sleep(2)
            title_field = find_element(self.app.driver, "//input[@name='title']")
            title_field.send_keys(title)
            description_field = find_element(self.app.driver, "//textarea[@name='description']")
            description_field.send_keys(description)
            if input_optional is not None:
                input_field = find_element(self.app.driver, "//textarea[@name='input']")
                input_field.send_keys(input_optional)
            if out_optional is not None:
                out_field = find_element(self.app.driver, "//textarea[@name='output']")
                out_field.send_keys(out_optional)

            source_job_id_field = find_element(self.app.driver, "//input[@name='jobid']")
            source_job_id_field.send_keys(source_job_id, Keys.RETURN)
            time.sleep(3)
            if invalid_source_job_id:
                error_message = find_elements(self.app.driver, "//input[@name='jobid']/following-sibling::div")
                assert len(error_message) > 0, "error message not found, it should show invalid id or template"
                return error_message[0].text
            else:
                # ToDo, add some optional fields
                # access_restriction_fields = find_elements(self.app.driver, "//div[@class='Select-value']//span")
                # access_restriction_fields[0].click()
                if use_cases_optional is not None:
                    self.app.navigation.click_checkbox_by_text(use_cases_optional)

                if tags_optional is not None:
                    self.app.navigation.click_checkbox_by_text(tags_optional)

                # upload csv data file
                self.app.job.data.upload_file(data_file, wait_time=10)
                error = find_elements(self.driver, "//div[contains(text(),'There was an error uploading Example Data.')]")
                if len(error) > 0:
                    assert False, f"Uploading file {data_file} failed"
                self.app.navigation.click_btn('Save')
                time.sleep(3)
                return self.app.driver.current_url

    def edit_job_template(self, new_title=None, new_description=None, new_source_job_id=None, input_optional=None, out_optional=None, delete_data_file=False):
        with allure.step('Edit job template'):
            if new_title is not None:
                title_field = find_element(self.app.driver, "//input[@name='title']")
                title_field.clear()
                time.sleep(1)
                title_field.send_keys(new_title)
                time.sleep(1)
            if new_description is not None:
                description_field = find_element(self.app.driver, "//textarea[@name='description']")
                description_field.clear()
                time.sleep(1)
                description_field.send_keys(new_description)
                time.sleep(1)
            if new_source_job_id is not None:
                source_job_id_field = find_element(self.app.driver, "//input[@name='jobid']")
                source_job_id_field.clear()
                time.sleep(1)
                source_job_id_field.send_keys(new_source_job_id, Keys.RETURN)
                time.sleep(1)
            if input_optional is not None:
                input_field = find_element(self.app.driver, "//textarea[@name='input']")
                input_field.clear()
                time.sleep(1)
                input_field.send_keys(input_optional)
                time.sleep(1)
            if out_optional is not None:
                out_field = find_element(self.app.driver, "//textarea[@name='output']")
                out_field.clear()
                time.sleep(1)
                out_field.send_keys(out_optional)
                time.sleep(1)
            if delete_data_file:
                delete_icon = find_element(self.app.driver,
                                           "//label[text()='Example data']/..//a[not(text())]//*[local-name() = 'svg']")
                delete_icon.click()
                time.sleep(2)

            self.app.navigation.click_btn('Save')
            time.sleep(3)

    def change_template_order(self, index1, index2):
        with allure.step('Change template order'):
            self.app.navigation.click_btn('Change Template Order')
            time.sleep(2)
            self.app.verification.current_url_contains('/job_templates/reorder')
            el = find_elements(self.driver, "//td[contains(@class,'b-JobTemplatesListReorder__table-cell')]")
            action = ActionChains(self.driver)
            # looks like hold does not take effect
            action.click_and_hold(el[index1]).pause(2).move_to_element(el[index2]).release().perform()
            time.sleep(3)

    def click_breadcrumb_link(self, link_name):
        with allure.step('Click breadcrumb link'):
            el = find_elements(self.driver, "//header//a[text()='%s']" % link_name)
            assert len(el) > 0, "link with name %s is not found" % link_name
            el[0].click()
            time.sleep(2)

    def click_edit_template_link(self):
        with allure.step('Click edit template link'):
            el = find_elements(self.driver, "//a[contains(@href,'/edit')]//*[local-name() = 'svg']")
            assert len(el) > 0, "edit template link is not found is not found"
            el[0].click()
            time.sleep(2)

    def get_job_template_title(self):
        with allure.step('Get job template title'):
            title = find_element(self.app.driver, "//input[@name='title']")
            return title.get_attribute('value')

    def get_job_template_description(self):
        with allure.step('Get job template description'):
            description = find_element(self.app.driver, "//textarea[@name='description']")
            return description.text

    def get_job_template_input(self):
        with allure.step('Get job template input'):
            input_field = find_element(self.app.driver, "//textarea[@name='input']")
            return input_field.text

    def get_job_template_output(self):
        with allure.step('Get job template output'):
            output_field = find_element(self.app.driver, "//textarea[@name='output']")
            return output_field.text

    def get_job_template_source_job_id(self):
        with allure.step('Get job template source job id'):
            source_job_id = find_element(self.app.driver, "//input[@name='jobid']")
            return source_job_id.get_attribute('value')

    def get_example_data_file_name(self):
        with allure.step('Get example data file name'):
            el = find_elements(self.app.driver, "//div[@class='b-JobTemplateForm__csv-link']//a")
            assert len(el) > 0, "example data file name not found"
            return el[0].text

    def click_delete_icon_for_template_title(self, template_title):
        with allure.step('Delete template with title %s' % template_title):
            template = find_elements(self.driver,
                                     "//div[./p[@title]][.//div[text()='%s']]" % template_title)
            assert len(template) > 0, "link with name %s is not found" % template_title
            actions = ActionChains(self.driver)
            actions.move_to_element(template[0]).perform()
            time.sleep(2)
            del_btn = template[0].find_elements('xpath',
                ".//img/following-sibling::div//a[2]//*[local-name() = 'svg']")
            actions.move_to_element(del_btn[0]).pause(2).click().perform()
            time.sleep(1)

    def find_job_template_by_tile(self, template_title):
        with allure.step('Find job template with title %s' % template_title):
            template = find_elements(self.driver,
                                     "//div[./p[@title]][.//div[text()='%s']]" % template_title)
            return len(template) > 0