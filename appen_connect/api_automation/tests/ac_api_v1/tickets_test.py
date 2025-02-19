from datetime import date
from random import randint

from appen_connect.api_automation.services_config.ac_api_v1 import AC_API_V1
from appen_connect.ui_automation.tests.v1_ui_tests.internal_home_test import generated_unique_digit
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_core, pytest.mark.regression_ac, pytest.mark.ac_api_v1, pytest.mark.ac_api_v1_tickets, pytest.mark.ac_api]


AUTH_KEY = get_test_data('auth_key', 'auth_key')
# *** incomplete as I see valid ticket ID also returning 404, not sure if the API is correctly documented in Swagger ***
@pytest.mark.skip(reason='Bug')
def test_get_ticket_prepare_response():
    api = AC_API_V1(AUTH_KEY)
    ticket_id = get_test_data('test_active_vendor_account', 'ticket_id')
    resp = api.get_ticket_prepare_response(ticketId=ticket_id)
    resp.assert_response_status(200)


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_ticket_smart_ticket_answering_by_id():
    api = AC_API_V1(AUTH_KEY)
    ticket_id = get_test_data('test_active_vendor_account', 'ticket_id')
    resp = api.get_smart_ticket_answering_by_id(ticketId=ticket_id)
    resp.assert_response_status(200)


def test_get_ticket_smart_ticket_answering_by_invalid_id():
    api = AC_API_V1(AUTH_KEY)
    ticket_id = randint(10000000,12000000)
    resp = api.get_smart_ticket_answering_by_id(ticketId=ticket_id)
    resp.assert_response_status(400)
    assert (len(resp.json_response)>0)


@pytest.mark.parametrize('auth_key, expected_status, error_msg',
                         [("1221jjidefghijklmn123opQRSTUVWreo09014bE", 403, {'error': 'Forbidden'}),
                          ("", 403, {'error': 'Forbidden'})])
def test_get_ticket_smart_ticket_answering_id_invalid_auth(auth_key, expected_status, error_msg):
    api = AC_API_V1(auth_key)
    ticket_id = get_test_data('test_active_vendor_account', 'ticket_id')
    resp = api.get_smart_ticket_answering_by_id(ticketId=ticket_id)
    resp.assert_response_status(expected_status)
    assert len(resp.json_response) > 0
    assert resp.json_response == error_msg


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_post_smart_ticket_answering():
    api = AC_API_V1(AUTH_KEY)
    ticket_id = get_test_data('test_active_vendor_account', 'ticket_id')
    user_id = get_test_data('test_active_vendor_account','id')
    team_names = ["HR", "Finance", "support", "Quality", "Recruiting"]
    ticket_title = "Post smart Ticket using api Automation" + str(generated_unique_digit())
    to_date = date.today()
    ticket_timestamp = to_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {
        "teamName": random.choice(team_names),
        "ticketBody": "test",
        "ticketTitle": ticket_title,
        "ticketTimestamp": ticket_timestamp,
        "userId": user_id,
        "ticketId": ticket_id
    }
    resp = api.post_smart_ticket_answering(payload=payload)
    resp.assert_response_status(200)


@pytest.mark.parametrize('auth_key, expected_status, error_msg',
                         [("1221jjidefghijklmn123opQRSTUVWreo09014bE", 403, {'error': 'Forbidden'}),
                          ("", 403, {'error': 'Forbidden'})])
def test_post_smart_ticket_answering_invalid_auth(auth_key, expected_status, error_msg):
    api = AC_API_V1(auth_key)
    ticket_id = get_test_data('test_active_vendor_account', 'ticket_id')
    user_id = get_test_data('test_active_vendor_account', 'id')

    team_names = ["HR", "Finance", "support", "Quality", "Recruiting"]
    ticketTitle = "Post smart Ticket using api Automation" + str(generated_unique_digit())
    to_date = date.today()
    ticketTimestamp = to_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {
        "teamName": random.choice(team_names),
        "ticketBody": "test",
        "ticketTitle": ticketTitle,
        "ticketTimestamp": ticketTimestamp,
        "userId": user_id,
        "ticketId": ticket_id
    }
    resp = api.post_smart_ticket_answering(payload=payload)
    resp.assert_response_status(expected_status)
    assert len(resp.json_response) > 0
    assert resp.json_response == error_msg