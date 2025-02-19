"""
doc - https://appen.atlassian.net/wiki/spaces/ENGR/pages/5903517197/ADAP+Team+Balance+Service#4.1.1-POST-%2Fv1%2Fteam-balance%2Fquery
"""

from adap.api_automation.services_config.cost_balance_api_client import CostBalanceApiClient
import pytest

from adap.api_automation.utils.data_util import get_user_team_id
from adap.api_automation.utils.helpers import wait_until

mark_env = pytest.mark.skipif(not pytest.running_in_preprod, reason="for Integration env")

pytestmark = [pytest.mark.cb_api,
              pytest.mark.regression_qf]


team_id = get_user_team_id('cost_balance_api', 0)
team_id2 = get_user_team_id('cost_balance_api', 1)


@pytest.fixture(scope='module', autouse=True)
def api_client():
    client = CostBalanceApiClient()
    return client


def test_get_team_balance(api_client):
    resp = api_client.get_teams_balance([team_id])
    assert resp.status_code == 200

    resp_json = resp.json_response
    assert resp_json['status'] == 'SUCCESS'
    assert resp_json['teamBalancesResult'][0]['teamId'] == team_id
    assert resp_json['teamBalancesResult'][0]['amountInCents'] >= 0


def test_get_team_balances(api_client):
    resp = api_client.get_teams_balance([team_id, team_id2])
    assert resp.status_code == 200

    resp_json = resp.json_response
    team_ids = list(map(lambda x: x['teamId'], resp_json['teamBalancesResult']))
    assert resp_json['status'] == 'SUCCESS'
    assert team_id in team_ids
    assert team_id2 in team_ids
    assert resp_json['teamBalancesResult'][0]['amountInCents'] >= 0
    assert resp_json['teamBalancesResult'][1]['amountInCents'] >= 0


@pytest.mark.parametrize('refund_amount', [1000, 0])
def test_confirm_refund_transaction(api_client, refund_amount):
    # 1. refund some money to team's balance
    # 2. check tx details
    # 3. confirm refund tx
    # 4. check tx details
    # 5. check updated team's balance

    initial_balance = api_client.get_teams_balance_content([team_id])['teamBalancesResult'][0]['amountInCents']

    resp_refund = api_client.initiate_refund_transaction(team_id, refund_amount)
    assert resp_refund.status_code == 200

    resp_refund_json = resp_refund.json_response

    resp_details = api_client.get_transaction_details(resp_refund_json['uri'])
    assert resp_details.status_code == 200

    resp_details_json = resp_details.json_response
    assert resp_details_json['uri'] == resp_refund_json['uri']
    assert resp_details_json['clientTransactionId'] == resp_refund_json['clientTransactionId']
    assert resp_details_json['message'] == 'PREPARED'
    assert resp_details_json['status'] == 'SUCCESS'
    assert resp_details_json['transactionType'] == 'INITIATE'
    assert resp_details_json['operation']['teamId'] == team_id
    assert resp_details_json['operation']['amountInCents'] == refund_amount
    assert resp_details_json['operation']['type'] == 'REFUND_BALANCE'

    resp_confirm = api_client.put_confirm_transaction(resp_refund_json['uri'], resp_refund_json['clientTransactionId'])
    assert resp_confirm.status_code == 200

    resp_confirm_json = resp_confirm.json_response
    assert resp_confirm_json['uri'] == resp_refund_json['uri']
    assert resp_confirm_json['clientTransactionId'] == resp_refund_json['clientTransactionId']
    assert resp_confirm_json['message'] == 'CONFIRM_COMPLETED'
    assert resp_confirm_json['status'] == 'SUCCESS'
    assert resp_confirm_json['transactionType'] == 'CONFIRM'

    resp_details_json = api_client.get_transaction_details_content(resp_refund_json['uri'])
    assert resp_details_json['uri'] == resp_refund_json['uri']
    assert resp_details_json['clientTransactionId'] == resp_refund_json['clientTransactionId']
    assert resp_details_json['message'] == 'CONFIRM_COMPLETED'
    assert resp_details_json['status'] == 'SUCCESS'
    assert resp_details_json['transactionType'] == 'CONFIRM'
    assert resp_details_json['operation']['teamId'] == team_id
    assert resp_details_json['operation']['amountInCents'] == refund_amount
    assert resp_details_json['operation']['type'] == 'REFUND_BALANCE'

    assert api_client.get_teams_balance_content([team_id])['teamBalancesResult'][0]['amountInCents'] \
           == initial_balance + refund_amount


