import allure

from adap.api_automation.services_config.endpoints import jobs_api_endpoints
from adap.api_automation.utils.http_util import HttpMethod
from adap.api_automation.services_config.endpoints.jobs_api_endpoints import *
import pytest
import logging

LOGGER = logging.getLogger(__name__)


class JobsApi:
    def __init__(self, payload=None, custom_url=None, api_version='v1', env=None, job_id=''):

        self.job_id = job_id
        self.jobs_id = []
        self.api_version = api_version
        self.payload = payload

        if env is None and custom_url is None: env = pytest.env

        self.env = env

        if custom_url is not None:
            self.url = custom_url
        else:
            self.url = URL.format(env)

        self.service = HttpMethod(self.url, self.payload)
        self.headers = {
            "Content-Type": "application/json",
        }

    @allure.step
    def archive_job(self, job_id=None):
        if job_id is None:
            job_id = self.job_id
        res = self.service.post(ARCHIVE_JOB % job_id, headers=self.headers)
        return res
