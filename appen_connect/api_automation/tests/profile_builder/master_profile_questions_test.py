from appen_connect.api_automation.services_config.endpoints.gateway import *
from appen_connect.api_automation.services_config.gateway import AC_GATEWAY
from adap.api_automation.utils.data_util import *

#TODO:  disable tests untill fix id generation approach

pytestmark = [pytest.mark.regression_ac_profile_builder, pytest.mark.regression_ac, pytest.mark.ac_api_gateway, pytest.mark.ac_api_gateway_master_profile, pytest.mark.ac_api]

# test json schema
expected_resp_fields_full_mode = [
        'id',
        'type',
        'category',
        'name',
        'question',
        'notes',
        'answerStyle',
        'excludeCountries',
        'timer',
        'questionLevel',
        'questionType',
        'metadataAnswered',
        'parentQuestion',
        'answerList'
]


expected_resp_fields_compact_mode = [
        'id',
        'category',
        'name',
        'question',
        'timer',
        'questionLevel',
        'questionType',
        'answerList'
]


@pytest.fixture(scope='module')
def _valid_cookies(app):
    vendor_name = get_test_data('test_ui_account', 'user_name')
    vendor_password = get_test_data('test_ui_account', 'password')
    app.ac_user.login_as(user_name=vendor_name, password=vendor_password)

    app.navigation.open_page(URL(pytest.env)+'/master-profile/questions')
    _cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in app.driver.get_cookies()}

    return _cookie


@pytest.fixture(scope='module')
def _test_data(_valid_cookies):
    ac_api = AC_GATEWAY(cookies=_valid_cookies)

    global _question_types, _question_categories

    _question_types = ac_api.get_question_types().json_response
    _question_categories = ac_api.get_question_categories().json_response


def test_get_master_profile_questions_vendor(app_test):
    vendor_name = get_test_data('test_express_active_vendor_account', 'user_name')
    vendor_password = get_test_data('test_express_active_vendor_account', 'password')
    app_test.ac_user.login_as(user_name=vendor_name, password=vendor_password)
    app_test.navigation.open_page(URL(pytest.env)+'/master-profile/questions')
    _cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in app_test.driver.get_cookies()}

    ac_api = AC_GATEWAY(cookies=_cookie)
    res = ac_api.get_master_profile_questions()
    res.assert_response_status(200)
    assert len(res.json_response)


def test_get_master_profile_questions_no_cookies():
    ac_api = AC_GATEWAY()
    res = ac_api.get_master_profile_questions(allow_redirects=False)
    res.assert_response_status(401)  # redirect to login
    assert res.json_response == {}


def test_get_master_profile_questions(_valid_cookies, _test_data):
    ac_api = AC_GATEWAY(cookies=_valid_cookies)
    res = ac_api.get_master_profile_questions(allow_redirects=False)
    res.assert_response_status(200)
    assert len(res.json_response) > 0

    random_questions = random.choices(res.json_response, k=min(10, len(res.json_response)))

    for question in random_questions:
        for ef in expected_resp_fields_full_mode:
            if ef not in question:
                assert False, "%s has not been found in response" % ef

        assert question['category'] in [x ['value'] for x in _question_categories]
        assert question['questionType'] in [x['value'] for x in _question_types]


def test_get_master_profile_questions_full_compact_mode(_valid_cookies, _test_data):
    ac_api = AC_GATEWAY(cookies=_valid_cookies)
    res_full_mode = ac_api.get_master_profile_questions(compact='false')
    res_full_mode.assert_response_status(200)

    res_compact_mode = ac_api.get_master_profile_questions(compact='true')
    res_compact_mode.assert_response_status(200)

    #TODO update if this is actual bug or invalid comparison - https://appen.atlassian.net/browse/ACE-17489
    #assert len(res_full_mode.json_response) == len(res_compact_mode.json_response)

    random_questions = random.choices(res_compact_mode.json_response, k=min(10, len(res_compact_mode.json_response)))
    for question_compact_mode in random_questions:
        for key in question_compact_mode.keys():
            assert key in expected_resp_fields_compact_mode

        question_full_mode = find_dict_in_array_by_value(res_full_mode.json_response, 'id', question_compact_mode['id'])
        assert question_full_mode['category'] == question_compact_mode['category']
        assert question_full_mode['name'] == question_compact_mode['name']
        assert question_full_mode['question'] == question_compact_mode['question']
        assert len(question_full_mode['answerList']) == len(question_compact_mode['answerList'])

