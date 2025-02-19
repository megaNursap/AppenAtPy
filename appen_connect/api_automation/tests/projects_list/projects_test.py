from appen_connect.api_automation.services_config.ac_api import AC_API, create_new_random_project
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_project_list, pytest.mark.regression_ac, pytest.mark.ac_api_v2, pytest.mark.ac_api_v2_projects, pytest.mark.ac_api]


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_projects_ascending_id(ac_api_cookie):
    api = AC_API(ac_api_cookie)
    params = {
        "disabled": "false",
        "viewType": "full",
        "nameOrAlias": "",
        "customerId": 55,
        "page": 1,
        "sort": "id",
        "direction": "ASC"
    }
    res = api.get_projects(params=params)
    res.assert_response_status(200)
    assert res.json_response == sorted_list_of_dict_by_value(res.json_response, 'id')


def test_get_projects_descending_id(ac_api_cookie):
    api = AC_API(ac_api_cookie)
    params = {
        "disabled": "false",
        "viewType": "full",
        "nameOrAlias": "",
        "customerId": 1,
        "page": 1,
        "sort": "id",
        "direction": "DESC"
    }
    res = api.get_projects(params=params)
    res.assert_response_status(200)
    assert res.json_response == sorted_list_of_dict_by_value(res.json_response, 'id', reverse=True)


def test_get_projects_ascending_name(ac_api_cookie):
    api = AC_API(ac_api_cookie)
    params = {
        "disabled": "false",
        "viewType": "full",
        "nameOrAlias": "",
        "customerId": 55,
        "page": 1,
        "sort": "name",
        "direction": "ASC"
    }
    res = api.get_projects(params=params)
    res.assert_response_status(200)
    assert res.json_response == sorted_list_of_dict_by_value(res.json_response, 'name')


def test_get_projects_descend_name(ac_api_cookie):
    api = AC_API(ac_api_cookie)
    params = {
        "disabled": "false",
        "viewType": "full",
        "nameOrAlias": "",
        "customerId": 55,
        "page": 1,
        "sort": "name",
        "direction": "DESC"
    }
    res = api.get_projects(params=params)
    res.assert_response_status(200)
    assert res.json_response == sorted_list_of_dict_by_value(res.json_response, 'name', reverse=True)


@pytest.mark.ac_api_uat
def test_get_projects_descend_by_status(ac_api_cookie):
    api = AC_API(ac_api_cookie)
    params = {
        "disabled": "True",
        "viewType": "full",
        "nameOrAlias": "",
        "customerId": 55,
        "page": 1,
        "sort": "disabled",
        "direction": "DESC"
    }
    res = api.get_projects(params=params)
    res.assert_response_status(200)
    assert res.json_response == sorted_list_of_dict_by_value(res.json_response, 'id')
    assert res.json_response[0]['disabled'] == True


def test_get_projects_ascend_by_status(ac_api_cookie):
    api = AC_API(ac_api_cookie)
    params = {
        "disabled": "false",
        "viewType": "full",
        "nameOrAlias": "",
        "customerId": 1,
        "page": 1,
        "sort": "disabled",
        "direction": "ASC"
    }
    res = api.get_projects(params=params)
    res.assert_response_status(200)
    assert res.json_response[0]['disabled'] == False
    assert res.json_response == sorted_list_of_dict_by_value(res.json_response, 'id')


@pytest.mark.ac_api_uat
def test_get_projects_ascend_by_customer(ac_api_cookie):
    api = AC_API(ac_api_cookie)
    params = {
        "disabled": "",
        "viewType": "full",
        "nameOrAlias": "",
        "customerId":"",
        "page": 1,
        "sort": "customer",
        "direction": "ASC"
    }
    res = api.get_projects(params=params)
    res.assert_response_status(200)
    project_customer_id_list = []
    for i in range (0, (len(res.json_response)-1)):
        project_customer_id_list .append(res.json_response[i]['customer']['name'])
    assert(project_customer_id_list == sorted(project_customer_id_list))


@pytest.mark.ac_api_uat
def test_get_projects_descend_by_workType(ac_api_cookie):
    api = AC_API(ac_api_cookie)
    params = {
        "disabled": "True",
        "viewType": "full",
        "nameOrAlias": "",
        "customerId": "",
        "sort": "workType",
        "direction": "DESC"
    }
    res = api.get_projects(params)
    res.assert_response_status(200)
    project_work_type = []
    for i in range (0, (len(res.json_response)-1)):
        project_work_type.append(res.json_response[i]['workType']['label'].upper())
    assert(project_work_type == sorted(project_work_type))


def test_get_projects_empty_cookies():
    api = AC_API()
    res = api.get_projects()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}
