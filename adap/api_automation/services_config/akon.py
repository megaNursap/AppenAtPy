from adap.api_automation.utils.http_util import HttpMethod
from adap.api_automation.services_config.endpoints.akon_endpoints import *
import pytest
import allure
import logging
import urllib.parse

LOGGER = logging.getLogger(__name__)


class AkonUser:

    def __init__(self, api_key, jwt_token=None, current_team=None, api_team=None, custom_url=None, payload=None, env=None):
        self.api_key = api_key
        self.current_team_id = current_team
        self.api_team_id = api_team
        self.akon_user_id = None
        self.user_id = None
        self.payload = payload
        self.teams = []
        self.team_ids = []
        self.organization_id = None
        self.jwt_token = jwt_token

        if env is None and custom_url is None: env = pytest.env
        self.env = env
        if custom_url is not None:
            self.url = custom_url
        elif env == "hipaa":
            self.url = HIPAA
        elif env == "staging":
            self.url = STAGING
        elif env == "fed":
            if pytest.customize_fed == 'true':
                self.url = FED_CUSTOMIZE.format(pytest.customize_fed_url)
            else:
                self.url = FED.format(pytest.env_fed)
        elif env != "live":
            self.url = URL.format(env)
        else:
            self.url = PROD

        self.service = HttpMethod(self.url, self.payload)

    @allure.step
    def get_akon_info(self):
        headers = {
            'Akon-Authentication-Token': self.api_key,
            'Authorization': "Token token=%s""" % self.api_key,
            'x-cf-jwt-token': self.jwt_token
        }
        if pytest.env == "fed":
            res = self.service.get(ME_FED, headers=headers, ep_name=ME_FED)
        else:
            res = self.service.get(ME, headers=headers, ep_name=ME)
        self.current_team_id = res.json_response.get('current_team_id')
        self.api_team_id = res.json_response.get('api_team_id')
        self.akon_user_id = res.json_response.get('id')
        self.teams = res.json_response.get('teams')
        self.organization_id = res.json_response.get('organization_id')

        if res.status_code == 200:
            for i in range(len(self.teams)):
                self.team_ids.append(self.teams[i]['id'])

        return res

    @allure.step
    def switch_current_team(self, team_id, user_id=None):
        headers = {
            'Akon-Authentication-Token': self.api_key,
            'Authorization': "Token token=%s""" % self.api_key
        }
        if user_id is None:
            user_id = self.akon_user_id
        res = self.service.post(SWITCH_CURRENT_TEAM % (user_id, team_id), headers=headers, ep_name=SWITCH_CURRENT_TEAM)
        return res

    @allure.step
    def switch_api_team(self, team_id, user_id=None):
        headers = {
            'Akon-Authentication-Token': self.api_key,
            'Authorization': "Token token=%s""" % self.api_key
        }
        if user_id is None:
            user_id = self.akon_user_id
        res = self.service.post(SWITCH_API_TEAM % (user_id, team_id), headers=headers, ep_name=SWITCH_API_TEAM)
        return res

    @allure.step
    def users_in_organization(self, org_id, email=None):
        """
        :param org_id: user needs to be in an organization for this endpoint to work
        :param email: Optional param; partial or exact match; has to be urlencoded
        :return: list of user's email, akon id, teams based on email filter
        """
        headers = {
            'Akon-Authentication-Token': self.api_key,
            'Authorization': "Token token=%s""" % self.api_key,
            'x-cf-jwt-token': self.jwt_token
        }
        if email is None:
            res = self.service.get(ORG_USERS % org_id, headers=headers, ep_name=ORG_USERS)
            return res
        else:
            res = self.service.get(USERS_FILTERED_BY_EMAIL % (org_id, urllib.parse.quote(email)), headers=headers,
                                   ep_name=USERS_FILTERED_BY_EMAIL)
            return res

    @allure.step
    def users_in_organization_paginated(self, org_id, page=None, per_page=None):
        headers = {
            'Akon-Authentication-Token': self.api_key,
            'Authorization': "Token token=%s""" % self.api_key
        }

        res = self.service.get(PAGINATED_USERS % (org_id, page, per_page), headers=headers, ep_name=PAGINATED_USERS)
        return res

    @allure.step
    def get_auth_for_wf(self):
        res = self.service.get(GET_JWT_FOR_AMBASSADOR % self.api_key, ep_name=GET_JWT_FOR_AMBASSADOR)
        return res

    @allure.step
    def user_belongs_to_team(self, user_email, team_id, org_id):
        teams = self.users_in_organization(org_id, user_email).json_response['users'][0]['teams']
        assert len(teams) > 0, "No teams have been found"
        for team in teams:
            if team['id'] == team_id:
                    return True
        return False

    @allure.step
    def get_auth_data(self, env=None):
        if not env:
            env = pytest.env

        headers = {
            'AUTHORIZATION': f'Token token={self.api_key}',
            'Host': f'api.{env}.cf3.us'
        }
        res = self.service.get(AUTH, headers=headers, ep_name=AUTH)

        return res


    @allure.step
    def get_appen_jwt_token(self):
        res = self.get_auth_data()
        return res.headers['x-appen-jwt']
