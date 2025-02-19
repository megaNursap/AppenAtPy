
from locust import TaskSet, task, between, events

import time
from bs4 import BeautifulSoup
from adap.api_automation.services_config.endpoints.client import URL as client_url
from pandas import read_csv
from adap.api_automation.utils.data_util import get_user
from adap.api_automation.utils.http_util import HttpMethod

from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.custom_locust import (
    CustomLocust,
    on_master_start_hatching,
    on_worker_listener
)
from adap.perf_platform.utils.data_feed import SourceDataReader
from adap.settings import Config
import random
import pytest

pytest.appen = 'false'

log = get_logger(__name__, stdout=False)

env = 'integration'
URL = f"https://requestor-proxy.{env}.cf3.us"
ORIGIN = f"https://client.{env}.cf3.us"

password = get_user('test_ui_account', env=env).get('password')

path = "adap/perf_platform/test_data/integration_contributor_emails_new.csv"
data = read_csv(path)
lst_setup = data['worker_email']

endpoints = [
    "/v1/me",
    "/v1/release_notes",
    "/v1/feature_list",
    "/v1/job_templates/template_types",
    "/v1/jobs/search?page=1&perPage=25&teamId=&visibility=team",
    "/v1/jobs/search?fields=alias&fields=id&fields=owner_email&fields=tags&fields=title&page=1&perPage=25&project=all"
    "&scope=user&state=all&tag=all&teamId=&visibility=user"
]

events.master_start_hatching += on_master_start_hatching
# Start ZMQ listener on workers for workload changes
if Config.WORKLOAD:
    events.locust_start_hatching += on_worker_listener

if Config.DATA_SOURCE_PATH:
    log.debug("Reading input data...")
    sdr = SourceDataReader(Config.DATA_SOURCE_PATH)
    INPUT_DATA = sdr.read()
    random.shuffle(INPUT_DATA)
    log.debug(f"{len(INPUT_DATA)} records read")


def get_sid_cookies_and_token(requested_env, username, user_password, api):
    url = client_url.format(env=requested_env)

    login_page = api.get(f'{url}/sessions/new', headers={"Accept": "text/html", "Origin": ORIGIN}, allow_redirects=False,
                         ep_name='/sessions/new')

    if login_page.status_code != 200:
        log.error({
            'resp.status_code': login_page.status_code,
            'message': 'Error response',
            'resp.status_message': getattr(login_page, 'status_message', ''),
            'resp.text': getattr(login_page, 'text', ''),
            'resp.url': getattr(login_page, 'url', ''),
            'endpoint': '/sessions/new',
            'account': username
        })
        return

    soup = BeautifulSoup(login_page.text, features='html.parser')
    csrf_token = soup.find("meta", {"name": "csrf-token"})['content']

    params = {
        "authenticity_token": csrf_token,
        "session[email]": username,
        "session[password]": user_password
    }

    headers = {
        'Accept': "text/html",
        'Content-Type': "application/x-www-form-urlencoded",
        'Origin': ORIGIN
    }

    cookies = {
        '_make_session': login_page.cookies['_make_session']
    }

    result = api.post(f'{url}/sessions', cookies=cookies, data=params, headers=headers, allow_redirects=False,
                      ep_name='/sessions')

    if result.status_code != 302:
        log.error({
            'resp.status_code': result.status_code,
            'message': 'Error response',
            'resp.status_message': getattr(login_page, 'status_message', ''),
            'resp.text': getattr(login_page, 'text', ''),
            'resp.url': getattr(login_page, 'url', ''),
            'session': '/sessions/new',
            'account': username
        })
        return
    return result.cookies, csrf_token


class LocustUserBehavior(TaskSet):

    data_source_env_paths = {
        'integration': 'integration_contributor_emails_new.csv'
    }

    def on_start(self):
        username = "Not_exist"

        self.service = HttpMethod()
        username = self.get_contributor_email()
        self.cookies, self.csrf_token = get_sid_cookies_and_token(env, username, password, self.service)
        self.base_url = URL
        self.account = username
        self._ping_endpoint_me()
        time.sleep(2100)


    def get_contributor_email(self):
        global lst_setup
        email = 'not exist'
        length = len(lst_setup)
        assert length > 0, "error: List of emails empty"
        if length > 0:
            get_email = lst_setup.pop(length-1)
            email = get_email.lstrip("\ufeff")
        log.info(f"Current contributor email {email}")
        assert email, 'contributor email not found'
        return email


    def _ping_endpoint(self):
        _endpoint = random.choice(endpoints)
        resp = self.service.get(
            self.base_url + _endpoint,
            headers={"content-type": "application/json", "Origin": ORIGIN},
            ep_name='%.30s' % _endpoint,
            cookies=self.cookies
        )

        if resp.status_code not in [302, 403]:
            log.error({
                'resp.status_code': resp.status_code,
                'message': 'Error response',
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'account': self.account,
                'endpoint': _endpoint
            })
            return


    def _ping_endpoint_me(self):
        _endpoint = "/v1/me"
        resp = self.service.get(
            self.base_url + _endpoint,
            headers={"content-type": "application/json", "Origin": ORIGIN},
            ep_name='%.30s' % _endpoint,
            cookies=self.cookies
        )

        if resp.status_code not in [302, 200]:
            log.error({
                'resp.status_code': resp.status_code,
                'message': 'Error response',
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'account': self.account,
                'endpoint': _endpoint
            })
            return


    @task(3)
    def ping_random_endpoint(self):
        self.client.locust_event(
            "Execute task",  # Request type
            "ping_random_endpoint",  # Request name
            self._ping_endpoint,
        )


class LocustUser(CustomLocust):
    wait_time = between(0.001, 0.001)

    task_set = LocustUserBehavior

    def __init__(self):
        self.host = ''
        super(LocustUser, self).__init__()
