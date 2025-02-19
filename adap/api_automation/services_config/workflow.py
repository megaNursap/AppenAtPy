import json
import os
import time

import allure
import pytest
import requests

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.endpoints.workflow_endpoints import *
from ..services_config.endpoints.scripts_endpoints import *
from adap.api_automation.utils.http_util import HttpMethod
import logging
from adap.settings import Config

LOGGER = logging.getLogger(__name__)


class Workflow:

    def __init__(self, api_key, payload=None, custom_url=None, env=None, wf_id=''):
        self.api_key = api_key
        self.wf_id = wf_id

        self.payload = payload
        self.env = env if env else pytest.env

        if custom_url:
            self.url = custom_url
        # elif self.env == 'staging':
        #     self.url = API_GATEWAY_STAGING
        elif self.env == 'live':
            self.url = LIVE
        elif self.env == 'fed':
            self.url = FED.format(pytest.env_fed)
        else:
            self.url = API_GATEWAY.format(self.env)
        self.service = HttpMethod(self.url, self.payload)
        self.headers = {
            "AUTHORIZATION": "Token token={token}".format(token=self.api_key)
        }

    @allure.step
    def create_wf(self, payload=None):
        headers = {
            "Content-Type": "application/json",
            "AUTHORIZATION": "Token token={token}".format(token=self.api_key)
        }
        res = self.service.post(CREATE_WF, data=json.dumps(payload), headers=headers, ep_name=CREATE_WF)
        self.wf_id = res.json_response.get('id')
        if os.environ.get("PYTEST_CURRENT_TEST"):
            if res.status_code == 201:
                pytest.data.wfs_collections[self.wf_id] = self.api_key
        return res

    @allure.step
    def get_info(self, wf_id=None):
        if wf_id is None:
            wf_id = self.wf_id

        res = self.service.get(WF_INFO % wf_id, headers=self.headers, ep_name=WF_INFO)
        return res

    @allure.step
    def get_owner(self, wf_id=None):
        if wf_id is None:
            wf_id = self.wf_id

        res = self.service.get(WF_OWNER % wf_id, headers=self.headers, ep_name=WF_OWNER)
        return res

    @allure.step
    def update_wf(self, wf_id=None, payload=None):
        headers = {
            "Content-Type": "application/json",
            "AUTHORIZATION": "Token token={token}".format(token=self.api_key)
        }
        if wf_id is None:
            wf_id = self.wf_id
        res = self.service.patch(WF_INFO % wf_id, headers=headers, data=json.dumps(payload), ep_name=WF_INFO)
        return res

    @allure.step
    def delete_wf(self, wf_id=None):
        if wf_id is None:
            wf_id = self.wf_id
        res = self.service.delete(WF_INFO % wf_id, headers=self.headers, ep_name=WF_INFO)
        return res

    @allure.step
    def get_list_of_wfs(self):
        res = self.service.get(CREATE_WF, headers=self.headers, ep_name=CREATE_WF)
        return res

    @allure.step
    def upload_data(self, file_name, wf_id=None, large_file=False):
        if wf_id is None:
            wf_id = self.wf_id

        with open(file_name, 'rb') as filereader:
            files = {
                'file': (file_name, filereader),
            }
            if large_file:
                _s = requests.session()
                _s.verify = False
                if self.env == 'staging':
                    url = API_GATEWAY_STAGING + UPLOAD_DATA % wf_id
                else:
                    url = API_GATEWAY.format(self.env) + UPLOAD_DATA % wf_id

                res = _s.post(
                    url=url,
                    verify=False,
                    files=files,
                    headers=self.headers,
                    data={},
                    timeout=30
                )
            else:
                res = self.service.post(
                    UPLOAD_DATA % wf_id,
                    verify=False,
                    files=files,
                    headers=self.headers,
                    data={}
                )
            return res

    @allure.step
    def get_data_upload_info(self, data_upload_id, file_name, wf_id=None, del_mode=False):
        if wf_id is None:
            wf_id = self.wf_id

        # files = {
        #     'file': (file_name, open(file_name, 'rb')),
        # }

        ep = UPLOAD_DATA_INFO % (wf_id, data_upload_id)

        if del_mode:
            res = self.service.delete(ep,  headers=self.headers, ep_name=UPLOAD_DATA_INFO)
        else:
            res = self.service.get(ep, headers=self.headers, ep_name=UPLOAD_DATA_INFO)

        return res

    @allure.step
    def get_list_of_data(self, file_name, wf_id=None):
        if wf_id is None:
            wf_id = self.wf_id

        # files = {
        #     'file': (file_name, open(file_name, 'rb')),
        # }
        res = self.service.get(LIST_DATA_INFO % wf_id, headers=self.headers, ep_name=LIST_DATA_INFO)
        return res

    @allure.step
    def delete_data_upload(self, data_upload_id, wf_id=None):
        if wf_id is None:
            wf_id = self.wf_id

        return self.service.delete(UPLOAD_DATA_INFO % (wf_id, data_upload_id), headers=self.headers,
                                   ep_name=UPLOAD_DATA_INFO)

    @allure.step
    def create_job_step(self, jobs, wf_id=None):
        headers = {
            "Content-Type": "application/json",
            "AUTHORIZATION": "Token token={token}".format(token=self.api_key)
        }
        if wf_id is None:
            wf_id = self.wf_id

        _steps = []
        for job in jobs:
            data = {'job_id': job}
            res = self.service.post(STEPS % wf_id, headers=headers, data=json.dumps(data), ep_name=STEPS)
            res.assert_response_status(201)
            _step_info = {
                "job_id": job,
                "step_id": res.json_response['id'],
                "data_processor_id": res.json_response['data_processor_id']
            }
            _steps.append(_step_info)

        return _steps

    @allure.step
    def create_model_step(self, models, wf_id=None):
        headers = {
            "Content-Type": "application/json",
            "AUTHORIZATION": "Token token={token}".format(token=self.api_key)
        }
        if wf_id is None:
            wf_id = self.wf_id

        _steps = []
        for model in models:
            data = {'mlapi_id': model}
            res = self.service.post(STEPS % wf_id, headers=headers, data=json.dumps(data), ep_name=STEPS)
            res.assert_response_status(201)
            _step_info = {
                "mlapi_id": model,
                "step_id": res.json_response['id'],
                "data_processor_id": res.json_response['data_processor_id']
            }
            _steps.append(_step_info)

        return _steps

    @allure.step
    def create_script_step(self, script_id, wf_id=None):
        headers = {
            "Content-Type": "application/json",
            "AUTHORIZATION": "Token token={token}".format(token=self.api_key)
        }
        if wf_id is None:
            wf_id = self.wf_id

        _steps = []
        data = {'script_id': script_id}
        res = self.service.post(STEPS % wf_id, headers=headers, data=json.dumps(data), ep_name=STEPS)
        res.assert_response_status(201)
        _step_info = {
            "script_id": script_id,
            "step_id": res.json_response['id'],
            "data_processor_id": res.json_response['data_processor_id']
        }

        _steps.append(_step_info)
        return _steps

    @allure.step
    def read_step(self, step_id, wf_id=None):
        if wf_id is None:
            wf_id = self.wf_id

        res = self.service.get(STEP % (wf_id, step_id), headers=self.headers, ep_name=STEP)
        return res

    @allure.step
    def delete_step(self, step_id, wf_id=None):
        if wf_id is None:
            wf_id = self.wf_id
        res = self.service.delete(STEP % (wf_id, step_id), headers=self.headers, ep_name=STEP)
        return res

    @allure.step
    def list_of_steps(self, wf_id=None):
        if wf_id is None:
            wf_id = self.wf_id
        res = self.service.get(STEPS % wf_id, headers=self.headers, ep_name=STEPS)
        return res

    @allure.step
    def create_route(self, step_id, destination_step_id, wf_id=None):
        headers = {
            "Content-Type": "application/json",
            "AUTHORIZATION": "Token token={token}".format(token=self.api_key)
        }
        if wf_id is None:
            wf_id = self.wf_id

        payload = {'destination_step_id': destination_step_id}
        res = self.service.post(ROUTES % (wf_id, step_id), headers=headers, data=json.dumps(payload), ep_name=ROUTES)
        return res

    @allure.step
    def read_route(self, step_id, route_id, wf_id=None):
        if wf_id is None:
            wf_id = self.wf_id

        res = self.service.get(ROUTE % (wf_id, step_id, route_id), headers=self.headers, ep_name=ROUTE)
        return res

    @allure.step
    def update_route(self, step_id, route_id, destination_step_id, wf_id=None):
        headers = {
            "Content-Type": "application/json",
            "AUTHORIZATION": "Token token={token}".format(token=self.api_key)
        }
        if wf_id is None:
            wf_id = self.wf_id
        payload = {'destination_step_id': destination_step_id}
        res = self.service.patch(ROUTE % (wf_id, step_id, route_id), headers=headers, data=json.dumps(payload),
                                 ep_name=ROUTE)
        return res

    @allure.step
    def delete_route(self, step_id, route_id, wf_id=None):
        if wf_id is None:
            wf_id = self.wf_id

        res = self.service.delete(ROUTE % (wf_id, step_id, route_id), headers=self.headers, ep_name=ROUTE)
        return res

    @allure.step
    def get_list_of_routes(self, step_id, wf_id=None):
        if wf_id is None:
            wf_id = self.wf_id

        res = self.service.get(ROUTES % (wf_id, step_id), headers=self.headers, ep_name=ROUTES)
        return res

    @allure.step
    def create_filter_rule(self, step_id, route_id, payload, wf_id=None):
        headers = {
            "Content-Type": "application/json",
            "AUTHORIZATION": "Token token={token}".format(token=self.api_key)
        }
        if wf_id is None:
            wf_id = self.wf_id

        res = self.service.post(FILTER_RULES % (wf_id, step_id, route_id), headers=headers,
                                data=json.dumps(payload), ep_name=FILTER_RULES)
        return res

    @allure.step
    def read_filter_rule(self, step_id, route_id, rule_id, wf_id=None):
        if wf_id is None:
            wf_id = self.wf_id

        res = self.service.get(FILTER_RULE % (wf_id, step_id, route_id, rule_id), headers=self.headers,
                               ep_name=FILTER_RULE)
        return res

    @allure.step
    def update_filter_rule(self, step_id, route_id, rule_id, payload, wf_id=None):
        headers = {
            "Content-Type": "application/json",
            "AUTHORIZATION": "Token token={token}".format(token=self.api_key)
        }
        if wf_id is None:
            wf_id = self.wf_id

        res = self.service.patch(FILTER_RULE % (wf_id, step_id, route_id, rule_id), headers=headers,
                                 data=json.dumps(payload), ep_name=FILTER_RULE)
        return res

    @allure.step
    def list_filter_rule(self, step_id, route_id, wf_id=None):
        if wf_id is None:
            wf_id = self.wf_id

        res = self.service.get(FILTER_RULES % (wf_id, step_id, route_id), headers=self.headers, ep_name=FILTER_RULES)
        return res

    @allure.step
    def delete_filter_rule(self, step_id, route_id, rule_id, wf_id=None):
        if wf_id is None:
            wf_id = self.wf_id

        res = self.service.delete(FILTER_RULE % (wf_id, step_id, route_id, rule_id), headers=self.headers,
                                  ep_name=FILTER_RULE)
        return res

    @allure.step
    def launch(self, num_rows, wf_id=None):
        if wf_id is None:
            wf_id = self.wf_id

        res = self.service.post(LAUNCH % (wf_id, num_rows), headers=self.headers, ep_name=LAUNCH)
        return res

    @allure.step
    def pause(self, wf_id=None):
        if wf_id is None:
            wf_id = self.wf_id

        res = self.service.post(PAUSE % wf_id, headers=self.headers, data={}, ep_name=PAUSE)
        return res

    @allure.step
    def resume(self, wf_id=None):
        if wf_id is None:
            wf_id = self.wf_id

        res = self.service.post(RESUME % wf_id, headers=self.headers, data={}, ep_name=RESUME)
        return res

    @allure.step
    def regenerate_report(self, report_type, wf_id=None):
        if not wf_id:
            wf_id = self.wf_id

        res = self.service.post(REGENERATE_WF_REPORT.format(wf_id=wf_id, report_type=report_type), headers=self.headers,
                                data={}, ep_name=REGENERATE_WF_REPORT)
        return res

    @allure.step
    def download_report(self, report_type, wf_id=None):
        if not wf_id:
            wf_id = self.wf_id

        res = self.service.get(DOWNLOAD_WF_REPORT.format(wf_id=wf_id, report_type=report_type), headers=self.headers,
                               data={}, ep_name=DOWNLOAD_WF_REPORT)
        return res

    @allure.step
    def get_statistics(self, wf_id=None):
        if wf_id is None:
            wf_id = self.wf_id

        res = self.service.get(STATISTICS % wf_id, headers=self.headers, ep_name=STATISTICS)
        return res

    @allure.step
    def count_wfs_for_user(self):
        res = self.service.get(COUNT_WFS, headers=self.headers, ep_name=COUNT_WFS)
        return res

    @allure.step
    def get_token(self, res):
        return res.headers.get('Authorization')

    @allure.step
    def copy_wf(self, wf_id=None):
        if wf_id is None:
            wf_id = self.wf_id

        res = self.service.post(COPY_WF.format(wf_id=wf_id), headers=self.headers, data={}, ep_name=COPY_WF)
        if os.environ.get("PYTEST_CURRENT_TEST"):
            if res.status_code == 201:
                pytest.data.wfs_collections[res.json_response['id']] = self.api_key

        return res

    def wait_until_wf_status(self, status, wf_id=None, max_time=0):
        if not max_time:
            max_time = Config.MAX_WAIT_TIME
        if wf_id is None:
            wf_id = self.wf_id
        wait = 2
        running_time = 0
        current_status = ""
        while (current_status != status) and (running_time < max_time):
            res = self.get_info(wf_id)
            res.assert_response_status(200)
            current_status = res.json_response['status']
            running_time += wait
            time.sleep(wait)

    @allure.step
    def get_title_of_job(self, job_id):
        job_titles = []
        for i in range(len(job_id)):
            _jobs = Builder(self.api_key)
            resp = _jobs.get_json_job_status(job_id[i])
            job_titles.append(resp.json_response.get('title'))
        return job_titles

    @allure.step
    def get_job_id_from_wf(self, wf_id):
        response = Workflow(self.api_key).get_info(wf_id)
        step_json = response.json_response['steps']
        job_ids = []
        for i in range(len(step_json)):
            id = step_json[i]['data_processor_id']
            job_ids.append(id)
        return job_ids

    @allure.step
    def get_model_id_from_wf(self, wf_id):
        response = Workflow(self.api_key).list_of_steps(wf_id)
        model_ids = []
        for i in range(len(response.json_response)):
            _id = response.json_response[i].get('data_processor_id')
            model_ids.append(_id)
        return model_ids

    @allure.step
    def get_scripts_catalog(self):
        scripts_url = URL.format(self.env) + SCRIPTS_CATALOG
        res = requests.get(scripts_url)
        assert res.status_code == 200
        return json.loads(res.text)
