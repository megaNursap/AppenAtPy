from appen_connect.api_automation.services_config.ac_api_v1 import AC_API_V1
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_core, pytest.mark.regression_ac, pytest.mark.ac_api_v1, pytest.mark.ac_api_v1_user, pytest.mark.ac_api]

USER_EMAIL = get_user_email("test_ui_account")
USER_PASSWORD = get_user_password("test_ui_account")
AUTH_KEY = get_test_data('auth_key', 'auth_key')

# TODO tests for stage only!!!


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_user_by_email():
    api = AC_API_V1(AUTH_KEY)

    payload = {
        "email":USER_EMAIL
    }
    resp = api.get_user_by_email(payload)
    resp.assert_response_status(200)

    assert resp.json_response['email'] == USER_EMAIL
    assert resp.json_response['status'] == 'INTERNAL'
    assert resp.json_response['source'] == 'LEAPFORCE'


def test_get_user_by_email_hide_projects():
    api = AC_API_V1(AUTH_KEY)

    # get users from project
    resp = api.get_users_for_project('324')

    user_info = resp.json_response[0]
    user_email = user_info['email']

    payload = {
        "email": user_email,
        "hideOtherSystemProjects": "true"
    }
    resp = api.get_user_by_email(payload)
    resp.assert_response_status(200)

    assert resp.json_response['email'] == user_email
    assert resp.json_response['projects'] == []

    payload = {
        "email": user_email,
        "hideOtherSystemProjects": "false"
    }
    resp = api.get_user_by_email(payload)
    resp.assert_response_status(200)

    assert resp.json_response['email'] == user_email
    assert len(resp.json_response['projects']) > 0

    _df = pd.DataFrame(resp.json_response['projects'])
    _df = _df[_df.projectId == 324]
    assert _df.shape[0] == 1
    # # TODO use with different project to make sure hide is working


@pytest.mark.parametrize('auth_key, expected_status, error_msg',
                         [("1221jjidefghijklmn123opQRSTUVWreo09014bE", 403, {'error': 'Forbidden'}),
                          ("", 403, {'error': 'Forbidden'})])
def test_get_user_by_email_invalid_auth_key(auth_key, expected_status, error_msg):
    api = AC_API_V1(auth_key)

    payload = {
        "email": USER_EMAIL
    }
    resp = api.get_user_by_email(payload)
    resp.assert_response_status(expected_status)
    assert len(resp.json_response) > 0
    assert resp.json_response == error_msg


@pytest.mark.ac_api_uat
def test_get_user_by_email_not_exist():
    api = AC_API_V1(AUTH_KEY)

    payload = {
        "email": 'test_api@test.com'
    }
    resp = api.get_user_by_email(payload)
    resp.assert_response_status(404)


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_user_by_id():
    api = AC_API_V1(AUTH_KEY)

    payload = {
        "email": USER_EMAIL
    }
    resp = api.get_user_by_email(payload)
    resp.assert_response_status(200)

    user_info = resp.json_response
    user_id = user_info['id']

    resp = api.get_user_by_id(user_id)
    resp.assert_response_status(200)
    assert user_info == resp.json_response


@pytest.mark.parametrize('auth_key, expected_status, error_msg',
                         [("1221jjidefghijklmn123opQRSTUVWreo09014bE", 403, {'error': 'Forbidden'}),
                          ("", 403, {'error': 'Forbidden'})])
def test_get_user_by_id_invalid_auth_key(auth_key, expected_status, error_msg):
    api = AC_API_V1(AUTH_KEY)

    payload = {
        "email": USER_EMAIL
    }
    resp = api.get_user_by_email(payload)
    resp.assert_response_status(200)

    user_info = resp.json_response
    user_id = user_info['id']

    api = AC_API_V1(auth_key)
    resp = api.get_user_by_id(user_id)
    resp.assert_response_status(expected_status)
    assert len(resp.json_response) > 0
    assert resp.json_response == error_msg

    # TODO hideOtherSystemProjects


def test_get_users_for_project():
    api = AC_API_V1(AUTH_KEY)

    # 324 - F8 integration
    resp = api.get_users_for_project('324')
    resp.assert_response_status(200)
    assert len(resp.json_response) > 0


