from appen_connect.api_automation.services_config.gateway import AC_GATEWAY
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_profile_builder, pytest.mark.regression_ac, pytest.mark.ac_api_gateway, pytest.mark.ac_api_gateway_profile_target, pytest.mark.ac_api]


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_question_categories(app_test):
    vendor_name = get_test_data('test_ui_account', 'user_name')
    vendor_password = get_test_data('test_ui_account', 'password')
    app_test.ac_user.login_as(user_name=vendor_name, password=vendor_password)

    # This is temporary solution for automation, because Eng Team is still working in Gateway
    url = {
        'stage': "https://gateway-connect-stage.integration.cf3.us/project-profile-builder/api/master-profile/questions",
        'qa': "https://gateway-connect-qa.sandbox.cf3.us/project-profile-builder/api/master-profile/questions",
    }
    app_test.navigation.open_page(url[app_test.env])
    _cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in app_test.driver.get_cookies()}

    api = AC_GATEWAY(cookies=_cookie)
    res = api.get_question_categories()
    res.assert_response_status(200)
    assert res.json_response == [
        {'description': '', 'label': 'Appen Work', 'value': 'APPEN_WORK'},
        {'description': '',
         'label': 'Entertainment & Activities',
         'value': 'ENTERTAINMENT_AND_ACTIVITIES'},
        {'description': '', 'label': 'Environmental', 'value': 'ENVIRONMENTAL'},
        {'description': '', 'label': 'Experiences', 'value': 'EXPERIENCES'},
        {'description': 'The following category of questions relates to demographic '
                        'information about yourself and your family. Training data '
                        'from diverse populations of contributors is needed to train '
                        'AI to perform equally well for everyone. To provide training '
                        'data that supports inclusive AI, and to ensure all groups '
                        'are fully represented in the data that we collect, we are '
                        'asking you to complete these questions. All questions in '
                        'this category are optional, and, as in all Appen projects, '
                        'you can opt out at any time.',
         'label': 'Family & Me',
         'value': 'FAMILY_AND_ME'},
        {'description': '', 'label': 'Health & Medical', 'value': 'HEALTH_AND_MEDICAL'},
        {'description': '', 'label': 'Home & Income', 'value': 'HOME_AND_INCOME'},
        {'description': '', 'label': 'Languages', 'value': 'LANGUAGES'},
        {'description': '', 'label': 'Leisure & Activities', 'value': 'LEISURE_AND_ACTIVITIES'},
        {'description': '', 'label': 'Metadata', 'value': 'METADATA'},
        {'description': '', 'label': 'Override', 'value': 'OVERRIDE'},
        {'description': '', 'label': 'Pets', 'value': 'PETS'},
        {'description': '', 'label': 'Politics', 'value': 'POLITICS'},
        {'description': '', 'label': 'Social', 'value': 'SOCIAL'},
        {'description': '', 'label': 'Technologies & Communications', 'value': 'TECHNOLOGY_AND_COMMUNICATIONS'},
        {'description': '', 'label': 'Transport', 'value': 'TRANSPORT'},
        {'description': '', 'label': 'Work & Education', 'value': 'WORK_AND_EDUCATION'},
    ]


def test_get_question_categories_no_cookies():
    api = AC_GATEWAY()
    res = api.get_question_categories()
    res.assert_response_status(401)
    assert len(res.json_response) == 0


def test_get_profile_target(app_test):
    vendor_name = get_test_data('test_ui_account', 'user_name')
    vendor_password = get_test_data('test_ui_account', 'password')
    app_test.ac_user.login_as(user_name=vendor_name, password=vendor_password)
    url = {
        'stage': "https://gateway-connect-stage.integration.cf3.us/project-profile-builder/api/master-profile/questions",
        'qa': "https://gateway-connect-qa.sandbox.cf3.us/project-profile-builder/api/master-profile/questions",
    }
    app_test.navigation.open_page(url[app_test.env])

    _cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in app_test.driver.get_cookies()}

    api = AC_GATEWAY(cookies=_cookie)
    res = api.get_profile_targets(target_id=4)
    res.assert_response_status(200)
    assert len(res.json_response) == 6


def test_get_profile_target_no_cookies():
    api = AC_GATEWAY()
    res = api.get_profile_targets(target_id=84)
    res.assert_response_status(401)
    assert len(res.json_response) == 0


@pytest.mark.ac_api_uat
def test_create_profile_target(app_test):
    vendor_name = get_test_data('test_ui_account', 'user_name')
    vendor_password = get_test_data('test_ui_account', 'password')
    app_test.ac_user.login_as(user_name=vendor_name, password=vendor_password)
    url = {
        'stage': "https://gateway-connect-stage.integration.cf3.us/project-profile-builder/api/master-profile/questions",
        'qa': "https://gateway-connect-qa.sandbox.cf3.us/project-profile-builder/api/master-profile/questions",
    }
    app_test.navigation.open_page(url[app_test.env])

    _cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in app_test.driver.get_cookies()}

    api = AC_GATEWAY(cookies=_cookie)
    target_name = "API: Edication" + str(random.randint(10000000, 99999999))
    target_payload = {
                  "name": target_name,
                  "description": "API Work & Education: description",
                  "profileQuestions": [
                      {
                          "projectProfileTargetId": 2,
                          "masterProfileQuestionId": 43,
                          "disabledSubQuestion": False,
                          "allChecked": True,
                          "allUnchecked": False,
                          "profileQuestionAnswerList": [
                              {

                                  "masterProfileQuestionAnswerId": 159,
                                  "action": "PASS_THROUGH"
                              },
                              {
                                  "masterProfileQuestionAnswerId": 160,
                                  "action": "REJECT"
                              }
                          ]

                      }
    ]
     }

    res = api.create_profile_targets(target_payload)
    res.assert_response_status(200)
    assert res.json_response["name"] == target_name
    assert res.json_response["description"] == "API Work & Education: description"
    full_name = get_test_data('test_ui_account', 'full_name')
    assert res.json_response["createdBy"] == full_name

    assert len(res.json_response["profileQuestions"]) == 1
    target_id = res.json_response["id"]
    res = api.get_profile_targets(target_id)
    res.assert_response_status(200)
    assert res.json_response["name"] == target_name
    assert res.json_response["description"] == "API Work & Education: description"
    assert res.json_response["createdBy"] == full_name
    assert 2 == len(res.json_response['profileQuestions'][0]['profileQuestionAnswerList'])


