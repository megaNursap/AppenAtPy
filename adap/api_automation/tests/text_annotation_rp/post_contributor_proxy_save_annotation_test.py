"""
https://appen.atlassian.net/browse/QED-1713
Covers contributor proxy save test annotation api testing
"""
import pytest
from adap.api_automation.utils.data_util import generate_random_string, generate_random_test_data, get_test_data

pytestmark = [pytest.mark.regression_text_annotation, pytest.mark.textannotation_api]

PREDEFINED_JOBS = pytest.data.predefined_data
JOB_ID = PREDEFINED_JOBS['textannotation_api'][pytest.env]['id']
UNIT_ID = PREDEFINED_JOBS['textannotation_api'][pytest.env]['unit_id']

JOB_ID_SS = PREDEFINED_JOBS['textannotation_api'][pytest.env]['job_id_ss']
ANNOTATION_ID1_SS = PREDEFINED_JOBS['textannotation_api'][pytest.env]['annotation_1_ss']
ANNOTATION_ID2_SS = PREDEFINED_JOBS['textannotation_api'][pytest.env]['annotation_2_ss']
BUCKET_ID = PREDEFINED_JOBS['textannotation_api'][pytest.env]['bucket_id']
JWT_TOKEN = get_test_data('test_ui_account', 'jwt_token')

@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_post_save_annotation_contributor_proxy(rp_adap):
    """
    Verify POST /contributor_proxy/v1/text_annotation/save is successful with valid payload (in Text Annotation storage)
    """
    payload = {
       "workerId": "anonymous",
       "unitId": UNIT_ID,
       "jobId": JOB_ID,
       "annotation": {
          "spans": [
             {
                "id": generate_random_string(),
                "tokens": [
                   {
                      "text": "When",
                      "startIdx": 0,
                      "endIdx": 4
                   }
                ],
                "annotated_by": "machine",
                "parent": "",
                "children": [],
                "classnames": []
             }
          ],
          "tokens": [
             {
                "text": "When",
                "startIdx": 0,
                "endIdx": 4
             }
          ],
          "text": "When Sebastian Thrun started working on self-driving cars at Google in 2007",
          "allow_nesting": "false"
       },
       "custom_bucket": "false"
    }

    # rp = RP(JWT_TOKEN)
    res = rp_adap.post_contributor_proxy_save_annotation_text_annotation(payload)
    res.assert_response_status(200)
    assert JOB_ID == res.json_response.get('job_id')
    assert len(res.json_response.get('annotation_id')) > 0
    assert res.json_response.get('custom_bucket') is False


@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
@pytest.mark.parametrize('case_desc, unit_id, job_id, text, expected_status, error_message',
                         [
                          ("unit id is missing", "", "predefine_job", "random_string", 400, 'Server error'),
                          # ("job id is missing", "predefine_unit", "", "random_string", 400, 'Validation errors'),
                          ("text is missing", "predefine_unit", "predefine_job", "", 200, None),
                          ("random unit id and job id", "random_string", "random_int", "random_string", 400, 'Server error')
                         ])
def test_post_save_annotation_contributor_proxy_various_input(case_desc, unit_id, job_id, text, expected_status, error_message, rp_adap):
    """
    Verify POST /contributor_proxy/v1/text_annotation/save returns appropriate results with different payloads
    """
    if unit_id == "predefine_unit":
        unit_id = UNIT_ID
    if job_id == "predefine_job":
        job_id = JOB_ID

    test_data = generate_random_test_data({'unit_id': unit_id,
                                           'text': text,
                                           'job_id': job_id
                                           })

    payload = {
       "workerId": "anonymous",
       "unitId": test_data['unit_id'],
       "jobId": test_data['job_id'],
       "annotation": {
          "spans": [
             {
                "id": generate_random_string(),
                "tokens": [
                   {
                      "text": "When",
                      "startIdx": 0,
                      "endIdx": 4
                   }
                ],
                "annotated_by": "machine",
                "parent": "",
                "children": [],
                "classnames": []
             }
          ],
          "tokens": [
             {
                "text": "When",
                "startIdx": 0,
                "endIdx": 4
             }
          ],
          "text": test_data['text'],
          "allow_nesting": "false"
       },
       "custom_bucket": "false"
    }

    # rp = RP(JWT_TOKEN)
    res = rp_adap.post_contributor_proxy_save_annotation_text_annotation(payload)
    res.assert_response_status(expected_status)
    if error_message is not None:
        assert error_message in res.json_response.get('message')


@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_post_save_annotation_contributor_proxy_ss(rp_adap):
    """
    Verify POST /contributor_proxy/v1/text_annotation/save is successful with valid payload (in Super Saver storage)
    """
    payload = {
       "workerId": "anonymous",
       "unitId": UNIT_ID,
       "jobId": JOB_ID_SS,
       "payload": {
          "spans": [
             {
                "id": generate_random_string(),
                "tokens": [
                   {
                      "text": "When",
                      "startIdx": 0,
                      "endIdx": 4
                   }
                ],
                "annotated_by": "machine",
                "parent": "",
                "children": [],
                "classnames": []
             }
          ],
          "tokens": [
             {
                "text": "When",
                "startIdx": 0,
                "endIdx": 4
             }
          ],
          "text": "When Sebastian Thrun started working on self-driving cars at Google in 2007",
          "allow_nesting": "false"
       },
        "format": "json"
    }

    # rp = RP(JWT_TOKEN)
    res = rp_adap.post_contributor_proxy_save_annotation_super_saver(payload)
    res.assert_response_status(200)
    assert JOB_ID_SS == res.json_response.get('job_id')
    assert len(res.json_response.get('annotation_id')) > 0
    assert res.json_response.get('bucket_id') == BUCKET_ID