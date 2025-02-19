from adap.api_automation.utils.http_util import HttpMethod
from adap.api_automation.services_config.endpoints.supersaver_endpoints import *

import pytest
import allure
import logging
import json


class SuperSaver:
    def __init__(self, custom_url=None, payload=None, env=None):
        self.payload = payload
        if env is None and custom_url is None: env = pytest.env
        self.env = env
        if custom_url:
            self.url = custom_url
        else:
            self.url = URL.format(env)

        self.service = HttpMethod(self.url, self.payload)

    @allure.step
    def post_annotation(self, payload):
        res = self.service.post(POST_ANNOTATION, data=json.dumps(payload), ep_name=POST_ANNOTATION)
        return res

    @allure.step
    def get_annotation(self, annotation_id, job_id, expire_time=600):
        res = self.service.get(GET_ANNOTATION % (annotation_id, job_id, expire_time), ep_name=GET_ANNOTATION)
        return res

    @allure.step
    def post_image_annotation(self, payload):
        res = self.service.post(POST_IMAGE_ANNOTATION, data=json.dumps(payload), ep_name=POST_IMAGE_ANNOTATION)
        return res

    @allure.step
    def put_image_annotation(self, payload):
        res = self.service.put(PUT_IMAGE_ANNOTATION, data=json.dumps(payload), ep_name=PUT_IMAGE_ANNOTATION)
        return res

    @allure.step
    def put_securelink(self, payload):
        res = self.service.put(PUT_SECURELINK, data=json.dumps(payload), ep_name=PUT_SECURELINK)
        return res

    @allure.step
    def get_securelink(self, token):
        res = self.service.get(GET_SECURELINK % token, ep_name=GET_SECURELINK)
        return res

    @allure.step
    def health_check(self):
        res = self.service.get(HEALTH_CHECK, ep_name=HEALTH_CHECK)
        return res