import pytest
from bs4 import BeautifulSoup

from adap.api_automation.utils.data_util import get_user_email, get_user_password
from adap.api_automation.utils.http_util import HttpMethod


# pytestmark = [pytest.mark.skip(reason='Needs Maintenance QED-2565')]


@pytest.fixture(scope="module")
def login_cookie(app):
    USER_NAME = get_user_email('test_ui_account')
    PASSWORD = get_user_password('test_ui_account')
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    flat_cookie_dict = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in app.driver.get_cookies()}
    return flat_cookie_dict


def get_host_url(pytest_env):
    hosts_mapping = {"local": "http://www.leapforcedev.com:8080",
                     "qa": "https://connect-qa.sandbox.cf3.us",
                     "stage": "https://connect-stage.integration.cf3.us"}
    assert hosts_mapping.get(pytest_env, "Not Found") != "Not found"
    return hosts_mapping[pytest_env]


@pytest.mark.connect_smoke
def test_host_resolves():
    assert get_host_url("local") == "http://www.leapforcedev.com:8080"
    assert get_host_url("qa") == "https://connect-qa.sandbox.cf3.us"
    assert get_host_url("stage") == "https://connect-stage.integration.cf3.us"


@pytest.mark.connect_smoke
def test_login_cookie(login_cookie):
    # should be a unit test.
    assert login_cookie.get('JSESSIONID')


@pytest.mark.connect_smoke
def test_core_service_health():
    host = get_host_url(pytest.env)
    resp = HttpMethod().get(host + "/qrp/core/service_health")
    assert resp.text == "Service OK", resp.url


@pytest.mark.connect_smoke
def test_public_service_health():
    host = get_host_url(pytest.env)
    resp = HttpMethod().get(host + "/qrp/public/service_health")
    assert resp.text == "Service OK", resp.url


@pytest.mark.connect_smoke
def test_core_recruiting_200_ok(login_cookie):
    host = get_host_url(pytest.env)
    resp = HttpMethod().get(host + "/qrp/core/recruiting", cookies=login_cookie)
    soup = BeautifulSoup(resp.content)
    page = soup.prettify()
    # table = soup.find_all("table", {"class": "action-center-table"})
    table = soup.find_all("table", class_="action-center-table")

    # need a more general way. to use beautiful soup api.
    assert table[0].text.find("228") != str(-1), "a false positive likely"