#
# def test_create_master_profile_question_no_cookies():
#     ac_api = AC_GATEWAY()
#     payload = {}
#     res = ac_api.post_master_profile_question(payload=payload, allow_redirects=False)
#     res.assert_response_status(302)  # redirect to login
#     assert res.json_response == {}
#
#
# def test_create_master_profile_question_empty_payload(_valid_cookies):
#     ac_api = AC_GATEWAY(_valid_cookies)
#     payload = {}
#
#     res = ac_api.post_master_profile_question(payload=payload)
#     res.assert_response_status(400)
#     assert res.json_response['error'] == 'Bad Request'
#
#
# @pytest.mark.dependency()
# def test_create_master_profile_question(_valid_cookies):
#     ac_api = AC_GATEWAY(_valid_cookies)
#
#     # find last question
#     res = ac_api.get_master_profile_questions()
#     res.assert_response_status(200)
#
#     last_question = res.json_response[-1]
#     new_id = last_question['id'] +1
#     last_answers = last_question['answerList']
#     last_answer_id = last_answers[-1]['id']
#
#     global new_question_payload
#     new_question_payload = { "id": new_id,
#                 "type": "PROFILE",
#                 "category": "LEISURE_AND_ACTIVITIES",
#                 "name": "Sport",
#                 "question": "Do you like to play soccer (delete)?",
#                 "timer": 12,
#                 "questionType": "YES_NO",
#                 "answerList": [{"answer": "Yes", "id": last_answer_id+1, "order": 0}, {"answer": "No", "id": last_answer_id+2, "order": 1}],
#                 "questionLevel": 0,
#                 "metadataAnswered": "VENDOR_ANSWERED"}
#
#     res = ac_api.post_master_profile_question(new_question_payload)
#     res.assert_response_status(200)
#
#     global new_question_id
#     new_question_id = res.json_response['id']
#     assert new_question_id
#     assert res.json_response['type'] == "PROFILE"
#     assert res.json_response['question'] == "Do you like to play soccer (delete)?"
#
#
# @pytest.mark.dependency(depends=["test_create_master_profile_question"])
# def test_get_master_profile_question_by_id(_valid_cookies):
#     ac_api = AC_GATEWAY(_valid_cookies)
#
#     res = ac_api.get_master_profile_question_by_id(new_question_id)
#     res.assert_response_status(200)
#
#     assert res.json_response['id'] == new_question_id
#     assert res.json_response['type'] == new_question_payload['type']
#     assert res.json_response['category'] == new_question_payload['category']
#     assert res.json_response['question'] == new_question_payload['question']
#
#
# @pytest.mark.dependency(depends=["test_create_master_profile_question"])
# def test_update_master_profile_question(_valid_cookies):
#     ac_api = AC_GATEWAY(_valid_cookies)
#
#     res = ac_api.get_master_profile_question_by_id(new_question_id)
#     res.assert_response_status(200)
#
#     update_payload = res.json_response
#     update_payload['question'] = "Do you like to play soccer (updated)?"
#     update_payload['timer'] = 3
#
#     res = ac_api.put_master_profile_question_by_id(new_question_id, update_payload)
#     res.assert_response_status(200)
#     assert res.json_response['id'] == new_question_id
#     assert res.json_response['question'] == "Do you like to play soccer (updated)?"
#     assert res.json_response['timer'] == 3
#
#
# @pytest.mark.dependency(depends=["test_create_master_profile_question"])
# def test_delete_master_profile_question(_valid_cookies):
#     ac_api = AC_GATEWAY(_valid_cookies)
#     new_question_id = 97
#     res = ac_api.get_master_profile_question_by_id(new_question_id)
#     res.assert_response_status(200)
#     assert res.json_response['id'] == new_question_id
#
#     res = ac_api.delete_master_profile_targets(new_question_id)
#     res.assert_response_status(200)
#
#     res = ac_api.get_master_profile_question_by_id(new_question_id)
#     res.assert_response_status(404)
#     assert res.json_response['error'] == 'Not Found'