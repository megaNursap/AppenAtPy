
from locust import TaskSet, task, between, events
import json
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

password = get_user('test_ui_account', env=env).get('password')



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

    login_page = api.get(f'{url}/sessions/new', headers={"Accept": "text/html", "Origin": url}, allow_redirects=False,
                         ep_name='/sessions/new')

    if login_page.status_code != 200:
        log.error({
            'message': 'Error response',
            'resp.status_code': login_page.status_code,
            'resp.status_message': getattr(login_page, 'status_message', ''),
            'resp.text': getattr(login_page, 'text', ''),
            'resp.url': getattr(login_page, 'url', ''),
            'endpoint': '/sessions/new'
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
        'Origin': url
    }

    cookies = {
        '_make_session': login_page.cookies['_make_session']
    }

    result = api.post(f'{url}/sessions', cookies=cookies, data=params, headers=headers, allow_redirects=False,
                      ep_name='/sessions')

    if result.status_code != 302:
        log.error({
            'message': 'Error response',
            'resp.status_code': result.status_code,
            'resp.status_message': getattr(login_page, 'status_message', ''),
            'resp.text': getattr(login_page, 'text', ''),
            'resp.url': getattr(login_page, 'url', ''),
            'session': '/sessions/new'
        })
        return
    return result.cookies, csrf_token


class LocustUserBehavior(TaskSet):

    data_source_env_paths = {
        'integration': 'integration_requestor_emails_new.csv'
    }

    def on_start(self):
        self.service = HttpMethod()
        username = self.get_requestor_email()
        self.cookies, self.csrf_token = get_sid_cookies_and_token(env, username, password, self.service)
        self.base_url = URL
        self.account = username



    def get_contributor_email(self):
        log.debug("Reading contrib emails input data...")
        data_source = Config.DATA_SOURCE_PATH
        data = read_csv(data_source)
        email = random.choice(data['worker_email']).lstrip("\ufeff")
        log.info(f"Current contributor email {email}")
        assert email, f'contributor email not found in {data_source}'
        return email


    def get_requestor_email(self):
        data_source = self.data_source_env_paths[env]
        path = f"adap/perf_platform/test_data/{data_source}"
        data = read_csv(path)
        email = random.choice(data['worker_email']).lstrip("\ufeff")
        log.info(f"Current requestor email {email}")
        assert email, f'requestor email not found in {path}'
        return email


    def _ping_endpoint(self):
        _endpoint = random.choice(endpoints)
        resp = self.service.get(
            self.base_url + _endpoint,
            headers={"content-type": "application/json", "Origin": self.base_url},
            ep_name='%.30s' % _endpoint,
            cookies=self.cookies
        )

        if resp.status_code not in [200, 201]:
            log.error({
                'message': 'Error response',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'account': self.account,
                'endpoint': _endpoint
            })
            return

    def _create_job(self):
        payload = {"authenticityToken": self.csrf_token}
        resp = self.service.post(
                       self.base_url + "/v1/jobs/scratch",
                       headers={"content-type": "application/json", "Origin": self.base_url},
                       data=json.dumps(payload),
                       cookies=self.cookies,
                       ep_name="/v1/jobs/scratch"
        )

        if resp.status_code != 200:
            log.error({
                'message': 'Error response',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'account': self.account,
                'endpoint': "/v1/jobs/scratch"
            })
            return

        job_id = resp.json_response['job_id']

        res = self.service.delete(
                       self.base_url + f"/v1/jobs/{job_id}",
                       headers={"content-type": "application/json", "Origin": self.base_url},
                       data=json.dumps(payload),
                       cookies=self.cookies,
                       ep_name=f"/v1/jobs/<job_id>"
        )

        if resp.status_code != 200:
            log.error({
                'message': 'Error response',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'account': self.account,
                'endpoint': "DELETE /v1/jobs/<job_id>"
            })
            return
        print(res.status_code)
        print(res.json_response)

    def _create_wf(self):
        resp = self.service.get(
                        self.base_url + "/v1/workflows?page=1&perPage=30&query=&userId=",
                        ep_name="/v1/workflows",
                        headers={"Origin": self.base_url},
                        cookies=self.cookies)

        if resp.status_code != 200:
            log.error({
                'message': 'Error response: get WF page',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'account': self.account,
                'endpoint': "/v1/workflows"
            })
            return

        payload = {"name": "WF perf test"}
        resp = self.service.post(
                    self.base_url+"/v1/workflows",
                    headers={"content-type": "application/json", "Origin": self.base_url},
                    data=json.dumps(payload),
                    ep_name="/v1/workflows",
                    cookies=self.cookies)

        if resp.status_code != 201:
            log.error({
                'message': 'Error response: create WF',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'account': self.account,
                'endpoint': "/v1/workflows"
            })
            return

        print(resp.status_code)
        print(resp.json_response)

        wf_id = resp.json_response['id']

        resp = self.service.get(
                       self.base_url+f"/v1/workflows/{wf_id}",
                       headers={"Origin": self.base_url},
                       ep_name="/v1/workflows/{wf_id}",
                       cookies=self.cookies)

        if resp.status_code != 200:
            log.error({
                'message': f'Error response: get WF {wf_id}',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'account': self.account,
                'endpoint': "/v1/workflows"
            })
            return

        resp = self.service.get(
                       self.base_url + f"/v1/workflows/{wf_id}/steps",
                       headers={"Origin": self.base_url},
                       ep_name="/v1/workflows/{wf_id}/steps",
                       cookies=self.cookies)

        if resp.status_code != 200:
            log.error({
                'message': f'Error response: get WF {wf_id} steps',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'account': self.account,
                'endpoint': "/v1/workflows/<wf_id>/steps"
            })
            return

        resp = self.service.get(
                     self.base_url + f"/v1/workflows/{wf_id}/data_uploads",
                     headers={"Origin": self.base_url},
                     ep_name="/v1/workflows/{wf_id}/data_uploads",
                     cookies=self.cookies)

        if resp.status_code != 200:
            log.error({
                'message': f'Error response: get WF {wf_id} data uploads',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'account': self.account,
                'endpoint': "/v1/workflows/<wf_id>/data_uploads"
            })
            return

        resp = self.service.delete(
                         self.base_url + f"/v1/workflows/{wf_id}",
                         headers={"content-type": "application/json", "Origin": self.base_url},
                         ep_name="/v1/workflows/{wf_id}",
                         cookies=self.cookies)

        if resp.status_code != 200:
            log.error({
                'message': f'Error response: delete WF {wf_id}',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'account': self.account,
                'endpoint': "/v1/workflows/<wf_id>"
            })
            return


    def _login_as_contributor(self):
        username = self.get_contributor_email()

        cont_api = HttpMethod()

        base_url = "https://account.integration.cf3.us/auth/keycloak"

        resp = cont_api.get(
            base_url,
            headers={'Content-Type': 'text/html', "Origin": base_url},
            ep_name='1_get_login_url',
            allow_redirects=True
        )

        if resp.status_code != 200:
            log.error({
                'message': 'Error response:/auth/keycloak ',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'endpoint': "/auth/keycloak",
                'account': username
            })
            return

        soup = BeautifulSoup(resp.text, 'html.parser')
        login_form_cookies = resp.cookies
        auth_url = soup.find('form', {'id': 'kc-form-login'}).get('action')

        if not auth_url:
            log.error({
                'message': 'Error: redirectUrl - not found',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'endpoint': "/auth/keycloak",
                'account': username
            })
            return

        sign_in_resp = cont_api.post(
            auth_url,
            data={
                'username': username,
                'password': password
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded', "Origin": auth_url},
            cookies=login_form_cookies,
            allow_redirects=False,
            ep_name='2_contributor_sign_in'
        )

        if sign_in_resp.status_code != 302:
            log.error({
                'message': 'Error response: contributor sign in',
                'resp.status_code': sign_in_resp.status_code,
                'resp.status_message': getattr(sign_in_resp, 'status_message', ''),
                'resp.text': getattr(sign_in_resp, 'text', ''),
                'resp.url': getattr(sign_in_resp, 'url', ''),
                'endpoint': "/login-actions/authenticate",
                'account': username
            })
            return

        callback_resp = cont_api.get(
            sign_in_resp.headers.get('location'),
            headers={'Content-Type': 'text/html', "Origin": auth_url},
            ep_name='3_contributor_callback',
            allow_redirects=False
        )

        if callback_resp.status_code != 302:
            log.error({
                'message': 'Error response: contributor callback',
                'resp.status_code': callback_resp.status_code,
                'resp.status_message': getattr(callback_resp, 'status_message', ''),
                'resp.text': getattr(callback_resp, 'text', ''),
                'resp.url': getattr(callback_resp, 'url', ''),
                'endpoint': "auth/keycloak/callback",
                'account': username
            })
            return

        location_url = callback_resp.headers.get('location')
        if not location_url:
            log.error({
                'message': 'Error: location_url - not found',
                'resp.status_code': callback_resp.status_code,
                'resp.status_message': getattr(callback_resp, 'status_message', ''),
                'resp.text': getattr(callback_resp, 'text', ''),
                'resp.url': getattr(callback_resp, 'url', ''),
                'account': username
            })
            return

        resp = cont_api.get(
            location_url,
            headers={'Content-Type': 'text/html', "Origin": location_url},
            ep_name='4_account',
            allow_redirects=True,
            cookies=callback_resp.cookies
        )

        if resp.status_code != 200:
            log.error({
                'message': 'Error response: contributor callback',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'endpoint': "/account",
                'account': username
            })
            return


    @task(3)
    def ping_random_endpoint(self):
        self.client.locust_event(
            "Execute task",  # Requst type
            "ping_random_endpoint",  # Requst name
            self._ping_endpoint,
        )

    @task(2)
    def create_job_adap(self):
        self.client.locust_event(
            "Execute task",  # Requst type
            "create_job",  # Requst name
            self._create_job,
        )

    @task(1)
    def create_wf_adap(self):
        self.client.locust_event(
            "Execute task",  # Requst type
            "create_wf",  # Requst name
            self._create_wf,
        )

    @task(1)
    def login_contributor(self):
        self.client.locust_event(
            "Execute task",  # Requst type
            "login_as_contributor",  # Requst name
            self._login_as_contributor,
        )


class LocustUser(CustomLocust):
    wait_time = between(0.001, 0.001)
    task_set = LocustUserBehavior

    def __init__(self):
        self.host = ''
        super(LocustUser, self).__init__()
