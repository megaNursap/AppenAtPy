import os
from bs4 import BeautifulSoup
from locust import TaskSet, task, between, events
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



pytest.appen = 'true'

log = get_logger(__name__, stdout=False)

env = os.environ['ENV']

base_urls = {
    'stage': 'https://feca-proxy.integration.cf3.us/auth/keycloak',
    'qa': 'https://feca-proxy.sandbox.cf3.us/auth/keycloak'
}
payment_urls = {
    'stage': 'https://feca-proxy.integration.cf3.us/v1/users/payments_summary',
    'qa': 'https://feca-proxy.sandbox.cf3.us/v1/users/payments_summary'
}

default_user = get_user('adap_keycloak', env=env)
password = default_user.get('password')

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


class LocustUserBehavior(TaskSet):

    def on_start(self):
        self.base_url = base_urls[env]
        self.payment_url = payment_urls[env]
        self.service = HttpMethod()

    def get_worker_email(self):
        row = random.choice(INPUT_DATA)
        email = row.get('worker_email')
        assert email, 'worker_email not found in data source'
        return email

    def _login(self):
        worker_email = self.get_worker_email()

        # ==============================================================================
        # ================  GET keycloak URL     =======================================
        # ==============================================================================

        resp = self.service.get(
            self.base_url,
            headers={'Content-Type': 'application/json'},
            ep_name='1_get_login_url'
        )

        if resp.status_code != 200:
            log.error({
                'message': 'Error response',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
            })
            return

        if resp.json_response.get('redirectUrl'):
            login_url = resp.json_response.get('redirectUrl')
        else:
            log.error({
                'message': 'Error: redirectUrl - not found',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', '')
            })
            return

        # ==============================================================================
        # ================  Render Login page    =======================================
        # ==============================================================================

        resp = self.service.get(
            login_url,
            headers={'Content-Type': 'text/html'},
            ep_name='2_get_login_form'
        )

        login_form_cookies = resp.cookies

        if resp.status_code != 200:
            log.error({
                'message': 'Error response',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'endpoint': login_url
            })
            return

        soup = BeautifulSoup(resp.content, 'html.parser')
        form = soup.find(id='kc-form-login')
        auth_url = form['action']

        if not auth_url:
            log.error({
                'message': 'Error: kc auth url has not been found',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'endpoint': login_url
            })
            return

        # ==============================================================================
        # ================  Sign In              =======================================
        # ==============================================================================

        resp = self.service.post(
            auth_url,
            data={
                'username': worker_email,
                'password': password
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            cookies=login_form_cookies,
            allow_redirects=False,
            ep_name='3_sign_in'
        )

        if resp.status_code != 302:
            log.error({
                'message': 'Error response: Sign In failed',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'endpoint': auth_url,
                'worker_email': worker_email
            })
            return

        #  find url in header (location)
        if not resp.headers.get('location'):
            log.error({
                'message': 'Error: location has not been found',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'endpoint': auth_url
            })
            return

        feca_proxy_url = resp.headers['location'].replace('annotate', 'feca-proxy')
        if not feca_proxy_url:
            log.error({
                'message': 'Error: feca-proxy url has not been found',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'endpoint': auth_url
            })
            return


        # ==============================================================================
        # ================ Complete the Oauth Handshake ================================
        # ==============================================================================

        resp = self.service.get(
            feca_proxy_url,
            headers={'Content-Type': 'text/html'},
            ep_name='4_feca_proxy_auth_callback'
        )

        if resp.status_code != 200:
            log.error({
                'message': 'Error response',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'endpoint': feca_proxy_url
            })
            return

        auth_cookies = resp.cookies

        # verify that userJWT in cookies
        if not auth_cookies.get('userJWT', None):
            log.error({
                'message': 'Error: userJWT has nor been found',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'endpoint': feca_proxy_url
            })
            return

        # verify json
        if not resp.json_response.get('name') or resp.json_response.get('name') != worker_email:
            log.error({
                'message': f'Error: "name" not found or not matched : {resp.json_response.get("name")} / {worker_email}',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'endpoint': feca_proxy_url,
                'worker_email': worker_email
            })
            return

        # ==============================================================================
        # ================ Verification   ==============================================
        # ==============================================================================

        # call /v1/users/payments_summary endpoint
        resp = self.service.get(
            self.payment_url,
            headers={'Content-Type': 'application/json'},
            cookies=auth_cookies,
            ep_name='5_payment'
        )

        if resp.status_code != 200:
            log.error({
                'message': 'Error response',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'endpoint': self.payment_url,
                'worker_email': worker_email
            })
            return

        for ef in ['available', 'lifetimeEarnings', 'requested', 'lastRequest']:
            if ef not in resp.json_response:
                log.error({
                    'message': f'Missing {ef} in response',
                    'resp.json': resp.json_response,
                    'worker_email': worker_email
                })

    @task(20)
    def user_authentication(self):
        self.client.locust_event(
            "Execute task",  # Requst type
            "keycloak_feca_sign_in",  # Requst name
            self._login
        )


class LocustUser(CustomLocust):
    wait_time = between(0.001, 0.001)
    task_set = LocustUserBehavior

    def __init__(self):
        self.host = ''
        super(LocustUser, self).__init__()
