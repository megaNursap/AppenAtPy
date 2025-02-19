import time
import datetime
from appen_connect.api_automation.services_config.ac_api import AC_API, create_new_random_project
from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_project_config, pytest.mark.regression_ac, pytest.mark.ac_api_v2, pytest.mark.ac_api_v2_create_project, pytest.mark.ac_api]


_country = "*"
_country_ui = "United States of America"
_locale = "English (United States)"
_fluency = "Native or Bilingual"
_lan = "eng"
_lan_ui = "English"
_lan_country = "*"
_pay_rate = 6
_tomorrow_date = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%m/%d/%Y")

project_config = {
    "projectType": 'Regular',
    "workType": "LINGUISTICS",
    "externalSystemId": 15,
    "qualificationProcessTemplateId": 1386,
    "registrationProcessTemplateId": 764,
    "locale": {
        "country": _country
    },
    "hiring_target": {
        "language": _lan,
        "languageCountry": _lan_country,
        "restrictToCountry": _country,
        "target": 10
    },
    "pay_rates": {
        "spokenFluency": _fluency.upper().replace(" ", "_"),
        "writtenFluency": _fluency.upper().replace(" ", "_"),
        "rateValue": _pay_rate,
        "taskType": "Default",
        "language": _lan,
        "languageCountry": "*",
        "restrictToCountry": _country
    },
    "invoice": "default",
    "update_status": "READY"
}

@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_projects(ac_api_cookie):
    api = AC_API(ac_api_cookie)
    res = api.get_projects()
    res.assert_response_status(200)
    assert len(res.json_response) > 0


def test_get_projects_no_cookies():
    api = AC_API()
    res = api.get_projects()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
def test_get_projects_disabled(ac_api_cookie):
    api = AC_API(ac_api_cookie)

    params = {"disabled": "true"}
    res = api.get_projects(params=params)
    res.assert_response_status(200)
    num_disabled_projects = res.json_response

    params = {"disabled": "false"}
    res = api.get_projects(params=params)
    res.assert_response_status(200)
    num_enabled_projects = res.json_response

    assert num_disabled_projects != num_enabled_projects
    # num_enabled = len(res.json_response)
    # when we run tests in parallel, number of project is not stable; so remove this assertions
    # res = api.get_projects()
    # res.assert_response_status(200)
    # num_all = len(res.json_response)
    #
    # assert num_all == num_disabled + num_enabled


@pytest.mark.ac_api_smoke
@pytest.mark.ac_api_uat
def test_get_single_project_by_name(ac_api_cookie):
    api = AC_API(ac_api_cookie)
    res = api.get_projects()

    project_name = res.json_response[0]['name']
    project_id = res.json_response[0]['id']

    params = {"name": project_name}

    res = api.get_projects(params=params)
    res.assert_response_status(200)
    assert len(res.json_response) == 1
    assert res.json_response[0]['name'] == project_name
    assert res.json_response[0]['id'] == project_id

    # TODO filter by alias
    # TODO more content verification


@pytest.mark.ac_api_uat
def test_create_project(ac_api_cookie):
    api = AC_API(ac_api_cookie)
    project_name = generate_project_name()
    payload = {
        "alias": project_name[1],
        "name": project_name[0],
        "taskVolume": "VERY_LOW",
        "workType": "LINGUISTICS",
        "customerId": 53,
        "description": project_name[0],
        "projectType": "Regular"

    }
    res = api.create_project(payload=payload)
    res.assert_response_status(201)

    assert res.json_response['name'] == project_name[0]
    assert res.json_response['alias'] == project_name[1]
    assert res.json_response['description'] == project_name[0]
    assert res.json_response['taskVolume'] == "VERY_LOW"
    assert res.json_response['projectType'] == "Regular"


def test_create_project_empty_payload(ac_api_cookie):
    api = AC_API(ac_api_cookie)
    res = api.create_project(payload={})
    res.assert_response_status(422)

    assert res.json_response['code'] == "VALIDATION_ERROR"
    assert res.json_response['message'] == "Validation Error"
    assert len(res.json_response['fieldErrors']) == 6


# TODO verify each required field
def test_create_project_empty_cookies():
    api = AC_API()
    res = api.create_project(payload={})
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


def test_get_project_by_id(ac_api_cookie):
    # create new project
    api = AC_API(ac_api_cookie)
    result = create_new_random_project(api)
    project_id = result["output"]['id']

    res = api.get_project_by_id(project_id)
    res.assert_response_status(200)

    assert res.json_response["id"] == project_id
    assert res.json_response['name'] == result["input"]["name"]
    assert res.json_response['alias'] == result["input"]['alias']
    assert res.json_response['description'] == result["input"]['description']
    assert res.json_response['taskVolume'] == result["input"]['taskVolume']
    assert res.json_response['projectType'] == result["input"]['projectType']


#   TODO: create new project and verify get_project_by_id() returns correct data


