from adap.api_automation.utils.http_util import HttpMethod
from adap.api_automation.services_config.endpoints.management_endpoints import *

import pytest
import allure
import logging
import json
# always used

LOGGER = logging.getLogger(__name__)
# always used


class Management:

    def __init__(self, api_key, custom_url=None, payload=None, env=None):
        self.payload = payload
        self.api_key = api_key
        if env is None and custom_url is None: env = pytest.env
        self.env = env
        if custom_url:
            self.url = custom_url
        elif env == "fed":
            if pytest.customize_fed == 'true':
                self.url = FED_CUSTOMIZE.format(pytest.customize_fed_url)
            else:
                self.url = FED.format(pytest.env_fed)
        elif env != "live":
            self.url = URL.format(env)
        else:
            self.url = PROD

        self.headers = {
            'Authentication-Token': self.api_key,
            'Content-Type': 'application/json'
        }
        self.service = HttpMethod(self.url, self.payload)


    @allure.step
    def create_user(self, payload):
        res = self.service.post(NEW_USER, headers=self.headers, data=json.dumps(payload), ep_name=NEW_USER)
        return res

    @allure.step
    def update_user_attributes(self, user_email, payload):
        res = self.service.put(USER.format(email=user_email), headers=self.headers, data=json.dumps(payload), ep_name=USER)
        return res


    @allure.step
    def make_user_team_admin(self, user_email):
        res = self.service.post(TEAM_ADMIN.format(email=user_email), headers=self.headers,  ep_name=TEAM_ADMIN)
        return res

    @allure.step
    def revoke_user_team_admin_access(self, user_email):
        res = self.service.delete(TEAM_ADMIN.format(email=user_email), headers=self.headers, ep_name=TEAM_ADMIN)
        return res

    @allure.step
    def make_user_org_admin(self, user_email):
        res = self.service.post(ORG_ADMIN.format(email=user_email), headers=self.headers, ep_name=ORG_ADMIN)
        return res

    @allure.step
    def revoke_user_org_admin_access(self, user_email):
        res = self.service.delete(ORG_ADMIN.format(email=user_email), headers=self.headers, ep_name=ORG_ADMIN)
        return res

    @allure.step
    def disable_user(self, user_email):
        res = self.service.post(DISABLE_USER.format(email=user_email), headers=self.headers, ep_name=DISABLE_USER)
        return res

    @allure.step
    def move_user_to_team(self, user_email, team_id):
        res = self.service.post(MOVE_USER_TO_TEAM.format(email=user_email, team_id=team_id), headers=self.headers, ep_name=MOVE_USER_TO_TEAM)
        return res

    @allure.step
    def create_userless_team(self, payload):
        res = self.service.post(USER_LESS_TEAM, headers=self.headers, data=json.dumps(payload), ep_name=USER_LESS_TEAM)
        return res

