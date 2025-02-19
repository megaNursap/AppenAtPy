import json

import allure
import pytest

from adap.api_automation.utils.http_util import HttpMethod

from appen_connect.api_automation.services_config.endpoints.user_service import *


class UserService:

    def __init__(self, cookies=None, payload=None, custom_url=None, headers=None, env=None):
        self.payload = payload
        self.cookies = cookies

        if env is None and custom_url is None:  env = pytest.env
        self.env = env

        if custom_url is not None:
            self.url = custom_url
        else:
            self.url = URL(pytest.env)

        if not headers:
            self.headers = {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache"
            }

        self.service = HttpMethod(self.url, self.payload)

    @allure.step
    def get_demographics_complexions(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(DEMOGRAPHICS_COMPLEXIONS, headers={'Content-Type': 'text/plain'}, cookies=cookies,
                               ep_name=DEMOGRAPHICS_COMPLEXIONS)
        return res

    @allure.step
    def get_demographics_disability_types(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(DEMOGRAPHICS_DISABILITY_TYPES, headers={'Content-Type': 'text/plain'}, cookies=cookies,
                               ep_name=DEMOGRAPHICS_DISABILITY_TYPES)
        return res

    @allure.step
    def get_demographics_ethnicities(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(DEMOGRAPHICS_ETHNICITIES, headers={'Content-Type': 'text/plain'}, cookies=cookies,
                               ep_name=DEMOGRAPHICS_ETHNICITIES)
        return res

    @allure.step
    def get_demographics_genders(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(DEMOGRAPHICS_GENDERS, headers={'Content-Type': 'text/plain'}, cookies=cookies,
                               ep_name=DEMOGRAPHICS_GENDERS)
        return res

    @allure.step
    def get_education_levels(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(EDUCATION_LEVELS, headers={'Content-Type': 'text/plain'}, cookies=cookies,
                               ep_name=EDUCATION_LEVELS)
        return res

    @allure.step
    def get_linguistics_qualification(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(LINGUISTICS_QUALIFICATION, headers={'Content-Type': 'text/plain'}, cookies=cookies,
                               ep_name=LINGUISTICS_QUALIFICATION)
        return res

    @allure.step
    def verify_email(self, payload):
        res = self.service.post(VERIFY_EMAIL, headers={'Content-Type': 'text/plain'}, data=json.dumps(payload),
                                ep_name=VERIFY_EMAIL)
        return res

    @allure.step
    def new_vendor(self, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.post(NEW_USER, headers={'Content-Type': 'application/json'}, data=json.dumps(payload),
                                cookies=cookies, ep_name=NEW_USER)
        return res

    @allure.step
    def get_vendor_profile(self, id, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(USER_PROFILE.format(id=id), headers={'Content-Type': 'text/plain'}, cookies=cookies,
                               ep_name=USER_PROFILE)
        return res

    @allure.step
    def update_vendor_profile(self, id, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.put(USER_PROFILE.format(id=id), data=json.dumps(payload), headers={'accept': '*/*',
                                                                                              'Content-Type': 'application/json'},
                               cookies=cookies,
                               ep_name=USER_PROFILE)
        return res

    @allure.step
    def get_all_false_positive(self, cookies=None):
        if not cookies:
            cookies = self.cookies

        res = self.service.get(FALSE_POSITIVE, cookies=cookies, ep_name=FALSE_POSITIVE)
        return res

    @allure.step
    def get_false_positive_by_user(self, user_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies

        res = self.service.get(FALSE_POSITIVE_USER.format(user_id=user_id), cookies=cookies, ep_name=FALSE_POSITIVE_USER)
        return res

    @allure.step
    def post_false_positive_by_user(self, payload, cookies=None):
        if not cookies:
            cookies = self.cookies

        res = self.service.post(FALSE_POSITIVE, headers={'Content-Type': 'application/json'}, data=json.dumps(payload),
                                ep_name=FALSE_POSITIVE,  cookies=cookies)
        return res

    @allure.step
    def put_false_positive_by_user(self, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.put(FALSE_POSITIVE, data=json.dumps(payload), headers={'accept': '*/*',
                                                                                              'Content-Type': 'application/json'},
                               cookies=cookies,
                               ep_name=FALSE_POSITIVE)
        return res

    @allure.step
    def post_create_ip_mask(self, vendor_email, vendor_ip, cookies=None):
        if not cookies:
            cookies = self.cookies

        payload = {
            "email": vendor_email,
            "ip": vendor_ip
        }

        res = self.service.post(USER_IP_MASK, headers={'Content-Type': 'application/json'}, data=json.dumps(payload),
                                ep_name=USER_IP_MASK,  cookies=cookies)
        return res

    @allure.step
    def get_ip_exists(self, vendor_ip=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        params = {
            'ip': vendor_ip
        }
        res = self.service.get(USER_IP_MASK_CHECK, params=params,cookies=cookies, ep_name=FALSE_POSITIVE_USER)
        return res

    @allure.step
    def whitelist_ip(self, vendor_email, vendor_ip, cookies=None):
        if not cookies:
            cookies = self.cookies

        ip_exist = self.get_ip_exists(vendor_ip=vendor_ip, cookies=cookies)
        assert ip_exist.status_code == 200, ip_exist.text
        assert not ip_exist.json_response, "IP already exists in the system"

        res = self.post_create_ip_mask(vendor_email, vendor_ip, cookies=cookies)
        assert res.status_code == 200
        assert res.json_response['email'] == vendor_email, "Error: IP is not whitelisted for vendor"

        return res

