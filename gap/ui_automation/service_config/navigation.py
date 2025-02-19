import logging
import time

import allure

from adap.ui_automation.services_config.navigation import Navigation
from adap.ui_automation.utils.js_utils import scroll_to_page_top
from adap.ui_automation.utils.selenium_utils import find_elements, go_to_page, click_element_by_xpath

log = logging.getLogger(__name__)


class GNavigation(Navigation):

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.driver = self.app.driver


    def open_page_login(self):
        with allure.step("Open login page"):
            chunk = Urls.URL_USER_LOGIN
            if not self.app.g_verify.gap_verify_current_url_contain(chunk):
                self.open_page(Urls.URL + chunk)
            self.app.g_verify.current_url_contains(chunk)
            time.sleep(1)
            login_page_uniq_el = find_elements(self.driver, "//div[contains(@id,'-tab-Account')]")
            assert len(login_page_uniq_el) > 0, 'Login page is not open'


    def open_page_welcome(self):
        with allure.step('Open welcome page'):
            if not self.app.g_verify.gap_verify_current_url_contain(Urls.URL_PG_WELCOME):
                self.open_page(Urls.URL + Urls.URL_PG_WELCOME)
                self.app.g_verify.current_url_contains(Urls.URL_PG_WELCOME)


    def open_page_projects(self):
        with allure.step("Open projects page"):
            if not self.app.g_verify.gap_verify_current_url_contain(Urls.URL_PG_PROJECTS):
                self.open_page(Urls.URL + Urls.URL_PG_PROJECTS)
                self.app.g_verify.current_url_contains(Urls.URL_PG_PROJECTS)


    def open_gap_project_tab(self, name, timeout=1):
        with allure.step(f"Open tab {name}"):
            self.gap_workflow_breadcrumb_navigate()
            tab_lst = ['Data Center', 'Workflow', 'Template Center', 'Interim Revise Job', 'Audit']
            low_case = name.lower().replace(' ', '-')
            if tab_lst.count(name):
                if not self.app.g_verify.gap_verify_current_url_contain(low_case):
                    click_element_by_xpath(self.driver,
                                           f"//ul[contains(@class,'ant-menu-horizontal')]//span[contains(text(),'{name}')]")
                    time.sleep(timeout)
            else:
                assert False, f"Tab name {name} is invalid"
            self.app.g_verify.current_url_contains(low_case)


    def open_gap_template_tab(self, category='LIDAR'):
        with allure.step(f"Select template category {category}"):
            self.app.g_verify.text_present_on_page("Choose template category")
            category = category.upper()
            tab_lst = ['LIDAR', 'IMAGE', 'AUDIO', 'VIDEO', 'TEXT']
            assert tab_lst.count(category) == 1, f"Category {category} unknown"
            xpath = f"//div[contains(@id,'tab-{category}')]"
            click_element_by_xpath(self.driver, xpath)


    def open_project_data_center(self, projectid):
        with allure.step("Open project Data Center"):
            go_to_page(self.driver, Urls.URL + Urls.URL_PG_PROJECT_DATA_CENTER % projectid)
            self.app.g_verify.gap_verify_current_url_contain(projectid, True)


    def open_project_template_center(self, projectid, project_display_id):
        with allure.step("Open project Template Center"):
            go_to_page(self.driver, Urls.URL + Urls.URL_PG_PROJECT_TEMPLATE_CENTER % (projectid, project_display_id))
            self.app.g_verify.gap_verify_current_url_contain(projectid, True)


    def open_project_details(self, projectid, timeout=2):
        with allure.step("Open project Details"):
            go_to_page(self.driver, Urls.URL + Urls.URL_PG_PROJECT_DETAILS % projectid)
            time.sleep(timeout)
            self.app.g_verify.gap_verify_current_url_contain(projectid, True)


    def go_to_workflow_detail(self, workflowid, projectid, project_displayid):
        with allure.step("Go to current workflow detail"):
            url = Urls.URL + Urls.URL_PG_PROJECT_WORKFLOW_DETAIL % (workflowid, project_displayid, projectid)
            go_to_page(self.driver, url)


    def gap_click_btn(self, btn_name, timeout=2):
        self.click_btn(btn_name, timeout)


    def gap_workflow_breadcrumb_navigate(self, to='project'):
        with allure.step(f"Navigate {to} via breadcrumb"):
            scroll_to_page_top(self.driver)
            bread_crumb = find_elements(self.driver,
                                        "//div[@class='ant-breadcrumb']//*[contains(@class,'ant-breadcrumb-link')]")
            num_of_sections = len(bread_crumb)
            assert num_of_sections >= 2, "Something wrong with bread_crumb"
            if to == 'project':
                bread_crumb[1].click()
            else:
                bread_crumb[0].click()
                # projects


class Urls:
    URL = "https://gap.appen.com"
    VERSION = "v3"
    URL_USER_LOGIN = "/user/login"
    URL_USER_PWD_RESET = "/user/password-forget"
    URL_USER_REGISTER = "/user/register"
    URL_PG_WELCOME = "/welcome"
    URL_PG_ACCOUNT_CENTER = "/profile"
    URL_PG_FILE_CENTER = "/file-center"
    URL_PG_PROJECTS = f"/{VERSION}/projects"
    URL_PG_PROJECT_DATA_CENTER_PARAMS = f"/data-center?version={VERSION}"
    URL_PG_PROJECT_DATA_CENTER = f"/{VERSION}/projects/%s{URL_PG_PROJECT_DATA_CENTER_PARAMS}"
    URL_PG_PROJECT_DETAILS = f"/{VERSION}/projects/%s/workflow?version={VERSION}"
    URL_PG_PROJECT_WORKFLOW_DETAIL = f"/workflows/%s/detail?projectDisplayId=%s&projectId=%s&version={VERSION}"
    URL_PG_PROJECT_TEMPLATE_CENTER = f"/{VERSION}/projects/%s/template-center?projectDisplayId=%s&version={VERSION}"
    URL_PG_PROJECT_INT_REV_JOB = f"/{VERSION}/projects/%s/interim-revise-job?version={VERSION}"
    URL_PG_PROJECT_AUDIT = f"/{VERSION}/projects/%s/audit?version={VERSION}"
    URL_PG_PROJECT_ACCESS_CONTROL = f"/{VERSION}/project-access?projectId=%s&version={VERSION}"
