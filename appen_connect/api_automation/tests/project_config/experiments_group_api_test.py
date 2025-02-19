import time

from adap.api_automation.utils.data_util import *
from appen_connect.api_automation.services_config.ac_api import AC_API, create_new_random_project
from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project

pytestmark = [pytest.mark.regression_ac_project_config, pytest.mark.regression_ac, pytest.mark.ac_api_v2, pytest.mark.ac_api_v2_experiments_group, pytest.mark.ac_api]

#
USER_NAME = get_test_data('test_ui_account', 'user_name')
PASSWORD = get_test_data('test_ui_account', 'password')


_country = "*"
_country_ui = "United States of America"
_locale  = "English (United States)"
_fluency = "Native or Bilingual"
_lan = "eng"
_lan_ui = "English"
_lan_country = "*"
_pay_rate = 6

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
        "spokenFluency": _fluency.upper().replace(" ","_"),
        "writtenFluency": _fluency.upper().replace(" ","_"),
        "rateValue": _pay_rate,
        "taskType": "Default",
        "language": _lan,
        "languageCountry": "*",
        "restrictToCountry": _country
    }
}


@pytest.fixture(scope="module")
def experiments_project(app, ac_api_cookie):
    _project = api_create_simple_project(project_config, ac_api_cookie)

    res = AC_API(cookies=ac_api_cookie).get_groups(customer_id=53)
    customer_groups = res.json_response

    return {"project_id":_project['id'],
            "customer_groups":customer_groups,
            "valid_cookie": ac_api_cookie}


def test_get_experiments_status_vendor(app_test):
    vendor_name = get_test_data('test_express_active_vendor_account', 'user_name')
    vendor_password = get_test_data('test_express_active_vendor_account', 'password')
    app_test.ac_user.login_as(user_name=vendor_name, password=vendor_password)
    time.sleep(2)
    _cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in app_test.driver.get_cookies()}

    ac_api = AC_API(cookies=_cookie)
    res = ac_api.get_experiments_status()
    res.assert_response_status(403)


@pytest.mark.ac_api_uat
def test_get_experiments_status(experiments_project):
    ac_api = AC_API(cookies=experiments_project['valid_cookie'])
    res = ac_api.get_experiments_status()
    res.assert_response_status(200)
    assert res.json_response == [{
                                    "value": "DRAFT",
                                    "label": "Draft"
                                  },
                                  {
                                    "value": "STAGED",
                                    "label": "Staged"
                                  },
                                  {
                                    "value": "OPENED",
                                    "label": "Opened"
                                  },
                                  {
                                    "value": "PAUSED",
                                    "label": "Paused"
                                  },
                                  {
                                    "value": "CLOSED",
                                    "label": "Closed"
                                  },
                                  {
                                    "value": "REVIEWED",
                                    "label": "Reviewed"
                                  },
                                  {
                                    "value": "ABANDONED",
                                    "label": "Abandoned"
                                  }]


def test_get_experiments_status_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_experiments_status()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
def test_get_experiments_create(experiments_project):
    api = AC_API(experiments_project['valid_cookie'])

    res = api.get_experiments_for_project(experiments_project['project_id'])
    res.assert_response_status(200)
    # experiment_is = res.json_response[0]["id"]
    # 5520
    assert res.json_response[0]["projectId"] == experiments_project['project_id']
    assert res.json_response[0]["status"] == "OPENED"
    assert res.json_response[0]["type"] == "EXTERNAL"


@pytest.mark.dependency()
@pytest.mark.parametrize('experiment_status, status_response, msg',
                         [("CLOSED", 400, {"code":"CannotUpdateExperimentStatus","message":"Cannot Update Experiment Status to Closed"}),
                          ("DRAFT", 400, {"code":"CannotUpdateExperimentStatus","message":"Cannot Update Experiment Status to Draft"}),
                          ("STAGED", 400, {"code": "CannotUpdateExperimentStatus","message": "Cannot Update Experiment Status to Staged"}),
                          ("PAUSED", 200, None),
                          ("REVIEWED", 200, None),
                          ("ABANDONED", 200, None),
                          ("OPENED", 200, None)])
def test_update_experiment_status_close(experiment_status, status_response, msg, experiments_project):
    api = AC_API(experiments_project['valid_cookie'])

    res = api.get_experiments_for_project(experiments_project['project_id'])
    res.assert_response_status(200)

    global experiment_info
    experiment_info = res.json_response

    experiment_id = experiment_info[0]["id"]
    experiment_name = experiment_info[0]["name"]

    payload = {
          "name": experiment_name,
          "projectId": experiments_project['project_id'],
          "status": experiment_status,
          "type": "EXTERNAL"
        }

    res = api.update_experiment(experiment_id, payload)
    res.assert_response_status(status_response)
    if msg:
        assert res.json_response == msg


