import allure

from adap.ui_automation.utils.selenium_utils import *


class QualityFlowProjectJobs:
    _JOBS_ALL_NODES = "//div[contains(@class, 'react-flow__viewport')]//div[contains(@class," \
                      "'react-flow__node-customNode')] "
    _DATA_SOURCE_NODES = "//div[contains(@class, 'react-flow__viewport')]//div[@data-id='project_data_source']"
    _JOBS_NODES = "//div[contains(@class, 'react-flow__viewport')]//div[not (@data-id='project_data_source') and " \
                  "contains(@class, 'react-flow__node-customNode')]"
    _DATA_SOURCE_JOB_CONNECTOR = "//div[@data-nodeid='project_data_source' and contains(@class,'connectable')]"
    _ADD_DATA_TO_PROJECT = "//div[contains(@class,'react-flow__node-customNode')][.//div[text()='Add data to project']]"
    _CONNECTION_CONFIG = "//g[.//path[@id='{path_id}']]"
    _JOBS_BY_NAME = "//div[contains(@class, 'react-flow__node-customNode') and not (@data-id='project_data_source')][" \
                    ".//div[text()='{job_name}']]"
    _JOBS_BY_TYPE = "//div[contains(@class, 'react-flow__node-customNode') and not (@data-id='project_data_source')][" \
                    ".//h5[text()='{job_type}']]"
    _JOB_CONNECTOR = "//div[@data-nodeid='{job_id}' and contains(@class,'connectable')]"
    _JOB_NAME = "//input[@name='title']"
    _NEW_JOB_TYPE = "//div[./img and  .//div[text()='{job_type}']]"
    _TEMPLATE_BY_NAME = "//h3[.//div[text()='Featured Job Templates']]/..//div[text()='{template_name}']"

    def __init__(self, project, app):
        self.project = project
        self.app = app
        self.driver = self.app.driver

    def click_add_data_to_project(self):
        with allure.step(f'Click Add data to project node'):
            double_click_element_by_xpath(self.driver, self._ADD_DATA_TO_PROJECT)

    def select_jobs_view(self):
        """
        flow/list
        """
        pass

    def select_jobs_layout(self):
        pass

    def click_add_new_job_to(self, connection_type='job_id', value=None):
        with allure.step(f'Click add new job to {connection_type} {value}'):
            if connection_type == 'data_source':
                double_click_element_by_xpath(self.driver, self._DATA_SOURCE_JOB_CONNECTOR)

            if connection_type == 'job_id':
                double_click_element_by_xpath(self.driver, self._JOB_CONNECTOR.format(job_id=value))

    def fill_out_job_name(self, job_name=None, action=None):
        with allure.step(f'Create new job with name - {job_name}'):
            if job_name:
                send_keys_by_xpath(self.driver, self._JOB_NAME, job_name, clear_current=True)

            if action:
                self.app.navigation.click_link(action)

    def _find_templates_by_name(self, template_name):
        with allure.step(f'Find template by name - {template_name}'):
            send_keys_by_xpath(self.driver, "//input[@name='search']", template_name, clear_current=True)
            el = find_elements(self.driver, self._TEMPLATE_BY_NAME.format(template_name=template_name))
            return el

    def select_template_by_name(self, template_name, index=0):
        with allure.step(f'Select template by name - {template_name}'):
            el = self._find_templates_by_name(template_name=template_name)
            assert len(el) > index, f"Template {template_name} has not been found"
            el[index].click()
            time.sleep(3)
            self.app.navigation.click_link('Use this template')

    def select_new_job_property(self, job_type='Work Job', template=None):
        with allure.step(f'Select properties for the new job: job type - {job_type};\n'
                         f' template - {template}'):

            if job_type not in ['Work Job', 'Quality Assurance (QA) Job']:
                assert False, "Job type {job_type} is not defined"

            if template == 'scratch':
                self.app.navigation.click_link('Start From Scratch')
            elif template:
                self.select_template_by_name(template_name=template)

    def open_connection_config_btw(self):
        pass

    def change_connection(self):
        pass

    def open_job_by(self, by='name', value=None, index=0):
        with allure.step(f'Open job by {by}: {value}'):
            _job = self.search_jobs(by=by, value=value)
            assert len(_job) > index, f"Job {value} has not been found"
            double_click_on_element(self.driver, _job[index])

    def search_jobs(self, by='name', value=None):
        with allure.step(f'Search jobs by {by}: {value}'):
            if by == 'name':
                _jobs = find_elements(self.driver, self._JOBS_BY_NAME.format(job_name=value))
                return _jobs

            return []

    def get_project_jobs_details(self):
        jobs = find_elements(self.driver, self._JOBS_NODES)

        result = []
        for job in jobs:
            _type = job.find_element('xpath',".//h5").text
            _name = job.find_element('xpath',".//h5/../following-sibling::div").text
            result.append({
                "job_type": _type,
                "job_name": _name
            })

        return result


    # zoom controller  - ? claass
