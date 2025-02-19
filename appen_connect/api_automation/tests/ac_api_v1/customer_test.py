from appen_connect.api_automation.services_config.ac_api_v1 import AC_API_V1
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_core, pytest.mark.regression_ac, pytest.mark.ac_api_v1, pytest.mark.ac_api_v1_customer, pytest.mark.ac_api]


AUTH_KEY = get_test_data('auth_key', 'auth_key')


@pytest.mark.ac_api_uat
def test_get_customer_attributes():
    api = AC_API_V1(AUTH_KEY)
    resp = api.get_customer_attributes(customer_id='1')
    resp.assert_response_status(200)
    assert len(resp.json_response) > 0
    assert resp.json_response[0]['customerId'] == 1
    assert resp.json_response[0]['name'] != ''
# ? customerId the same on all env?


@pytest.mark.parametrize('auth_key, expected_status, error_msg',
                         [("1221jjidefghijklmn123opQRSTUVWreo09014bE", 403, {'error': 'Forbidden'}),
                          ("", 403, {'error': 'Forbidden'})])
def test_get_customer_attributes_invalid_auth_key(auth_key, expected_status, error_msg):
    api = AC_API_V1(auth_key)
    resp = api.get_customer_attributes(customer_id='1')
    resp.assert_response_status(expected_status)
    assert len(resp.json_response) > 0
    assert resp.json_response == error_msg


def test_get_customer_attributes_not_exist():
    api = AC_API_V1(AUTH_KEY)
    resp = api.get_customer_attributes(customer_id='100000000')
    resp.assert_response_status(404)
    assert resp.json_response == {}


def test_get_customer_attributes_invalid_id():
    api = AC_API_V1(AUTH_KEY)
    resp = api.get_customer_attributes(customer_id='abc')
    resp.assert_response_status(400)
    assert resp.json_response == {'fieldErrors': [{'field': 'error', 'message': 'For input string: "abc"'}]}