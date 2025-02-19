"""
Tests Customer Data Service internal endpoints for SDA use case:
/generate_url
/redirect
"""
from adap.api_automation.services_config.akon import AkonUser
from adap.api_automation.services_config.customer_data_service import CDS
from adap.api_automation.utils.data_util import get_user_team_id, get_test_data
from adap.api_automation.utils.helpers import retry
from pytest_dependency import depends
import pytest
import time
import requests
import base64


def to_base64(text: str) -> str:
    text_bytes = text.encode('ascii')
    base64_bytes = base64.b64encode(text_bytes)
    base64_text = base64_bytes.decode('ascii')
    return base64_text


mark_only_envs = pytest.mark.skipif(
    not pytest.running_in_preprod_subset,
    reason="Only sandbox and integration enabled feature")

pytestmark = [
    pytest.mark.cds,
    pytest.mark.sda,
    pytest.mark.regression_core,
    mark_only_envs
]

sda_team_id = get_user_team_id('test_sda', 0)
test_provider = {
    'name': 'gap_test'
}
sda_generate_url_params = {
    'url': to_base64('https://storage.cloud.google.com/helentestbucket/ReceiptSwiss.jpeg'),
    'provider': test_provider.get('name'),
    'team_id': sda_team_id,
    'email': 'foo@bar.com',
    'user_id': 1,
    'unit_id': 1,
    'channel_id': 1
}


@pytest.mark.dependency()
@pytest.mark.parametrize(
    'params',
    [
        (sda_generate_url_params)
    ]
)
def test_cds_generate_url(params, adap_cds):
    """ Verify url can be generated """
    resp = adap_cds.generate_url(params)
    assert resp.status_code == 200, resp.text
    assert resp.text.startswith(
        f"https://api.{pytest.env}.cf3.us/v1/secure/redirect?token="
    ), resp.text


@pytest.mark.dependency()
@pytest.mark.parametrize(
    'params',
    [
        (sda_generate_url_params)
    ]
)
def test_cds_redirect(request, params, adap_cds):
    """ Verify data can be fetched via generated url """
    tc_param = request.node.name.strip(request.node.originalname)
    depends(request, [f"test_cds_generate_url{tc_param}"])
    url_redirect = adap_cds.generate_url(params).text

    resp = requests.get(url_redirect, allow_redirects=True, headers=adap_cds.headers)
    assert resp.status_code == 200, resp.text
    assert resp.content.startswith(b'\xff\xd8\xff\xe0\x00\x10JFIF'), resp.text


@pytest.mark.dependency()
@pytest.mark.parametrize(
    'params',
    [
        (sda_generate_url_params)
    ]
)
def test_cds_redirect_expired(request, params, adap_cds):
    """ Verify link expires """
    tc_param = request.node.name.strip(request.node.originalname)
    depends(request, [f"test_cds_redirect{tc_param}"])
    url_redirect = adap_cds.generate_url(params).text
    time.sleep(60)
    resp = requests.get(url_redirect, allow_redirects=True, headers=adap_cds.headers)
    assert resp.status_code == 403, resp.text[:200]
    assert resp.json().get('reason') == 'Expired', resp.content


@pytest.mark.dependency()
@pytest.mark.parametrize(
    'params',
    [
        (sda_generate_url_params)
    ]
)
def test_cds_get_storage_providers_for_team(request, params, adap_cds):
    """ Get team's storage providers """
    tc_param = request.node.name.strip(request.node.originalname)
    depends(request, [f"test_cds_redirect_expired{tc_param}"])
    resp = adap_cds.get_team_storage_providers([sda_team_id])
    assert resp.status_code == 200, resp.text[:200]
    s3_test_sp = [i for i in resp.json_response if i.get('name') == test_provider['name']]
    assert s3_test_sp, f"Missing 's3_test' storage provider in: {resp.json_response}"
    test_provider.update(s3_test_sp[0])


@pytest.mark.dependency()
def test_cds_deactivate_storage_provider(request, adap_cds):
    """ Verify Deactivate a storage provider """
    depends(request, ['test_cds_get_storage_providers_for_team'])
    assert test_provider['status'] == 'active', '' \
                                                f"Storage provider is already inactive: {test_provider}"
    adap_cds.update_storage_provider_status(test_provider['id'], 'pending')

    def verify_inactive():
        """ Verify secure links do not work """
        url_redirect = adap_cds.generate_url(sda_generate_url_params).text
        resp = requests.get(url_redirect, allow_redirects=True, headers=adap_cds.headers)
        assert resp.status_code != 200, "Storage provider is still active"

    try:
        retry(verify_inactive, max_wait=20)
    except:
        adap_cds.update_storage_provider_status(test_provider['id'], 'active')
        raise


@pytest.mark.dependency()
def test_cds_activate_storage_provider(request, adap_cds):
    """ Verify Activate a storage provider """
    depends(request, ['test_cds_deactivate_storage_provider'])
    assert test_provider['status'] != 'active', '' \
                                                f"Storage provider is already active: {test_provider}"
    adap_cds.update_storage_provider_status(test_provider['id'], 'active')

    def verify_active():
        """ Verify secure links work """
        url_redirect = adap_cds.generate_url(sda_generate_url_params).text
        resp = requests.get(url_redirect, allow_redirects=True, headers=adap_cds.headers)
        assert resp.status_code == 200, "Storage provider is still inactive"

    retry(verify_active, max_wait=20)
