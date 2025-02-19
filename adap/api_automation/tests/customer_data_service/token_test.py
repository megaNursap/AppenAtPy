"""
Tests Customer Data Service internal endpoints
for requesting and redeeming a data access token
"""
from adap.api_automation.services_config.akon import AkonUser
from adap.api_automation.services_config.customer_data_service import CDS
from adap.api_automation.utils.data_util import get_user_team_id, get_test_data
from pytest_dependency import depends
import pytest
import time

mark_only_envs = pytest.mark.skipif(
    not pytest.running_in_preprod_subset,
    reason="Only sandbox and integration enabled feature")
pytestmark = [pytest.mark.cds, pytest.mark.regression_core, mark_only_envs]

managed_team_id = get_user_team_id('perf_platform', 0)
path = 'jobs/3/units/3.json'
data = {'test': 'token'}

tokens = {}

@pytest.mark.dependency()
@pytest.mark.parametrize(
    'team_id',
    [(managed_team_id)]
)
def test_cds_request_token(team_id, adap_cds):
    """ validate a token can be requested """
    resp = adap_cds.request_token(team_id=team_id, path=path, expires_in=60)
    assert resp.status_code == 200, resp.text
    token = resp.text
    assert token.startswith('token='), f"Invalid token: {token}"
    tokens[team_id] = token


@pytest.mark.dependency()
@pytest.mark.parametrize(
    'team_id',
    [(managed_team_id)]
)
def test_cds_redeem_token(request, team_id, adap_cds):
    """ validate a token can be redeemed """
    depends(request, [f"test_cds_request_token[{team_id}]"])
    token = tokens[team_id]
    resp = adap_cds.redeem_token(token=token)
    assert resp.status_code == 200, resp.text
    assert resp.json_response == data


@pytest.mark.dependency()
@pytest.mark.parametrize(
    'team_id',
    [(managed_team_id)]
)
def test_cds_token_expiration(request, team_id, adap_cds):
    """ validate a token expires as expected """
    depends(request, [
        f"test_cds_request_token[{team_id}]",
        f"test_cds_redeem_token[{team_id}]"
        ])
    # get token with expiration period = 3s 
    resp = adap_cds.request_token(team_id=team_id, path=path, expires_in=3)
    assert resp.status_code == 200, resp.text
    token = resp.text
    # redeem token 
    resp = adap_cds.redeem_token(token=token)
    assert resp.status_code == 200, resp.text
    assert resp.json_response == data
    # wait for token expire
    time.sleep(3)
    resp = adap_cds.redeem_token(token=token)
    assert resp.status_code == 403, resp.text
    assert resp.json_response.get('reason') == 'Expired', resp.text
