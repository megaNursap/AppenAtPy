import os
import time

import pytest
import requests
import json

from adap.perf_platform.utils.logging import get_logger
from adap.support.spira.core.config import get_config

LOGGER = get_logger(__name__)
_spira_errors = []


def format_date(seconds):
    """
    Returns an Inflectra formatted date based on the seconds passed in (obtained by time.time())
    """
    millis = int(round(seconds * 1000))
    offset = time.timezone / 3600
    return '/Date(' + str(millis) + '-0' + str(offset) + '00)/'


def send_updates_to_spira(_msg):
    spira = SpiraApiClient()
    all_tests = spira.mytests
    for test, message in _msg.items():
        try:
            for spira_id in all_tests[test]['id']:
                res = spira.send_test_run(test, spira_id, message['runner_msg'], message['execution_status'],
                                          message['duration'], message['runner_stack_trace'])
                if res.status_code != 200:
                    _spira_errors.append({test: res.content})
        except:
            _spira_errors.append(test)

    if len(_spira_errors) > 0:
        LOGGER.info(f"""Spira Errors: {_spira_errors} """)


class SpiraApiClient:
    def __init__(self):
        LOGGER.info('Initialize Spira API client')
        self.cfg = get_config()

        self.base_url = self.cfg["url"]
        self.project_id = self.cfg["project_id"]
        self._token = self.cfg["basic_auth"]

        self._set_api_headers()
        self.endpoints = Endpoints(self.base_url, self.project_id)
        # self._get_data()

    def send_test_run(
            self,
            test_name,
            spira_id,
            runner_message,
            execution_status_id,
            duration,
            runner_stack_trace):
        if not self.mytests.get(test_name):
            LOGGER.info(f"""Spira - No ID for tests: {test_name} """)
            return {}

        LOGGER.info("Send updates for test case ID", self.mytests[test_name]['id'])

        payload = {"TestRunFormatId": 1,
                   "TestSetId": self.current_test_set,
                   'StartDate': format_date(time.time() - duration),
                   "RunnerName": "PyTest",
                   "EndDate": format_date(time.time()),
                   "RunnerTestName": test_name,
                   "RunnerMessage": runner_message,
                   "RunnerStackTrace": runner_stack_trace,
                   "TestRunTypeId": 1,
                   "TestCaseId": str(spira_id),
                   "ExecutionStatusId": execution_status_id,
                   "CustomProperties": [{
                       "PropertyNumber": 4,
                       "StringValue": pytest.env
                   }]
                   }

        LOGGER.info(f"""Spira: Sending POST API request
                                       Endpoint: %s
                                       Request Payload: %s""" % (self.base_url + self.endpoints.test_run_record, payload))
        res = requests.post(
            self.base_url + self.endpoints.test_run_record.format(project_id=self.project_id),
            data=json.dumps(payload),
            headers=self._headers)

        LOGGER.info("Response Code: %s" % res.status_code)
        return res

    def get_test_case(self, tc_id):
        LOGGER.info("Get test case info", tc_id)
        resp = requests.get(
            self.endpoints.test_case.format(test_case_id=tc_id),
            headers=self._headers)

        if not resp.ok:
            LOGGER.error('Request Failed: {0}'.format(resp.text))

        json_resp = json.loads(resp.content)

        return json_resp

    def get_test_cases_by_suite_id(self, suite_id):
        LOGGER.info("Get test cases inside a folder", suite_id)
        resp = requests.get(
            self.endpoints.test_cases_by_folder_id.format(test_case_folder_id=suite_id),
            headers=self._headers)

        if not resp.ok:
            LOGGER.error('Request Failed: {0}'.format(resp.text))

        json_resp = json.loads(resp.content)

        return json_resp

    def get_all_test_cases(self):
        LOGGER.info("Get all available test cases from the project")
        resp = requests.get(
            self.endpoints.test_cases_all,
            headers=self._headers)

        if not resp.ok:
            LOGGER.error('Request Failed: {0}'.format(resp.text))

        json_resp = json.loads(resp.content)

        return json_resp

    def get_case_properties(self):
        LOGGER.info("Get all available test case properties")
        resp = requests.get(
            self.endpoints.custom_properties,
            headers=self._headers)

        if not resp.ok:
            LOGGER.error('Request Failed: {0}'.format(resp.text))

        json_resp = json.loads(resp.content)

        return json_resp

    @staticmethod
    def get_test_suites():
        LOGGER.info("Get available test suites data")

        return get_config(section='test-suites')

    def _get_data(self):
        with open(os.path.dirname(__file__) + "/../data/spira_tests.json", "r") as f:
            self.mytests = json.loads(f.read())
        with open(os.path.dirname(__file__) + "/../data/spira_test_set.json", "r") as f:
            self.test_sets = json.loads(f.read())
        if self.test_sets.get(pytest.set):
            self.current_test_set = self.test_sets[pytest.set]['id']
        else:
            self.current_test_set = self.test_sets['all']['id']

    def _set_api_headers(self):
        self._headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'PyTest',
            'Authorization': 'Basic {0}'.format(self._token)
        }


class Endpoints:
    def __init__(self, base_url, project_id):
        self.base_url = base_url
        self.project_id = project_id
        cfg = get_config(section='spira_endpoints')

        self.test_run_record = self.build_url(cfg["test_run_record"])
        self.test_case = self.build_url(cfg["test_case"])
        self.test_cases_by_folder_id = self.build_url(cfg["test_cases_by_folder_id"])
        self.test_cases_all = self.build_url(cfg["test_cases_all"])
        self.custom_properties = self.build_url(cfg["custom_properties"])

    def build_url(self, path):
        return (self.base_url + path).replace("{project_id}", self.project_id)
