import logging
import os
import time

import allure

from adap.api_automation.utils.data_util import get_data_file
from adap.ui_automation.utils.js_utils import enable_element_by
from adap.ui_automation.utils.selenium_utils import go_to_page, get_text_by_xpath, find_elements, \
    click_element_by_xpath, send_keys_by_xpath
from gap.ui_automation.service_config.navigation import Urls

log = logging.getLogger(__name__)


class GProject:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.current_project_name = None
        self.current_projectid = None
        self.current_project_displayid = None
        self.current_project_workflows = []
        self.data_records_batch_list = []


    def gap_project_create_new(self, do_click=True):
        with allure.step("Click on Create new project"):
            self.app.g_nav.open_page_projects()
            btn_value = 'Create new project'
            el = find_elements(self.driver, "//span[contains(text(),'Create new project')]")
            assert len(el) > 0, f"Button {btn_value} not displayed"
            if do_click:
                el[0].click()
            return True


    def gap_project_add_workflow(self, workflow_data):
        self.current_project_workflows.append(workflow_data)


    def gap_project_set_current_id(self, projectid):
        with allure.step(f"Set current projectid to {projectid}"):
            self.current_projectid = projectid


    def gap_project_create_populate_form(self, name, presales, cost_center, customer_code, descr=None, do_submit=True):
        with allure.step("Gap project populate create new/edit form params"):
            # project name
            send_keys_by_xpath(self.driver, "//input[@id='name']", name)
            # presales
            opt_presales_xpath = "//input[@class='ant-radio-input']"
            opt_presales = find_elements(self.driver, opt_presales_xpath)
            assert len(opt_presales) > 1, "opt presales not exist"
            # if 'Yes' in data.get('opt_presales'):
            if presales == 'yes':
                opt_presales[0].click()
            else:
                opt_presales[1].click()
            # cost center
            click_element_by_xpath(self.driver, "//input[@id='costCenter']")
            time.sleep(1)
            click_element_by_xpath(self.driver, f"//*[@title='{cost_center}']")
            send_keys_by_xpath(self.driver, "//input[@id='customerCode']", customer_code)
            # description
            send_keys_by_xpath(self.driver, "//textarea[@id='description']", descr)
            btn_name = 'Submit'
            if not do_submit:
                btn_name = 'Close'
            self.app.g_nav.gap_click_btn(btn_name)


    def gap_project_parse_id_from_current_url(self):
        with allure.step("Parse projectid from current url"):
            current_url = self.driver.current_url
            self.app.g_verify.gap_verify_current_url_contain('data-center', do_assert=True)
            temp = current_url.replace(Urls.URL + Urls.URL_PG_PROJECTS + "/", '')
            self.current_projectid = temp.replace(Urls.URL_PG_PROJECT_DATA_CENTER_PARAMS, '')
            log.info(f"Project id: {self.current_projectid}")
            assert self.current_projectid is not None, "Project id not parsed from url"
            return self.current_projectid


    def get_project_displayid(self):
        with allure.step("Get project displayid"):
            self.current_project_displayid = get_text_by_xpath(self.driver,
                                                               "//div[@class='ant-card-meta-detail']//p[boolean(@title)]")
            log.info(f"Current project displayid: {self.current_project_displayid}")
            assert self.current_project_displayid is not None, "Projectid cannot be None"
            return self.current_project_displayid


    def gap_project_data_record_upload(self, file_path, data_type='LiDAR', button_name='Confirm', do_publish=1):
        with allure.step(f"Upload data {file_path}"):
            file_to_upload = get_data_file(file_path)
            log.debug(f"File path: {file_to_upload}")
            file_name = os.path.basename(file_path)
            log.debug(f"File name: {file_name}")

            click_element_by_xpath(self.driver, "//span[contains(text(),'Origin Data Management')]")
            time.sleep(1)
            click_element_by_xpath(self.driver, "//span[contains(text(),'Append Data')]")
            time.sleep(1)
            get_text_by_xpath(self.driver, "//strong[contains(text(),'Upload Data')]")  # verify
            click_element_by_xpath(self.driver, "//button[@class='antd-pro-pages-job-styles-jobTypeContainer']")
            time.sleep(1)

            get_text_by_xpath(self.driver, "//label[contains(text(),'Upload File')]")  # verify
            enable_element_by(self.driver, "file")
            time.sleep(1)
            send_keys_by_xpath(self.driver, "//span[@class='ant-upload']//input[@id='file']", file_to_upload)
            get_text_by_xpath(self.driver, f"//span[contains(text(),'{file_name}')]")  # verify file uploaded

            # select data type
            click_element_by_xpath(self.driver, "//input[@id='dataType']")
            time.sleep(1)
            click_element_by_xpath(self.driver, f"//div[contains(text(),'{data_type}')]")

            self.app.g_nav.gap_click_btn(button_name)
            if button_name == 'Cancel':
                click_element_by_xpath(self.driver, "//*[@class='ant-modal-close-x']")
                do_publish = False

            data_batch = None
            if do_publish == 1:
                click_element_by_xpath(self.driver, "//span[contains(text(),'Publish')]")
                data_records = find_elements(self.driver,
                                             "//div[@class='ant-modal-body']//td[@class='ant-table-cell'][1]")
                assert len(data_records) > 0, "No data listed"
                data_batch = data_records[0].text
                log.debug(f"Data batch is {data_batch}")
                assert data_batch is not None, "Data record batch cannot be None"
                assert data_batch.isdigit(), "Data batch is not a digit"
                self.data_records_batch_list.append(data_batch)
            elif do_publish == -1:
                click_element_by_xpath(self.driver, "//span[contains(text(),'Delete')]")
            click_element_by_xpath(self.driver, "//*[@class='ant-modal-close-x']")
            return data_batch


    def gap_project_open_by_name(self, name):
        with allure.step(f"Open project {name}"):
            assert self.gap_project_search_by_params(name=name), f"Project {name} not found"
            project_displayid = self.get_project_displayid()
            self.app.g_nav.gap_click_btn('View')  # //button[contains(text(),'View')]
            self.app.g_verify.current_url_contains('data-center')
            return project_displayid


    def gap_project_search_by_params(self, name=None, project_id=None, code=None, owner=None, proceed=True):
        with allure.step("Search project"):
            go_to_page(self.driver, Urls.URL + Urls.URL_PG_PROJECTS)
            self.app.g_nav.gap_click_btn("Reset")
            value_set = False
            if name is not None:
                self.gap_project_search_populate_field("Project Name", name)
                value_set = True
            if project_id is not None:
                self.gap_project_search_populate_field("Project ID", project_id)
                value_set = True
            if code is not None:
                self.gap_project_search_populate_field("Customer Code", code)
                value_set = True
            if owner is not None:
                self.gap_project_search_populate_field("Project Owner", owner)
                value_set = True
            if value_set and proceed:
                self.app.g_nav.gap_click_btn("Search")
                time.sleep(1)
                if get_text_by_xpath(self.driver, f"//button[contains(text(),'View')]") == 'View':
                    return True
            return False


    def gap_project_search_populate_field(self, placeholder, value):
        with allure.step(f"Gap project search: populate field {placeholder} with value {value}"):
            el_name = find_elements(self.driver, f"//input[@placeholder='{placeholder}']")
            assert len(el_name) > 0, f"Field {placeholder} not found"
            el_name[0].send_keys(value)
            # TODO verify


    def gap_project_modify(self, project_name, do_delete=False):
        if self.gap_project_search_by_params(name=project_name):
            click_element_by_xpath(self.driver, "//div[@class='ant-card-body']")
            click_element_by_xpath(self.driver, "//div[@class='ant-card-body']//*[local-name() = 'svg']")
            index = 2 if do_delete else 1

            click_element_by_xpath(self.driver,
                                   f"//div[contains(@class,'ant-dropdown-placement-bottomRight')]//li[{index}]//*[local-name() = 'svg']")
            # //div[@class='ant-card-body']//*[local-name() = 'svg']
            if do_delete:
                assert self.app.g_verify.text_present_on_page("Are you sure to delete this project?")
                self.app.g_nav.gap_click_btn("Ok")


    def gap_generate_project_name(self):
        with allure.step("Generate new project name"):
            self.current_project_name = f"AutoTest_{self.app.uniq_mark}"
            log.info(f"Current project name: {self.current_project_name}")
            return self.current_project_name