def test_create_profile_target_no_cookies(app_test):
    api = AC_GATEWAY()
    target_name = "API: Technologies & Communications" + str(random.randint(10000000, 99999999))
    target_payload = {"id": None,
                      "name": target_name,
                      "description": "API Technologies & Communications: description",
                      "profileQuestions": [
                          {
                              "masterProfileQuestionId": "44",
                              "disabledSubQuestion": False,
                              "profileQuestionAnswerList": [
                                  {
                                      "masterProfileQuestionAnswerId": 213,
                                      "action": "PASS_THROUGH",
                                      "customAnswer": None
                                  },
                                  {
                                      "masterProfileQuestionAnswerId": 214,
                                      "action": "PASS_THROUGH",
                                      "customAnswer": None
                                  },
                                  {
                                      "masterProfileQuestionAnswerId": 215,
                                      "action": "PASS_THROUGH",
                                      "customAnswer": None
                                  },
                                  {
                                      "masterProfileQuestionAnswerId": 216,
                                      "action": "REJECT",
                                      "customAnswer": None
                                  },
                                  {
                                      "masterProfileQuestionAnswerId": 217,
                                      "action": "REJECT",
                                      "customAnswer": None
                                  },
                                  {
                                      "masterProfileQuestionAnswerId": 218,
                                      "action": "REJECT",
                                      "customAnswer": None
                                  },
                                  {
                                      "masterProfileQuestionAnswerId": 219,
                                      "action": "PASS_THROUGH",
                                      "customAnswer": None
                                  },
                                  {
                                      "masterProfileQuestionAnswerId": 220,
                                      "action": "PASS_THROUGH",
                                      "customAnswer": None
                                  },
                                  {
                                      "masterProfileQuestionAnswerId": 221,
                                      "action": "REJECT",
                                      "customAnswer": None
                                  },
                                  {
                                      "masterProfileQuestionAnswerId": 222,
                                      "action": "REJECT",
                                      "customAnswer": None
                                  }
                              ]
                          }
                      ]
                      }

    res = api.create_profile_targets(target_payload)
    res.assert_response_status(401)
    assert len(res.json_response) == 0



# API should not allow an vendor to create  the Target or Get
# def test_create_profile_target_no_auth(app_test):
#     vendor_name = get_test_data('test_consent_form_vendor', 'user_name')
#     vendor_password = get_test_data('test_consent_form_vendor', 'password')
#     app_test.ac_user.login_as(user_name=vendor_name, password=vendor_password)
#     app_test.navigation.open_page(
#         "https://gateway-connect-" + app_test.env + ".integration.cf3.us/project-profile-builder/api/master-profile/questions")
#     _cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in app_test.driver.get_cookies()}
#
#     api = AC_GATEWAY(cookies=_cookie)
#     target_name = "API: Technologies & Communications" + str(random.randint(10000000, 99999999))
#     target_payload = {"id": None,
#                       "name": target_name,
#                       "description": "API Technologies & Communications: description",
#                       "profileQuestions": [
#                           {
#                               "masterProfileQuestionId": "44",
#                               "disabledSubQuestion": False,
#                               "profileQuestionAnswerList": [
#                                   {
#                                       "masterProfileQuestionAnswerId": 213,
#                                       "action": "PASS_THROUGH",
#                                       "customAnswer": None
#                                   },
#                                   {
#                                       "masterProfileQuestionAnswerId": 214,
#                                       "action": "PASS_THROUGH",
#                                       "customAnswer": None
#                                   },
#                                   {
#                                       "masterProfileQuestionAnswerId": 215,
#                                       "action": "PASS_THROUGH",
#                                       "customAnswer": None
#                                   },
#                                   {
#                                       "masterProfileQuestionAnswerId": 216,
#                                       "action": "REJECT",
#                                       "customAnswer": None
#                                   },
#                                   {
#                                       "masterProfileQuestionAnswerId": 217,
#                                       "action": "REJECT",
#                                       "customAnswer": None
#                                   },
#                                   {
#                                       "masterProfileQuestionAnswerId": 218,
#                                       "action": "REJECT",
#                                       "customAnswer": None
#                                   },
#                                   {
#                                       "masterProfileQuestionAnswerId": 219,
#                                       "action": "PASS_THROUGH",
#                                       "customAnswer": None
#                                   },
#                                   {
#                                       "masterProfileQuestionAnswerId": 220,
#                                       "action": "PASS_THROUGH",
#                                       "customAnswer": None
#                                   },
#                                   {
#                                       "masterProfileQuestionAnswerId": 221,
#                                       "action": "REJECT",
#                                       "customAnswer": None
#                                   },
#                                   {
#                                       "masterProfileQuestionAnswerId": 222,
#                                       "action": "REJECT",
#                                       "customAnswer": None
#                                   }
#                               ]
#                           }
#                       ]
#                       }
#
#     res = api.create_profile_targets(target_payload)
#     res.assert_response_status(200)
#     print(res.json_response)