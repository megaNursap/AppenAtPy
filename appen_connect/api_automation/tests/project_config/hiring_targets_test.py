import datetime

from appen_connect.api_automation.services_config.ac_api import AC_API, create_new_random_project
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_project_config, pytest.mark.regression_ac, pytest.mark.ac_api_v2, pytest.mark.ac_api_v2_hiring_targets, pytest.mark.ac_api]


@pytest.fixture(scope="module")
def new_project_ht(ac_api_cookie):
    new_project_api = AC_API(ac_api_cookie)
    result = create_new_random_project(new_project_api)
    return result

# TODO workflow: create new , get, update, delete


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_hiring_target(ac_api_cookie, new_project_ht):
    project_id = new_project_ht['output']['id']
    api = AC_API(ac_api_cookie)

    res = api.get_hiring_target(project_id)
    res.assert_response_status(200)
    assert res.json_response == []


def test_get_hiring_target_no_cookies(new_project_ht):
    project_id = new_project_ht['output']['id']
    api = AC_API()
    res = api.get_hiring_target(project_id)
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
def test_add_hiring_target(ac_api_cookie, new_project_ht):
    api = AC_API(ac_api_cookie)
    project_id = new_project_ht['output']['id']

    payload = {
        "country": "RUS",
        "projectId": project_id,
        "tenantId": 1
    }

    res = api.create_locale_tenant(payload)
    res.assert_response_status(201)

    tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1)).isoformat()
    payload = {
          "deadline": tomorrow,
          "language": "rus",
          "languageCountry": "RUS",
          "languageCountryTo": "",
          "languageTo": "",
          "ownerId": 0,
          "priority": 0,
          "projectId": project_id,
          "restrictToCountry": "RUS",
          "target": 1
    }
    res = api.add_hiring_target(payload)
    res.assert_response_status(201)
    h_target_id = res.json_response['id']
    assert res.json_response['projectId'] == project_id
    assert res.json_response['language'] == 'rus'
    assert res.json_response['languageCountry'] == "RUS"

    res = api.get_hiring_target(project_id)
    res.assert_response_status(200)
    assert len(res.json_response) == 1
    assert res.json_response[0]['id'] == h_target_id
    assert res.json_response[0]['languageCountry'] == 'RUS'


@pytest.mark.ac_api_uat
def test_update_hiring_target(ac_api_cookie, new_project_ht):
    api = AC_API(ac_api_cookie)
    project_id = new_project_ht['output']['id']

    res = api.get_hiring_target(project_id)
    res.assert_response_status(200)

    tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1)).isoformat()

    payload = {
        "country": "USA",
        "projectId": project_id,
        "tenantId": 1
    }

    res = api.create_locale_tenant(payload)
    res.assert_response_status(201)

    payload = {
        "country": "ITA",
        "projectId": project_id,
        "tenantId": 1
    }

    res = api.create_locale_tenant(payload)
    res.assert_response_status(201)

    payload = {
        "country": "ALB",
        "projectId": project_id,
        "tenantId": 1
    }

    res = api.create_locale_tenant(payload)
    res.assert_response_status(201)

    payload = {
        "deadline": tomorrow,
        "language": "eng",
        "languageCountry": "USA",
        "languageCountryTo": "",
        "languageTo": "",
        "ownerId": 0,
        "priority": 0,
        "projectId": project_id,
        "restrictToCountry": "ITA",
        "target": 1
    }
    res = api.add_hiring_target(payload)
    res.assert_response_status(201)
    target_id = res.json_response['id']

    new_payload = {
        "deadline": tomorrow,
        "language": "eng",
        "languageCountry": "USA",
        "languageCountryTo": "",
        "languageTo": "",
        "ownerId": 0,
        "priority": 0,
        "projectId": project_id,
        "restrictToCountry": "ALB",
        "target": 2
    }

    update_res = api.update_hiring_targets(target_id, new_payload)
    update_res.assert_response_status(200)
    assert update_res.json_response['id'] == target_id
    assert update_res.json_response['projectId'] == project_id
    assert update_res.json_response['restrictToCountry'] == "ALB"
    assert update_res.json_response['target'] == 2

    res = api.get_hiring_target(project_id)
    res.assert_response_status(200)

    updated_target = [ t for t in res.json_response if t['id']==target_id]
    assert updated_target[0]['id'] == target_id
    assert updated_target[0]['target'] == 2
    assert updated_target[0]['restrictToCountry'] == 'ALB'
    assert updated_target[0]['languageCountry'] == 'USA'
    assert updated_target[0]['language'] == 'eng'


def test_delete_hiring_target(ac_api_cookie, new_project_ht):
    api = AC_API(ac_api_cookie)
    project_id = new_project_ht['output']['id']

    res = api.get_hiring_target(project_id)
    res.assert_response_status(200)

    if len(res.json_response) == 0:
        # create  new target

        tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1)).isoformat()

        payload = {
            "country": "USA",
            "projectId": project_id,
            "tenantId": 1
        }

        res = api.create_locale_tenant(payload)
        res.assert_response_status(201)

        payload = {
            "deadline": tomorrow,
            "language": "eng",
            "languageCountry": "USA",
            "languageCountryTo": "",
            "languageTo": "",
            "ownerId": 0,
            "priority": 0,
            "projectId": project_id,
            "restrictToCountry": "ITA",
            "target": 1
        }
        res = api.add_hiring_target(payload)
        res.assert_response_status(201)
        target_id = res.json_response['id']
    else:
        target_id = res.json_response[0]['id']


    res = api.delete_hiring_target(target_id)
    res.assert_response_status(204)


# TODO expand test coverage: invalid payload, locale tenant not exist, duplicates and ...