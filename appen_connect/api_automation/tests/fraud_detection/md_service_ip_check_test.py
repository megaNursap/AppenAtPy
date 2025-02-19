import allure
import pytest

from adap.api_automation.utils.data_util import get_test_data
from appen_connect.api_automation.services_config.md_service import AC_MD_API

mark_only_envs = pytest.mark.skipif(
    pytest.env not in ["stage"],
    reason="Only AC Stage enabled feature")

# Removed markers due to ACE-17177, gateway service has been deprecated
# pytestmark = [pytest.mark.md_service, pytest.mark.regression_ac_user_service, pytest.mark.ac_fraud_detection,
#               mark_only_envs]


@allure.issue("https://appen.atlassian.net/browse/ACE-17177", 'Bug: ACE-17177')
def test_md_service_healthcheck(ac_api_cookie):
    md_res = AC_MD_API().get_md_healthcheck(cookies=ac_api_cookie)
    assert md_res.status_code == 200
    assert md_res.json_response['status'] == 'pass'
    assert md_res.json_response['app-name'] == 'Fraud Watchlist Service'


def test_md_service_check_worker_ip_no_cookies():
    worker = get_test_data('fraud_detection', 'check_ip')
    md_res = AC_MD_API().get_check_md_level_with_ip_by_worker(worker_id=worker)
    assert md_res.status_code == 401


@allure.issue("https://appen.atlassian.net/browse/ACE-17177", 'Bug: ACE-17177')
def test_md_service_check_worker_ip_no_vpn(ac_api_cookie):
    worker = get_test_data('fraud_detection', 'check_ip_us_no_vpn')
    md_res = AC_MD_API().get_check_md_level_with_ip_by_worker(worker_id=worker, cookies=ac_api_cookie)
    assert md_res.status_code == 200
    assert md_res.json_response['user_id'] == worker
    assert md_res.json_response['ip_quality']
    assert md_res.json_response['self_reported_country'] == 'US'
    assert not md_res.json_response['ip_quality']['failed']
    assert md_res.json_response['ip_quality']['connection_type'] == 'Residential'
    assert md_res.json_response['ip_quality']['region_name'] == 'California'
    assert md_res.json_response['ip_quality']['country_code'] == 'US'
    assert md_res.json_response['ip_quality']['fraud_score'] == 0
    assert not md_res.json_response['ip_quality']['vpn']
    assert not md_res.json_response['ip_quality']['proxy']
    assert not md_res.json_response['ip_quality']['mobile']
    assert not md_res.json_response['ip_quality']['tor']
    assert not md_res.json_response['ip_quality']['active_vpn']


@allure.issue("https://appen.atlassian.net/browse/ACE-17177", 'Bug: ACE-17177')
def test_md_service_check_worker_ip_vpn(ac_api_cookie):
    worker = get_test_data('fraud_detection', 'check_ip_vpn_ua')
    md_res = AC_MD_API().get_check_md_level_with_ip_by_worker(worker_id=worker, cookies=ac_api_cookie)
    assert md_res.status_code == 200
    assert md_res.json_response['user_id'] == worker
    assert md_res.json_response['ip_quality']
    assert md_res.json_response['self_reported_country'] == 'UA'
    assert md_res.json_response['ip_quality']['failed']
    assert md_res.json_response['ip_quality']['connection_type'] == "Data Center"
    assert md_res.json_response['ip_quality']['abuse_velocity'] == "high"
    assert md_res.json_response['ip_quality']['region_name'] == 'Kyiv City'
    assert md_res.json_response['ip_quality']['country_code'] == 'UA'
    assert md_res.json_response['ip_quality']['fraud_score'] == 100
    assert md_res.json_response['ip_quality']['vpn']
    assert md_res.json_response['ip_quality']['proxy']
    assert not md_res.json_response['ip_quality']['tor']
    assert not md_res.json_response['ip_quality']['mobile']
    assert md_res.json_response['ip_quality']['active_vpn']

    assert md_res.json_response['flags']['ip_country_mismatch']['description'] \
           == "Self-reported country mismatch from country associated with IP"
    assert md_res.json_response['flags']['ip_country_mismatch']['type'] == "ip_signals"


@allure.issue("https://appen.atlassian.net/browse/ACE-17177", 'Bug: ACE-17177')
def test_md_service_check_worker_whitelisted(ac_api_cookie):
    worker = get_test_data('fraud_detection', 'check_ip_whitelisted')
    md_res = AC_MD_API().get_check_md_level_with_ip_by_worker(worker_id=worker, cookies=ac_api_cookie)
    assert md_res.status_code == 200
    assert md_res.json_response['user_id'] == worker
    assert md_res.json_response['ip_quality']
    assert md_res.json_response['maliciousness_level'] == 'low'
    assert not md_res.json_response['ip_quality']['failed']
    assert not md_res.json_response['ip_quality']['vpn']
    assert not md_res.json_response['ip_quality']['proxy']
    assert not md_res.json_response['ip_quality']['mobile']
    assert not md_res.json_response['ip_quality']['active_vpn']
    assert md_res.json_response['flags'] == {}
    assert md_res.json_response['self_reported_country'] == 'US'
