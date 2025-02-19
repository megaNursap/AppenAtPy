from appen_connect.api_automation.services_config.ac_api_v3 import *

from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_reports, pytest.mark.regression_ac, pytest.mark.ac_api_v3, pytest.mark.ac_api_v3_metric_controller, pytest.mark.ac_api]


# list all reports
@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_all_metrics(ac_api_cookie):
    api = AC_API_V3(ac_api_cookie)
    # report_type = 2
    for report_type in range(1, 3):
        payload = {'reportType': report_type}
        res = api.get_metrics(payload)
        res.assert_response_status(200)
        assert len(res.json_response) > 0
        print("LENGTH", len(res.json_response))
        for i in range(1, len(res.json_response)):
            assert res.json_response[i]['reportTypeId'] == report_type


@pytest.mark.parametrize('reportType', ['10000000000000000001', 'one', '123!'])
def test_get_all_metrics_with_invalid_values(ac_api_cookie, reportType):
    api = AC_API_V3(ac_api_cookie)
    payload = {'reportType': reportType}
    res = api.get_metrics(payload)
    res.assert_response_status(500)
    assert res.json_response['message'] == "Failed to convert value of type 'java.lang.String' to required type " \
                                           "'java.lang.Long'; nested exception is java.lang.NumberFormatException: " \
                                           "For input string: \"%s\"" %reportType


@pytest.mark.parametrize('reportType', ['10', ' '])
def test_get_all_metrics_with_non_valid_numbers(ac_api_cookie, reportType):
    api = AC_API_V3(ac_api_cookie)
    payload = {'reportType': reportType}
    res = api.get_metrics(payload)
    res.assert_response_status(200)
    assert len(res.json_response) == 0


def test_get_metrics_no_cookies():
    api = AC_API_V3()
    payload = {'reportType': 1}
    res = api.get_metrics(payload)
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
def test_get_metrics_no_parameter(ac_api_cookie):
    api = AC_API_V3(ac_api_cookie)
    payload = None
    res = api.get_metrics(payload)
    res.assert_response_status(500)
    assert res.json_response == {'message': "Required Long parameter 'reportType' is not present"}
    assert len(res.json_response) > 0


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_wbr_metrics_mapping(ac_api_cookie):
    api = AC_API_V3(ac_api_cookie)
    payload = None
    res = api.get_wbr_metrics_mapping(payload)
    res.assert_response_status(200)


def test_get_wbr_metrics_mapping_no_cookie():
    api = AC_API_V3()
    payload = None
    res = api.get_wbr_metrics_mapping(payload)
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}
