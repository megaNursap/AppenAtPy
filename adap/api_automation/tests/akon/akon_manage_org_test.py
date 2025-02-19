import pytest
import allure
import random
import time
from adap.api_automation.services_config.akon import AkonUser
from adap.api_automation.utils.data_util import get_user_api_key, get_user_org_id, get_user_email, get_user_password, get_user_name
from adap.api_automation.services_config.requestor_proxy import RP

pytestmark = pytest.mark.regression_core


# for fed, get Akon info is through request proxy, we need to call 2 apis to get jwt token.
# 1. call get session to get the session id 2. use session id to call v1/me api to get jwt token,
# then call v1/me to get akon info
@allure.parent_suite('/me:get')
@pytest.mark.parametrize('user_role_type, expected_status',
                         [('cf_internal_role', 200),
                          ('non_cf_team', 200)])
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.skipif(pytest.running_in_preprod, reason="Only enabled in fed")
def test_access_to_me_endpoint_fed(user_role_type, expected_status):
    rp = RP(jwt_token=None)
    payload = {
        "email": get_user_email(user_role_type),
        "password": get_user_password(user_role_type)
    }
    res1 = rp.get_session(payload)
    session_id = res1.json_response.get('id')
    res2 = rp.get_jwt_from_session(session_id)
    jwt = res2.headers.get('x-cf-jwt-token')
    user = AkonUser(get_user_api_key('cf_internal_role'), jwt_token=jwt)
    res3 = user.get_akon_info()
    res3.assert_response_status(expected_status)
    assert res3.json_response['name'] == get_user_name(user_role_type)
    assert res3.json_response['email'] == get_user_email(user_role_type)


@allure.parent_suite('/organizations/{org_id}/users:get')
@pytest.mark.cross_team
@pytest.mark.akon
@pytest.mark.adap_api_uat
@pytest.mark.parametrize('user_role_type, expected_status',
                         [('internal_app_role', 200),
                          ('cf_internal_role', 200),
                          ('team_admin', 403),
                          ('org_admin', 403),
                          ('standard_user', 403)])
def test_get_org_users(user_role_type, expected_status):
    user = AkonUser(get_user_api_key(user_role_type))
    res = user.get_akon_info()
    res.assert_response_status(expected_status)

    if expected_status == 200:
        assert user.current_team_id is not None
        assert user.api_team_id is not None
        assert user.team_ids is not None
        assert user.organization_id is not None

    resp = user.users_in_organization(user.organization_id)
    resp.assert_response_status(expected_status)


@allure.parent_suite('/organizations/{org_id}/users:get')
@pytest.mark.cross_team
@pytest.mark.parametrize('user_role_type, expected_status',
                         [("internal_app_role", 404),
                          ("cf_internal_role", 404)])
def test_get_org_users_invalid_key_valid_org_id(user_role_type, expected_status):
    user = AkonUser("invalid_key")

    res = user.users_in_organization(get_user_org_id(user_role_type))
    # NOTE: the http status code is 302. The requests library redirects to a 404
    res.assert_response_status(expected_status)


@allure.parent_suite('/organizations/{org_id}/users:get')
@pytest.mark.cross_team
@pytest.mark.parametrize('user_role_type, expected_status',
                         [("internal_app_role", 404),
                          ("cf_internal_role", 404)])
def test_get_org_users_valid_key_invalid_org_id(user_role_type, expected_status):
    user = AkonUser(get_user_api_key(user_role_type))

    res = user.users_in_organization("invalid_org_id")
    # NOTE: the http status code is 302. The requests library redirects to a 404
    res.assert_response_status(expected_status)


@allure.parent_suite('/organizations/{org_id}/users?email={email}:get')
@pytest.mark.cross_team
@pytest.mark.akon
@pytest.mark.parametrize('user_role_type, expected_status',
                         [('internal_app_role', 200),
                          ('cf_internal_role', 200)])
def test_get_user_by_email_from_list_exact_match(user_role_type, expected_status):
    user = AkonUser(get_user_api_key(user_role_type))

    res = user.get_akon_info()
    res.assert_response_status(expected_status)

    resp = user.users_in_organization(user.organization_id)
    resp.assert_response_status(expected_status)
    user_emails = []

    # stores the user emails
    users = resp.json_response.get('users')
    for i in range(0, len(users) - 1):
        user_emails.append(users[i]['email'])
    print(user_emails)
    # search for a random user in the list
    i = random.randint(0, len(user_emails) - 1)
    resp_filtered = user.users_in_organization(user.organization_id, user_emails[i])
    resp_filtered.assert_response_status(200)

    # Verify that the email in the response matches the email passed in to filter.
    # It's an exact match so we're always looking at the first item in the json list
    assert user_emails[i] == resp_filtered.json_response.get('users')[0]['email']


