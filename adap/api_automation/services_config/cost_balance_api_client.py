import allure
import operator

import functools

import uuid

import json
import pytest

import adap.api_automation.services_config.endpoints.cost_balance_endpoints as cost_balance_endpoints
from adap.api_automation.utils.data_util import get_data_file
from adap.api_automation.utils.http_util import HttpMethod
from adap.perf_platform.utils.logging import get_logger

LOGGER = get_logger(__name__)

# TODO delete _content functions

class CostBalanceApiClient:
    def __init__(self, authorize=True, env = None):
        LOGGER.info('Initialize Cost balance API client')

        if env is None:  env = pytest.env

        self.env = env
        self.url = cost_balance_endpoints.URL.format(env)

        self.service = HttpMethod(self.url)

        if authorize:
            self._get_headers()
        else:
            self.headers = {'Content-Type': 'application/json'}

    def _get_headers(self):
        LOGGER.info('Authorise the client by getting bearer token')
        temp_client = HttpMethod(f'https://id.internal.{self.env}.cf3.us')
        resp = temp_client.get(
            '/auth',
            headers={
                'AUTHORIZATION': 'Token token=quality-flow-service-authentication-token',
                'Host': f'api.{self.env}.cf3.us',
            }
        )

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': resp.headers._store['x-appen-jwt'][1]
        }

    @allure.step
    def get_teams_balance(self, team_ids):
        LOGGER.info(f'Get teams balances: {team_ids}')
        payload = {'teamIds': team_ids}
        resp = self.service.post(
            cost_balance_endpoints.TEAM_BALANCE,
            data=json.dumps(payload),
            headers=self.headers
        )

        return resp

    @allure.step
    def get_teams_balance_content(self, team_ids):
        resp = self.get_teams_balance(team_ids)

        if resp.status_code is not 200:
            LOGGER.error('Request Failed: {0}'.format(resp.text))

        json_resp = json.loads(resp.content)

        return json_resp

    @allure.step
    def initiate_deduct_transaction(self, team_id, amount_in_cents):
        tx_id = str(uuid.uuid1())
        LOGGER.info(f'Initiate deduct transaction - {tx_id}')
        payload = {
            'operation': {
                'teamId': team_id,
                'amountInCents': amount_in_cents,
                'type': "DEDUCT_BALANCE"
            },
            'teamBalanceTxType': "INITIATE",
            'clientTransactionId': tx_id
        }
        resp = self.service.post(
            cost_balance_endpoints.TRANSACTION,
            data=json.dumps(payload),
            headers=self.headers
        )

        return resp

    @allure.step
    def initiate_deduct_transaction_content(self, team_id, amount_in_cents):
        resp = self.initiate_deduct_transaction(team_id, amount_in_cents)

        if resp.status_code != 200:
            LOGGER.error('Request Failed: {0}'.format(resp.text))

        json_resp = json.loads(resp.content)

        return json_resp

    @allure.step
    def initiate_refund_transaction(self, team_id, amount_in_cents):
        tx_id = str(uuid.uuid1())
        LOGGER.info(f'Initiate refund transaction - {tx_id}')
        payload = {
          'operation': {
            'teamId': team_id,
            'amountInCents': amount_in_cents,
            'type': "REFUND_BALANCE"
          },
          'teamBalanceTxType': "INITIATE",
          'clientTransactionId': tx_id
        }
        resp = self.service.post(
            cost_balance_endpoints.TRANSACTION,
            data=json.dumps(payload),
            headers=self.headers
        )

        return resp

    @allure.step
    def initiate_refund_transaction_content(self, team_id, amount_in_cents):
        resp = self.initiate_refund_transaction(team_id, amount_in_cents)

        if resp.status_code != 200:
            LOGGER.error('Request Failed: {0}'.format(resp.text))

        json_resp = json.loads(resp.content)

        return json_resp

    @allure.step
    def get_transaction_details(self, uri):
        LOGGER.info('Get transaction details')
        resp = self.service.get(uri, headers=self.headers)

        return resp

    @allure.step
    def get_transaction_details_content(self, uri):
        resp = self.get_transaction_details(uri)

        if resp.status_code != 200:
            LOGGER.error('Request Failed: {0}'.format(resp.text))

        json_resp = json.loads(resp.content)

        return json_resp

    @allure.step
    def put_confirm_transaction(self, uri, tx_id):
        LOGGER.info(f'Confirm transaction - {tx_id}')
        payload = {
          'teamBalanceTxType': "CONFIRM",
          'clientTransactionId': tx_id
        }
        resp = self.service.put(
            uri,
            data=json.dumps(payload),
            headers=self.headers,
        )

        return resp

    @allure.step
    def confirm_transaction_content(self, uri, tx_id):
        LOGGER.info(f'Confirm transaction - {tx_id}')
        payload = {
          'teamBalanceTxType': "CONFIRM",
          'clientTransactionId': tx_id
        }
        try:
            resp = self.service.put(
                uri,
                data=json.dumps(payload),
                headers=self.headers,
                name='confirm-transaction'
            )

            if resp.status_code != 200:
                LOGGER.error('Request Failed: {0}'.format(resp.text))

            json_resp = json.loads(resp.content)

            return json_resp
        except TypeError as e:
            LOGGER.warn(e)

    @allure.step
    def put_cancel_transaction(self, uri, tx_id):
        LOGGER.info(f'Cancel transaction - {tx_id}')
        payload = {
            'teamBalanceTxType': "CANCEL",
            'clientTransactionId': tx_id
        }
        resp = self.service.put(
            uri,
            data=json.dumps(payload),
            headers=self.headers
        )

        return resp

    @allure.step
    def cancel_transaction_content(self, uri, tx_id):
        LOGGER.info(f'Cancel transaction - {tx_id}')
        payload = {
          'teamBalanceTxType': "CANCEL",
          'clientTransactionId': tx_id
        }
        try:
            resp = self.service.put(
                uri,
                data=json.dumps(payload),
                headers=self.headers,
                name='cancel-transaction'
            )

            if resp.status_code != 200:
                LOGGER.error('Request Failed: {0}'.format(resp.text))

            json_resp = json.loads(resp.content)

            return json_resp
        except TypeError as e:
            LOGGER.warn(e)


def clean_balance(base_url):
    path = get_data_file("/team_integration.json", "integration")
    with open(path) as json_file:
        data = json.load(json_file)

    api_client = CostBalanceApiClient(HttpMethod(base_url))
    team_ids = [i['id']for i in data]
    r_balances = api_client.get_teams_balance_content(team_ids)['teamBalancesResult']
    for r_team in r_balances:
        amount = r_team['amountInCents']
        if amount:
            r_deduct = api_client.initiate_deduct_transaction_content(r_team['teamId'], amount)
            api_client.confirm_transaction_content(r_deduct['uri'], r_deduct['clientTransactionId'])

    r_balances = api_client.get_teams_balance_content(team_ids)['teamBalancesResult']
    assert not functools.reduce(operator.add, [b['amountInCents'] for b in r_balances])
    LOGGER.info('Teams balances have been cleaned')
