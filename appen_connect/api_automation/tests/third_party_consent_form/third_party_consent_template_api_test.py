import time
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name
from adap.api_automation.utils.data_util import *
from appen_connect.api_automation.services_config.ac_api import AC_API, create_new_random_project
from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project

pytestmark = [pytest.mark.regression_ac_consent_form, pytest.mark.regression_ac, pytest.mark.ac_api_v2, pytest.mark.ac_api_v2_third_party_consent, pytest.mark.ac_api]

USER_NAME = get_test_data('test_ui_account', 'user_name')
PASSWORD = get_test_data('test_ui_account', 'password')


_country = "*"
_country_ui = "Canada"
_locale = "English (Canada)"
_fluency = "Native or Bilingual"
_lan = "eng"
_lan_ui = "English"
_lan_country = "*"
_pay_rate = 6

project_config = {
    "projectType": 'Express',
    "workType": "LINGUISTICS",
    "externalSystemId": 15,
    "qualificationProcessTemplateId": 1926,
    "registrationProcessTemplateId": 1646,
    "locale": {
        "country": _country
    },
    "hiring_target": {
        "language": _lan,
        "languageCountry": _lan_country,
        "restrictToCountry": _country,
        "target": 100
    },
    "pay_rates": {
        "spokenFluency": _fluency.upper().replace(" ", "_"),
        "writtenFluency": _fluency.upper().replace(" ", "_"),
        "rateValue": _pay_rate,
        "taskType": "Default",
        "language": _lan,
        "languageCountry": "*",
        "restrictToCountry": _country
    }
}


@pytest.fixture(scope="module")
def project_data(app, ac_api_cookie):
    _project = api_create_simple_project(project_config, ac_api_cookie)

    return {"project_id": _project['id'],
            "valid_cookie": ac_api_cookie}


@pytest.mark.ac_api_uat
def test_get_empty_dc_consent_form(project_data):
    ac_api = AC_API(cookies=project_data['valid_cookie'])
    res = ac_api.get_dc_consent_form(project_data['project_id'])
    res.assert_response_status(404)
    assert res.json_response == {}


def test_get_dc_consent_form_no_cookies(project_data):
    ac_api = AC_API()
    res = ac_api.get_dc_consent_form(project_data['project_id'])
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
def test_get_appen_entities(project_data):
    ac_api = AC_API(cookies=project_data['valid_cookie'])
    res = ac_api.get_appen_entities()
    res.assert_response_status(200)
    assert res.json_response == [{"id": 1, "name": "Appen Butler Hill Pty Ltd", "country": "AUS"},
                                 {"id": 2, "name": "Beijing Appen Technology Co.", "country": "CHN"},
                                 {"id": 3, "name": "Appen Technology Wuxi Co.", "country": "CHN"},
                                 {"id": 4, "name": "Appen Data Technology", "country": "CHN"},
                                 {"id": 5, "name": "Appen Services Philippines", "country": "PHL"},
                                 {"id": 6, "name": "Appen Europe LTD", "country": "GBR"},
                                 {"id": 7, "name": "Mendip Media Group LTD", "country": "GBR"},
                                 {"id": 8, "name": "Appen Butler Hill Inc.", "country": "USA"},
                                 {"id": 9, "name": "Figure Eight Federal LLC", "country": "USA"}]


def test_get_appen_entities_no_cookies(project_data):
    ac_api = AC_API()
    res = ac_api.get_appen_entities()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
def test_get_pii_data(project_data):
    ac_api = AC_API(cookies=project_data['valid_cookie'])
    res = ac_api.get_pii_data()
    res.assert_response_status(200)
    assert res.json_response == [{"id": 1, "name": "Racial or ethnic origin", "description": None, "sensitive": True},
                                 {"id": 2, "name": "Political opinions ", "description": None, "sensitive": True},
                                 {"id": 3, "name": "Religious or philosophical beliefs", "description": None, "sensitive": True},
                                 {"id": 4, "name": "Trade union membership", "description": None, "sensitive": True},
                                 {"id": 5, "name": "Genetic information", "description": None, "sensitive": True},
                                 {"id": 6, "name": "Uniquely identifiable biometric data",
                                  "description": "Processing physical or behavioral characteristics to uniquely identify that data subject.  Facial identification for secured access purposes would be “biometric data.”  Processing facial images to train AI technology in general and not to uniquely identify who’s face is who’s, is not biometric data.",
                                  "sensitive": True},
                                 {"id": 7, "name": "Health data",
                                  "description": "including data concerning a person’s sex life or sexual orientation.",
                                  "sensitive": True},
                                 {"id": 8, "name": "Voice conversations between two or more individuals",
                                  "description": None, "sensitive": True},
                                 {"id": 9, "name": "Data to access private accounts",
                                  "description": "Social security number, payment access data, passwords.",
                                  "sensitive": True},
                                 {"id": 10, "name": "Other sensitive data",
                                  "description": "Any other data defined as sensitive by your applicable contract.",
                                  "sensitive": True},
                                 {"id": 11, "name": "Non identifiable voice data",
                                  "description": "Used for a purpose other than specifically identifying the data subject.",
                                  "sensitive": False},
                                 {"id": 12, "name": "Non identifiable facial/body images or videos",
                                  "description": "Example: collecting facial images to train AI to better recognize people in general and not a specific person.",
                                  "sensitive": False},
                                 {"id": 13, "name": "Other non-sensitive data",
                                  "description": "Any other PII that does not fall within the sensitive data category above: gender, height, weight, DOB, name, address, email, etc.",
                                  "sensitive": False}]


