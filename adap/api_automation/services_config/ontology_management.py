from adap.api_automation.utils.http_util import HttpMethod
from adap.api_automation.services_config.endpoints.ontology_management_endpoints import *
import pytest
import allure
import json


class OntologyManagement:
    def __init__(self, custom_url=None, payload=None, env=None):
        self.payload = payload
        if env is None and custom_url is None: env = pytest.env
        self.env = env
        if custom_url:
            self.url = custom_url
        else:
            self.url = URL.format(env)
        if env == "fed":
            if pytest.customize_fed == 'true':
                self.url = FED_CUSTOMIZE.format(pytest.customize_fed_url)
            else:
                self.url = FED.format(pytest.env_fed)
        # if env == "staging":
        #     self.url = STAGING

        self.headers = {"Content-Type": "application/json",
                        "Authorization": "{api_key}"}

        self.service = HttpMethod(self.url, self.payload)

    @allure.step
    def get_csv_ontology_report(self, job_id, api_key):
        headers = {"Authorization": api_key}
        res = self.service.get(CSV_ONTOLOGY % (job_id), ep_name=CSV_ONTOLOGY, headers=headers)
        return res

    @allure.step
    def get_json_ontology_report(self, job_id, api_key):
        self.headers['Authorization'] = api_key
        res = self.service.get(JSON_ONTOLOGY % (job_id), ep_name=JSON_ONTOLOGY, headers=self.headers)
        return res

    @allure.step
    def upload_csv_ontology_file(self, job_id, api_key, file_name):
        headers = {"Authorization": api_key}
        if file_name != "":
            files = {'file': (file_name, open(file_name, 'rb'))}
            res = self.service.put(endpoint=CSV_ONTOLOGY % (job_id), data={}, headers=headers,
                                   ep_name=CSV_ONTOLOGY, files=files)
            print(res.content)
        else:
            res = self.service.put(CSV_ONTOLOGY % (job_id), data={}, headers=headers, ep_name=CSV_ONTOLOGY)
        return res

    @allure.step
    def upload_json_ontology(self, job_id, api_key, payload):
        self.headers['Authorization'] = api_key
        res = self.service.put(JSON_ONTOLOGY % (job_id), data=json.dumps(payload), headers=self.headers,
                               ep_name=JSON_ONTOLOGY)
        return res