@pytest.mark.dependency(name="test_update_experiment_status_close")
def test_update_experiment_no_cookies():
    api = AC_API()

    payload = {
        "name": experiment_info[0]["name"],
        "projectId": experiment_info[0]["projectId"],
        "status": "PAUSED",
        "type": "EXTERNAL"
    }

    res = api.update_experiment(experiment_info[0]['id'], payload)
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
def test_update_experiment_required_fields(experiments_project):
    api = AC_API(experiments_project['valid_cookie'])

    res = api.get_experiments_for_project(experiments_project['project_id'])
    res.assert_response_status(200)

    experiment_info = res.json_response

    experiment_id = experiment_info[0]["id"]
    experiment_name = experiment_info[0]["name"]

    payload_no_name = {
        "projectId": experiments_project['project_id'],
        "status": "PAUSED",
        "type": "EXTERNAL"
    }

    res = api.update_experiment(experiment_id, payload_no_name)
    res.assert_response_status(422)
    assert res.json_response == {"code": "VALIDATION_ERROR",
                                  "message": "Validation Error",
                                  "fieldErrors": [
                                    {"field": "name",
                                      "message": "may not be null",
                                      "code": "NotNull"
                                    }]}

    payload_no_status = {
        "projectId": experiments_project['project_id'],
        "name": experiment_name,
        "type": "EXTERNAL"
    }

    res = api.update_experiment(experiment_id, payload_no_status)
    res.assert_response_status(422)
    assert res.json_response == {"code": "VALIDATION_ERROR",
                                  "message": "Validation Error",
                                  "fieldErrors": [
                                    {"field": "status",
                                      "message": "may not be null",
                                      "code": "NotNull"
                                    }]}


def test_create_group_empty_experiment(experiments_project):
    api = AC_API(experiments_project['valid_cookie'])

    res = api.get_experiments_for_project(experiments_project['project_id'])
    res.assert_response_status(200)

    experiment_info = res.json_response
    payload_no_experiment = [
              {
                "experimentId": 0,
                "groupId": 0
              }
            ]

    res = api.create_experiment_group(experiment_info[0]['id'], payload_no_experiment)
    res.assert_response_status(400)
    assert res.json_response == {"code": "ErrorCodeExperiment", "message": "Experiment not found"}


def test_create_group_invalid_experiment(experiments_project):
    api = AC_API(experiments_project['valid_cookie'])
    res = api.get_experiments_for_project(experiments_project['project_id'])
    res.assert_response_status(200)

    experiment_info = res.json_response
    payload = [
              {
                "experimentId": "abc",
                "groupId": 0
              }
            ]

    res = api.create_experiment_group(experiment_info[0]['id'], payload)
    res.assert_response_status(400)
    assert res.json_response['code'] == "TYPE_PARAMETER_ERROR"


def test_create_group_not_found(experiments_project):
    api = AC_API(experiments_project['valid_cookie'])

    res = api.get_experiments_for_project(experiments_project['project_id'])
    res.assert_response_status(200)

    experiment_info = res.json_response

    payload_no_experiment = [
              {
                "experimentId": experiment_info[0]['id'],
                "groupId": 0
              }
            ]

    res = api.create_experiment_group(experiment_info[0]['id'], payload_no_experiment)
    res.assert_response_status(400)
    assert res.json_response == {"code": "ErrorCodeGroup", "message": "Group not found"}


def test_create_group_invalid_id(experiments_project):
    api = AC_API(experiments_project['valid_cookie'])

    res = api.get_experiments_for_project(experiments_project['project_id'])
    res.assert_response_status(200)

    experiment_info = res.json_response

    payload_no_experiment = [
              {
                "experimentId": experiment_info[0]['id'],
                "groupId": 'abc'
              }
            ]

    res = api.create_experiment_group(experiment_info[0]['id'], payload_no_experiment)
    res.assert_response_status(400)
    assert res.json_response['code'] == "TYPE_PARAMETER_ERROR"


def test_create_group_valid(experiments_project):
    api = AC_API(experiments_project['valid_cookie'])

    res = api.get_experiments_for_project(experiments_project['project_id'])
    res.assert_response_status(200)

    experiment_info = res.json_response
    random_group = random.choice(experiments_project['customer_groups'][1:-1])['id']
    payload = [
        {
            "experimentId": experiment_info[0]['id'],
            "groupId": random_group
        }
    ]

    res = api.create_experiment_group(experiment_info[0]['id'], payload)
    res.assert_response_status(201)
    assert res.json_response[0]['experimentId'] == experiment_info[0]['id']
    assert res.json_response[0]['groupId'] == random_group


