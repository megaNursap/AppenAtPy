import datetime

from appen_connect.api_automation.services_config.ac_api import AC_API, create_new_random_project
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_project_config, pytest.mark.regression_ac, pytest.mark.ac_api_v2, pytest.mark.ac_api_v2_pay_rates, pytest.mark.ac_api]


@pytest.fixture(scope="module")
def new_project_pay_rate(ac_api_cookie):
    new_project_api = AC_API(ac_api_cookie)
    result = create_new_random_project(new_project_api)
    return result


@pytest.mark.ac_api_uat
def test_get_pay_rates_for_project(ac_api_cookie, new_project_pay_rate):
    project_id = new_project_pay_rate['output']['id']
    api = AC_API(ac_api_cookie)
    res = api.get_pay_rates(project_id)

    res.assert_response_status(200)
    assert res.json_response == []


def test_get_pay_rates_for_project_empty_cookies(new_project_pay_rate):
    project_id = new_project_pay_rate['output']['id']
    api = AC_API()
    res = api.get_pay_rates(project_id)
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.dependency()
@pytest.mark.ac_api_uat
def test_create_pay_rate(ac_api_cookie, new_project_pay_rate):
    project_id = new_project_pay_rate['output']['id']
    api = AC_API(ac_api_cookie)

    # add tenant
    # add target
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
    for task_type in ["DEFAULT", "Annotation"]:
        payload = {
                "certifiedFluency": 'true',
                "countryPayRateId": 0,
                "defaultRate": 'false',
                "disabled": 'true',
                "groupId": 1,
                "language": "rus",
                "languageCountry": "RUS",
                "languageCountryTo": "",
                "languageTo": "",
                "projectId": project_id,
                "rateValue": 5,
                "restrictToCountry": "RUS",
                "spokenFluency": "BEGINNER",
                "state": "AL",
                "taskType": task_type,
                "workdayTaskId": "",
                "writtenFluency": "BEGINNER"
        }
        if task_type == "DEFAULT":
            res = api.create_pay_rate(payload)
            res.assert_response_status(201)

            assert res.json_response['language'] == 'rus'
            assert res.json_response['languageCountry'] == 'RUS'
            assert res.json_response['projectId'] == project_id
            pay_rates_id = res.json_response['id']

            res = api.get_pay_rates(project_id)
            res.assert_response_status(200)
            assert len(res.json_response) == 1
            assert res.json_response[0]['id'] == pay_rates_id
            assert res.json_response[0]['projectId'] == project_id
            assert res.json_response[0]['language'] == 'rus'
            assert res.json_response[0]['languageCountry'] == 'RUS'

            res = api.get_pay_rates_by_id(pay_rates_id)
            res.assert_response_status(200)
            assert res.json_response['id'] == pay_rates_id
            assert res.json_response['projectId'] == project_id
            assert res.json_response['language'] == 'rus'
            assert res.json_response['languageCountry'] == 'RUS'
        else:
            res = api.create_pay_rate(payload)
            res.assert_response_status(400)
            assert res.json_response['code'] == '500'
            assert res.json_response['message'] == 'Possible duplicate Entry for payrate RUS'


@pytest.mark.dependency(depends=["test_create_pay_rate"])
# @pytest.mark.skip(reason='Bug')
def test_update_pay_rates(ac_api_cookie, new_project_pay_rate):
    project_id = new_project_pay_rate['output']['id']
    api = AC_API(ac_api_cookie)

    current_pay_rates = api.get_pay_rates(project_id)
    current_pay_rates.assert_response_status(200)

    pay_rate_id = current_pay_rates.json_response[0]['id']
    payload = {
            "rateValue": 10
    }

    res = api.update_pay_rate(pay_rate_id, payload)
    res.assert_response_status(200)

    assert res.json_response['id'] == pay_rate_id
    assert res.json_response['projectId'] == project_id
    assert res.json_response['language'] == 'rus'
    assert res.json_response['languageCountry'] == 'RUS'
    assert res.json_response['rateValue'] == 10


@pytest.mark.dependency(depends=["test_create_pay_rate"])
# @pytest.mark.skip(reason='Bug')
def test_delete_pay_rates(ac_api_cookie, new_project_pay_rate):
    project_id = new_project_pay_rate['output']['id']
    api = AC_API(ac_api_cookie)

    current_pay_rates = api.get_pay_rates(project_id)
    current_pay_rates.assert_response_status(200)
    num_rates = len(current_pay_rates.json_response)

    pay_rate_id = current_pay_rates.json_response[0]['id']

    res = api.delete_pay_rate(pay_rate_id)
    res.assert_response_status(204)

    new_pay_rates = api.get_pay_rates(project_id)
    new_pay_rates.assert_response_status(200)
    new_num_rates = len(new_pay_rates.json_response)

    assert new_num_rates == num_rates - 1

    res = api.get_pay_rates_by_id(pay_rate_id)
    res.assert_response_status(404)
# error msg? ^^


def test_rate_types(ac_api_cookie):
    api = AC_API(ac_api_cookie)

    res = api.get_rate_types()
    res.assert_response_status(200)

    assert res.json_response == [{"value": "HOURLY","label": "Hourly"},
                                 {"value": "PIECERATE","label": "By Task"}]


# TODO expand : invalid payload, negative scenarios, hr target not exist , duplicates and ....
# TODO get default pay rates