def test_get_pii_data_no_cookies(project_data):
    ac_api = AC_API()
    res = ac_api.get_pii_data()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


def test_create_dc_consent_no_cookies(project_data):
    api = AC_API()

    template_payload = {"projectId": project_data['project_id'],
                        "appenEntityId": 1,
                        "datasetOwnerType": "CUSTOMER_OWNS_ALL",
                        "contactEmail": "support@connect-mail.appen.com",
                        "countries": ["CAN"],
                        "piiData": [{"id": 1}, {"id": 11}],
                        "customerDpoEmail": "FMICHALCH@APPEN.COM",
                        "customerFullLegalName": "",
                        "customerCountry": ""}

    res = api.create_dc_consent_form(project_data['project_id'], template_payload)
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
def test_create_dc_consent_customer_required(project_data):
    api = AC_API(project_data['valid_cookie'])

    template_payload = {"projectId": project_data['project_id'],
                        "appenEntityId": 1,
                        "datasetOwnerType": "CUSTOMER_OWNS_ALL",
                        "contactEmail": "support@connect-mail.appen.com",
                        "countries": ["CAN"],
                        "piiData": [{"id": 1}, {"id": 11}],
                        "customerDpoEmail": "FMICHALCH@APPEN.COM",
                        "customerFullLegalName": "",
                        "customerCountry": ""}

    res = api.create_dc_consent_form(project_data['project_id'], template_payload)
    res.assert_response_status(400)
    assert res.json_response == {"code": "Customer info is required", "message": "Customer info is required"}


# Create a basic Template for Project
@pytest.mark.ac_api_uat
def test_create_dc_consent_form(project_data):
    api = AC_API(project_data['valid_cookie'])

    template_payload = {"projectId": project_data['project_id'],
                        "appenEntityId": 1,
                        "datasetOwnerType": "CUSTOMER_OWNS_ALL",
                        "contactEmail": "support@connect-mail.appen.com",
                        "countries": ["CAN"],
                        "piiData": [{"id": 1}, {"id": 11}],
                        "customerDpoEmail": "FMICHALCH@APPEN.COM",
                        "customerFullLegalName": "customerFullLegalName",
                        "customerCountry": "CAN"}

    res = api.create_dc_consent_form(project_data['project_id'], template_payload)
    res.assert_response_status(201)

    assert res.json_response["projectId"] == project_data['project_id']
    assert res.json_response["appenEntityId"] == 1
    assert res.json_response["datasetOwnerType"] == "CUSTOMER_OWNS_ALL"
    assert res.json_response["contactEmail"] == "support@connect-mail.appen.com"
    assert res.json_response["countries"] == ["CAN"]
    assert res.json_response["thirdPartyAgeType"] is None
    assert res.json_response["customerDpoEmail"] == "FMICHALCH@APPEN.COM"
    assert res.json_response["customerFullLegalName"] == "customerFullLegalName"
    assert res.json_response["customerCountry"] == 'CAN'
    assert res.json_response["version"] == 1
    assert len(res.json_response["piiData"]) == 2

    global dc_id
    dc_id = res.json_response["id"]


@pytest.mark.ac_api_uat
def test_update_dc_consent_form(project_data):
    api = AC_API(project_data['valid_cookie'])
    template_payload = {"projectId": project_data['project_id'],
                        "appenEntityId": 4,
                        "datasetOwnerType": "APPEN_OWNS_SOME_OR_ALL",
                        "contactEmail": "ac.automation.qa1@appencorporation.com",
                        "countries": ["CHN", "HKG"],
                        "piiData": [{"id": 11}, {"id": 12}, {"id": 13}],
                        "thirdPartyAgeType": "ADULT_AND_MINOR",
                        "customerDpoEmail": "",
                        "customerFullLegalName": "",
                        "customerCountry": ""}

    res = api.update_dc_consent_form(dc_id, template_payload)
    res.assert_response_status(201)
    assert res.json_response["id"] == int(dc_id) + 1
    assert res.json_response["projectId"] == project_data['project_id']
    assert res.json_response["appenEntityId"] == 4
    assert res.json_response["datasetOwnerType"] == "APPEN_OWNS_SOME_OR_ALL"
    assert res.json_response["contactEmail"] == "ac.automation.qa1@appencorporation.com"
    assert res.json_response["countries"] == ["CHN", "HKG"]
    assert res.json_response["thirdPartyAgeType"] == "ADULT_AND_MINOR"
    assert res.json_response["customerDpoEmail"] == ""
    assert res.json_response["customerFullLegalName"] == ""
    assert res.json_response["customerCountry"] == ""
    assert res.json_response["version"] == 2
    assert len(res.json_response["piiData"]) == 3


def test_update_dc_consent_form_no_cookies(project_data):
    api = AC_API()
    template_payload = {"projectId": project_data['project_id'],
                        "appenEntityId": 4,
                        "datasetOwnerType": "APPEN_OWNS_SOME_OR_ALL",
                        "contactEmail": "ac.automation.qa1@appencorporation.com",
                        "countries": ["CHN", "HKG"],
                        "piiData": [{"id": 11}, {"id": 12}, {"id": 13}],
                        "thirdPartyAgeType": "ADULT_AND_MINOR",
                        "customerDpoEmail": "",
                        "customerFullLegalName": "",
                        "customerCountry": ""}

    res = api.update_dc_consent_form(dc_id, template_payload)
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}