def test_add_all_users_group(experiments_project):
    api = AC_API(experiments_project['valid_cookie'])

    res = api.get_experiments_for_project(experiments_project['project_id'])
    res.assert_response_status(200)
    experiment_info = res.json_response

    res =  api.get_experiments_groups(experiment_info[0]['id'])
    current_groups = res.json_response

    payload = [
        {
            "experimentId": experiment_info[0]['id'],
            "groupId": 1
        }
    ]

    res = api.create_experiment_group(experiment_info[0]['id'], payload)
    res.assert_response_status(201)
    assert res.json_response[0]['experimentId'] == experiment_info[0]['id']
    assert res.json_response[0]['groupId'] == 1

    res = api.get_experiments_groups(experiment_info[0]['id'])
    new_groups = res.json_response

    assert len(current_groups) + 1 == len(new_groups)


@pytest.mark.parametrize('group_id, status_response, msg',
                         [("", 400, {
                                      "code": "UNSPECIFIED_ERROR",
                                      "message": "Something went wrong, please try again soon"
                                    }),
                          ("abc", 400, {
                                      "code": "TYPE_PARAMETER_ERROR",
                                      "message": 'Cannot deserialize value of type `long` from String "abc": not a valid `long` value\n at [Source: (PushbackInputStream); line: 1, column: 37] (through reference chain: java.util.ArrayList[0]->com.appen.connect.dto.ExperimentGroupDto["groupId"])'
                                    }),
                          (None, 400, {
                                      "code": "UNSPECIFIED_ERROR",
                                      "message": "Something went wrong, please try again soon"
                                    }),
                          (0, 400, {
                                      "code": "ErrorCodeGroup",
                                      "message": "Group not found"
                                    })
                          ])
def test_update_experiment_group_invalid_id(group_id, status_response, msg, experiments_project):
    api = AC_API(experiments_project['valid_cookie'])

    res = api.get_experiments_for_project(experiments_project['project_id'])
    res.assert_response_status(200)
    experiment_info = res.json_response

    payload = [
        {
            "experimentId": experiment_info[0]['id'],
            "groupId": group_id
        }
    ]

    res = api.update_experiment_group(experiment_info[0]['id'], payload)
    res.assert_response_status(status_response)
    assert res.json_response == msg


def test_update_experiment_group_empty_payload(experiments_project):
    api = AC_API(experiments_project['valid_cookie'])

    res = api.get_experiments_for_project(experiments_project['project_id'])
    res.assert_response_status(200)
    experiment_info = res.json_response

    payload = []

    res = api.update_experiment_group(experiment_info[0]['id'], payload)
    res.assert_response_status(200)
    assert res.json_response == []


def test_update_experiment_groups(experiments_project):
    api = AC_API(experiments_project['valid_cookie'])

    res = api.get_experiments_for_project(experiments_project['project_id'])
    res.assert_response_status(200)
    experiment_info = res.json_response

    res = api.get_experiments_groups(experiment_info[0]['id'])
    current_groups = res.json_response
    current_groups.append({"experimentId": experiment_info[0]['id'],
                           "groupId": experiments_project['customer_groups'][-1]['id']})

    res = api.update_experiment_group(experiment_info[0]['id'], payload=current_groups)
    res.assert_response_status(200)

    res = api.get_experiments_groups(experiment_info[0]['id'])
    assert len(current_groups) == len(res.json_response)
    assert find_dict_in_array_by_value(res.json_response, 'groupId', experiments_project['customer_groups'][-1]['id'])


def test_update_experiment_groups_remove(experiments_project):
    api = AC_API(experiments_project['valid_cookie'])

    res = api.get_experiments_for_project(experiments_project['project_id'])
    res.assert_response_status(200)
    experiment_info = res.json_response

    res = api.get_experiments_groups(experiment_info[0]['id'])
    current_groups = res.json_response
    remove_group = current_groups.pop()

    res = api.update_experiment_group(experiment_info[0]['id'], payload=current_groups)
    res.assert_response_status(200)

    res = api.get_experiments_groups(experiment_info[0]['id'])
    assert len(current_groups) == len(res.json_response)
    assert not find_dict_in_array_by_value(res.json_response, 'groupId', remove_group['groupId'])
