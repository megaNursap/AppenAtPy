from appen_connect.api_automation.services_config.ac_api_v1 import *

from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_core, pytest.mark.regression_ac, pytest.mark.ac_api_v1, pytest.mark.ac_api_v1_project, pytest.mark.ac_api]

AUTH_KEY = get_test_data('auth_key', 'auth_key')


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_project_with_id():
    api = AC_API_V1(AUTH_KEY)
    resp = api.get_project(project_id="511")
    resp.assert_response_status(200)
    assert len(resp.json_response) > 0


def test_get_project_with_invalid_id():
    api = AC_API_V1(AUTH_KEY)
    resp = api.get_project(project_id="123455")
    resp.assert_response_status(404)
    assert len(resp.json_response) == 0


@pytest.mark.ac_api_uat
def test_get_project_ias():
    api = AC_API_V1(AUTH_KEY)
    resp = api.get_project_ias(project_id="511")
    resp.assert_response_status(200)
    assert len(resp.json_response) > 0