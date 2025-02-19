
from appen_connect.api_automation.services_config.ac_api import AC_API, create_new_random_project
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_project_process, pytest.mark.regression_ac, pytest.mark.ac_api_v2, pytest.mark.ac_api_v2_bpm, pytest.mark.ac_api]


@pytest.mark.ac_api_uat
@pytest.mark.parametrize('filter_type, expected_status,expected_result',
                         [('', 400, {"code": "MISSING_REQUEST_PARAMETER_ERROR",
                                     "message": "Required String parameter 'type' is not present"}),
                          ('project', 200,  'not_empty_array'),
                          ('main', 200,  [{"name": "Send Email",
                                          "type": "QUALIFICATION_MAIN",
                                           "description": "Sends the specified template email to the user.",
                                           "sequenceFlow": "sendEmailFlow"}])])
def test_get_bpm_steps(ac_api_cookie, filter_type, expected_status, expected_result):
    """
    listQualificationProcessesProcessesSteps
    """
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_bpm_qualification_steps(filter_type)
    res.assert_response_status(expected_status)

    if expected_result == 'not_empty_array':
        assert len(res.json_response) > 0
    elif type(expected_result) is dict:
        assert res.json_response == expected_result
    else:
        assert res.json_response[0]['name'] == expected_result[0]['name']
        assert res.json_response[0]['type'] == expected_result[0]['type']
        assert res.json_response[0]['description'] == expected_result[0]['description']
        assert res.json_response[0]['sequenceFlow'] == expected_result[0]['sequenceFlow']


def test_get_bpm_steps_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_bpm_qualification_steps('main')
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}
 # TODO content verification


def test_get_bpm_step_info(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    all_steps = ac_api.get_bpm_qualification_steps('project')
    all_steps.assert_response_status(200)

    num_steps = len(all_steps.json_response)
    random_step = all_steps.json_response[random.randint(0, num_steps-1)]

    step_id = random_step['id']
    res = ac_api.get_bpm_qualification_step(step_id)
    res.assert_response_status(200)

    assert res.json_response['id'] == step_id
    assert res.json_response['name'] == random_step['name']
    assert res.json_response['type'] == random_step['type']
    assert res.json_response['description'] == random_step['description']
    assert res.json_response['sequenceFlow'] == random_step['sequenceFlow']
    assert len(res.json_response['attributes']) > 0


def test_get_bpm_step_no_cookies(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    all_steps = ac_api.get_bpm_qualification_steps('project')
    all_steps.assert_response_status(200)

    num_steps = len(all_steps.json_response)
    random_step = all_steps.json_response[random.randint(0, num_steps - 1)]
    step_id = random_step['id']

    ac_api = AC_API()
    res = ac_api.get_bpm_qualification_step(step_id)
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


def test_get_bpm_step_not_exist(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)

    res = ac_api.get_bpm_qualification_step(999)
    res.assert_response_status(400)
    assert res.json_response == {"code": "UNSPECIFIED_ERROR",
                                 "message": "Something went wrong, please try again soon"}
# TODO content verification



#  ============== BPM registration steps ========
# ===============================================

@pytest.mark.parametrize('filter_type, expected_status,expected_result',
                         [('', 400, {"code": "MISSING_REQUEST_PARAMETER_ERROR",
                                     "message": "Required String parameter 'type' is not present"}),
                          ('project', 200,  'not_empty_array'),
                          ('main', 200, 'not_empty_array')])
def test_get_bpm_registration_steps(ac_api_cookie, filter_type, expected_status, expected_result):
    """
    listRegistrationProcessesSteps
    """
    ac_api = AC_API(cookies=ac_api_cookie)
    res = ac_api.get_bpm_registration_steps(filter_type)
    res.assert_response_status(expected_status)

    if expected_result == 'not_empty_array':
        assert len(res.json_response) > 0
    else:
        assert res.json_response == expected_result


def test_get_bpm_registration_steps_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_bpm_registration_steps('main')
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}
 # TODO content verification


@pytest.mark.skip(reason="Works not for all steps")
def test_get_bpm_registration_step_info(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    all_steps = ac_api.get_bpm_registration_steps('project')
    all_steps.assert_response_status(200)

    num_steps = len(all_steps.json_response)
    random_step = all_steps.json_response[random.randint(0, num_steps-1)]

    step_id = random_step['id']
    res = ac_api.get_bpm_registration_step(step_id)
    res.assert_response_status(200)

    assert res.json_response['id'] == step_id
    assert res.json_response['name'] == random_step['name']
    assert res.json_response['type'] == random_step['type']
    assert res.json_response['description'] == random_step['description']
    assert res.json_response['sequenceFlow'] == random_step['sequenceFlow']
    assert len(res.json_response['attributes']) > 0


def test_get_bpm_registration_step_no_cookies(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)
    all_steps = ac_api.get_bpm_qualification_steps('project')
    all_steps.assert_response_status(200)

    num_steps = len(all_steps.json_response)
    random_step = all_steps.json_response[random.randint(0, num_steps - 1)]
    step_id = random_step['id']

    ac_api = AC_API()
    res = ac_api.get_bpm_registration_step(step_id)
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


def test_get_bpm_registration_step_not_exist(ac_api_cookie):
    ac_api = AC_API(cookies=ac_api_cookie)

    res = ac_api.get_bpm_registration_step(999)
    res.assert_response_status(400)
    assert res.json_response == {"code": "UNSPECIFIED_ERROR",
                                 "message": "Something went wrong, please try again soon"}
# TODO content verification,
