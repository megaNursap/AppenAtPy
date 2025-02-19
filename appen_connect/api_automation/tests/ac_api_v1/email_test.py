from appen_connect.api_automation.services_config.ac_api_v1 import *

from adap.api_automation.utils.data_util import *

AUTH_KEY = get_test_data('auth_key', 'auth_key')

pytestmark = [pytest.mark.regression_ac_core, pytest.mark.regression_ac, pytest.mark.ac_api_v1, pytest.mark.ac_api_v1_email, pytest.mark.ac_api]


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_send_email_with_project_ids():
    payload = {
        "email": "payrateconnect.stage.xyz@gmail.com",
        "projectIds": [511, 469, 1
                       ]
    }

    resp = AC_API_V1(AUTH_KEY).send_email(payload)
    resp.assert_response_status(200)
    assert len(resp.json_response) > 0


def test_send_email_with_empty_payload():
    api = AC_API_V1(AUTH_KEY)
    resp = api.send_email(payload={})
    resp.assert_response_status(422)
    assert len(resp.json_response['fieldErrors']) == 2


def test_send_email_with_invalid_auth_key():
    api = AC_API_V1(AUTH_KEY + "x67")
    resp = api.send_email(payload={})
    resp.assert_response_status(403)
    assert resp.json_response == {'error': 'Forbidden'}