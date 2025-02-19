import pytest
import allure
import jwt
from adap.api_automation.services_config.workflow import Workflow
from adap.api_automation.services_config.akon import AkonUser
from adap.api_automation.utils.data_util import get_user_api_key, get_user_email

WHITELISTED_ROLES = {'cf_internal', 'internal_app', 'organization_manager', 'finance_manager', 'super_admin'}

pytestmark = [pytest.mark.regression_wf, pytest.mark.adap_wf_api]


@allure.parent_suite('/extauth/workflows:get')
@pytest.mark.skip_hipaa
@pytest.mark.workflow
@pytest.mark.parametrize('user_role_type',
                         ['internal_app_role',
                          'cf_internal_role',
                          'team_admin',
                          'standard_user',
                          'multi_team_user'])
def test_generate_jwt_token(user_role_type):
    """
    This test verifies that a token is generated from Akon to be used by api gateway.
    Any user role can generate a token. api gateway will only
    recognize it if the permissions are correct
    """
    api_key = get_user_api_key(user_role_type)
    email = get_user_email(user_role_type)
    akon = AkonUser(api_key)
    resp = akon.get_auth_for_wf()
    resp.assert_response_status(200)

    wf_1 = Workflow(api_key)
    bearer_token = wf_1.get_token(resp)

    if not bearer_token:
        raise Exception("JWT token cannot be None. Exiting the test")

    extracted_token = bearer_token.split(" ")
    token = extracted_token[1]
    decoded_token = jwt.decode(token, options={"verify_signature": False})

    assert decoded_token['aud'] == ['workflows']
    assert decoded_token['sub'] == email

    roles = decoded_token['data']['global_roles']

    if roles:
        assert set(roles).issubset(WHITELISTED_ROLES), "None of of the whitelisted roles \
        are being returned list for global roles"
