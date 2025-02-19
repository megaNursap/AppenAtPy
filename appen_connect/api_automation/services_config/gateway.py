import allure
import pytest
import json

from adap.api_automation.utils.http_util import HttpMethod
from appen_connect.api_automation.services_config.endpoints.gateway import *


class AC_GATEWAY:
    def __init__(self, cookies=None, payload=None, custom_url=None, headers=None, env=None):
        self.payload = payload
        self.cookies = cookies

        if env is None and custom_url is None:  env = pytest.env
        self.env = env

        if custom_url is not None:
            self.url = custom_url
        else:
            self.url = URL(self.env)

        if not headers:
            self.headers = {
                'accept': 'application/json',
                'Content-Type': 'text/plain'
            }

        self.service = HttpMethod(self.url, self.payload)

    @allure.step
    def get_master_profile_questions(self, cookies=None, compact=None, **kwargs):
        if not cookies:
            cookies = self.cookies

        _params = ''
        if compact:
            _params = '?compact=%s' % compact

        res = self.service.get(MASTER_PROFILE_QUESTIONS+_params, headers=self.headers, cookies=cookies,
                               ep_name=MASTER_PROFILE_QUESTIONS, **kwargs)
        return res

    @allure.step
    def get_question_categories(self, cookies=None):
        if not cookies:
            cookies = self.cookies

        res = self.service.get(QUESTION_CATEGORIES, headers=self.headers, cookies=cookies, ep_name=QUESTION_CATEGORIES)
        return res

    @allure.step
    def create_profile_targets(self, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        res = self.service.post(CREATE_PROFILE_TARGETS, data=json.dumps(payload), headers=headers,
                                cookies=cookies, ep_name=CREATE_PROFILE_TARGETS)
        return res


    @allure.step
    def get_profile_targets(self, target_id, cookies=None):

        if not cookies:
            cookies = self.cookies

        res = self.service.get(GET_PROFILE_TARGETS.format(target_id=target_id), headers=self.headers, cookies=cookies,
                               ep_name=GET_PROFILE_TARGETS)
        return res

    @allure.step
    def get_question_types(self, cookies=None):
        if not cookies:
            cookies = self.cookies

        res = self.service.get(QUESTION_TYPES, headers=self.headers, cookies=cookies, ep_name=QUESTION_TYPES)
        return res

    @allure.step
    def post_master_profile_question(self, payload, cookies=None, **kwargs):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        res = self.service.post(MASTER_PROFILE_QUESTIONS, data=json.dumps(payload), headers=headers,
                                cookies=cookies, ep_name=MASTER_PROFILE_QUESTIONS, **kwargs)
        return res

    @allure.step
    def delete_master_profile_targets(self, question_id, cookies=None):

        if not cookies:
            cookies = self.cookies

        res = self.service.delete(MASTER_PROFILE_QUESTIONS_ID.format(id=question_id), headers=self.headers, cookies=cookies,
                               ep_name=MASTER_PROFILE_QUESTIONS_ID)
        return res

    @allure.step
    def get_master_profile_question_by_id(self, question_id, cookies=None):
        if not cookies:
            cookies = self.cookies

        res = self.service.get(MASTER_PROFILE_QUESTIONS_ID.format(id=question_id), headers=self.headers, cookies=cookies,
                               ep_name=MASTER_PROFILE_QUESTIONS_ID)
        return res

    @allure.step
    def put_master_profile_question_by_id(self, question_id, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': '*/*',
            'Content-Type': 'application/json'
        }

        res = self.service.put(MASTER_PROFILE_QUESTIONS_ID.format(id=question_id), headers=headers,
                               data=json.dumps(payload),
                               cookies=cookies, ep_name=MASTER_PROFILE_QUESTIONS)
        return res

    @allure.step
    def get_user_match_project(self, user_id, project_id, cookies=None):
        if not cookies:
            cookies = self.cookies

        res = self.service.get(USER_MATCH_PROJECT.format(user_id=user_id, project_id=project_id), headers=self.headers,
                               cookies=cookies,
                               ep_name=USER_MATCH_PROJECT)
        return res



