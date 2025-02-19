import json

import allure
import pytest

from adap.api_automation.utils.http_util import HttpMethod
from appen_connect.api_automation.services_config.endpoints.sql_report_service import *


class SqlReportService:
    def __init__(self, cookies=None, payload=None, custom_url=None, headers=None, env=None):
        self.payload = payload
        self.cookies = cookies

        if env is None and custom_url is None:  env = pytest.env
        self.env = env

        if custom_url is not None:
            self.url = custom_url
        else:
            self.url = URL(env=pytest.env)

        if not headers:
            self.headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Cache-Control": "no-cache"
            }
        self.service = HttpMethod(self.url, self.payload)

    @allure.step
    def get_report_by_id(self, report_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(REPORT_SESSION_BY_ID.format(id=report_id), headers=self.headers, cookies=cookies,
                               ep_name=REPORT_SESSION_BY_ID)
        return res

    @allure.step
    def create_report_session(self, payload=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        self.headers1 = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
        res = self.service.post(REPORT_SESSION,
                                headers=self.headers1,
                                cookies=cookies,
                                data=json.dumps(payload), ep_name=REPORT_SESSION)
        return res


    @allure.step
    def update_report_session_by_id(self, report_id=None, payload=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        self.headers1 = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
        res = self.service.put(REPORT_SESSION_BY_ID.format(id=report_id),
                                headers=self.headers1,
                                cookies=cookies,
                                data=json.dumps(payload), ep_name=REPORT_SESSION_BY_ID)
        return res

    @allure.step
    def download_report_session_by_id(self, report_id=None, payload=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        self.headers1 = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
        res = self.service.get(REPORT_SESSION_DOWNLOAD.format(id=report_id),
                               headers=self.headers1,
                               cookies=cookies,
                               ep_name=REPORT_SESSION_DOWNLOAD)
        return res


    @allure.step
    def get_template_by_id(self, template_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(REPORT_TEMPLATE_BY_ID.format(id=template_id), headers=self.headers, cookies=cookies,
                               ep_name=REPORT_TEMPLATE_BY_ID)
        return res
    @allure.step
    def create_template(self, payload=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        self.headers1 = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
        res = self.service.post(REPORT_TEMPLATE, headers=self.headers1, cookies=cookies, data=json.dumps(payload),
                               ep_name=REPORT_TEMPLATE)
        return res

    @allure.step
    def update_template(self, template_id= None, payload=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        self.headers1 = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
        res = self.service.put(REPORT_TEMPLATE_BY_ID.format(id=template_id), headers=self.headers1, cookies=cookies, data=json.dumps(payload),
                               ep_name=REPORT_TEMPLATE_BY_ID)
        return res
    @allure.step
    def delete_template(self, template_id= None, payload=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        self.headers1 = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
        res = self.service.delete(REPORT_TEMPLATE_BY_ID.format(id=template_id), headers=self.headers1, cookies=cookies, data=json.dumps(payload),
                               ep_name=REPORT_TEMPLATE_BY_ID)
        return res

    @allure.step
    def get_template_categories(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(REPORT_TEMPLATE_CATEGORIES, headers=self.headers, cookies=cookies,
                               ep_name=REPORT_TEMPLATE_CATEGORIES)
        return res
    @allure.step
    def get_templates(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(REPORT_TEMPLATE, headers=self.headers, cookies=cookies,
                               ep_name=REPORT_TEMPLATE)
        return res
