"""
https://appen.atlassian.net/browse/QED-1713
Covers text annotation post accuracy request proxy test
"""
import allure
import requests
import pytest
import random
from adap.api_automation.utils.data_util import generate_random_test_data
from adap.api_automation.utils.data_util import get_test_data
from adap.api_automation.utils.helpers import hashed_unit_id

pytestmark = [pytest.mark.regression_text_annotation, pytest.mark.textannotation_api]

TEST_DATA = pytest.data.predefined_data['data_validation_api'].get(pytest.env)
PREDEFINED_JOBS = pytest.data.predefined_data
TEAM_ID = TEST_DATA['team_id']
JOB_ID = PREDEFINED_JOBS['textannotation_api'].get(pytest.env, {}).get('id', "")
UNIT_ID = PREDEFINED_JOBS['textannotation_api'].get(pytest.env, {}).get('unit_id', "")
UNIT_ID_EDIT = PREDEFINED_JOBS['textannotation_api'].get(pytest.env, {}).get('unit_id_edit',"")
ANNOTATION_ID1 = PREDEFINED_JOBS['textannotation_api'].get(pytest.env, {}).get('annotation_1', "")
ANNOTATION_ID2 = PREDEFINED_JOBS['textannotation_api'].get(pytest.env, {}).get('annotation_2', "")


@pytest.mark.smoke
@pytest.mark.uat_api
#@allure.issue("https://appen.atlassian.net/browse/QED-3135", "BUG  on Sandbox QED-3135")
#@allure.issue("https://appen.atlassian.net/browse/QED-3150","BUG:Integration QED-3150")
@allure.issue("https://appen.atlassian.net/browse/DO-11210", "BUG: Integration DO-11210")
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_post_accuracy_rp(rp_adap):
    """
    Verify POST /text_annotation/accuracy is successful with valid payload
    """
    unit_id_hash = hashed_unit_id(str(UNIT_ID_EDIT))
    payload = {
        "unit_id": UNIT_ID,
        "team_id": TEAM_ID,
        "job_id": JOB_ID,
        "judgments": [
            {
                "id": random.randint(1, 100000),
                "trust": 0.86,
                "data": {
                    "job_id": JOB_ID,
                    "annotation_id": ANNOTATION_ID1,
                    "custom_bucket": False
                }
            }
        ],
        "correct_response": {
            "job_id": JOB_ID,
            "annotation_id": ANNOTATION_ID2
        },
        "expiration_time": random.randint(1, 3000)
    }

    storage_ref_token = get_test_data('test_ui_account', 'x_storage_refs_token')

    # rp = RP(cookies=valid_cookies_adap, jwt_token=jwt_token, refs_token=refs_token)
    res = rp_adap.post_accuracy_details_text_annotation(payload, storage_ref_token)

    res.assert_response_status(200)
    assert 'accuracy_details_url' in res.json_response
    assert 'error_judgments' in res.json_response
    assert len(res.json_response.get('error_judgments')) == 0
    url = res.json_response.get('accuracy_details_url')
    assert 'accuracy_details' in url
    assert unit_id_hash in url
    payload = {
        "ref": {
            "type": "text_annotation/agg_report",
            "valueRef": "jobs/%a/%s/accuracy_details" % (JOB_ID, unit_id_hash)
        }
    }
    res = rp_adap.post_refs_url(payload, storage_ref_token)
    assert res.status_code == 200
    url = res.json_response.get('url')
    url_res = requests.get(url)
    assert 'avg_pass_rate' in url_res.json()
    assert 'spans' in url_res.json()
    # this is not on integration
    # assert len(url_res.json().get('spans')[0].get('classnames')) > 0
    # assert len(url_res.json().get('spans')[0].get('tokens')) > 0
    # assert url_res.json().get('spans')[0].get('pass_rate') >= 0


@pytest.mark.parametrize('case_desc, unit_id, judgment_id, job_id, annotation_id1, '
                         'annotation_id2, expiration_time, expected_status, error_message',
                         [
                           ("missing unit id", "", "random_int", "predefine_job", "predefine_annotation", "predefine_annotation",  "random_int", 400, "Validation errors"),
                           ("missing judgment id", "predefine_unit", "", "predefine_job", "predefine_annotation", "predefine_annotation",  "random_int", 400, "Validation errors"),
                           #("missing judgment annotation id", "predefine_unit", "random_int", "predefine_job", "", "predefine_annotation", "random_int", 500, "Internal Server Error"),
                           # ("missing job id", "predefine_unit", "random_int", "", "random_string", "random_string",  "random_int", 400, "Validation errors"),
                           ("invalid random job id", "predefine_unit", "random_int", "random_int", "", "random_string", "random_int", 400, "Validation errors"),
                           ("missing response annotation id", "predefine_unit", "random_int", "random_int", "random_string", "",  "random_int", 400, "Validation errors"),
                           ("missing response annotation id and expiration time, random job id", "predefine_unit", "random_int", "random_int", "random_string", "",  "", 400, "Validation errors"),
                           ("correct judgment, incorrect response annotation id", "predefine_unit", "random_int", "predefine_job", "predefine_annotation", "random_string",  "random_int", 400, "Validation errors"),
                           ("incorrect annotation id in judgments, correct response", "predefine_unit", "random_int", "predefine_job", "random_string", "predefine_annotation",  "random_int", 400, "Validation errors"),
                          ])
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
# @allure.issue("https://appen.atlassian.net/browse/QED-3135", "BUG  on Sandbox QED-3135")
def test_post_accuracy_rp_invalid_input(rp_adap, case_desc, unit_id, judgment_id, job_id, annotation_id1, annotation_id2,
                                        expiration_time, expected_status, error_message):
    """
    Verify POST /text_annotation/accuracy fails with invalid payload
    """
    if unit_id == "predefine_unit":
        unit_id = UNIT_ID
    if job_id == "predefine_job":
        job_id = JOB_ID
    if annotation_id1 == "predefine_annotation":
        annotation_id1 = ANNOTATION_ID1
    if annotation_id2 == "predefine_annotation":
        annotation_id2 = ANNOTATION_ID2

    test_data = generate_random_test_data({'unit_id': unit_id,
                                           'judgment_id': judgment_id,
                                           'annotation_id1': annotation_id1,
                                           'annotation_id2': annotation_id2,
                                           'job_id': job_id,
                                           'expiration_time': expiration_time})
    payload = {
        "unit_id": test_data['unit_id'],
        "team_id": TEAM_ID,
        "job_id": job_id,
        "judgments": [
            {
                "id": test_data['judgment_id'],
                "trust": 0.86,
                "job_id": test_data['job_id'],
                "annotation_id": test_data['annotation_id1']
            }
        ],
        "correct_response": {
            "job_id": test_data['job_id'],
            "annotation_id": test_data['annotation_id2']
        },
        "expiration_time": test_data['expiration_time']
     }

    # jwt_token = get_test_data('test_ui_account', 'jwt_token')
    # refs_token = get_test_data('test_ui_account', 'refs_token')
    storage_ref_token = get_test_data('test_ui_account', 'x_storage_refs_token')

    # rp = RP(cookies=valid_cookies_adap, jwt_token=jwt_token, refs_token=refs_token)
    res = rp_adap.post_accuracy_details_text_annotation(payload, storage_ref_token)
    res.assert_response_status(expected_status)

    res.assert_response_status(expected_status)
    if error_message == "empty accuracy details url":
        assert res.json_response.get('accuracy_details_url') == ''
    elif expected_status == 422:
        assert error_message in res.json_response.get('errors')[0]
    else:
        assert error_message in res.json_response.get('message')