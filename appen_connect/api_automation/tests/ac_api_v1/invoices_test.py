from datetime import date

from dateutil.relativedelta import relativedelta

from appen_connect.api_automation.services_config.ac_api_v1 import AC_API_V1
from adap.api_automation.utils.data_util import *


pytestmark = [pytest.mark.regression_ac_core, pytest.mark.regression_ac, pytest.mark.ac_api_v1, pytest.mark.ac_api_v1_invoices, pytest.mark.ac_api]

AUTH_KEY = get_test_data('auth_key', 'auth_key')

def get_invoice_dates():
    first_day_of_this_month = date.today().replace(day=1)
    last_month_first_day = first_day_of_this_month - relativedelta(months=1)
    prev_last_month_first_day = first_day_of_this_month - relativedelta(months=2)
    first_day_of_prev_month = [last_month_first_day.strftime("%Y-%m-%dT%H:%M:%SZ"),
                               prev_last_month_first_day.strftime("%Y-%m-%dT%H:%M:%SZ")]
    return first_day_of_prev_month


@pytest.mark.ac_api_uat
def test_create_invoice():
    api = AC_API_V1(AUTH_KEY)
    user_id = get_test_data('test_active_vendor_account', 'id')
    invoice_dates = get_invoice_dates()
    endDate = invoice_dates[0]
    startDate = invoice_dates[1]
    api.payload = {
        "userId": user_id,
        "startDate": startDate,
        "endDate": endDate,
        "specialFeeDtos": [{"specialFeeCode": "ROW_PAY", "amount": "1.99"
                            }]
    }
    resp = api.create_invoice(payload=api.payload)
    resp.assert_response_status(200)
    assert (resp.json_response['userId'] == int(user_id))
    assert (resp.json_response['status'] == 'DRAFT')


def test_create_invoice_invalid_data():
    api = AC_API_V1(AUTH_KEY)
    user_id = get_test_data('test_active_vendor_account', 'id')
    invoice_dates = get_invoice_dates()
    endDate = invoice_dates[0]
    startDate = invoice_dates[1]
    api.payload = {
        "userId": user_id,
        "startDate": startDate,
        "endDate": endDate,
        "specialFeeDtos": [{"specialFeeCode": "ROW_PAY"
                            }]
    }
    resp = api.create_invoice(payload=api.payload)
    resp.assert_response_status(400)
    assert (resp.json_response == {'fieldErrors': [{'field': 'error', 'message': None}]})


@pytest.mark.ac_api_uat
def test_find_invoices():
    api = AC_API_V1(AUTH_KEY)
    user_id = get_test_data('test_active_vendor_account', 'id')
    invoice_dates = get_invoice_dates()
    endDate = invoice_dates[0]
    startDate = invoice_dates[1]
    api.payload = {"list":
                   [{"userId": user_id,
                     "startDate": startDate,
                     "endDate": endDate}]
               }

    resp = api.find_invoices(payload=api.payload)
    resp.assert_response_status(200)
    assert resp.json_response[0]['userId'] == int(user_id)
    assert resp.json_response[0]['startDate'] == startDate


def test_find_invoices_invalid_data():
    api = AC_API_V1(AUTH_KEY)
    user_id = get_test_data('test_active_vendor_account', 'id')
    invoice_dates = get_invoice_dates()
    endDate = invoice_dates[0]
    startDate = "2019-03-31T12:00:00"
    api.payload = {"list":
                   [{"userId": user_id,
                     "startDate": startDate,
                     "endDate": endDate}]
               }

    resp = api.find_invoices(payload=api.payload)
    resp.assert_response_status(400)


@pytest.mark.ac_api_uat
def test_create_invoices():
    api = AC_API_V1(AUTH_KEY)
    user_id = get_test_data('test_active_vendor_account', 'id')
    invoice_dates = get_invoice_dates()
    endDate = invoice_dates[0]
    startDate = invoice_dates[1]
    api.payload = {"list":
                   [{"userId": user_id,
                     "startDate": startDate,
                     "endDate": endDate,
                     "specialFeeDtos": [{"specialFeeCode": "ROW_PAY", "amount": "1.99"
                                         }]
                     }]
               }
    resp = api.create_invoices(payload=api.payload)
    resp.assert_response_status(200)
    assert resp.json_response[0]['userId'] == int(user_id)


def test_create_invoices_invalid_data():
    api = AC_API_V1(AUTH_KEY)
    user_id = get_test_data('test_active_vendor_account', 'id')
    invoice_dates = get_invoice_dates()
    endDate = invoice_dates[0]
    startDate = invoice_dates[1]
    api.payload = {"userId": user_id,
               "startDate": startDate,
               "endDate": endDate,
               "specialFeeDtos": [{"specialFeeCode": "ROW_PAY", "amount": "1.99"
                                   }]
               }
    resp = api.create_invoices(payload=api.payload)
    resp.assert_response_status(400)
    assert (resp.json_response == {'fieldErrors': [{'field': 'error', 'message': None}]})


@pytest.mark.ac_api_uat
def test_get_invoice():
    api = AC_API_V1(AUTH_KEY)
    # Create invoice and get invoice ID
    user_id = get_test_data('test_active_vendor_account', 'id')
    invoice_dates = get_invoice_dates()
    endDate = invoice_dates[0]
    startDate = invoice_dates[1]
    api.payload = {
        "userId": user_id,
        "startDate": startDate,
        "endDate": endDate,
        "specialFeeDtos": [{"specialFeeCode": "ROW_PAY", "amount": "1.99"
                            }]
    }
    resp_create_invoice = api.create_invoice(payload=api.payload)
    invoice_id = int(resp_create_invoice.json_response['id'])

    # Get invoice that has been created above
    resp = api.get_invoice(invoice_id=invoice_id)
    resp.assert_response_status(200)
    assert len(resp.json_response) > 0
    assert resp.json_response['id'] == invoice_id
    assert resp.json_response['userId'] == int(get_test_data('test_active_vendor_account', 'id'))


def test_get_invoice_invalid_id():
    api = AC_API_V1(AUTH_KEY)
    resp = api.get_invoice(invoice_id='416345444')
    resp.assert_response_status(404)
    assert (resp.json_response == {})


@pytest.mark.ac_api_uat
def test_find_invoice():
    api = AC_API_V1(AUTH_KEY)
    user_id = get_test_data('test_active_vendor_account', 'id')
    invoice_dates = get_invoice_dates()
    endDate = invoice_dates[0]
    startDate = invoice_dates[1]
    params = {'startDate': startDate, 'endDate': endDate, 'userId': user_id}
    resp = api.find_invoice(params=params)
    resp.assert_response_status(200)
    assert resp.json_response['userId'] == int(user_id)
    assert resp.json_response['startDate'] == startDate


def test_find_invoice_invalid_data():
    api = AC_API_V1(AUTH_KEY)
    user_id = get_test_data('test_active_vendor_account', 'id')
    invoice_dates = get_invoice_dates()
    endDate = "2019-03-31T12:00:00"
    startDate = invoice_dates[1]
    params = {'startDate': startDate, 'endDate': endDate, 'userId': user_id}
    resp = api.find_invoice(params=params)
    print(resp)
    resp.assert_response_status(400)
    assert (resp.json_response == {})