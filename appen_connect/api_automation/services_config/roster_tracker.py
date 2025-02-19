import json

import allure
import pytest

from adap.api_automation.utils.http_util import HttpMethod
from appen_connect.api_automation.services_config.endpoints.roster_tracker import *


class RosterTracker:
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
    def get_trackers_by_id(self, tracker_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(GET_TRACKER.format(trackerId=tracker_id), headers=self.headers, cookies=cookies,
                               ep_name=GET_TRACKER)
        return res

###  PRODUCTIVITY_TRACKER APIs of Roster tracker

    @allure.step
    def get_productivity_metrics_by_id(self, tracker_id=None, metric_id=None, payload=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(PRODUCTIVITY_METRICS.format(projectId=tracker_id, metricId=metric_id),
                               headers=self.headers,
                               cookies=cookies, params=payload, ep_name=PRODUCTIVITY_METRICS)
        return res

    @allure.step
    def get_quality_metrics_by_id(self, tracker_id=None, metric_id=None, payload=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(QUALITY_METRICS.format(projectId=tracker_id, metricId=metric_id), headers=self.headers,
                               cookies=cookies, params=payload, ep_name=QUALITY_METRICS)
        return res

    @allure.step
    def get_tracker_markets(self, tracker_id=None, metric_id=None, payload=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(MARKETS.format(trackerId=tracker_id), headers=self.headers, cookies=cookies,
                               params=payload,
                               ep_name=MARKETS)
        return res

    @allure.step
    def get_workers_of_market(self, tracker_id=None, market=None, payload=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(WORKERS.format(trackerId=tracker_id, market=market), headers=self.headers,
                               cookies=cookies,
                               params=payload, ep_name=WORKERS)
        return res

    @allure.step
    def get_metrics_of_market(self, tracker_id=None, market=None, payload=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(METRICS.format(trackerId=tracker_id, market=market), headers=self.headers,
                               cookies=cookies,
                               params=payload, ep_name=METRICS)
        return res

    @allure.step
    def post_export_workers(self, tracker_id=None, market=None, payload=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.post(WORKERS_EXPORT.format(trackerId=tracker_id, market=market), headers=headers,
                                cookies=cookies, data=json.dumps(payload), ep_name=WORKERS_EXPORT)
        return res

    @allure.step
    def post_export_all_workers(self, tracker_id=None, market=None, payload=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.post(WORKERS_EXPORT_ALL.format(trackerId=tracker_id, market=market), headers=headers,
                                cookies=cookies, data=json.dumps(payload), ep_name=WORKERS_EXPORT_ALL)
        return res

    @allure.step
    def get_goals_history(self, project_id=None, payload=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(GOALS_HISTORY.format(projectId=project_id), headers=self.headers,
                               cookies=cookies,
                               params=payload, ep_name=GOALS_HISTORY)
        return res

    @allure.step
    def post_project_goals(self, payload=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.post(GOALS, headers=headers,
                                cookies=cookies, data=json.dumps(payload), ep_name=GOALS)
        return res

    @allure.step
    def get_project_metrics(self, project_id=None, payload=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(GET_METRICS + "?projectId={id}".format(id=project_id), headers=self.headers,
                               cookies=cookies,
                               params=payload, ep_name=GET_METRICS)
        return res

    @allure.step
    def post_project_metrics(self, payload=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        self.headers1 = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
        res = self.service.post(POST_METRICS, headers=self.headers1,
                                cookies=cookies,
                                data=json.dumps(payload), ep_name=POST_METRICS)
        return res


###  ONBOARDING_TRACKER APIs of Roster tracker

    @allure.step
    def get_onboarding_trackers_by_id(self, tracker_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(GET_ONBOARDING_TRACKER.format(trackerId=tracker_id)+"?trackerId={id}".format(id=tracker_id), headers=self.headers, cookies=cookies,
                               ep_name=GET_TRACKER)
        return res

    @allure.step
    def post_project_onboarding_metrics(self, payload=None, project_id=None, market_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        self.headers1 = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
        res = self.service.post(EXPORT_ONBOARDING_TRACKER_PER_MARKET.format(projectId=project_id, marketId=market_id), headers=self.headers1,
                                cookies=cookies,
                                data=json.dumps(payload), ep_name=POST_METRICS)
        return res





