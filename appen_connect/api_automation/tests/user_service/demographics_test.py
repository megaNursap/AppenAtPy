import pytest

from appen_connect.api_automation.services_config.ac_user_service import UserService

# pytestmark = [pytest.mark.regression_ac, pytest.mark.ac_api_user_service, pytest.mark.ac_api_user_service_demographics]
pytestmark = [pytest.mark.skip(reason='Test deprecated')]


def test_demographics_complexions(ac_api_cookie_no_customer):
    api = UserService(cookies=ac_api_cookie_no_customer)

    res = api.get_demographics_complexions()
    res.assert_response_status(200)
    assert res.json_response == [{
                                    "value": "TYPE_1",
                                    "label": "Type 1: Light - pale white"
                                  },
                                  {
                                    "value": "TYPE_2",
                                    "label": "Type 2: White - fair"
                                  },
                                  {
                                    "value": "TYPE_3",
                                    "label": "Type 3: Median - white to light brown"
                                  },
                                  {
                                    "value": "TYPE_4",
                                    "label": "Type 4: Olive - moderate brown"
                                  },
                                  {
                                    "value": "TYPE_5",
                                    "label": "Type 5: Brown - dark brown"
                                  },
                                  {
                                    "value": "TYPE_6",
                                    "label": "Type 6: Very dark brown to black"
                                  }
                                ]


def test_demographics_complexions_unauthorized():
    api = UserService()
    res = api.get_demographics_complexions()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


def test_demographics_disability_types(ac_api_cookie_no_customer):
    api = UserService(cookies=ac_api_cookie_no_customer)

    res = api.get_demographics_disability_types()
    res.assert_response_status(200)
    assert res.json_response == [{
                                    "value": "YES",
                                    "label": "Yes - I have a disability"
                                  },
                                  {
                                    "value": "NO",
                                    "label": "No - I don’t have a disability"
                                  },
                                  {
                                    "value": "DONT_WISH",
                                    "label": "I don’t wish to answer"
                                  }
                                ]


def test_demographics_disability_types_unauthorized():
    api = UserService()
    res = api.get_demographics_disability_types()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


def test_demographics_ethnicities(ac_api_cookie_no_customer):
    api = UserService(cookies=ac_api_cookie_no_customer)

    res = api.get_demographics_ethnicities()
    res.assert_response_status(200)
    assert res.json_response == [{
                                    "value": "BLACK_OR_AFRICAN_AMERICAN",
                                    "label": "Black or African American"
                                  },
                                  {
                                    "value": "HISPANIC_OR_LATIN_AMERICAN",
                                    "label": "Hispanic or Latin American"
                                  },
                                  {
                                    "value": "AMERICAN_INDIAN_OR_ALASKA_NATIVE",
                                    "label": "American Indian or Alaska Native"
                                  },
                                  {
                                    "value": "EUROPEAN",
                                    "label": "European"
                                  },
                                  {
                                    "value": "EAST_ASIAN",
                                    "label": "East Asian"
                                  },
                                  {
                                    "value": "SOUTH_ASIAN",
                                    "label": "South Asian"
                                  },
                                  {
                                    "value": "INDIAN",
                                    "label": "Indian"
                                  },
                                  {
                                    "value": "MIDDLE_EASTERN",
                                    "label": "Middle Eastern"
                                  },
                                  {
                                    "value": "OCEANIAN",
                                    "label": "Oceanian"
                                  },
                                  {
                                    "value": "NATIVE_OR_PACIFIC_ISLANDER",
                                    "label": "Native or Pacific Islander"
                                  },
                                  {
                                    "value": "ABORIGINAL",
                                    "label": "Aboriginal / Torres Strait Islander"
                                  },
                                  {
                                    "value": "MIXED",
                                    "label": "Mixed"
                                  },
                                  {
                                    "value": "OTHER",
                                    "label": "Other"
                                  }
                                ]


def test_demographics_ethnicities_unauthorized():
    api = UserService()
    res = api.get_demographics_ethnicities()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


def test_demographics_genders(ac_api_cookie_no_customer):
    api = UserService(cookies=ac_api_cookie_no_customer)

    res = api.get_demographics_genders()
    res.assert_response_status(200)
    assert res.json_response ==[{
                                    "value": "FEMALE",
                                    "label": "Female"
                                  },
                                  {
                                    "value": "MALE",
                                    "label": "Male"
                                  },
                                  {
                                    "value": "OTHER",
                                    "label": "Non-Binary / Other"
                                  }
                                ]


def test_demographics_genders_unauthorized():
    api = UserService()
    res = api.get_demographics_genders()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}
