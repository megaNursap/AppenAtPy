from appen_connect.api_automation.services_config.ac_api_v1 import AC_API_V1
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_core, pytest.mark.regression_ac, pytest.mark.ac_api_v1, pytest.mark.ac_api_v1_payrate, pytest.mark.ac_api]


AUTH_KEY = get_test_data('auth_key', 'auth_key')


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_pay_rate_by_business_unit():
    api = AC_API_V1(AUTH_KEY)
    businessUnits = ["LR", "CR", "F8"]
    rateTypes = ["HOURLY", "PIECERATE"]
    businessUnit = random.choice(businessUnits)
    rateType = random.choice(rateTypes)
    resp = api.get_payrate(businessUnit, rateType)
    resp.assert_response_status(200)
    assert resp.json_response[0]['businessUnit'] == businessUnit
    assert resp.json_response[0]['rateType'] == rateType


def test_get_pay_rate_invalid_business_unit():
    api = AC_API_V1(AUTH_KEY)
    businessUnit = "F9"
    rateTypes = ["HOURLY", "PIECERATE"]
    rateType = random.choice(rateTypes)
    resp = api.get_payrate(businessUnit, rateType)
    resp.assert_response_status(400)
    assert resp.json_response['fieldErrors'][0]['field'] == 'error'
    assert resp.json_response['fieldErrors'][0][
               'message'] == 'No enum constant com.lf.model.enumeration.BusinessUnit.{}'.format(businessUnit)


def test_get_invalid_pay_rate():
    api = AC_API_V1(AUTH_KEY)
    businessUnits = ["LR", "CR", "F8"]
    businessUnit = random.choice(businessUnits)
    rateType = "YEARLY"
    resp = api.get_payrate(businessUnit, rateType)
    resp.assert_response_status(400)
    assert resp.json_response['fieldErrors'][0]['field'] == 'error'
    assert resp.json_response['fieldErrors'][0][
               'message'] == 'No enum constant com.lf.model.enumeration.RateType.{}'.format(rateType)


@pytest.mark.parametrize('auth_key, expected_status, error_msg',
                         [("1221jjidefghijklmn123opQRSTUVWreo09014bE", 403, {'error': 'Forbidden'}),
                          ("", 403, {'error': 'Forbidden'})])
def test_get_pay_rate_invalid_auth_key(auth_key, expected_status, error_msg):
    api = AC_API_V1(auth_key)
    businessUnits = ["LR", "CR", "F8"]
    rateTypes = ["HOURLY", "PIECERATE"]
    businessUnit = random.choice(businessUnits)
    rateType = random.choice(rateTypes)
    resp = api.get_payrate(businessUnit, rateType)
    resp.assert_response_status(expected_status)
    assert resp.json_response == error_msg