@pytest.mark.parametrize('auth_key, expected_status, error_msg',
                         [("1221jjidefghijklmn123opQRSTUVWreo09014bE", 403, {'error': 'Forbidden'}),
                          ("", 403, {'error': 'Forbidden'})])
def test_get_users_for_project_invalid_auth_key(auth_key, expected_status, error_msg):
    api = AC_API_V1(auth_key)

    # 324 - F8 integration
    resp = api.get_users_for_project('324')
    resp.assert_response_status(expected_status)
    assert len(resp.json_response) > 0
    assert resp.json_response == error_msg


def test_get_users_for_project_include_internals():
    api = AC_API_V1(AUTH_KEY)

    payload = {
        "includeInternals" : 'true'
    }
    # 324 - F8 integration
    resp = api.get_users_for_project('324', payload)
    resp.assert_response_status(200)
    assert len(resp.json_response) > 0

    count_include_internal_users = len(resp.json_response)

    _df = pd.DataFrame(resp.json_response)
    _df = _df[_df.isInternal == True]
    assert _df.shape[0] > 0
    internal_user = _df.shape[0]

    payload = {
        "includeInternals": 'false'
    }
    # 324 - F8 integration
    resp = api.get_users_for_project('324', payload)
    resp.assert_response_status(200)
    count_not_include_internal_users = len(resp.json_response)

    assert count_include_internal_users == count_not_include_internal_users + internal_user


@pytest.mark.ac_api_uat
def test_check_password_valid():
    api = AC_API_V1(AUTH_KEY)

    resp = api.check_user_password(USER_EMAIL, USER_PASSWORD)
    resp.assert_response_status(200)
    assert resp.json_response


@pytest.mark.ac_api_uat
def test_check_password_empty():
    api = AC_API_V1(AUTH_KEY)

    resp = api.check_user_password(USER_EMAIL, '')
    resp.assert_response_status(400)
    assert resp.json_response == {}


@pytest.mark.ac_api_uat
def test_check_password_invalid():
    api = AC_API_V1(AUTH_KEY)

    resp = api.check_user_password(USER_EMAIL, '123ABC')
    resp.assert_response_status(200)
    assert resp.json_response == False


@pytest.mark.parametrize('auth_key, expected_status, error_msg',
                         [("1221jjidefghijklmn123opQRSTUVWreo09014bE", 403, {'error': 'Forbidden'}),
                          ("", 403, {'error': 'Forbidden'})])
def test_user_password_invalid_auth_key(auth_key, expected_status, error_msg):
    api = AC_API_V1(auth_key)

    resp = api.check_user_password(USER_EMAIL, USER_PASSWORD)
    resp.assert_response_status(expected_status)
    assert resp.json_response == error_msg


def test_set_up_faceid():
    api = AC_API_V1(AUTH_KEY)

    payload = {
        "email": USER_EMAIL
    }
    resp = api.get_user_by_email(payload)
    resp.assert_response_status(200)

    user_info = resp.json_response
    user_id = user_info['id']

    random_id = str(random.randint(10000, 20000))
    res = api.post_faceid_for_user(user_id, random_id)
    res.assert_response_status(200)

    assert res.json_response['id'] == user_id
    assert res.json_response['faceId'] == random_id


def test_set_up_faceid_empty():
    api = AC_API_V1(AUTH_KEY)

    payload = {
        "email": USER_EMAIL
    }
    resp = api.get_user_by_email(payload)
    resp.assert_response_status(200)

    user_info = resp.json_response
    user_id = user_info['id']

    res = api.post_faceid_for_user(user_id, '')
    res.assert_response_status(400)


@pytest.mark.parametrize('auth_key, expected_status, error_msg',
                         [("1221jjidefghijklmn123opQRSTUVWreo09014bE", 403, {'error': 'Forbidden'}),
                          ("", 403, {'error': 'Forbidden'})])
def test_set_up_faceid_invalid_auth_key(auth_key, expected_status, error_msg):
    api = AC_API_V1(AUTH_KEY)

    payload = {
        "email": USER_EMAIL
    }
    resp = api.get_user_by_email(payload)
    resp.assert_response_status(200)

    user_info = resp.json_response
    user_id = user_info['id']

    api = AC_API_V1(auth_key)
    res = api.post_faceid_for_user(user_id, user_id)
    res.assert_response_status(expected_status)
    assert res.json_response == error_msg