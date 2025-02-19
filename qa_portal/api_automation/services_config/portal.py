from adap.api_automation.utils.http_util import HttpMethod
import allure
import logging
from qa_portal.api_automation.services_config.endpoints.portal_endpoints import *

LOGGER = logging.getLogger(__name__)


class Portal:
    def __init__(self, payload=None):
        self.url = PROD_URL
        self.payload = payload
        self.service = HttpMethod(self.url, self.payload)

    @allure.step
    def get_healthcheck(self):
        res = self.service.get(HEALTHCHECK)
        return res

    @allure.step
    def get_env_details(self, env=None):
        payload = {
            "env": env
        }
        res = self.service.get(ENV_DETAILS, params=payload)
        return res


