import pytest
from appen_connect.api_automation.services_config.gateway import AC_GATEWAY
from adap.api_automation.utils.data_util import get_test_data

pytestmark = [pytest.mark.regression_ac_profile_builder, pytest.mark.regression_ac, pytest.mark.ac_api_gateway, pytest.mark.ac_api_gateway_master_profile, pytest.mark.ac_api]


@pytest.fixture(scope='module')
def _valid_cookies(app):
    vendor_name = get_test_data('test_ui_account', 'user_name')
    vendor_password = get_test_data('test_ui_account', 'password')
    app.ac_user.login_as(user_name=vendor_name, password=vendor_password)

    _cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in app.driver.get_cookies()}

    return _cookie


def test_gw_empty_cookies():
    ac_api = AC_GATEWAY()
    res = ac_api.get_master_profile_questions(allow_redirects=False)
    res.assert_response_status(401)


def test_gw_valid_cookies(_valid_cookies):
    ac_api = AC_GATEWAY(cookies=_valid_cookies)
    res = ac_api.get_master_profile_questions()
    res.assert_response_status(200)


def test_qw_old_cookies(app, _valid_cookies):
    app.ac_user.sign_out()

    vendor_name = get_test_data('test_ui_account', 'user_name')
    vendor_password = get_test_data('test_ui_account', 'password')
    app.ac_user.login_as(user_name=vendor_name, password=vendor_password)

    # app.navigation.open_page(URL(pytest.env) + '/master-profile/questions')
    new_cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in app.driver.get_cookies()}

    ac_api = AC_GATEWAY(cookies=_valid_cookies)
    res = ac_api.get_master_profile_questions()
    res.assert_response_status(200)

    ac_api = AC_GATEWAY(cookies=new_cookie)
    res = ac_api.get_master_profile_questions()
    res.assert_response_status(200)