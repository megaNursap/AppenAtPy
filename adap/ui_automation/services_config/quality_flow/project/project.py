import os
import time

import allure
import pytest
from selenium.webdriver import Keys

from adap.api_automation.services_config.endpoints.client import URL
from adap.api_automation.services_config.requestor_proxy import RP
from adap.api_automation.utils.data_util import get_test_data
from adap.ui_automation.services_config.quality_flow.job import QFJob
from adap.ui_automation.services_config.quality_flow.project.project_crowd import QualityFlowProjectCrowd
from adap.ui_automation.services_config.quality_flow.project.project_dashboard import QualityFlowProjectDashboard
from adap.ui_automation.services_config.quality_flow.project.project_data import QualityFlowProjectData
from adap.ui_automation.services_config.quality_flow.project.project_jobs import QualityFlowProjectJobs
from adap.ui_automation.utils.selenium_utils import send_keys_by_xpath, click_element_by_xpath, \
    get_text_by_xpath, find_elements, find_element, clear_text_field_by_xpath


class QualityFlowProject:
    # xpath
    _PROJECT_NAME = "//input[@name='name']"
    _PROJECT_DESCRIPTION = "//textarea[@name='description']"
    _UNIT_TYPE = "//label[.//span[text()='{unit_type}']]"
    _CLOSE_NEW_PROJECT_WINDOW = "//h3/..//a[@href='/quality/projects']//*[local-name() = 'svg']"
    _SEARCH_PROJECT_BY_NAME = '//tr[.//td[./a and .="{}"]]'
    _SEARCH_PROJECT_BY_ID = '//tr//td[1][text()="{}"]'

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

        self.data = QualityFlowProjectData(self, app)
        self.jobs = QualityFlowProjectJobs(self, app)
        self.crowd = QualityFlowProjectCrowd(self, app)
        self.dashboard = QualityFlowProjectDashboard(self, app)
        self.job = QFJob(self, app)

    def qf_is_enabled_to_team(self, team_id):
        with allure.step(f'QF is enabled for team:{team_id}'):
            admin_username = get_test_data('test_account', 'email')
            admin_password = get_test_data('test_account', 'password')
            rp = RP()
            rp.get_valid_sid(username=admin_username, password=admin_password)
            res = rp.get_team_settings(team_id=team_id)
            return res.json_response['quality_flow_enabled']


    def enable_qf_for_team(self, team_id):
        with allure.step(f'Enable QF for team:{team_id}'):
            admin_username = get_test_data('test_account', 'email')
            admin_password = get_test_data('test_account', 'password')
            rp = RP()
            rp.get_valid_sid(username=admin_username, password=admin_password)
            res = rp.get_team_settings(team_id=team_id)

            current_settings = res.json_response
            current_settings['quality_flow_enabled'] = True

            payload = {"team": current_settings}
            res = rp.put_team_settings(team_id=team_id, payload=payload)
            return res

    def fill_out_project_details(self, name=None, unit_type=None, description=None, action=None):
        with allure.step(f'Create new project with data: name - {name}\n'
                         f'                              unit type - {unit_type}\n'
                         f'                              description - {description}'):
            if name:
                send_keys_by_xpath(self.driver, self._PROJECT_NAME, name, clear_current=True)

            if unit_type:
                click_element_by_xpath(self.driver, self._UNIT_TYPE.format(unit_type=unit_type))

            if description:
                send_keys_by_xpath(self.driver, self._PROJECT_DESCRIPTION, description, clear_current=True)

            if action:
                if action == 'close':
                    self.close_create_project_window()
                else:
                    self.app.navigation.click_link(action)

    def edit_project(self):
        pass

    def find_project(self, by='name', value=None):
        with allure.step(f'Search project by {by}:{value}'):
            if by == 'name':
                project_row = find_elements(self.driver, self._SEARCH_PROJECT_BY_NAME.format(value))
            elif by == 'id':
                project_row = find_elements(self.driver, self._SEARCH_PROJECT_BY_ID.format(value))
            else:
                return []

            return project_row

    def open_project(self, by='name', value=None):
        with allure.step(f'Open project by {by}:{value}'):
            project = self.find_project(by=by, value=value)
            assert len(project), f"Project with {by}={value} has not been found"

            _link = project[0].find_elements('xpath', ".//a[contains(@href, '/quality/projects')]")
            assert len(_link), f"Link with {by}={value} has not been found"
            _link[0].click()

    def get_projects_on_page(self):
        pass

    def clean_project_name(self):
        with allure.step('Clean project name'):
            clear_text_field_by_xpath(self.driver, self._PROJECT_NAME)

    def clean_project_description(self):
        with allure.step('Clean project description'):
            el = find_elements(self.driver, self._PROJECT_DESCRIPTION)
            assert len(el) > 0, "Element has not been found by xpath: %s" % self._PROJECT_DESCRIPTION
            len_el = len(el[0].text)
            while len_el > 0:
                el[0].send_keys(Keys.BACK_SPACE)
                len_el -= 1

    def close_create_project_window(self):
        with allure.step('Close create project window'):
            click_element_by_xpath(self.driver, self._CLOSE_NEW_PROJECT_WINDOW)

    def get_project_details(self):
        with allure.step('Get projects details'):
            """
            return dict with id and project name
            """
            project_id_el = find_elements(self.driver, "//h3//div[contains(text(), 'ID')]")
            assert len(project_id_el), "Project ID has not been found"
            _id = project_id_el[0].text.replace("ID ", "")

            project_name_el = find_elements(self.driver,
                                            "//a[@href='/quality/projects' and text()='Projects']//following-sibling::span[2]")
            assert len(project_name_el), "Project name has not been found"
            _name = project_name_el[0].text

            return {
                "id": _id,
                "name": _name
            }

    def get_project_id_from_url(self):
        with allure.step('Get projects id from URL'):
            """
              get project ID from current URL, project must be open 
            """
            url = self.driver.current_url
            try:
                return url.split('/projects')[1].split('/')[1]
            except:
                return 'Not found'

    def add_project_to_tear_down_collection(self, project_id, account_name, account_password, team_id):
        if os.environ.get("PYTEST_CURRENT_TEST", ""):
            if project_id != 'Not found':
                pytest.data.qf_project_collection.append({'account': {"name": account_name,
                                                                      "password": account_password,
                                                                      "team_id": team_id},
                                                          'project_id': project_id})

    def open_project_by_id(self, project_id):
        with allure.step(f'open project by ID {project_id}'):
            url = f'{URL.format(env=pytest.env)}/quality/projects/{project_id}'
            self.app.navigation.open_page(url)
            time.sleep(3)

    def open_jobs_page_by_project_id(self, project_id):
        with allure.step(f'open project jobs page by project ID  {project_id}'):
            url = f'{URL.format(env=pytest.env)}/quality/projects/{project_id}/jobs'
            self.app.navigation.open_page(url)
            time.sleep(3)

    def navigate_to_project(self):
        with allure.step('Navigate to project resource page'):
            self.app.navigation.click_link_by_href('/quality')

    def navigate_to_dataset_page_by_project_id(self, project_id):
        with allure.step(f'open setting page by project ID  {project_id}'):
            url = f'{URL.format(env=pytest.env)}/quality/projects/{project_id}/dataset'
            self.app.navigation.open_page(url)
            time.sleep(3)

    def navigate_to_design_page_by_project_id(self, project_id, job_id):
        with allure.step(f'open setting page by project ID  {project_id} and {job_id}'):
            url = f'{URL.format(env=pytest.env)}/quality/projects/{project_id}/jobs/{job_id}/design'
            self.app.navigation.open_page(url)
            time.sleep(3)

    def navigate_to_job_setting_page_by_project_id(self, project_id, job_id):
        with allure.step(f'open setting page by project ID  {project_id} and {job_id}'):
            url = f'{URL.format(env=pytest.env)}/quality/projects/{project_id}/jobs/{job_id}/settings'
            self.app.navigation.open_page(url)
            time.sleep(3)

    def navigate_to_data_page_by_project_id_and_job_id(self, project_id, job_id):
        with allure.step(f'open dataset page by project ID  {project_id}'):
            url = f'{URL.format(env=pytest.env)}/quality/projects/{project_id}/jobs/{job_id}/data'
            self.app.navigation.open_page(url)
            time.sleep(5)

    def navigate_to_job_setting_page_by_project_id_and_job_id(self, project_id, job_id):
        with allure.step(f'open setting page by project ID  {project_id} and {job_id}'):
            url = f'{URL.format(env=pytest.env)}/quality/projects/{project_id}/jobs/{job_id}/settings'
            self.app.navigation.open_page(url)
            time.sleep(3)

    def navigate_to_result_by_project_id_and_job_id(self, project_id, job_id):
        with allure.step(f'open setting page by project ID  {project_id} and {job_id}'):
            url = f'{URL.format(env=pytest.env)}/quality/projects/{project_id}/jobs/{job_id}/monitor'
            self.app.navigation.open_page(url)
            time.sleep(3)

    def navigate_to_job_quality_page_by_project_id_and_job_id(self, project_id, job_id):
        with allure.step(f'open setting page by project ID  {project_id} and {job_id}'):
            url = f'{URL.format(env=pytest.env)}/quality/projects/{project_id}/jobs/{job_id}/quality/test_questions'
            self.app.navigation.open_page(url)
            time.sleep(3)

    def navigate_to_manage_contributor_page_by_project_id_and_job_id(self, project_id, job_id):
        with allure.step(f'open manage contributor page by project ID  {project_id} and {job_id}'):
            url = f'{URL.format(env=pytest.env)}/quality/projects/{project_id}/jobs/{job_id}/settings/assign-contributors'
            self.app.navigation.open_page(url)
            time.sleep(5)

    def assert_job_flow_have_no_create_button_for_new_following_job(self, job_id):
        with allure.step(f'assert job flow have not create new following job button at the flow end {job_id}'):
            find_elements(self.driver, f"//div[contains(@data-id, '{job_id}')]")
            job_element_in_flow = find_elements(self.driver,
                                                f"//div[contains(@data-id, '{job_id}') and contains(@class, 'react-flow__handle-bottom')]")
            assert job_element_in_flow is not None
            assert len(job_element_in_flow) == 1
            create_following_job_button = find_elements(self.driver,
                                                        f"//div[contains(@data-id, '{job_id}') and contains(@class, 'jtfaHx')]")

            assert len(create_following_job_button) == 0, "create_following_job_button should not present"
            job_element_in_flow = find_elements(self.driver,
                                                f"//div[contains(@data-id, '{job_id}') and contains(@class, 'react-flow__handle-bottom')]")
            assert job_element_in_flow is not None
            assert len(job_element_in_flow) == 1
            create_following_job_button = find_elements(self.driver,
                                                        f"//div[contains(@data-id, '{job_id}') and contains(@class, 'jtfaHx')]")
            assert len(create_following_job_button) == 0, "create_following_job_button should not present"

    def latest_process_running_background(self):
        with allure.step(f'Check latest process running in background'):
            process = get_text_by_xpath(self.driver,"//table[@role='table']/tbody/tr[1]/td[2]")
            return process

