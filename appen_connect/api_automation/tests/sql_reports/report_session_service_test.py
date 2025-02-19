import time
from random import randint

from adap.api_automation.utils.data_util import *
from appen_connect.api_automation.services_config.sql_report_service import SqlReportService

pytestmark = [pytest.mark.regression_ac_sql_reports,
              pytest.mark.regression_ac,
              pytest.mark.ac_api_v2,
              pytest.mark.ac_api_v2_sql_reports]


def test_get_report_by_id(ac_api_cookie):
    api = SqlReportService(ac_api_cookie)
    res = api.get_report_by_id(39)
    res.assert_response_status(200)
    assert len(res.json_response) > 0
    assert res.json_response['id'] == 39


def test_get_report_by_invalid_id(ac_api_cookie):
    api = SqlReportService(ac_api_cookie)
    res = api.get_report_by_id(0)
    res.assert_response_status(400)
    assert res.json_response['errorMessage'] == 'The id must be present.'


def test_create_report(ac_api_cookie):
    api = SqlReportService(ac_api_cookie)
    payload = {
        "templateId": "1",
        "name": "session automation",
        "category": "",
        "description": "testing",
        "syntax": "MYSQL",
        "statement": "select id from qrp.users where age>30 limit 10"
    }
    created_user_email = get_test_data('test_ui_account', 'email')
    created_user_id = get_test_data('test_ui_account', 'id')
    res = api.create_report_session(payload)
    res.assert_response_status(201)
    assert res.json_response['createdByUserEmail'] == created_user_email
    assert res.json_response['createdByUserId'] == int(created_user_id)
    assert res.json_response['syntax'] == payload['syntax']
    assert res.json_response['status'] == 'ENQUEUED'


def test_update_report_by_id(ac_api_cookie):
    api = SqlReportService(ac_api_cookie)
    payload = {
        "templateId": "13",
        "name": "session automation create" + str(randint(1, 9)),
        "category": "Engineering",
        "description": "testing",
        "syntax": "MYSQL",
        "statement": "select u.id from qrp.users u limit 10"
    }
    res = api.create_report_session(payload)
    res.assert_response_status(201)
    report_id = res.json_response['id']
    res1 = api.get_report_by_id(report_id)
    res1.assert_response_status(200)
    assert len(res1.json_response) > 0
    assert res1.json_response['id'] == res.json_response['id']
    time.sleep(60)
    payload1 = {
        "templateId": "13",
        "name": "session automation update" + str(randint(1, 9)),
        "category": "Finance",
        "description": "testing",
        "syntax": "MYSQL",
        "statement": "select u.id from qrp.users u limit 10"
    }
    res2 = api.update_report_session_by_id(report_id, payload1)
    res2.assert_response_status(200)
    assert res2.json_response['category'] == payload1['category']


def test_download_report_by_id(ac_api_cookie):
    api = SqlReportService(ac_api_cookie)
    payload = {
        "templateId": "8",
        "name": "test recruit template",
        "category": "Recruiting",
        "description": "testing",
        "syntax": "MYSQL",
        "statement": "select id from qrp.users where age>30 limit 10"
    }
    res = api.create_report_session(payload)
    res.assert_response_status(201)
    time.sleep(60)
    report_id = res.json_response['id']
    res1 = api.download_report_session_by_id(report_id)
    res1.assert_response_status(200)
