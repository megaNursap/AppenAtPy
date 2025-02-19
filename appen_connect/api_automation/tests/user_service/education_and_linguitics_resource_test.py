import pytest

from appen_connect.api_automation.services_config.ac_user_service import UserService

pytestmark = [pytest.mark.regression_ac_user_service, pytest.mark.regression_ac, pytest.mark.ac_api_user_service, pytest.mark.ac_api_user_service_education, pytest.mark.ac_api]


@pytest.mark.ac_api_uat
def test_education_levels(ac_api_cookie_no_customer):
    api = UserService(cookies=ac_api_cookie_no_customer)

    res = api.get_education_levels()
    res.assert_response_status(200)

    # Updated Education Levels response per https://appen.atlassian.net/browse/ACE-17179
    assert res.json_response == [{
                                        "value": "HIGH_SCHOOL_COURSEWORK",
                                        "description": "Primary/ Elementary or equivalent",
                                        "abbreviation": "HS"
                                      },
                                      {
                                        "value": "HIGH_SCHOOL_EQUIVALENT",
                                        "description": "Middle/ Junior school or equivalent",
                                        "abbreviation": "GED"
                                      },
                                      {
                                        "value": "SOME_COLLEGE",
                                        "description": "High school/secondary school or equivalent",
                                        "abbreviation": "SC"
                                      },
                                      {
                                        "value": "COLLEGE_IN_PROGRESS",
                                        "description": "Undergraduate or equivalent",
                                        "abbreviation": "COL"
                                      },
                                      {
                                        "value": "ASSOCIATE_DEGREE",
                                        "description": "Post-secondary diploma or equivalent",
                                        "abbreviation": "AA"
                                      },
                                      {
                                        "value": "BACHELOR_DEGREE",
                                        "description": "Graduate degree or equivalent",
                                        "abbreviation": "BA"
                                      },
                                      {
                                        "value": "MASTERS_DEGREE",
                                        "description": "Master's degree or equivalent",
                                        "abbreviation": "MA"
                                      },
                                      {
                                        "value": "DOCTORATE",
                                        "description": "Doctorate degree or equivalent",
                                        "abbreviation": "PHD"
                                      },
                                      {
                                          "value": "OTHER",
                                          "description": "Other",
                                          "abbreviation": "OTH"
                                      }
                                    ]


def test_education_levels_unauthorized():
    api = UserService()
    res = api.get_education_levels()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
def test_linguistics_qualification(ac_api_cookie_no_customer):
    api = UserService(cookies=ac_api_cookie_no_customer)

    res = api.get_linguistics_qualification()
    res.assert_response_status(200)
    assert res.json_response == [
                               {
                                  "value":"NO_QUALIFICATION",
                                  "label":"No qualification"
                               },
                               {
                                  "value":"DIPLOMA_STUDYING",
                                  "label":"Diploma – Studying"
                               },
                               {
                                  "value":"DIPLOMA_COMPLETED",
                                  "label":"Diploma – Completed"
                               },
                               {
                                  "value":"BACHELORS_DEGREE_STUDYING",
                                  "label":"Bachelor’s degree – Studying"
                               },
                               {
                                  "value":"BACHELORS_DEGREE_COMPLETED",
                                  "label":"Bachelor’s degree – Completed"
                               },
                               {
                                  "value":"MASTERS_DEGREE_STUDYING",
                                  "label":"Master’s degree – Studying"
                               },
                               {
                                  "value":"MASTERS_DEGREE_COMPLETED",
                                  "label":"Master’s degree – Completed"
                               },
                               {
                                  "value":"DOCTORAL_DEGREE_STUDYING",
                                  "label":"Doctoral degree – Studying"
                               },
                               {
                                  "value":"DOCTORAL_DEGREE_COMPLETED",
                                  "label":"Doctoral degree – Completed"
                               }
                            ]


def test_linguistics_qualification_unauthorized():
    api = UserService()
    res = api.get_linguistics_qualification()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}

