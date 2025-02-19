import pytest
import allure
import random
from adap.api_automation.services_config.requestor_proxy import RP
from adap.api_automation.utils.data_util import get_user_org_id, get_test_data

pytestmark = [pytest.mark.regression_core, pytest.mark.v]


@allure.parent_suite('RP/organizations/{org_id}/users:get')
@pytest.mark.cross_team
@pytest.mark.parametrize('user_role_type, expected_status',
                         [('cf_internal_role', 200),
                          ('team_admin', 404),
                          ('org_admin', 200),
                          ('standard_user', 404)])
def test_access_to_org_users_endpoint_rp(user_role_type, expected_status):
    """
        This test ensures that org admins are able to get the list of users in an organization through RP
    """
    # rp = RP(get_test_data(user_role_type, 'jwt_token'))
    username = get_test_data(user_role_type, 'email')
    password = get_test_data(user_role_type, 'password')

    rp = RP()
    rp.get_valid_sid(username, password)

    org_id = get_user_org_id(user_role_type)
    res = rp.get_org_users_rp(org_id)
    res.assert_response_status(expected_status)

    users = res.json_response.get('users')
    pagination = res.json_response.get('pagination')

    if expected_status == 200:
        assert users is not None
        assert pagination is not None
        assert len(users) == pagination['total_users']


# TODO change test when https://appen.atlassian.net/browse/AT-5192 is ready
# @allure.parent_suite('RP/organizations/{org_id}/users:get')
# @pytest.mark.cross_team
# @pytest.mark.parametrize('user_role_type, expected_status',
#                          [('cf_internal_role', 401),
#                           ('team_admin', 401),
#                           ('org_admin', 401),
#                           ('standard_user', 401)])
# def test_org_users_invalid_token_rp(user_role_type, expected_status):
#     # rp = RP(get_test_data(user_role_type, 'jwt_token'))
#     username = get_test_data(user_role_type, 'email')
#     password = get_test_data(user_role_type, 'password')
#
#     rp = RP()
#     # rp.get_valid_sid(username, password)
#
#     org_id = get_user_org_id(user_role_type)
#     res = rp.get_org_users_rp(org_id, jwt_token='invalid_jwt')
#     res.assert_response_status(expected_status)
#     assert res.content == b'You need to sign in or sign up before continuing.'


@allure.parent_suite('RP/organizations/{org_id}/users:get')
@pytest.mark.cross_team
@pytest.mark.parametrize('user_role_type, expected_status',
                         [('cf_internal_role', 200),
                          ('org_admin', 200)])
def test_org_users_less_than_three_char_rp(user_role_type, expected_status):
    username = get_test_data(user_role_type, 'email')
    password = get_test_data(user_role_type, 'password')

    rp = RP()
    rp.get_valid_sid(username, password)

    org_id = get_user_org_id(user_role_type)
    user_emails = []

    res = rp.get_org_users_rp(org_id)
    res.assert_response_status(expected_status)

    users = res.json_response.get('users')

    for i in range(0, len(users) - 1):
        user_emails.append(users[i]['email'])

    # search for a random user in the list
    i = random.randint(0, len(user_emails) - 1)
    j = random.randint(1, 2)

    # get the first 1 or 2 chars of the email string
    partial_email = user_emails[i][0:j]

    res_filtered = rp.get_org_users_rp(org_id, partial_email)
    res_filtered.assert_response_status(expected_status)

    filtered_users = res_filtered.json_response.get('users')

    assert filtered_users == []
