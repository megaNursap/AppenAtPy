
from adap.api_automation.utils.http_util import HttpMethod
from adap.api_automation.services_config.endpoints.make_endpoints import *
import pytest
import logging


LOGGER = logging.getLogger(__name__)

class Make:
    def __init__(self, api_key, payload=None, custom_url=None, api_version='v1', env=None, job_id='', env_fed=None):

        self.api_key = api_key
        self.job_id = job_id
        self.jobs_id = []
        self.api_version = api_version
        self.payload = payload

        if env is None and custom_url is None:  env = pytest.env

        self.env = env

        if custom_url is not None:
            self.url = custom_url
        elif env == "live":
            self.url = PROD
        elif env == "fed":
            if pytest.customize_fed == 'true':
                self.url = FED_CUSTOMIZE.format(pytest.customize_fed_url)
            elif env_fed:
                self.url = FED.format(env_fed)
            else:
                self.url = FED.format(pytest.env_fed)
        elif env == "hipaa":
            self.url = HIPAA
        # elif env == "staging":
        #     self.url = STAGING
        else:
            if api_version == 'v1':
                self.url = URL.format(env)
            else:
                self.url = URL_V2.format(env)

        self.service = HttpMethod(self.url, self.payload)
        self.headers = {
            "Content-Type": "application/json",
            "AUTHORIZATION": "Token token={token}".format(token=self.api_key)
        }

    def get_jobs_cml_tag(self, job_id=None):
        if job_id is None:
            job_id = self.job_id
        res = self.service.get(GET_CML_TAG % job_id, ep_name=GET_CML_TAG, headers=self.headers)
        return res

    def get_jobs_setting(self, job_id=None):
        if job_id is None:
            job_id = self.job_id
        res = self.service.get(GET_SETTING % job_id, ep_name=GET_SETTING, headers=self.headers)
        return res

    def get_dashboard(self, job_id=None):
        if job_id is None:
            job_id = self.job_id
        res = self.service.get(GET_DASHBOARD % job_id, ep_name=GET_DASHBOARD, headers=self.headers)
        return res

    def get_output_required_fields(self, jobs=[], cookies=None):
        res = self.service.get(OUTPUT_AND_REQUIRED_FIELDS,
                               params=[('job_ids[]', _job ) for _job in jobs],
                               ep_name=OUTPUT_AND_REQUIRED_FIELDS,
                               headers=self.headers,
                               cookies=cookies)
        return res

    def get_json_workers(self, job_id=None):
        if job_id is None:
            job_id = self.job_id

        res = self.service.get(WORKERS.format(job_id), ep_name=WORKERS, headers=self.headers)
        return res
