
from random import randint

from adap.api_automation.utils.data_util import *
from appen_connect.api_automation.services_config.sql_report_service import SqlReportService

pytestmark = [pytest.mark.regression_ac_sql_reports,
              pytest.mark.regression_ac,
              pytest.mark.ac_api_v2,
              pytest.mark.ac_api_v2_sql_reports]


def test_get_template_by_id(ac_api_cookie):
    api = SqlReportService(ac_api_cookie)
    res = api.get_template_by_id(35)
    res.assert_response_status(200)
    assert len(res.json_response) > 0
    assert res.json_response['id'] == 35


def test_create_report_template(ac_api_cookie):
    api = SqlReportService(ac_api_cookie)
    payload = {
        "category": "Recruiting",
        "name": "template using Automation" + str(randint(1, 99)),
        "description": "Make a consult for users",
        "syntax": "MySql",
        "statement": "SELECT u.id FROM QRP.users u limit 10"
    }
    created_user_id = get_test_data('test_ui_account', 'id')
    res = api.create_template(payload)
    res.assert_response_status(201)
    assert res.json_response['createdByUserId'] == int(created_user_id)


def test_update_report_template(ac_api_cookie):
    api = SqlReportService(ac_api_cookie)
    payload = {
        "category": "Finance",
        "name": "template using Automation" + str(randint(1, 99)),
        "description": "Make a consult for users",
        "syntax": "MySql",
        "statement": "SELECT u.id FROM QRP.users u limit 10"
    }
    res = api.create_template(payload)
    res.assert_response_status(201)
    template_id = res.json_response['id']
    payload1 = {
        "id": template_id,
        "category": "Finance",
        "name": "template using Automation" + str(randint(1, 99)),
        "description": "Make a consult for users",
        "syntax": "MySql",
        "statement": "SELECT u.id FROM QRP.users u limit 10"
    }
    updated_user_id = get_test_data('test_ui_account', 'id')
    res1 = api.update_template(template_id, payload1)
    res1.assert_response_status(200)
    print(res1.json_response)
    res1.json_response['updatedByUserId'] = updated_user_id
    res1.json_response['category'] = payload1['category']


def test_delete_report_template(ac_api_cookie):
    api = SqlReportService(ac_api_cookie)
    payload = {
        "category": "Finance",
        "name": "template using Automation" + str(randint(1, 99)),
        "description": "Make a consult for users",
        "syntax": "MySql",
        "statement": "SELECT u.id FROM QRP.users u limit 10"
    }
    res = api.create_template(payload)
    res.assert_response_status(201)
    template_id = res.json_response['id']
    payload1 = {
        "id": template_id,
        "category": "Finance",
        "name": "template using Automation" + str(randint(1, 99)),
        "description": "Make a consult for users",
        "syntax": "MySql",
        "statement": "SELECT u.id FROM QRP.users u limit 10"
    }
    res1 = api.delete_template(template_id, payload1)
    res1.assert_response_status(200)


def test_get_template_categories(ac_api_cookie):
    api = SqlReportService(ac_api_cookie)
    categories = ["Engineering", "Finance", "Human Resources", "Project Manager", "Quality", "Recruiting"]
    res = api.get_template_categories()
    res.assert_response_status(200)
    assert len(res.json_response) > 0
    res.json_response == categories

def test_get_templates(ac_api_cookie):
    api = SqlReportService(ac_api_cookie)
    res = api.get_templates()
    res.assert_response_status(200)
    assert len(res.json_response) > 0
