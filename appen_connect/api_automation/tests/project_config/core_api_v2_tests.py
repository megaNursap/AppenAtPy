from appen_connect.api_automation.services_config.ac_api import AC_API
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_project_config, pytest.mark.regression_ac, pytest.mark.ac_api_v2, pytest.mark.ac_api_v2_general_test, pytest.mark.ac_api]
#
USER_NAME = get_user_name('test_ui_account')


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_session_valid(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_session()
    res.assert_response_status(200)


def test_get_session_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_session()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
def test_get_session_me_valid(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_session_me()
    res.assert_response_status(200)
    assert len(res.json_response) == 6
    assert res.json_response['email'] == USER_NAME


def test_get_session_me_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_session_me()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_project_status(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_project_status()
    res.assert_response_status(200)
    assert len(res.json_response) == 5
    assert res.json_response == [{'value': 'DRAFT', 'label': 'Draft'}, {'value': 'READY', 'label': 'Ready'},
                                 {'value': 'ENABLED', 'label': 'Enabled'},  {'value': 'PAUSED', 'label': 'Paused'},{'value': 'DISABLED', 'label': 'Disabled'}]


def test_get_project_status_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_project_status()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
def test_get_business_units_valid(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_business_units()
    res.assert_response_status(200)
    assert res.json_response == [{'value': 'CR', 'label': 'CR'}, {'value': 'LR', 'label': 'LR'},
                                 {'value': 'F8', 'label': 'F8'}]


def test_get_business_units_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_business_units()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_countries_valid(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_countries()
    res.assert_response_status(200)
    assert len(res.json_response) > 0


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_countries_by_language(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_countries(language='rus')
    res.assert_response_status(200)
    assert len(res.json_response) > 0
    assert res.json_response == [{'value': '*', 'label': 'All Countries', 'alpha2': '*', 'alpha3': '*'},
                                 {'value': 'BLR', 'label': 'Belarus', 'alpha2': 'BY', 'alpha3': 'BLR'},
                                 {'value': 'KAZ', 'label': 'Kazakhstan', 'alpha2': 'KZ', 'alpha3': 'KAZ'},
                                 {'value': 'KGZ', 'label': 'Kyrgyzstan', 'alpha2': 'KG', 'alpha3': 'KGZ'},
                                 {'value': 'RUS', 'label': 'Russian Federation', 'alpha2': 'RU', 'alpha3': 'RUS'},
                                 {'value': 'UKR', 'label': 'Ukraine', 'alpha2': 'UA', 'alpha3': 'UKR'}]
    assert res.json_response[0]['label'] == 'All Countries'


def test_get_countries_by_language_exclude_wildcard(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_countries(language='rus', exclude_wildcard='true')
    res.assert_response_status(200)
    assert len(res.json_response) > 0
    assert res.json_response == [
        {'value': 'BLR', 'label': 'Belarus', 'alpha2': 'BY', 'alpha3': 'BLR'},
        {'value': 'KAZ', 'label': 'Kazakhstan', 'alpha2': 'KZ', 'alpha3': 'KAZ'},
        {'value': 'KGZ', 'label': 'Kyrgyzstan', 'alpha2': 'KG', 'alpha3': 'KGZ'},
        {'value': 'RUS', 'label': 'Russian Federation', 'alpha2': 'RU', 'alpha3': 'RUS'},
        {'value': 'UKR', 'label': 'Ukraine', 'alpha2': 'UA', 'alpha3': 'UKR'}]
    assert res.json_response[0]['label'] != 'All Countries'

# ' Confirm that Now Countries dont need cookies'
#@pytest.mark.skip(reason='ignore')
def test_get_countries_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_countries()
    res.assert_response_status(200)
    #assert res.json_response == {'error': 'Unauthorized'}


def test_get_countries_by_language_por(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_countries(language='por', exclude_wildcard='true')
    res.assert_response_status(200)
    assert len(res.json_response) > 0
    assert res.json_response == [{'value': 'AGO', 'label': 'Angola', 'alpha2': 'AO', 'alpha3': 'AGO'},
                                 {'value': 'BRA', 'label': 'Brazil', 'alpha2': 'BR', 'alpha3': 'BRA'},
                                 {'value': 'CPV', 'label': 'Cape Verde', 'alpha2': 'CV', 'alpha3': 'CPV'},
                                 {'value': 'GNQ', 'label': 'Equatorial Guinea', 'alpha2': 'GQ', 'alpha3': 'GNQ'},
                                 {'value': 'GNB', 'label': 'Guinea-Bissau', 'alpha2': 'GW', 'alpha3': 'GNB'},
                                 {'value': 'MAC', 'label': 'Macau', 'alpha2': 'MO', 'alpha3': 'MAC'},
                                 {'value': 'MOZ', 'label': 'Mozambique', 'alpha2': 'MZ', 'alpha3': 'MOZ'},
                                 {'value': 'PRT', 'label': 'Portugal', 'alpha2': 'PT', 'alpha3': 'PRT'},
                                 {'value': 'STP', 'label': 'Sao Tome and Principe', 'alpha2': 'ST', 'alpha3': 'STP'},
                                 {'value': 'TLS', 'label': 'Timor-Leste', 'alpha2': 'TL', 'alpha3': 'TLS'}]
    assert res.json_response[0]['label'] != 'All Countries'


def test_get_countries_invalid_language(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_countries(language='999', exclude_wildcard='true')
    res.assert_response_status(200)
    assert res.json_response == []


def test_get_countries_by_exclude_wildcard_true(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_countries(exclude_wildcard='true')
    res.assert_response_status(200)
    assert len(res.json_response) > 0
    assert res.json_response[0]['label'] != 'All Countries'


def test_get_countries_by_exclude_wildcard_false(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_countries(exclude_wildcard='false')
    res.assert_response_status(200)
    assert len(res.json_response) > 0
    assert res.json_response[0]['label'] == 'All Countries'


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_states_valid(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_states(country_id='usa', include_territories='true')
    res.assert_response_status(200)
    assert len(res.json_response) == 56


def test_get_states_exclude_territories(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_states(country_id='usa', include_territories='false')
    res.assert_response_status(200)
    assert len(res.json_response) == 51


def test_get_states_country_id_invalid(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_states(country_id='999', include_territories='false')
    res.assert_response_status(200)
    assert res.json_response == []


def test_get_states_include_territories_invalid(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_states(country_id='usa', include_territories='9999')
    res.assert_response_status(400)
    assert len(res.json_response) > 0

# 'Confirm that Now States dont need cookies'
@pytest.mark.skip(reason='ignore')
def test_get_states_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_states(country_id='usa', include_territories='true')
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_external_systems(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_external_systems()
    res.assert_response_status(200)


def test_get_external_systems_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_external_systems()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_groups_all(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_groups()
    res.assert_response_status(200)

    res_param = ac_api.get_groups(by_current_customer='false')
    res_param.assert_response_status(200)

    assert res.json_response == res_param.json_response

# ' Verify why is not selecting the customer '
@pytest.mark.skip(reason='ignore')
def test_get_groups_by_customer(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_groups(by_current_customer='true')
    res.assert_response_status(200)
    assert len(res.json_response) > 0
#     TODO more test


def test_get_groups_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_groups()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
def test_get_task_volumes(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_task_volumes()
    res.assert_response_status(200)
    assert res.json_response == [{"value": "VERY_LOW", "label": "Very Low"},
                                 {"value": "BELOW_AVERAGE", "label": "Below Average"},
                                 {"value": "AVERAGE", "label": "Average"},
                                 {"value": "ABOVE_AVERAGE", "label": "Above Average"},
                                 {"value": "VERY_HIGH", "label": "Very High"}]


def test_get_task_volumes_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_task_volumes()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_languages(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_languages()

    res.assert_response_status(200)
    assert len(res.json_response)>0


def test_get_languages_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_languages()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
def test_get_language_fluency_level(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_language_fluency_level()

    res.assert_response_status(200)
    assert res.json_response == [{"value": "BEGINNER", "label": "Beginner"},
                                 {"value": "INTERMEDIATE", "label": "Intermediate"},
                                 {"value": "ADVANCED", "label": "Advanced"},
                                 {"value": "FLUENT", "label": "Fluent"},
                                 {"value": "NEAR_NATIVE", "label": "Near Native"},
                                 {"value": "NATIVE_OR_BILINGUAL", "label": "Native or Bilingual"}]


def test_get_language_fluency_level_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_language_fluency_level()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_task_types(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_task_types()

    res.assert_response_status(200)
    assert len(res.json_response)>0


def test_get_task_types_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_task_types()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


#    TODO filter for team types
@pytest.mark.ac_api_uat
def test_get_team_types(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_team_types()

    res.assert_response_status(200)
    assert len(res.json_response) > 0
    assert res.json_response == [{"value": "QUALITY","label": "Quality"},
                                 {"value": "FINANCE","label": "Finance"},
                                 {"value": "HR","label": "Human Resources"},
                                 {"value": "RECRUITING", "label": "Recruitment"},
                                 {"value": "SUPPORT", "label": "Support"},
                                 {"value": "ENGINEERING","label": "Engineering"},
                                 {"value": "PROJECT_MANAGER","label": "Project Manager"}]


def test_get_task_team_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_team_types()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


# TODO country filter
@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_tenants(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_tenants()

    res.assert_response_status(200)
    assert len(res.json_response)>0
    assert res.json_response == [{"id": 1,
                                 "name": "Appen Ltd.",
                                 "shortName": "Appen",
                                 "employmentType": {
                                      "value": "CONTRACTOR",
                                      "label": "Contractor"
                                     }
                                },
                                {
                                    "id": 2,
                                    "name": "RaterLabs, Inc.",
                                    "shortName": "RaterLabs",
                                    "employmentType": {
                                      "value": "EMPLOYEE",
                                      "label": "Employee"
                                    }
                                },
                                {
                                    "id": 3,
                                    "name": "Appen Ltd.",
                                    "shortName": "Facility",
                                    "employmentType": {
                                      "value": "FACILITY_EMPLOYEE",
                                      "label": "Facility Employee"
                                    }
                                },
                                {
                                    "id": 4,
                                    "name": "Appen Ltd.",
                                    "shortName": "Appen",
                                    "employmentType": {
                                      "value": "AGENCY",
                                      "label": "Agency"
                                    }
                                }]


def test_get_tenants_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_tenants()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


# TODO filter by user type
@pytest.mark.ac_api_uat
def test_get_users(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_users('internal')

    res.assert_response_status(200)
    assert len(res.json_response) > 0


def test_get_users_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_users()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
def test_get_work_types(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_work_types()

    res.assert_response_status(200)
    assert len(res.json_response)>0
    assert res.json_response == [{"value": "LINGUISTICS","label": "Linguistics"},
                                 {"value": "DATA_COLLECTION","label": "Express"},
                                 {"value": "SEARCH_EVALUATION","label": "Search Evaluation"},
                                 {"value": "SOCIAL_MEDIA","label": "Social Media"},
                                 {"value": "TRANSCRIPTION","label": "Transcription"},
                                 {"value": "TRANSLATION","label": "Translation"},
                                 {"value": "WEB_RESEARCH","label": "Web Research"}]


def test_get_work_types_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_work_types()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}

# TODO add verification for each enpoint: 403, 404
# TODO content verification for each json response
