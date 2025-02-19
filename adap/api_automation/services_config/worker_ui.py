import allure
import logging

from adap.api_automation.utils.data_util import *
from adap.api_automation.utils.http_util import HttpMethod
from adap.api_automation.services_config.endpoints.worker_ui_endpoints import *

LOGGER = logging.getLogger(__name__)


class WUI:

    def __init__(self, api_key='', env=None):
        self.api_key = api_key
        self.payload = ""

        if env is None:
            env = pytest.env

        self.env = env
        self.url = URL.format(env)

        self.service = HttpMethod(self.url, self.payload)

    @allure.step
    def generate_productivity_report(self, job_id):
        res = self.service.get(PRODUCTIVITY_METRICS_REPORT.format(job_id=job_id, key=self.api_key))
        return res
