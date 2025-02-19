from adap.api_automation.utils.http_util import HttpMethod
from adap.api_automation.services_config.endpoints.textannotation_endpoints import *

import pytest
import allure
import logging
import json


class TextAnnotation:
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
    def put_securelink(self, payload):
        res = self.service.put(PUT_SECURELINK, data=json.dumps(payload), ep_name=PUT_SECURELINK)
        return res

    @allure.step
    def get_securelink(self, token):
        res = self.service.get(GET_SECURELINK % token, ep_name=GET_SECURELINK)
        return res

    @allure.step
    def post_grade(self, payload):
        res = self.service.post(GRADE_RESULT, data=json.dumps(payload), ep_name=GRADE_RESULT)
        return res

    @allure.step
    def put_grade(self, payload):
        res = self.service.put(GRADE_RESULT, data=json.dumps(payload), ep_name=GRADE_RESULT)
        return res

    @allure.step
    def post_accuracy_details(self, payload):
        res = self.service.post(ACCURACY_DETAILS, data=json.dumps(payload), ep_name=ACCURACY_DETAILS)
        return res

    @allure.step
    def generate_aggregated_report(self, payload):
        res = self.service.post(AGGREGATED_REPORT, data=json.dumps(payload), ep_name=AGGREGATED_REPORT)
        return res