from appen_connect.api_automation.services_config.ac_api import AC_API
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_project_config, pytest.mark.regression_ac, pytest.mark.ac_api_v3, pytest.mark.ac_api_v3_general, pytest.mark.ac_api]

#
USER_NAME = get_user_name('test_ui_account')

@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_countries_valid_v3(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie, version='v3')
    res = ac_api.get_countries()
    res.assert_response_status(200)
    assert len(res.json_response) > 0


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_countries_by_language_v3(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie, version='v3')
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


def test_get_countries_by_language_exclude_wildcard_v3(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie, version='v3')
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
@pytest.mark.skip(reason='ignore')
def test_get_countries_no_cookies_v3():
    ac_api = AC_API(version='v3')
    res = ac_api.get_countries()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


def test_get_countries_by_language_por_v3(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie, version='v3')
    res = ac_api.get_countries(language='por', exclude_wildcard='true')
    res.assert_response_status(200)
    assert len(res.json_response) > 0
    assert res.json_response == [{'value': 'AGO', 'label': 'Angola', 'alpha2': 'AO', 'alpha3': 'AGO'},
                                 {'value': 'BRA', 'label': 'Brazil', 'alpha2': 'BR', 'alpha3': 'BRA'},
                                 {'value': 'CPV', 'label': 'Cape Verde', 'alpha2': 'CV', 'alpha3': 'CPV'},
                                 {'value': 'GNQ', 'label': 'Equatorial Guinea', 'alpha2': 'GQ', 'alpha3': 'GNQ'},
                                 {'value': 'GNB', 'label': 'Guinea-Bissau', 'alpha2': 'GW', 'alpha3': 'GNB'},
                                 {'value': 'MAC', 'label': 'Macao', 'alpha2': 'MO', 'alpha3': 'MAC'},
                                 {'value': 'MOZ', 'label': 'Mozambique', 'alpha2': 'MZ', 'alpha3': 'MOZ'},
                                 {'value': 'PRT', 'label': 'Portugal', 'alpha2': 'PT', 'alpha3': 'PRT'},
                                 {'value': 'STP', 'label': 'Sao Tome and Principe', 'alpha2': 'ST', 'alpha3': 'STP'},
                                 {'value': 'TLS', 'label': 'Timor-Leste', 'alpha2': 'TL', 'alpha3': 'TLS'}]
    assert res.json_response[0]['label'] != 'All Countries'


def test_get_countries_invalid_language_v3(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie, version='v3')
    res = ac_api.get_countries(language='999', exclude_wildcard='true')
    res.assert_response_status(200)
    assert res.json_response == []


def test_get_countries_by_exclude_wildcard_true_v3(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie, version='v3')
    res = ac_api.get_countries(exclude_wildcard='true')
    res.assert_response_status(200)
    assert len(res.json_response) > 0
    assert res.json_response[0]['label'] != 'All Countries'


def test_get_countries_by_exclude_wildcard_false_v3(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie, version='v3')
    res = ac_api.get_countries(exclude_wildcard='false')
    res.assert_response_status(200)
    assert len(res.json_response) > 0
    assert res.json_response[0]['label'] == 'All Countries'


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_states_valid_v3(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie, version='v3')
    res = ac_api.get_states(country_id='usa', include_territories='true')
    res.assert_response_status(200)
    assert len(res.json_response) == 56


@pytest.mark.ac_api_uat
def test_get_states_exclude_territories_v3(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie, version='v3')
    res = ac_api.get_states(country_id='usa', include_territories='false')
    res.assert_response_status(200)
    assert len(res.json_response) == 51


@pytest.mark.ac_api_uat
def test_get_states_country_id_invalid_v3(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie, version='v3')
    res = ac_api.get_states(country_id='999', include_territories='false')
    res.assert_response_status(200)
    assert res.json_response == []


def test_get_states_include_territories_invalid_v3(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie, version='v3')
    res = ac_api.get_states(country_id='usa', include_territories='9999')
    res.assert_response_status(400)
    assert len(res.json_response) > 0


# 'Confirm that Now States dont need cookies'
@pytest.mark.skip(reason='ignore')
def test_get_states_no_cookies_v3():
    ac_api = AC_API(version='v3')
    res = ac_api.get_states(country_id='usa', include_territories='true')
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}

# ------------------------------------
# /api/v3/language-fluency-levels
# ------------------------------------
def test_get_language_fluency_level_v3(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie, version='v3')
    res = ac_api.get_language_fluency_level()

    res.assert_response_status(200)
    assert res.json_response == [{"value": "BEGINNER", "label": "Beginner"},
                                 {"value": "INTERMEDIATE", "label": "Intermediate"},
                                 {"value": "ADVANCED", "label": "Advanced"},
                                 {"value": "FLUENT", "label": "Fluent"},
                                 {"value": "NEAR_NATIVE", "label": "Near Native"},
                                 {"value": "NATIVE_OR_BILINGUAL", "label": "Native or Bilingual"}]

@pytest.mark.skip(reason='ignore')
def test_get_language_fluency_level_no_cookies_v3():
    ac_api = AC_API(version='v3')
    res = ac_api.get_language_fluency_level()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}



# ------------------------------------
# /api/v3/languages
# ------------------------------------
@pytest.mark.ac_api_uat
def test_get_languages_v3(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie, version='v3')
    res = ac_api.get_languages()

    res.assert_response_status(200)
    assert len(res.json_response) > 0


@pytest.mark.skip(reason='ignore')
def test_get_languages_no_cookies_v3():
    ac_api = AC_API(version='v3')
    res = ac_api.get_languages()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


# TODO /api/v3/languages/search
# TODO /api/v3/user-processes/registration
