import time

from adap.api_automation.utils.data_util import *
from appen_connect.api_automation.services_config.ac_api import AC_API, create_new_random_project
from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project

pytestmark = [pytest.mark.regression_ac_project_config, pytest.mark.regression_ac, pytest.mark.ac_api_v2, pytest.mark.ac_api_v2_resource_mappings, pytest.mark.ac_api]
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
def resources_project(app, ac_api_cookie):
    global _project
    _project = api_create_simple_project(project_config, ac_api_cookie)

    res = AC_API(cookies=ac_api_cookie).get_groups(customer_id=53)
    customer_groups = res.json_response

    return {"project_id": _project['id'],
            "customer_groups": customer_groups,
            "valid_cookie": ac_api_cookie}


@pytest.mark.ac_api_uat
def test_get_resource_quizzes(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_resource_quizzes()
    res.assert_response_status(200)
    assert "id" in res.json_response[0]
    assert "name" in res.json_response[0]
    assert {'id': 493, 'name': '13697 Cosmos Guidelines Screener - Canadian French'} in res.json_response


@pytest.mark.ac_api_uat
def test_get_resource_survey(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_resource_survey()
    res.assert_response_status(200)
    assert "id" in res.json_response[0]
    assert "name" in res.json_response[0]
    assert {"id": 219, "name": "VTX French Screening Test"} in res.json_response


@pytest.mark.ac_api_uat
def test_get_resource_academies(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_resource_academies()
    res.assert_response_status(200)
    assert "id" in res.json_response[0]
    assert "name" in res.json_response[0]
    assert {'id': 11, 'name': '[Atlas] Image Relevance Academy'} in res.json_response


@pytest.mark.ac_api_uat
def test_get_resource_documents(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_resource_documents()
    res.assert_response_status(200)
    assert "id" in res.json_response[0]
    assert "name" in res.json_response[0]
    assert {"id": 105, "name": "VTX French Annotation Guidelines"} in res.json_response


@pytest.mark.ac_api_uat
def test_empty_resource_mappings(resources_project):
    ac_api = AC_API(cookies=resources_project['valid_cookie'])
    res = ac_api.get_resource_mappings(resources_project['project_id'])
    res.assert_response_status(200)
    assert res.json_response == {"documents": [], "surveys": [], "quizzes": [], "academies": []}


def test_get_resources_status_no_cookies(resources_project):
    ac_api = AC_API()
    res = ac_api.get_resource_mappings(resources_project['project_id'])
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
def test_create_quiz_resource(resources_project):
    ac_api = AC_API(cookies=resources_project['valid_cookie'])

    payload = {
                   "type": "PROJECT_QUIZ",
                   "resourceId": 493,
                   "unlimited": True,
                   "maxQuizAttempts": -1,
                   "subsetSize": 1,
                   "passingScore": 70,
                   "questionsShuffled":False,
                   "showFeedback": True,
                   "projectId": resources_project['project_id'],
                   "usageType": "TRAINING"
                }

    res = ac_api.post_resource_mappings(resources_project['project_id'], payload)
    res.assert_response_status(201)
    assert res.json_response["projectId"] == resources_project['project_id']
    assert res.json_response["resourceId"] == 493
    assert res.json_response["passingScore"] == 70
    assert res.json_response["maxQuizAttempts"] == -1
    assert res.json_response["subsetSize"] == 1
    assert res.json_response["type"] == "PROJECT_QUIZ"
    assert res.json_response["usageType"] == "TRAINING"
    assert res.json_response["active"] == None
    assert res.json_response["questionsShuffled"] == False
    assert res.json_response["showFeedback"] == True
    global resourceid
    resourceid = res.json_response["id"]


def test_create_duplicated_quiz_resource(resources_project):
    ac_api = AC_API(cookies=resources_project['valid_cookie'])

    payload = {
                   "type": "PROJECT_QUIZ",
                   "resourceId": 493,
                   "unlimited": True,
                   "maxQuizAttempts": -1,
                   "subsetSize": 1,
                   "passingScore": 70,
                   "questionsShuffled": False,
                   "showFeedback": True,
                   "projectId": resources_project['project_id'],
                   "usageType": "TRAINING"
                }

    res = ac_api.post_resource_mappings(resources_project['project_id'], payload)
    res.assert_response_status(400)
    assert res.json_response == {"code": "InvalidQuiz",
                                 "message": "There is already a resource with this quiz."
                                 }


def test_update_resource_mappings(resources_project):
    ac_api = AC_API(cookies=resources_project['valid_cookie'])

    payload = {"id": resourceid,
               "projectId": resources_project['project_id'],
               "resourceId": 493,
               "type": "PROJECT_QUIZ",
               "usageType": "TRAINING",
               "active": None,
               "passingScore": 70,
               "questionsShuffled": True,
               "showFeedback": True,
               "maxQuizAttempts": -1,
               "subsetSize": 1,
               "unlimited": True,
               "allQuestions": False
               }

    res = ac_api.update_resource_mappings(resources_project['project_id'], resourceid, payload)
    res.assert_response_status(200)
    assert res.json_response["projectId"] == resources_project['project_id']
    assert res.json_response["id"] == resourceid
    assert res.json_response["questionsShuffled"] == True


@pytest.mark.ac_api_uat
def test_create_survey_resource(resources_project):
    ac_api = AC_API(cookies=resources_project['valid_cookie'])

    payload = {
        "type": "PROJECT_QUIZ",
        "resourceId": 219,
        "unlimited": False,
        "maxQuizAttempts": 1,
        "allQuestions": True,
        "subsetSize": -1,
        "questionsShuffled": True,
        "projectId": resources_project['project_id'],
        "usageType": "TRAINING"}


    res = ac_api.post_resource_mappings(resources_project['project_id'], payload)
    res.assert_response_status(201)
    assert res.json_response["projectId"] == resources_project['project_id']
    assert res.json_response["resourceId"] == 219
    assert res.json_response["passingScore"] == 0
    assert res.json_response["maxQuizAttempts"] == 1
    assert res.json_response["subsetSize"] == -1
    assert res.json_response["type"] == "PROJECT_QUIZ"
    assert res.json_response["usageType"] == "TRAINING"
    assert res.json_response["active"] == None
    assert res.json_response["questionsShuffled"] == True
    assert res.json_response["showFeedback"] == False


def test_create_duplicated_survey_resource(resources_project):
    ac_api = AC_API(cookies=resources_project['valid_cookie'])

    payload = {
        "type": "PROJECT_QUIZ",
        "resourceId": 219,
        "unlimited": False,
        "maxQuizAttempts": 1,
        "allQuestions": True,
        "subsetSize": -1,
        "questionsShuffled": True,
        "projectId": resources_project['project_id'],
        "usageType": "TRAINING"}

    res = ac_api.post_resource_mappings(resources_project['project_id'], payload)
    res.assert_response_status(400)
    assert res.json_response == {"code": "InvalidQuiz",
                                 "message": "There is already a resource with this quiz."
                                 }


@pytest.mark.ac_api_uat
def test_create_academy_resource(resources_project):
    ac_api = AC_API(cookies=resources_project['valid_cookie'])

    payload = {
         "type": "PROJECT_ACADEMY",
         "allowQualifyingApplicantAccess": True,
         "resourceId": 11,
         "allowActiveUserAccess": True,
         "projectId": resources_project['project_id'],
         "usageType": "TRAINING"}

    res = ac_api.post_resource_mappings(resources_project['project_id'], payload)
    res.assert_response_status(201)
    assert res.json_response["projectId"] == resources_project['project_id']
    assert res.json_response["resourceId"] == 11
    assert res.json_response["type"] == "PROJECT_ACADEMY"
    assert res.json_response["usageType"] == "TRAINING"
    assert res.json_response["allowQualifyingApplicantAccess"] == True
    assert res.json_response["allowActiveUserAccess"] == True
    assert res.json_response["active"] == None


def test_duplicate_academy_resource(resources_project):
    ac_api = AC_API(cookies=resources_project['valid_cookie'])

    payload = {
         "type": "PROJECT_ACADEMY",
         "allowQualifyingApplicantAccess": True,
         "resourceId": 87,
         "allowActiveUserAccess": True,
         "projectId": resources_project['project_id'],
         "usageType": "TRAINING"}

    res = ac_api.post_resource_mappings(resources_project['project_id'], payload)
    res.assert_response_status(400)
    assert res.json_response == {"code": "PARAMETER_ERROR",
                                 "message": "Cannot set Academy Mapping with a null or non-existent academy."
                                 }


@pytest.mark.ac_api_uat
def test_create_document_resource(resources_project):
    ac_api = AC_API(cookies=resources_project['valid_cookie'])

    payload = {"type": "PROJECT_DOCUMENT",
               "active": True,
               "usageType": "GUIDELINE",
               "hasNotesToRaters": True,
               "resourceId": 105,
               "requireAcknowledgement": True,
               "allowQualifyingApplicantAccess": True,
               "noteToRater": "Notes to Raters",
               "projectId": resources_project['project_id']}

    res = ac_api.post_resource_mappings(resources_project['project_id'], payload)
    res.assert_response_status(201)
    assert res.json_response["projectId"] == resources_project['project_id']
    assert res.json_response["resourceId"] == 105
    assert res.json_response["type"] == "PROJECT_DOCUMENT"
    assert res.json_response["usageType"] == "GUIDELINE"
    assert res.json_response["noteToRater"] == "Notes to Raters"
    assert res.json_response["allowQualifyingApplicantAccess"] == True
    assert res.json_response["requireAcknowledgement"] == True
    assert res.json_response["active"] == True


def test_duplicate_document_resource(resources_project):
    ac_api = AC_API(cookies=resources_project['valid_cookie'])

    payload = {"type": "PROJECT_DOCUMENT",
               "active": True,
               "usageType": "GUIDELINE",
               "hasNotesToRaters": True,
               "resourceId": 105,
               "requireAcknowledgement": True,
               "allowQualifyingApplicantAccess": True,
               "noteToRater": "Notes to Raters",
               "projectId": resources_project['project_id']}

    res = ac_api.post_resource_mappings(resources_project['project_id'], payload)
    res.assert_response_status(400)
    assert res.json_response == {"code": "CannotCreateDocumentMapping",
                                 "message": "Document mapping already exists."}


@pytest.mark.ac_api_uat
def test_get_resources_status_vendor(app_test, resources_project):
    vendor_name = get_test_data('test_express_active_vendor_account', 'user_name')
    vendor_password = get_test_data('test_express_active_vendor_account', 'password')
    app_test.ac_user.login_as(user_name=vendor_name, password=vendor_password)
    time.sleep(2)
    _cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in app_test.driver.get_cookies()}

    ac_api = AC_API(cookies=_cookie)
    res = ac_api.get_resource_mappings(resources_project['project_id'])
    res.assert_response_status(403)