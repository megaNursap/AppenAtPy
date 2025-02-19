from adap.api_automation.utils.http_util import HttpMethod
from adap.api_automation.services_config.endpoints.pointcloud_endpoints import *

import pytest
import allure
import logging
import json

class PointCloud:
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
    def get_healthcheck(self):
        res = self.service.get(GET_HEALTHCHECK, ep_name=GET_HEALTHCHECK)
        return res

    @allure.step
    def get_scene(self, base_url):
        res = self.service.get(GET_SCENE % base_url, ep_name=GET_SCENE)
        return res

    @allure.step
    def get_frame_binary(self, base_url):
        res = self.service.get(GET_FRAMEBINARY % base_url, ep_name=GET_FRAMEBINARY)
        return res

    @allure.step
    def get_annotation(self, base_url, file_name):
        res = self.service.get(GET_ANNOTATION % (base_url, file_name), ep_name=GET_ANNOTATION)
        return res

    @allure.step
    def submit_annotation(self, payload):
        res = self.service.put(PUT_SUBMITANNOTATION, data=json.dumps(payload), ep_name=PUT_SUBMITANNOTATION)
        return res

    @allure.step
    def post_predict_bounding_box(self, payload):
        res = self.service.post(POST_PREDICTBOX, data=json.dumps(payload), ep_name=POST_PREDICTBOX)
        return res

    @allure.step
    def get_result(self, result_url):
        res = self.service.get(GET_RESULT % result_url, ep_name=GET_RESULT)
        return res

    @allure.step
    def get_callibration(self, base_url, image_id, frame_id=None):
        if frame_id:
            res = self.service.get(GET_CALLIBRATION % (base_url, image_id) + '&frameid=%s' % frame_id, ep_name=GET_CALLIBRATION)
        else:
            res = self.service.get(GET_CALLIBRATION % (base_url, image_id), ep_name=GET_CALLIBRATION)
        return res
