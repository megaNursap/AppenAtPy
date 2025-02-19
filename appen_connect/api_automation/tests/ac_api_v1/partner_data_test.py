import dateutil
import jwt

from appen_connect.api_automation.services_config.ac_api_v1 import AC_API_V1
from adap.api_automation.utils.data_util import *
from datetime import date

pytestmark = [pytest.mark.regression_ac_core, pytest.mark.regression_ac, pytest.mark.ac_api_v1, pytest.mark.ac_api_v1_partner_data, pytest.mark.ac_api]


AUTH_KEY = get_test_data('auth_key', 'auth_key')


def get_a9_token(claims):
    token = jwt.encode(claims, 'secret', algorithm='HS256')
    return token


@pytest.mark.ac_api_uat
def test_opt_in_acknowledgement():
    id = get_test_data('test_active_vendor_account', 'id')
    project = get_test_data('test_active_vendor_account','project_id')
    api_key_a9 = get_test_data('a9', 'api_key')

    claims = {'key': api_key_a9, 'id': id, 'project_name': project}

    token = get_a9_token(claims)
    api = AC_API_V1(AUTH_KEY)
    resp = api.post_opt_in_acknowledge(payload=token)
    resp.assert_response_status(200)


def test_opt_in_acknowledgement_empty_token():
    token = ''
    api = AC_API_V1(AUTH_KEY)
    resp = api.post_opt_in_acknowledge(payload=token)
    resp.assert_response_status(200)
    assert resp.text == 'Error: JWT String argument cannot be null or empty.'


def test_opt_in_acknowledgement_invalid_token():
    token = 'jfdskjwerew2fdd'
    api = AC_API_V1(AUTH_KEY)
    resp = api.post_opt_in_acknowledge(payload=token)
    resp.assert_response_status(200)
    assert resp.text == 'Error: JWT strings must contain exactly 2 period characters. Found: 0'


@pytest.mark.parametrize('auth_key, expected_status, error_msg',
                         [("1221jjidefghijklmn123opQRSTUVWreo09014bE", 403, {'error': 'Forbidden'}),
                          ("", 403, {'error': 'Forbidden'})])
def test_opt_in_acknowledge_invalid_auth(auth_key, expected_status, error_msg):
    id = get_test_data('test_active_vendor_account', 'id')

    project = get_test_data('test_active_vendor_account', 'project_id')

    claims = {'some': 'none', 'id': id, 'project_name': project}
    token = get_a9_token(claims)
    api = AC_API_V1(auth_key)
    resp = api.post_opt_in_acknowledge(payload=token)
    resp.assert_response_status(expected_status)
    assert len(resp.json_response) > 0
    assert resp.json_response == error_msg


@pytest.mark.ac_api_uat
def test_create_partner_data():
    user_id = get_test_data('test_active_vendor_account', 'id')

    api = AC_API_V1(AUTH_KEY)
    project_id = get_test_data('test_active_vendor_account', 'project_id')

    to_date = date.today()
    report_date = to_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    complete_date = (to_date + dateutil.relativedelta.relativedelta(months=-1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    api.payload = {
        "projectId": project_id,
        "invoiceData": True,
        "completionDate": complete_date,
        "reportDate": report_date,
        "taskId": "5555",
        "taskType": "DEFAULT",
        "city": "Fremont",
        "language": "ENG",
        "userId": user_id,
        "unitsOfWorkAvailable": 3.67,
        "unitsOfWorkCompleted": 1
    }
    resp = api.create_partner_data(payload=api.payload)
    resp.assert_response_status(200)
    assert resp.json_response['taskId'] == api.payload['taskId']
    assert resp.json_response['projectId'] == int(project_id)


def test_create_partner_data_invalid_task():
    user_id = get_test_data('test_active_vendor_account', 'id')

    api = AC_API_V1(AUTH_KEY)
    project_id = get_test_data('test_active_vendor_account', 'project_id')

    to_date = date.today()
    report_date = to_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    completed_date = (to_date + dateutil.relativedelta.relativedelta(months=-1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {
        "projectId": project_id,
        "invoiceData": True,
        "completionDate": completed_date,
        "reportDate": report_date,
        "taskId": "5555",
        "taskType": "DEFAULT_new",
        "city": "Fremont",
        "language": "ENG",
        "userId": user_id,
        "unitsOfWorkAvailable": 3.67,
        "unitsOfWorkCompleted": 1
    }
    resp = api.create_partner_data(payload=payload)
    resp.assert_response_status(400)
    assert (resp.json_response['fieldErrors'][0][
                'message'] == 'Invalid task specified. A payrate does not exist for this project id %s and taskType: %s' % (
                project_id, "DEFAULT_new"))


def test_create_partner_data_invalid_project():
    user_id = get_test_data('test_active_vendor_account', 'id')

    api = AC_API_V1(AUTH_KEY)
    to_date = date.today()
    report_date = to_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    completed_date = (to_date + dateutil.relativedelta.relativedelta(months=-1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {
        "projectId": 6789899,
        "invoiceData": True,
        "completionDate": completed_date,
        "reportDate": report_date,
        "taskId": "5555",
        "taskType": "DEFAULT",
        "dateCreated": "2020-03-20T12:00:00Z",
        "city": "Fremont",
        "language": "ENG",
        "userId": user_id,
        "unitsOfWorkAvailable": 3.67,
        "unitsOfWorkCompleted": 1
    }
    resp = api.create_partner_data(payload=payload)
    resp.assert_response_status(400)
    assert (len(resp.json_response) > 0)


@pytest.mark.parametrize('auth_key, expected_status, error_msg',
                         [("1221jjidefghijklmn123opQRSTUVWreo09014bE", 403, {'error': 'Forbidden'}),
                          ("", 403, {'error': 'Forbidden'})])
def test_partner_data_invalid_auth(auth_key, expected_status, error_msg):
    user_id = get_test_data('test_active_vendor_account', 'id')

    api = AC_API_V1(auth_key)
    project_id = get_test_data('test_active_vendor_account', 'project_id')

    to_date = date.today()
    report_date = to_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    complete_date = (to_date + dateutil.relativedelta.relativedelta(months=-1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {
        "projectId": project_id,
        "invoiceData": True,
        "completionDate": complete_date,
        "reportDate": report_date,
        "taskId": "5555",
        "taskType": "DEFAULT",
        "city": "Fremont",
        "language": "ENG",
        "userId": user_id,
        "unitsOfWorkAvailable": 3.67,
        "unitsOfWorkCompleted": 1
    }
    resp = api.create_partner_data(payload=payload)
    resp.assert_response_status(expected_status)
    assert len(resp.json_response) > 0
    assert resp.json_response == error_msg