"""
https://appen.atlassian.net/browse/QED-1713
Covers text annotation post aggregation request proxy test
"""
import pytest
import requests
import random
from adap.api_automation.utils.data_util import generate_random_string, generate_random_test_data, get_test_data
import logging

from adap.api_automation.utils.helpers import hashed_unit_id

LOGGER = logging.getLogger(__name__)

pytestmark = [pytest.mark.regression_text_annotation, pytest.mark.textannotation_api]

PREDEFINED_JOBS = pytest.data.predefined_data
TEST_DATA = pytest.data.predefined_data['data_validation_api'].get(pytest.env)
TEAM_ID = TEST_DATA['team_id']
JOB_ID = PREDEFINED_JOBS['textannotation_api'].get(pytest.env, {}).get('id','')
UNIT_ID = PREDEFINED_JOBS['textannotation_api'].get(pytest.env, {}).get('unit_id', "")
UNIT_ID_EDIT = PREDEFINED_JOBS['textannotation_api'].get(pytest.env, {}).get('unit_id_edit', "")
ANNOTATION_ID1 = PREDEFINED_JOBS['textannotation_api'].get(pytest.env, {}).get('annotation_1', "")
ANNOTATION_ID2 = PREDEFINED_JOBS['textannotation_api'].get(pytest.env, {}).get('annotation_2', "")


@pytest.mark.smoke
@pytest.mark.uat_api
#@allure.issue("https://appen.atlassian.net/browse/QED-3135", "BUG  on Sandbox QED-3135")
#@allure.issue("https://appen.atlassian.net/browse/QED-3150","BUG:Integration QED-3150" )
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_post_aggregation_rp(rp_adap):
    """
    Verify POST /text_annotation/aggregation is successful with valid payload
    """
    unit_id_hash = hashed_unit_id(str(UNIT_ID_EDIT))
    payload = {
        "unit_id": UNIT_ID,
        "team_id": TEAM_ID,
        "job_id": JOB_ID,
        "text": generate_random_string(),
        "judgments_count": 2,
        "judgments": [
            {
                "data": {
                    "job_id": JOB_ID,
                    "annotation_id": ANNOTATION_ID1
                },
                "id": random.randint(1, 3000),
                "trust": 0.86
            },
            {
                "data": {
                    "job_id": JOB_ID,
                    "annotation_id": ANNOTATION_ID2
                },
                "id": random.randint(1, 3000),
                "trust": 0.86
           }
        ],
        "confidence_threshold": 0.68
    }

    # jwt_token = get_test_data('test_ui_account', 'jwt_token')
    # refs_token = get_test_data('test_ui_account', 'refs_token')
    storage_ref_token = get_test_data('test_ui_account', 'x_storage_refs_token')

    # rp = RP(cookies=valid_cookies_adap, jwt_token=jwt_token, refs_token=refs_token)
    res = rp_adap.post_aggregation_report_text_annotation(payload, storage_ref_token)
    res.assert_response_status(200)
    assert res.json_response.get('confidence') >= 0
    assert 'error_judgments' in res.json_response
    assert len(res.json_response.get('error_judgments')) == 0

    url = res.json_response.get('agg_report_url')
    assert 'valueRef' in url
    assert 'text_annotation/agg_report' in url
    assert 'text_annotation/agg_report' in url
    assert unit_id_hash in url
    assert str(JOB_ID) in url
    payload = {
        "ref": {
            "type": "text_annotation/agg_report",
            "valueRef": "jobs/%a/%s/agg_report" % (JOB_ID, unit_id_hash)
        }
    }
    res = rp_adap.post_refs_url(payload, storage_ref_token)
    url = res.json_response.get('url')
    url_res = requests.get(url)
    assert res.status_code == 200
    assert 'judgments_count' in url_res.json()
    assert 'spans' in url_res.json()
    assert url_res.json().get('judgments_count') == 2
    assert len(url_res.json().get('spans')[0].get('tokens')[0].get('text')) > 0
    # this is not on integration
    # assert len(url_res.json().get('spans')[0].get('classnames')[0]) > 0
    # assert len(url_res.json().get('spans')[0].get('id')) > 0
    # assert url_res.json().get('spans')[0].get('confidence') >= 0
    assert 'annotated_by' in url_res.json().get('spans')[0]
    assert 'parent' in url_res.json().get('spans')[0]
    assert 'children' in url_res.json().get('spans')[0]
    assert len(url_res.json().get('tokens')[0].get('text')) > 0
    assert 'startIdx' in url_res.json().get('tokens')[0]
    assert 'endIdx' in url_res.json().get('tokens')[0]


