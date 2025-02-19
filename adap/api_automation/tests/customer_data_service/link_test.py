"""
Tests Customer Data Service internal endpoint /link
"""
from adap.api_automation.services_config.akon import AkonUser
from adap.api_automation.services_config.customer_data_service import CDS
from adap.api_automation.utils.data_util import get_user_team_id, get_test_data
from pytest_dependency import depends
import requests
import pytest
import json

mark_only_envs = pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
pytestmark = [pytest.mark.cds, pytest.mark.regression_core, mark_only_envs]

managed_team_id = get_user_team_id('perf_platform', 0)
path = 'jobs/2/units/1.json'
data = {'test': 'link'}


@pytest.mark.dependency()
@pytest.mark.parametrize(
    'team_id',
    [
        (managed_team_id)
    ]
)
def test_cds_link_put(request, team_id, adap_cds):
    # get managed link
    link = adap_cds.put_link(team_id=team_id, path=path)
    link.assert_response_status(302)
    loc = link.headers.get('Location')
    # put data using the link
    resp = requests.put(loc, data=json.dumps(data))
    assert resp.status_code == 200, f"Expected 200, Actual {resp.status_code}"


@pytest.mark.dependency()
@pytest.mark.parametrize(
    'team_id',
    [
        (managed_team_id)
    ]
)
def test_cds_link_get(request, team_id, adap_cds):
    depends(request, [f"test_cds_link_put[{team_id}]"])

    # get managed link
    link = adap_cds.get_link(team_id=team_id, path=path)
    link.assert_response_status(200)
    loc = link.url
    # get data using the link 
    resp = requests.get(loc)
    assert resp.status_code == 200, f"Expected 200, Actual {resp.status_code}"
    assert resp.json() == data, '' \
                                f'Expected response: {data}\n' \
                                f'Actual response: {resp.text}'


@pytest.mark.dependency()
@pytest.mark.parametrize(
    'team_id',
    [(managed_team_id)]
)
def test_cds_link_delete(request, team_id, adap_cds):
    depends(request, [
        f"test_cds_link_put[{team_id}]",
        f"test_cds_link_get[{team_id}]",
    ])
    # get managed link
    link = adap_cds.delete_link(team_id=team_id, path=path)
    link.assert_response_status(302)
    loc = link.headers.get('Location')
    # delete data using the link
    resp = requests.delete(loc)
    assert resp.status_code == 204, f"Expected 204, Actual {resp.status_code}"
    # verify file not exists
    resp = adap_cds.get_proxy(team_id=team_id, path=path)
    assert resp.status_code != 200, 'File has not been deleted!'