def test_cancel_refund_transaction(api_client):
    # 1. refund some money to team's balance
    # 2. cancel refund tx
    # 3. check tx details
    # 4. check team's balance is the same

    refund_amount = 1000
    initial_balance = api_client.get_teams_balance_content([team_id])['teamBalancesResult'][0]['amountInCents']

    resp_refund_json = api_client.initiate_refund_transaction_content(team_id, refund_amount)

    resp_cancel = api_client.put_cancel_transaction(resp_refund_json['uri'], resp_refund_json['clientTransactionId'])
    assert resp_cancel.status_code == 200

    resp_cancel_json = resp_cancel.json_response
    assert resp_cancel_json['uri'] == resp_refund_json['uri']
    assert resp_cancel_json['clientTransactionId'] == resp_refund_json['clientTransactionId']
    assert resp_cancel_json['message'] == 'CANCEL_COMPLETED'
    assert resp_cancel_json['status'] == 'SUCCESS'
    assert resp_cancel_json['transactionType'] == 'CANCEL'

    resp_details_json = api_client.get_transaction_details_content(resp_refund_json['uri'])
    assert resp_details_json['uri'] == resp_refund_json['uri']
    assert resp_details_json['clientTransactionId'] == resp_refund_json['clientTransactionId']
    assert resp_details_json['message'] == 'CANCEL_COMPLETED'
    assert resp_details_json['status'] == 'SUCCESS'
    assert resp_details_json['transactionType'] == 'CANCEL'
    assert resp_details_json['operation']['teamId'] == team_id
    assert resp_details_json['operation']['amountInCents'] == refund_amount
    assert resp_details_json['operation']['type'] == 'REFUND_BALANCE'

    assert api_client.get_teams_balance_content([team_id])['teamBalancesResult'][0]['amountInCents'] \
           == initial_balance


@pytest.mark.parametrize('deduct_amount', [500, 0])
def test_confirm_deduct_transaction(api_client, deduct_amount):
    # 1. refund some money to team's balance
    # 2. confirm refund tx
    # 3. deduct refunded money/2 from team's balance
    # 4. check tx details
    # 5. confirm deduct tx
    # 6. check tx details
    # 7. check updated team's balance

    refund_amount = 1000
    resp_refund = api_client.initiate_refund_transaction_content(team_id, refund_amount)
    api_client.confirm_transaction_content(resp_refund['uri'], resp_refund['clientTransactionId'])
    initial_balance = api_client.get_teams_balance_content([team_id])['teamBalancesResult'][0]['amountInCents']

    resp_deduct = api_client.initiate_deduct_transaction(team_id, deduct_amount)
    assert resp_deduct.status_code == 200

    resp_deduct_json = resp_deduct.json_response

    resp_details = api_client.get_transaction_details(resp_deduct_json['uri'])
    assert resp_details.status_code == 200

    resp_details_json = resp_details.json_response
    assert resp_details_json['uri'] == resp_deduct_json['uri']
    assert resp_details_json['clientTransactionId'] == resp_deduct_json['clientTransactionId']
    assert resp_details_json['message'] == 'PREPARED'
    assert resp_details_json['status'] == 'SUCCESS'
    assert resp_details_json['transactionType'] == 'INITIATE'
    assert resp_details_json['operation']['teamId'] == team_id
    assert resp_details_json['operation']['amountInCents'] == deduct_amount
    assert resp_details_json['operation']['type'] == 'DEDUCT_BALANCE'

    resp_confirm = api_client.put_confirm_transaction(resp_deduct_json['uri'], resp_deduct_json['clientTransactionId'])
    assert resp_confirm.status_code == 200

    resp_confirm_json = resp_confirm.json_response
    assert resp_confirm_json['uri'] == resp_deduct_json['uri']
    assert resp_confirm_json['clientTransactionId'] == resp_deduct_json['clientTransactionId']
    assert resp_confirm_json['message'] == 'CONFIRM_COMPLETED'
    assert resp_confirm_json['status'] == 'SUCCESS'
    assert resp_confirm_json['transactionType'] == 'CONFIRM'

    resp_details_json = api_client.get_transaction_details_content(resp_deduct_json['uri'])
    assert resp_details_json['uri'] == resp_deduct_json['uri']
    assert resp_details_json['clientTransactionId'] == resp_deduct_json['clientTransactionId']
    assert resp_details_json['message'] == 'CONFIRM_COMPLETED'
    assert resp_details_json['status'] == 'SUCCESS'
    assert resp_details_json['transactionType'] == 'CONFIRM'
    assert resp_details_json['operation']['teamId'] == team_id
    assert resp_details_json['operation']['amountInCents'] == deduct_amount
    assert resp_details_json['operation']['type'] == 'DEDUCT_BALANCE'

    assert api_client.get_teams_balance_content([team_id])['teamBalancesResult'][0]['amountInCents'] \
           == initial_balance - deduct_amount