@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only Sandbox & Integraiton has data configured")
#@allure.issue("https://appen.atlassian.net/browse/QED-3135", "BUG  on Sandbox QED-3135")
#@allure.issue("https://appen.atlassian.net/browse/QED-3150","BUG:Integration QED-3150")
@pytest.mark.parametrize('case_desc, unit_id, text, judgment_id1, job_id, annotation_id1,'
                         'judgment_id2, annotation_id2, expected_status, error_message, error_judgments',
                         [
                          ("mandatory param unit id is missing", "", "random_string", "random_int", "predefine_job", "predefine_annotation", "random_int", "predefine_annotation", 400, "Server error", None),
                          ("non mandatory param text in data is missing", "predefine_unit", "", "random_int", "predefine_job", "predefine_annotation", "random_int", "predefine_annotation", 400, None, None),
                          ("judgment id is missing", "predefine_unit", "random_string", "", "predefine_job", "predefine_annotation", "", "predefine_annotation", 400, "Validation errors", None),
                          # ("job id is missing", "predefine_unit", "random_string", "random_int", "", "predefine_annotation", "random_int", "predefine_annotation", 400, "Validation errors", None),
                          # ("annotation id is missing", "predefine_unit", "random_string", "random_int", "predefine_job", "", "random_int", "", 500, "Internal Server Error", None),
                          ("random job id and random annotation id", "predefine_unit", "random_string", "random_int", "random_int", "random_string", "random_int", "random_string", 400, None, None)
                          ])
def test_post_aggregation_rp_invalid_input(rp_adap, case_desc, unit_id, text, judgment_id1, job_id, annotation_id1,
                                          judgment_id2, annotation_id2, expected_status, error_message, error_judgments):
    """
    Verify POST /text_annotation/aggregation fail with invalid payload
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
                                           'text': text,
                                           'judgment_id1': judgment_id1,
                                           'judgment_id2': judgment_id2,
                                           'annotation_id1': annotation_id1,
                                           'annotation_id2': annotation_id2,
                                           'job_id': job_id
                                           })
    payload = {
        "unit_id": test_data['unit_id'],
        "team_id": TEAM_ID,
        "job_id": job_id,
        "text": test_data['text'],
        "judgments_count": 2,
        "judgments": [
            {
                "id": test_data['judgment_id1'],
                "trust": 0.86,
                "job_id": test_data['job_id'],
                "annotation_id": test_data['annotation_id1']

            },
            {
                "id": test_data['judgment_id2'],
                "trust": 0.86,
                "job_id": test_data['job_id'],
                "annotation_id": test_data['annotation_id2']
            }
        ],
        "confidence_threshold": 0.68
    }

    jwt_token = get_test_data('test_ui_account', 'jwt_token')
    refs_token = get_test_data('test_ui_account', 'refs_token')
    storage_ref_token = get_test_data('test_ui_account', 'x_storage_refs_token')

    # rp = RP(cookies=valid_cookies_adap, jwt_token=jwt_token, refs_token=refs_token)
    res = rp_adap.post_aggregation_report_text_annotation(payload, storage_ref_token)
    res.assert_response_status(expected_status)
    if error_message is not None:
        assert res.json_response.get('message'), error_message
    if error_judgments is not None:
        assert error_judgments == res.json_response.get('error_judgments')[0].get('reason')