def test_get_project_by_id_empty_cookies():
    api = AC_API()
    res = api.get_project_by_id(1)
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
def test_update_project(ac_api_cookie):
    api = AC_API(ac_api_cookie)

    result = create_new_random_project(api)
    project_id = result["output"]['id']

    new_project_name = generate_project_name()

    payload ={
        "name": new_project_name[0],
        "alias": new_project_name[1],
        "description": new_project_name[0],
        "taskVolume": "AVERAGE",
        "projectType": "Regular",
         "workType": "LINGUISTICS"
    }

    res_update = api.update_project(project_id, payload)
    res_update.assert_response_status(200)

    assert res_update.json_response["id"] == project_id
    assert res_update.json_response["name"] == new_project_name[0]
    assert res_update.json_response["alias"] == new_project_name[1]
    assert res_update.json_response["description"] == new_project_name[0]
#   TODO verify content, different json, not existing id....


def test_pause_draft_project(ac_api_cookie):
    api = AC_API(ac_api_cookie)

    result = create_new_random_project(api)
    project_id = result["output"]['id']

    new_project_name = generate_project_name()

    payload ={
        "name": new_project_name[0],
        "alias": new_project_name[1],
        "description": new_project_name[0],
        "taskVolume": "AVERAGE",
        "projectType": "Regular",
         "workType": "LINGUISTICS"
    }

    res_update = api.update_project(project_id, payload)
    res_update.assert_response_status(200)

    status_payload = {
        "status": "PAUSED"
    }
    status = api.update_project_status(project_id, status_payload)
    assert status.status_code == 400
    assert status.json_response == {'code': 'CannotUpdateProjectStatus', 'message': 'Canot pause a project with DRAFT status'}

    time.sleep(5)
    res = api.get_project_by_id(id=project_id)
    assert res.status_code == 200
    assert res.json_response['status'] == "DRAFT"


@pytest.mark.dependency()
def test_pause_enabled_project(ac_api_cookie):
    global _project
    _project = api_create_simple_project(project_config, ac_api_cookie)
    status_payload = {
        "status": "ENABLED"
    }
    project_id = _project['id']
    api = AC_API(ac_api_cookie)
    status = api.update_project_status(project_id, status_payload)
    status.assert_response_status(200)

    status_payload = {
        "status": "PAUSED"
    }
    status = api.update_project_status(project_id, status_payload)
    status.assert_response_status(200)

    res = api.get_project_by_id(id=project_id)
    assert res.status_code == 200
    assert res.json_response['status'] == "PAUSED"


@pytest.mark.dependency(depends=["test_pause_enabled_project"])
def test_enable_paused_project(ac_api_cookie):
    api = AC_API(ac_api_cookie)
    project_id = _project['id']

    status_payload = {
        "status": "ENABLED"
    }
    status = api.update_project_status(project_id, status_payload)
    status.assert_response_status(200)

    res = api.get_project_by_id(id=project_id)
    assert res.status_code == 200
    assert res.json_response['status'] == "ENABLED"


@pytest.mark.dependency(depends=["test_enable_paused_project"])
def test_pause_disable_project(ac_api_cookie):
    api = AC_API(ac_api_cookie)
    project_id = _project['id']

    status_payload = {
        "status": "DISABLED"
    }
    status = api.update_project_status(project_id, status_payload)
    status.assert_response_status(200)

    res = api.get_project_by_id(id=project_id)
    assert res.status_code == 200
    assert res.json_response['status'] == "DISABLED"

    status_payload = {
        "status": "PAUSED"
    }
    status = api.update_project_status(project_id, status_payload)
    status.assert_response_status(200)

    res = api.get_project_by_id(id=project_id)
    assert res.status_code == 200
    assert res.json_response['status'] == "PAUSED"


@pytest.mark.dependency(depends=["test_pause_disable_project"])
def test_disable_paused_project(ac_api_cookie):
    api = AC_API(ac_api_cookie)
    project_id = _project['id']

    status_payload = {
        "status": "DISABLED"
    }
    status = api.update_project_status(project_id, status_payload)
    status.assert_response_status(200)

    res = api.get_project_by_id(id=project_id)
    assert res.status_code == 200
    assert res.json_response['status'] == "DISABLED"


def test_update_project_empty_cookie(ac_api_cookie):
    new_project_api = AC_API(ac_api_cookie)
    result = create_new_random_project(new_project_api)
    project_id = result["output"]['id']

    api = AC_API()
    project_name = generate_project_name()

    payload ={
        "name": project_name[0],
        "alias": project_name[1],
        "description": project_name[0],
        "projectType": "Regular",
        "taskVolume": "AVERAGE",
        "workType": "LINGUISTICS"
    }

    res_update = api.update_project(project_id, payload)
    res_update.assert_response_status(401)
    assert res_update.json_response == {'error': 'Unauthorized'}


# # TODO later when all endpoints will be done
# @pytest.mark.skip
# def test_create_full_project():
#     pass
