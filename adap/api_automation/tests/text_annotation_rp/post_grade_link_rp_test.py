"""
https://appen.atlassian.net/browse/QED-1713
Covers text annotation get grade link request proxy test
"""
import pytest
import requests
from adap.api_automation.utils.data_util import generate_random_test_data
from adap.api_automation.utils.data_util import get_test_data

pytestmark = [pytest.mark.regression_text_annotation, pytest.mark.textannotation_api]

PREDEFINED_JOBS = pytest.data.predefined_data
JOB_ID = PREDEFINED_JOBS['textannotation_api'][pytest.env]['id']
ANNOTATION_ID = PREDEFINED_JOBS['textannotation_api'][pytest.env]['annotation_1']

JOB_ID_SS = PREDEFINED_JOBS['textannotation_api'][pytest.env]['job_id_ss']
BUCKET_ID = PREDEFINED_JOBS['textannotation_api'][pytest.env]['bucket_id']
ANNOTATION_ID_SS = PREDEFINED_JOBS['textannotation_api'][pytest.env]['annotation_1_ss']


@pytest.mark.uat_api
#@allure.issue("https://appen.atlassian.net/browse/QED-3135", "BUG  on Sandbox QED-3135")
# @allure.issue("https://appen.atlassian.net/browse/QED-3150","BUG: Integration QED-3150")
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_post_grade_link_rp(rp_adap):
    """
    Verify POST /text_annotation/grade_link is successful with valid parameters
    """
    # jwt_token = get_test_data('test_ui_account', 'jwt_token')
    # refs_token = get_test_data('test_ui_account', 'refs_token')
    storage_ref_token = get_test_data('test_ui_account', 'x_storage_refs_token')
    payload = {
         "job_id": JOB_ID,
         "annotation_id": ANNOTATION_ID
     }

    # rp = RP(cookies=valid_cookies_adap, jwt_token=jwt_token, refs_token=refs_token)
    res = rp_adap.post_grade_link_text_annotation(payload, storage_ref_token)
    res.assert_response_status(200)
    url = res.json_response.get('url')

    assert str(JOB_ID) in url
    assert "f8-text-annotation" in url
    assert ANNOTATION_ID in url
    url_res = requests.get(url)
    assert url_res.status_code == 200
    assert 'status' in url_res.json()
    assert 'correct_span_ratio' in url_res.json()
    assert 'threshold' in url_res.json()
    assert 'failed_spans' in url_res.json()
    assert 'correct_spans' in url_res.json()

@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only QA, Integration and Sandbox has data configured")
# @allure.issue("https://appen.atlassian.net/browse/QED-3150","BUG on Integration QED-3150")
# @allure.issue("https://appen.atlassian.net/browse/QED-3135", "BUG  on Sandbox QED-3135")
@pytest.mark.parametrize('case_desc, job_id, annotation_id, expected_status',
                         [("missing job id", "", "predefine_annotation", 404),
                          ("missing annotation id", "predefine_job", "", 404),
                          ("random job id and annotation id", "random_int", "random_string", 404)
                          ])
def test_post_grade_link_invalid_input(case_desc, job_id, annotation_id, expected_status, rp_adap):
    """
    Verify POST /text_annotation/grade_link fails with invalid parameters
    """
    if job_id == "predefine_job":
        job_id = JOB_ID
    if annotation_id == "predefine_annotation":
        annotation_id = ANNOTATION_ID

    test_data = generate_random_test_data({'annotation_id': annotation_id,
                                           'job_id': job_id
                                           })

    payload = {
        "job_id": test_data['job_id'],
        "annotation_id": test_data['annotation_id']
    }

    storage_ref_token = get_test_data('test_ui_account', 'x_storage_refs_token')

    res = rp_adap.post_grade_link_text_annotation(payload, storage_ref_token)
    res.assert_response_status(expected_status)

