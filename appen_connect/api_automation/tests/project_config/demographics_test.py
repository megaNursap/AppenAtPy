import datetime

from appen_connect.api_automation.services_config.ac_api import AC_API, create_new_random_project
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_project_config, pytest.mark.regression_ac, pytest.mark.ac_api_v2, pytest.mark.ac_api_v2_demographics, pytest.mark.ac_api]


@pytest.fixture(scope="module")
def new_project_demog(ac_api_cookie):
    new_project_api = AC_API(ac_api_cookie)
    new_project = create_new_random_project(new_project_api)

    project_id = new_project['output']['id']

    payload = {
        "country": "RUS",
        "projectId": project_id,
        "tenantId": 1
    }

    res = new_project_api.create_locale_tenant(payload)
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
    res = new_project_api.add_hiring_target(payload)
    res.assert_response_status(201)
    h_target_id = res.json_response['id']

    return {'project_id':project_id, 'h_target_id':h_target_id}


@pytest.mark.ac_api_uat
def test_get_empty_demograph_requirements(ac_api_cookie, new_project_demog):
    api = AC_API(ac_api_cookie)

    res = api.get_demographics_requirements(new_project_demog['project_id'],new_project_demog['h_target_id'])
    res.assert_response_status(200)
    assert res.json_response == []


def test_get_empty_demograph_requirements_no_cookies(new_project_demog):
    api = AC_API()

    res = api.get_demographics_requirements(new_project_demog['project_id'], new_project_demog['h_target_id'])
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.dependency()
@pytest.mark.ac_api_uat
def test_create_demograph_requirements(ac_api_cookie, new_project_demog):
    payload = {
        "demographicRequirements": [
            {
                "group": [
                    {"count": 70,
                     "parameter": "Gender",
                     "target": 70,
                     "value": "FEMALE"
                    },
                    {"count": 30,
                      "parameter": "Gender",
                      "target": 30,
                       "value": "MALE"
                    }
                ],
                "hiringTargetId": new_project_demog['h_target_id']}],
        "demographicTargetType": "PERCENT",
        "projectId": new_project_demog['project_id']
    }
    api = AC_API(ac_api_cookie)
    res = api.create_demographics_requirements(payload)
    res.assert_response_status(200)
    assert res.json_response == [{'hiringTargetId': new_project_demog['h_target_id'], 'group':
                                         [{'target': 70, 'parameter': 'Gender', 'value': 'FEMALE'},
                                          {'target': 30, 'parameter': 'Gender', 'value': 'MALE'}]}]


    res = api.get_demographics_requirements(new_project_demog['project_id'], new_project_demog['h_target_id'])
    res.assert_response_status(200)
    assert res.json_response[0]['hiringTargetId'] == new_project_demog['h_target_id']
    assert sorted_list_of_dict_by_value(res.json_response[0]['group'], 'value') ==  \
           sorted_list_of_dict_by_value([{'target': 70, 'parameter': 'Gender', 'value': 'FEMALE'},
                                              {'target': 30, 'parameter': 'Gender', 'value': 'MALE'}], 'value')

# TODO create demograph with different requirements
# TODO create demogr with multiple req's


@pytest.mark.dependency(depends=["test_create_demograph_requirements"])
def test_update_demograph_requirements(ac_api_cookie, new_project_demog):
    payload = {
        "demographicRequirements": [
            {
                "group": [
                    {"count": 50,
                     "parameter": "Gender",
                     "target": 50,
                     "value": "FEMALE"
                    },
                    {"count": 50,
                      "parameter": "Gender",
                      "target": 50,
                       "value": "MALE"
                    }
                ],
                "hiringTargetId": new_project_demog['h_target_id']}],
        "demographicTargetType": "PERCENT",
        "projectId": new_project_demog['project_id']
    }
    api = AC_API(ac_api_cookie)
    res = api.update_demographics_requirements(payload)
    res.assert_response_status(200)
    assert res.json_response == [{'hiringTargetId': new_project_demog['h_target_id'], 'group':
                                 [{'target': 50, 'parameter': 'Gender', 'value': 'FEMALE'},
                                  {'target': 50, 'parameter': 'Gender', 'value': 'MALE'}]}]

    res = api.get_demographics_requirements(new_project_demog['project_id'], new_project_demog['h_target_id'])
    res.assert_response_status(200)
    assert res.json_response[0]['hiringTargetId'] == new_project_demog['h_target_id']
    assert sorted_list_of_dict_by_value(res.json_response[0]['group'], 'value') == \
           sorted_list_of_dict_by_value([{'target': 50, 'parameter': 'Gender', 'value': 'FEMALE'},
                                         {'target': 50, 'parameter': 'Gender', 'value': 'MALE'}], 'value')