def test_cancel_deduct_transaction(api_client):
    # 1. refund some money to team's balance
    # 2. confirm refund tx
    # 3. deduct refunded money/2 from team's balance
    # 4. cancel deduct tx
    # 5. check tx details
    # 6. check team's balance

    refund_amount = 1000
    resp_refund = api_client.initiate_refund_transaction_content(team_id, refund_amount)
    api_client.confirm_transaction_content(resp_refund['uri'], resp_refund['clientTransactionId'])
    initial_balance = api_client.get_teams_balance_content([team_id])['teamBalancesResult'][0]['amountInCents']

    deduct_amount = refund_amount / 2
    resp_deduct_json = api_client.initiate_deduct_transaction_content(team_id, deduct_amount)

    resp_cancel = api_client.put_cancel_transaction(resp_deduct_json['uri'], resp_deduct_json['clientTransactionId'])
    assert resp_cancel.status_code == 200

    resp_cancel_json = resp_cancel.json_response
    assert resp_cancel_json['uri'] == resp_deduct_json['uri']
    assert resp_cancel_json['clientTransactionId'] == resp_deduct_json['clientTransactionId']
    assert resp_cancel_json['message'] == 'CANCEL_COMPLETED'
    assert resp_cancel_json['status'] == 'SUCCESS'
    assert resp_cancel_json['transactionType'] == 'CANCEL'

    resp_details_json = api_client.get_transaction_details_content(resp_deduct_json['uri'])
    assert resp_details_json['uri'] == resp_deduct_json['uri']
    assert resp_details_json['clientTransactionId'] == resp_deduct_json['clientTransactionId']
    assert resp_details_json['message'] == 'CANCEL_COMPLETED'
    assert resp_details_json['status'] == 'SUCCESS'
    assert resp_details_json['transactionType'] == 'CANCEL'
    assert resp_details_json['operation']['teamId'] == team_id
    assert resp_details_json['operation']['amountInCents'] == deduct_amount
    assert resp_details_json['operation']['type'] == 'DEDUCT_BALANCE'

    assert api_client.get_teams_balance_content([team_id])['teamBalancesResult'][0]['amountInCents'] \
           == initial_balance


# Negative cases
def test_get_team_balance_unauthorized():
    client = CostBalanceApiClient(authorize=False)
    resp = client.get_teams_balance([team_id])
    assert resp.status_code == 401
    assert resp.json_response['error'] == 'Unauthorized'


def test_get_team_balance_when_team_id_is_not_found(api_client):
    unknown_team_id = '8a142da6-1442-4a50-a2b0-789af61ca940'
    resp = api_client.get_teams_balance([team_id, unknown_team_id])
    assert resp.status_code == 422

    resp_json = resp.json_response
    assert resp_json['status'] == 'FAILED'
    assert resp_json['statusReason'] == f'one or more teamIds not found - [{unknown_team_id}]'


def test_get_team_balance_when_no_team_id_is_provided(api_client):
    resp = api_client.get_teams_balance([])
    assert resp.status_code == 422

    resp_json = resp.json_response
    assert resp_json['status'] == 'FAILED'
    assert resp_json['statusReason'] == 'no team ids found to query'


def test_deduct_more_than_team_has(api_client):
    # 1. get team's balance
    # 2. deduct more than team has

    initial_balance = api_client.get_teams_balance_content([team_id])['teamBalancesResult'][0]['amountInCents']
    deduct_amount = initial_balance + 100
    resp_deduct = api_client.initiate_deduct_transaction(team_id, deduct_amount)
    assert resp_deduct.status_code == 422

    resp_deduct_json = resp_deduct.json_response
    assert resp_deduct_json['message'] == 'could not create a transaction as the update to team balance ' \
                                          'is not possible - check if sufficient team balance'
    assert resp_deduct_json['status'] == 'FAILED'
    assert resp_deduct_json['transactionType'] == 'INITIATE'

    assert api_client.get_teams_balance_content([team_id])['teamBalancesResult'][0]['amountInCents'] \
           == initial_balance


def test_deduct_negative_amount(api_client):
    initial_balance = api_client.get_teams_balance_content([team_id])['teamBalancesResult'][0]['amountInCents']
    deduct_amount = -100
    resp_deduct = api_client.initiate_deduct_transaction(team_id, deduct_amount)
    assert resp_deduct.status_code == 400

    resp_deduct_json = resp_deduct.json_response
    assert resp_deduct_json['message'] == 'team balance operation should have 0 or greater amountInCents value'
    assert resp_deduct_json['status'] == 'FAILED'
    assert resp_deduct_json['transactionType'] == 'INITIATE'

    assert api_client.get_teams_balance_content([team_id])['teamBalancesResult'][0]['amountInCents'] \
           == initial_balance


