from adap.api_automation.utils.http_util import HttpMethod
from adap.deprecated.testrail.core.config import get_config
from adap.deprecated.testrail.core.testrail import *

from adap.perf_platform.utils.logging import get_logger

LOGGER = get_logger(__name__)


class TestRailClient:
    def __init__(self):
        LOGGER.info('Initialize TestRail API client')
        self.cfg = get_config()
        self.base_url = self.cfg["url"]
        self.user = self.cfg["user_auth"]
        self.api_key = self.cfg["basic_auth"]

        auth = str(
            base64.b64encode(
                bytes('%s:%s' % (self.user, self.api_key), 'utf-8')
            ),
            'ascii'
        ).strip()

        self.headers = {'Authorization': 'Basic ' + auth}
        self.service = HttpMethod()
        self.endpoints = Endpoints(self.base_url)

    def get_projects(self):
        res = self.service.get(self.endpoints.get_projects, headers=self.headers)
        return res

    def get_suites(self, project_id):
        res = self.service.get(self.endpoints.get_suites.format(project_id=project_id), headers=self.headers)
        return res

    def get_cases(self, project_id, suite_id):
        res = self.service.get(self.endpoints.get_cases.format(project_id=project_id, suite_id=suite_id), headers=self.headers)
        return res

    def update_case(self, case_id, payload):
        headers = self.headers
        headers['Content-Type'] = 'application/json'
        res = self.service.post(self.endpoints.update_case.format(case_id=case_id),
                                data=json.dumps(payload),
                                headers=headers)
        return res


    # for migration (we do not use it)
    # def add_test_cases(self, section_id, payload):
    #     case = self.client.send_post(f'add_case/{section_id}', payload)
    #     LOGGER.info(case)
    #     return case
    #
    # def suite_name(self, suite_id):
    #     suite_name_el = self.client.send_get(f'get_suite/{suite_id}')
    #     LOGGER.info(suite_name_el)
    #     return suite_name_el
    #
    # def section_name(self, section_id):
    #     section_name_el = self.client.send_get(f'get_sections/{section_id}')
    #     LOGGER.info(section_name_el)
    #     return section_id
    #
    # def sections_name(self, project_id, suite_id):
    #     section_names_el = self.client.send_get(f'get_sections/{project_id}&suite_id={suite_id}')
    #     LOGGER.info(section_names_el)
    #     list_of_sections = [section_name_el['id'] for section_name_el in section_names_el['sections']]
    #     return list_of_sections
    #

class Endpoints:
    def __init__(self, base_url):
        self.base_url = base_url
        cfg = get_config(section='testrail_endpoints')

        self.get_projects = self.build_url(cfg["projects"])
        self.get_suites = self.build_url(cfg["suites"])
        self.get_cases = self.build_url(cfg["cases"])
        self.update_case = self.build_url(cfg["update_case"])

    def build_url(self, path):
        return self.base_url + path
