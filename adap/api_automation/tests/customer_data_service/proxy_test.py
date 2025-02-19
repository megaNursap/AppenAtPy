"""
Tests Customer Data Service internal endpoint /proxy
"""
from adap.api_automation.services_config.akon import AkonUser
from adap.api_automation.services_config.customer_data_service import CDS
from adap.api_automation.utils.data_util import get_user_team_id, get_test_data
import pytest
from pytest_dependency import depends

mark_only_envs = pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
pytestmark = [pytest.mark.cds, pytest.mark.regression_core, mark_only_envs]

managed_team_id = get_user_team_id('perf_platform', 0)
path = 'jobs/1/units/1.json'
data = {'test': 'proxy'}


@pytest.mark.dependency()
@pytest.mark.parametrize(
    'team_id',
    [(managed_team_id)]
)
def test_cds_proxy_put(team_id, adap_cds):
    resp = adap_cds.put_proxy(team_id=team_id, path=path, data=data)
    assert resp.status_code == 201, '' \
                                    "Expected status_code: 201\n" \
                                    f'Actual status_code: {resp.status_code}, resp.text: {resp.text}'


@pytest.mark.dependency()
@pytest.mark.parametrize(
    'team_id',
    [(managed_team_id)]
)
def test_cds_proxy_get(request, team_id, adap_cds):
    depends(request, [f"test_cds_proxy_put[{team_id}]"])
    resp = adap_cds.get_proxy(team_id=team_id, path=path)
    resp.assert_response_status(200)
    assert resp.json_response == data, '' \
                                       f'Expected response: {data}\n' \
                                       f'Actual response: {resp.json_response}, resp.text: {resp.text}'


@pytest.mark.dependency()
@pytest.mark.parametrize(
    'team_id',
    [(managed_team_id)]
)
def test_cds_proxy_delete(request, team_id, adap_cds):
    depends(request, [
        f"test_cds_proxy_put[{team_id}]",
        f"test_cds_proxy_get[{team_id}]",
    ])
    resp = adap_cds.delete_proxy(team_id=team_id, path=path)
    resp.assert_response_status(204)
    # verify file not exists
    resp = adap_cds.get_proxy(team_id=team_id, path=path)
    assert resp.status_code != 200, 'File has not been deleted!'
