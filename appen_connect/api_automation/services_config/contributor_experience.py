import json

import pytest
from bs4 import BeautifulSoup

from adap.api_automation.utils.http_util import HttpMethod
from appen_connect.api_automation.services_config.endpoints.contributor_experience import URL, POST_USER, \
    GET_ONBOARDING, POST_SIGNATURE, LOGIN, DELETE_USER, GET_PROFILE


class ContributorExperience:

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
                "Content-Type": "application/json"
            }

        self.service = HttpMethod(self.url, self.payload)

    def post_create_user(self, email, password, firstname, lastname, verificationCode="999999", ac2=True):
        payload = {
            "email": email,
            "password": password,
            "firstName": firstname,
            "lastName": lastname,
            "fromAC2": ac2,
            "verificationCode": verificationCode
        }
        res = self.service.post(POST_USER, headers=self.headers, data=json.dumps(payload))

        return res

    def get_onboarding_document(self, token=None):
        header = {
            "Content-Type": "application/json",
            "authorization": "Bearer %s" % token
        }
        res = self.service.get(GET_ONBOARDING, headers=header)
        return res

    def post_document_signature(self, payload, token=None):
        header = {
            "Content-Type": "application/json",
            "authorization": "Bearer %s" % token
        }
        res = self.service.post(POST_SIGNATURE, headers = header, data=json.dumps(payload))
        return res

    def delete_user(self, token=None):
        header = {
            "Content-Type": "application/json",
            "authorization": "Bearer %s" % token
        }
        res = self.service.post(DELETE_USER, headers=header)
        return res

    def get_profile(self, token=None):
        header = {
            "Content-Type": "application/json",
            "authorization": "Bearer %s" % token
        }
        res = self.service.get(GET_PROFILE, headers=header)
        return res

    def update_profile(self, payload, token=None):
        header = {
            "Content-Type": "application/json",
            "authorization": "Bearer %s" % token
        }
        res = self.service.put(GET_PROFILE, headers=header, data=json.dumps(payload))
        return res