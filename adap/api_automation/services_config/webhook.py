from adap.api_automation.utils.http_util import HttpMethod
from adap.api_automation.services_config.endpoints.webhook_endpoints import *
import pytest
import allure
import logging
import json
LOGGER = logging.getLogger(__name__)

class Webhook:

    def __init__(self, api_key, payload=None, env=None):
        if env is None:
            self.env = pytest.env
        else:
            self.env = env
        self.webhook_service_url = WEBHOOK_SERVICE_URL.format(self.env)
        self.api_key = api_key
        if payload == None:
            payload = ''
        logging.info(f"DEBUG !! {self.webhook_service_url}")
        self.service = HttpMethod(self.webhook_service_url, payload=payload)
        self.header = {
            "Content-Type": "application/json",
            "AUTHORIZATION": "Token token={token}".format(token=self.api_key),
            'x-appen-api-key': 'requestor-proxy-webhooks',
            'x-appen-app-name': 'requestor-proxy',
            'x-appen-api-key-version': '2'
        }

    def get_webhook_url(self):
        return 'https://webhook.site/f2a74cf2-e8d0-4bab-8582-16bd8cd9d0ab'

    @allure.step
    def make_webhook(self, job_id, team_id):
        logging.debug("Create webhook")
        payload = {
                'uri':self.get_webhook_url(),
                'object_id':str(job_id),
                'object_type': 'job',
                'team_id' : str(team_id),
                'enabled': 'true',
                'created_by':str(team_id)
        }
        return self.service.post(POST_CREATE_WEBHOOK, data=json.dumps(payload), ep_name=POST_CREATE_WEBHOOK,headers=self.header)

    @allure.step
    def ignit_webhook(self):
        logging.debug("Ignit webhook")
        payload = {
            'uri':f'{self.get_webhook_url()}'
        }
        return self.service.post(POST_IGNIT_TEST_WEBHOOK, data=json.dumps(payload), ep_name=POST_IGNIT_TEST_WEBHOOK, headers=self.header)


    @allure.step
    def check_job_hooked(self, job_id):
        logging.debug("Check is job hooked")
        assert job_id > 0, f"Job id {job_id} not found"
        url = GET_CHECK_WEBHOOK % job_id
        return self.service.get(url, self.header)




