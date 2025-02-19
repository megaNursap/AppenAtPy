"""
https://appen.atlassian.net/browse/QED-1713
Covers text annotation post predict request proxy test
"""

import pytest
from adap.api_automation.utils.data_util import generate_random_string, generate_random_test_data, get_test_data


pytestmark = [pytest.mark.regression_text_annotation, pytest.mark.textannotation_api]

PREDEFINED_JOBS = pytest.data.predefined_data
JOB_ID = PREDEFINED_JOBS['textannotation_api'][pytest.env]['id']
UNIT_ID = PREDEFINED_JOBS['textannotation_api'][pytest.env]['unit_id']
TEXT = generate_random_string()


@pytest.mark.smoke
@pytest.mark.uat_api
# @allure.issue("https://appen.atlassian.net/browse/QED-3135", "BUG  on Sandbox QED-3135")
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_post_predict_rp(rp_adap):
    """
    Verify POST /ml/pretrained-spacy-tokenizer/predict is successful with valid payload
    """
    storage_ref_token = get_test_data('test_ui_account', 'x_storage_refs_token')
    # rp = RP(cookies=valid_cookies_adap)
    payload = {
       "text": TEXT,
       "lang": "en",
       "job_id": str(JOB_ID),
       "contributor_id": "anonymous",
       "unit_id": UNIT_ID
    }
    res = rp_adap.post_predict_text_annotation(payload, storage_ref_token)
    res.assert_response_status(200)
    assert len(res.json_response.get('unit_id')) > 0
    assert 'anonymous' == res.json_response.get('contributor_id')
    assert str(JOB_ID) == res.json_response.get('job_id')
    assert TEXT == res.json_response.get('text')
    assert 'en' == res.json_response.get('lang')
    assert TEXT == res.json_response.get('tokens')[0]


# seems all fields are not mandatory
# @allure.issue("https://appen.atlassian.net/browse/QED-3135", "BUG  on Sandbox QED-3135")
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
@pytest.mark.parametrize('case_desc, text, job_id, contributor_id, unit_id, expected_status',
                         [
                          ("param text is missing", "", "predefine_job", "anonymous", "predefine_unit", 200),
                          ("non mandatory param job id, contributor id and unit id are missing", "random_string", "", "", "", 200),
                          ("random job id and unit id", "random_string", "random_string", "anonymous", "random_string", 500),
                         ])
def test_post_predict_rp_various_input(case_desc, text, job_id, contributor_id, unit_id, expected_status, rp_adap):
    """
    Verify POST /ml/pretrained-spacy-tokenizer/predict returns appropriate results with different payloads
    """
    if unit_id == "predefine_unit":
        unit_id = UNIT_ID
    if job_id == "predefine_job":
        job_id = JOB_ID

    test_data = generate_random_test_data({'unit_id': unit_id,
                                           'text': text,
                                           'job_id': job_id
                                           })

    storage_ref_token = get_test_data('test_ui_account', 'x_storage_refs_token')

    # rp = RP(cookies=valid_cookies_adap)
    payload = {
        "text": test_data['text'],
        "lang": "en",
        "job_id": str(test_data['job_id']),
        "contributor_id": contributor_id,
        "unit_id": test_data['unit_id']
    }
    res = rp_adap.post_predict_text_annotation(payload, storage_ref_token)
    res.assert_response_status(expected_status)