@allure.parent_suite('/organizations/{org_id}/users?page={num}&per_page={num}:get')
@pytest.mark.cross_team
@pytest.mark.parametrize('scenario, page, per_page, expected_status',
                         [("page=0", 0, 1, 422),
                          ("per_page=0", 1, 0, 422),
                          ("negative", -1, -1, 422),
                          ("per_page as text", 1, "invalid", 422),
                          ("page as text", "invalid", 1, 422),
                          ("happy path", 2, 3, 200)])
def test_paginate_org_users_invalid(scenario, page, per_page, expected_status):
    user = AkonUser(get_user_api_key('cf_internal_role'))

    res = user.get_akon_info()
    res.assert_response_status(200)

    resp = user.users_in_organization_paginated(user.organization_id, page, per_page)
    resp.assert_response_status(expected_status)


@allure.parent_suite('/organizations/{org_id}/users?page={num}&per_page={num}:get')
@pytest.mark.cross_team
@pytest.mark.akon
@pytest.mark.parametrize('role, page, per_page, expected_status',
                         [('internal_app_role', 1, 1, 200),
                          ('cf_internal_role', 10, 10, 200)])
def test_paginate_org_users_valid(role, page, per_page, expected_status):
    user = AkonUser(get_user_api_key(role))

    res = user.get_akon_info()
    res.assert_response_status(200)

    resp = user.users_in_organization_paginated(user.organization_id, page, per_page)
    resp.assert_response_status(expected_status)

    pagination = resp.json_response.get('pagination')
    assert page == pagination['page']
    assert per_page == pagination['per_page']
    assert pagination['total_users']
    assert pagination['total_pages']


@allure.parent_suite('/organizations/{org_id}/users?email={email}:get')
@pytest.mark.cross_team
@pytest.mark.parametrize('user_role_type, expected_status',
                         [('internal_app_role', 200),
                          ('cf_internal_role', 200)])
def test_get_user_by_email_less_than_three_char(user_role_type, expected_status):
    """
        This test is to ensures that if you enter 1 or 2 chars to search for an email, it shouldn't return
        anything.
    """
    user = AkonUser(get_user_api_key(user_role_type))

    res = user.get_akon_info()
    res.assert_response_status(expected_status)

    resp = user.users_in_organization(user.organization_id)
    resp.assert_response_status(expected_status)
    user_emails = []

    # stores the user emails
    users = resp.json_response.get('users')
    for i in range(0, len(users) - 1):
        user_emails.append(users[i]['email'])

    # search for a random user in the list
    i = random.randint(0, len(user_emails) - 1)
    j = random.randint(1, 2)

    # get the first 1 or 2 char(s) of the email string
    partial_email = user_emails[i][0:j]

    resp_filtered = user.users_in_organization(user.organization_id, partial_email)
    resp_filtered.assert_response_status(200)

    pagination = resp_filtered.json_response.get('pagination')
    users = resp_filtered.json_response.get('users')
    time.sleep(2)
    assert pagination['page'] == 1
    assert pagination['per_page'] == 10
    assert pagination['total_users'] == 0, "this shouldn't return any users"
    assert users == []
    assert pagination['total_pages'] == 1


@allure.parent_suite('/organizations/{org_id}/users?email={email}:get')
@pytest.mark.cross_team
@pytest.mark.parametrize('user_role_type, expected_status',
                         [('internal_app_role', 200),
                          ('cf_internal_role', 200)])
def test_get_user_by_email_three_char(user_role_type, expected_status):
    """
        This test is to ensures that a 3 char min should result in emails returned
        anything.
    """
    user = AkonUser(get_user_api_key(user_role_type))

    res = user.get_akon_info()
    res.assert_response_status(expected_status)

    resp = user.users_in_organization(user.organization_id)
    resp.assert_response_status(expected_status)
    user_emails = []

    # stores the user emails
    users = resp.json_response.get('users')
    for i in range(0, len(users) - 1):
        user_emails.append(users[i]['email'])

    # search for a random user in the list
    i = random.randint(0, len(user_emails) - 1)

    # get the first 3 chars of the email string
    partial_email = user_emails[i][2:5]

    resp_filtered = user.users_in_organization(user.organization_id, partial_email)
    resp_filtered.assert_response_status(200)

    pagination = resp_filtered.json_response.get('pagination')
    users = resp_filtered.json_response.get('users')
    time.sleep(2)
    assert pagination['page'] == 1
    assert pagination['per_page'] == 10
    assert pagination['total_users'] != 0, "this should return users!"
    assert users != []
    assert pagination['total_pages'] != 0