# TODO different req's

def test_get_demograph_general_metrics(ac_api_cookie, new_project_demog):
    api = AC_API(ac_api_cookie)
    res = api.get_demographics_metrics(generalMetrics='true', hiring_target_id=new_project_demog['h_target_id'])
    res.assert_response_status(200)
    assert res.json_response == [{"hiringTargetId": new_project_demog['h_target_id'],
                                    "group": [
                                          {"target": 0, "parameter": "Age Range","value": "EIGHTEEN_TO_TWENTY_FOUR"},
                                          {"target": 0, "parameter": "Age Range","value": "TWENTY_FIVE_TO_THIRTY_FOUR"},
                                          {"target": 0,"parameter": "Age Range", "value": "THIRTY_FIVE_TO_FORTY_FOUR"},
                                          {"target": 0, "parameter": "Age Range", "value": "FORTY_FIVE_TO_FIFTY_FOUR"},
                                          { "target": 0, "parameter": "Age Range", "value": "FIFTY_FIVE_OR_ABOVE"},
                                          {"target": 0, "parameter": "Device", "value": "ANDROID" },
                                          { "target": 0, "parameter": "Device", "value": "IOS" },
                                          {"target": 0, "parameter": "Gender","value": "FEMALE" },
                                          {'parameter': 'Gender', 'target': 0, 'value': 'MALE'},
                                          {'parameter': 'Gender', 'target': 0, 'value': 'OTHER'}]
                                  }]



@pytest.mark.dependency(depends=["test_update_demograph_requirements"])
def test_get_demograph_not_general_metrics(ac_api_cookie, new_project_demog):
    api = AC_API(ac_api_cookie)
    res = api.get_demographics_metrics(generalMetrics='false', project_id=new_project_demog['project_id'], hiring_target_id=new_project_demog['h_target_id'])
    assert res.json_response[0]['hiringTargetId'] == new_project_demog['h_target_id']
    assert sorted_list_of_dict_by_value(res.json_response[0]['group'], 'value') == \
           sorted_list_of_dict_by_value([{'target': 50, 'parameter': 'Gender', 'value': 'FEMALE'},
                                         {'target': 50, 'parameter': 'Gender', 'value': 'MALE'}], 'value')


def test_get_demograph_parameters(ac_api_cookie):
    api = AC_API(ac_api_cookie)
    res = api.get_demographics_parameters()
    res.assert_response_status(200)
    assert res.json_response == [{
                                    "name": "Gender",
                                    "values": [
                                      {
                                        "value": "FEMALE",
                                        "label": "Female"
                                      },
                                      {
                                        "value": "MALE",
                                        "label": "Male"
                                      },
                                      {'label': 'Non-Binary / Other',
                                       'value': 'OTHER'}
                                    ]
                                  },
                                  {
                                    "name": "Age Range",
                                    "values": [
                                      {
                                        "value": "EIGHTEEN_TO_TWENTY_FOUR",
                                        "label": "18-24"
                                      },
                                      {
                                        "value": "TWENTY_FIVE_TO_THIRTY_FOUR",
                                        "label": "25-34"
                                      },
                                      {
                                        "value": "THIRTY_FIVE_TO_FORTY_FOUR",
                                        "label": "35-44"
                                      },
                                      {
                                        "value": "FORTY_FIVE_TO_FIFTY_FOUR",
                                        "label": "45-54"
                                      },
                                      {
                                        "value": "FIFTY_FIVE_OR_ABOVE",
                                        "label": "55+"
                                      }
                                    ]
                                  },
                                  {
                                    "name": "Device",
                                    "values": [
                                      {
                                        "value": "ANDROID",
                                        "label": "Android"
                                      },
                                      {
                                        "value": "IOS",
                                        "label": "iOS"
                                      }
                                    ]
                                  }
                                ]


@pytest.mark.dependency(depends=["test_create_demograph_requirements"])
def test_delete_demograph_requirements(ac_api_cookie, new_project_demog):
    api = AC_API(ac_api_cookie)

    res = api.delete_demographics_requirements(hiring_target_id=new_project_demog['h_target_id'])
    res.assert_response_status(204)

    res = api.get_demographics_requirements(hiring_target_id= new_project_demog['h_target_id'])
    res.assert_response_status(200)
    assert res.json_response == []

# TODO delete demegraph by project id, only one h target

