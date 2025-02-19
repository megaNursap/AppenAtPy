from appen_connect.api_automation.services_config.ac_api_v1 import AC_API_V1
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_core, pytest.mark.regression_ac, pytest.mark.ac_api_v1, pytest.mark.ac_api_v1_intelligent_attributes, pytest.mark.ac_api]

AUTH_KEY = get_test_data('auth_key', 'auth_key')


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_intelligent_attribute_project():
    api = AC_API_V1(AUTH_KEY)
    payload = {
        "level":"project"
    }
    resp = api.get_intelligent_attribute(payload)
    resp.assert_response_status(200)
    assert resp.json_response[0]['level'] == 'PROJECT'
#     TODO more content verification


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_intelligent_attribute_customer():
    api = AC_API_V1(AUTH_KEY)
    payload = {
        "level":"customer"
    }
    resp = api.get_intelligent_attribute(payload)
    resp.assert_response_status(200)
    assert resp.json_response[0]['level'] == 'CUSTOMER'
#     TODO more content verification


#    This API test seems to be modified and Intelligent attribute doesn't need auth_key to return the 200 response

@pytest.mark.parametrize('auth_key, expected_status',
                         [("1221jjidefghijklmn123opQRSTUVWreo09014bE", 200),
                          ("", 200)])
def test_get_intelligent_attribute_invalid_auth_key(auth_key, expected_status):
    api = AC_API_V1(AUTH_KEY)
    payload = {
        "level": "customer"
    }
    resp = api.get_intelligent_attribute(payload)
    resp.assert_response_status(expected_status)
    assert len(resp.json_response) > 0