def test_deduct_unauthorized(api_client):
    deduct_amount = 100
    client_unauthorized = CostBalanceApiClient(authorize=False)
    initial_balance = api_client.get_teams_balance_content([team_id])['teamBalancesResult'][0]['amountInCents']

    resp_deduct = client_unauthorized.initiate_deduct_transaction(team_id, deduct_amount)
    assert resp_deduct.status_code == 401
    assert resp_deduct.json_response['error'] == 'Unauthorized'

    assert api_client.get_teams_balance_content([team_id])['teamBalancesResult'][0]['amountInCents'] \
           == initial_balance


def test_refund_negative_amount(api_client):
    initial_balance = api_client.get_teams_balance_content([team_id])['teamBalancesResult'][0]['amountInCents']
    deduct_amount = -100
    resp_refund = api_client.initiate_refund_transaction(team_id, deduct_amount)
    assert resp_refund.status_code == 400

    resp_refund_json = resp_refund.json_response
    assert resp_refund_json['message'] == 'team balance operation should have 0 or greater amountInCents value'
    assert resp_refund_json['status'] == 'FAILED'
    assert resp_refund_json['transactionType'] == 'INITIATE'

    assert api_client.get_teams_balance_content([team_id])['teamBalancesResult'][0]['amountInCents'] \
           == initial_balance


def test_refund_unauthorized(api_client):
    deduct_amount = 100
    client_unauthorized = CostBalanceApiClient(authorize=False)
    initial_balance = api_client.get_teams_balance_content([team_id])['teamBalancesResult'][0]['amountInCents']

    resp_refund = client_unauthorized.initiate_refund_transaction(team_id, deduct_amount)
    assert resp_refund.status_code == 401
    assert resp_refund.json_response['error'] == 'Unauthorized'

    assert api_client.get_teams_balance_content([team_id])['teamBalancesResult'][0]['amountInCents'] \
           == initial_balance


def test_rollback_refund_transaction(api_client):
    refund_amount = 1000
    initial_balance = api_client.get_teams_balance_content([team_id2])['teamBalancesResult'][0]['amountInCents']

    resp_refund_json = api_client.initiate_refund_transaction_content(team_id2, refund_amount)

    assert wait_until(
        lambda: api_client.get_transaction_details_content(resp_refund_json['uri'])['message'] == 'ROLLBACK_COMPLETED',
        60 * 10,
        10), 'Can not get ROLLBACK REFUND transaction in time (10 minutes)'

    resp_details_json = api_client.get_transaction_details_content(resp_refund_json['uri'])
    assert resp_details_json['uri'] == resp_refund_json['uri']
    assert resp_details_json['clientTransactionId'] == resp_refund_json['clientTransactionId']
    assert resp_details_json['status'] == 'SUCCESS'
    assert resp_details_json['transactionType'] == 'CANCEL'
    assert resp_details_json['operation']['teamId'] == team_id2
    assert resp_details_json['operation']['amountInCents'] == refund_amount
    assert resp_details_json['operation']['type'] == 'REFUND_BALANCE'

    assert api_client.get_teams_balance_content([team_id2])['teamBalancesResult'][0]['amountInCents'] == initial_balance


def test_rollback_deduct_transaction(api_client):
    refund_amount = 1000
    initial_balance = api_client.get_teams_balance_content([team_id2])['teamBalancesResult'][0]['amountInCents']
    resp_refund = api_client.initiate_refund_transaction_content(team_id2, refund_amount)
    resp_confirm = api_client.put_confirm_transaction(resp_refund['uri'], resp_refund['clientTransactionId'])
    resp_confirm_json = resp_confirm.json_response
    assert resp_confirm_json['message'] == 'CONFIRM_COMPLETED'
    refund_balance = api_client.get_teams_balance_content([team_id2])['teamBalancesResult'][0]['amountInCents']
    assert refund_balance == initial_balance + refund_amount

    deduct_amount = refund_amount / 2
    resp_deduct_json = api_client.initiate_deduct_transaction_content(team_id2, deduct_amount)

    assert wait_until(
        lambda: api_client.get_transaction_details_content(resp_deduct_json['uri'])['message'] == 'ROLLBACK_COMPLETED',
        60 * 10,
        10), 'Can not get ROLLBACK DEDUCT transaction in time (10 minutes)'

    resp_details_json = api_client.get_transaction_details_content(resp_deduct_json['uri'])
    assert resp_details_json['uri'] == resp_deduct_json['uri']
    assert resp_details_json['clientTransactionId'] == resp_deduct_json['clientTransactionId']
    assert resp_details_json['status'] == 'SUCCESS'
    assert resp_details_json['transactionType'] == 'CANCEL'
    assert resp_details_json['operation']['teamId'] == team_id2
    assert resp_details_json['operation']['amountInCents'] == deduct_amount
    assert resp_details_json['operation']['type'] == 'DEDUCT_BALANCE'

    assert api_client.get_teams_balance_content([team_id2])['teamBalancesResult'][0]['amountInCents'] == refund_balance
