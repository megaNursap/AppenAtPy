"""
EPIC:https://appen.atlassian.net/browse/QED-1334
JIRA:https://appen.atlassian.net/browse/QED-1338
SWAGGER:https://app.swaggerhub.com/apis/CrowdFlower/text-annotation/1.0.0#/Annotations/post_annotations
"""
import random
from adap.api_automation.services_config.textannotation import *
from adap.api_automation.utils.data_util import generate_random_string, generate_random_test_data
from adap.api_automation.utils.helpers import hashed_unit_id

pytestmark = [pytest.mark.regression_text_annotation, pytest.mark.textannotation_api]

TEST_DATA = pytest.data.predefined_data['data_validation_api'].get(pytest.env)
PREDEFINED_JOBS = pytest.data.predefined_data
TEAM_ID = TEST_DATA['team_id']
JOB_ID = PREDEFINED_JOBS['textannotation_api'][pytest.env]['id']
ANNOTATION_ID1 = PREDEFINED_JOBS['textannotation_api'][pytest.env]['annotation_report1']
ANNOTATION_ID2 = PREDEFINED_JOBS['textannotation_api'][pytest.env]['annotation_report2']

JOB_ID_SS = PREDEFINED_JOBS['textannotation_api'][pytest.env]['job_id_ss']
ANNOTATION_ID1_SS = PREDEFINED_JOBS['textannotation_api'][pytest.env]['annotation_1_ss']
ANNOTATION_ID2_SS = PREDEFINED_JOBS['textannotation_api'][pytest.env]['annotation_2_ss']
BUCKET_ID = PREDEFINED_JOBS['textannotation_api'][pytest.env]['bucket_id']

@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_aggregated_report_ta_storage():
    """
    Verify POST /aggregations/agg is successful when valid payload is passed (using judgments in Text Annotation storage)
    """
    unit_id = random.randint(1, 3000)
    payload = {
     "unit_id": unit_id,
     "team_id": TEAM_ID,
     "job_id": JOB_ID,
     "data": {
        "text": generate_random_string()
      },
     "judgments_count": 2,
     "judgments": [
      {
         "id": random.randint(1, 3000),
         "trust": 0.86,
         "data":{
            "job_id": JOB_ID,
            "annotation_id": ANNOTATION_ID1,
            "custom_bucket": False
         }
      },
      {
         "id": random.randint(1, 3000),
         "trust": 0.86,
         "data": {
            "job_id": JOB_ID,
            "annotation_id": ANNOTATION_ID2,
            "custom_bucket": False
         }
      }
     ],
     "confidence_threshold": 0.68
    }
    res = TextAnnotation().generate_aggregated_report(payload)
    res.assert_response_status(200)
    assert str(JOB_ID) in res.json_response.get('agg_report_url')
    assert hashed_unit_id(str(unit_id)) in res.json_response.get('agg_report_url')
    assert 'agg_report' in res.json_response.get('agg_report_url')
    assert 'valueRef' in res.json_response.get('agg_report_url')
    assert 'text_annotation/agg_report' in res.json_response.get('agg_report_url')
    assert res.json_response.get('confidence') is not None
    assert 'error_judgments' in res.json_response
    assert len(res.json_response.get('error_judgments')) == 0


# TODO: Check the response code when empty string is provided for annotation_id param. 500 is not the expected code, hence disabling
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.parametrize('case_desc, unit_id, text, judgment_id1, job_id, annotation_id1,'
                         'judgment_id2, annotation_id2, expected_status, error_message, error_judgments',
                         [("mandatory param unit id is missing", "", "random_string", "random_int", "predefine_job", "predefine_annotation", "random_int", "predefine_annotation", 400, "Bad Request", None),
                          ("non mandatory param text in data is missing", "random_int", "", "random_int", "predefine_job", "predefine_annotation", "random_int", "predefine_annotation", 200, None, None),
                          ("judgment id is missing", "random_int", "random_string", "", "predefine_job", "predefine_annotation", "", "predefine_annotation", 200, None, None),
                          ("job id is missing", "random_int", "random_string", "random_int", "", "predefine_annotation", "random_int", "predefine_annotation", 200, None, "Contributor response not found in storage"),
                          #("annotation id is missing", "random_int", "random_string", "random_int", "predefine_job", "", "random_int", "", 500, "Internal Server Error", None),
                          ("random job id and random annotation id", "random_int", "random_string", "random_int", "random_int", "random_string", "random_int", "random_string", 200, None, "Contributor response not found in storage")
                          ])
def test_aggregated_report_various_input(case_desc, unit_id, text, judgment_id1, job_id, annotation_id1,
                                         judgment_id2, annotation_id2, expected_status, error_message, error_judgments):
    """
    Verify POST /aggregations/agg fails when invalid payload is passed
    """
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
        "job_id": JOB_ID,
        "data": {
            "text": test_data['text']
        },
        "judgments_count": 2,
        "judgments": [
            {
                "id": test_data['judgment_id1'],
                "trust": 0.86,
                "data": {
                    "job_id": test_data['job_id'],
                    "annotation_id": test_data['annotation_id1'],
                    "custom_bucket": False
                }
            },
            {
                "id": test_data['judgment_id2'],
                "trust": 0.86,
                "data": {
                    "job_id": test_data['job_id'],
                    "annotation_id": test_data['annotation_id2'],
                    "custom_bucket": False
                }
            }
        ],
        "confidence_threshold": 0.68
    }
    res = TextAnnotation().generate_aggregated_report(payload)
    res.assert_response_status(expected_status)
    if error_message is not None:
        assert error_message in res.json_response.get('error')
    if error_judgments is not None:
        assert error_judgments == res.json_response.get('error_judgments')[0].get('reason')

@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_aggregated_report_ss_storage():
    """
    Verify fetching aggregated report from super-saver storage (ie POST /aggregations/agg endpoint)
    """
    unit_id = random.randint(1, 3000)
    payload = {
     "unit_id": unit_id,
     "team_id": TEAM_ID,
     "job_id": JOB_ID,
     "data": {
        "text": generate_random_string()
      },
     "judgments_count": 2,
     "judgments": [
      {
         "id": random.randint(1, 3000),
         "trust": 0.86,
         "data": {
            "job_id": JOB_ID_SS,
            "annotation_id": ANNOTATION_ID1_SS,
            "bucket_id": BUCKET_ID
         }
      },
      {
         "id": random.randint(1, 3000),
         "trust": 0.86,
         "data": {
            "job_id": JOB_ID_SS,
            "annotation_id": ANNOTATION_ID2_SS,
            "bucket_id": BUCKET_ID
         }
      }
     ],
     "confidence_threshold": 0.68
    }
    res = TextAnnotation().generate_aggregated_report(payload)
    res.assert_response_status(200)
    assert str(JOB_ID) in res.json_response.get('agg_report_url')
    assert hashed_unit_id(str(unit_id)) in res.json_response.get('agg_report_url')
    assert 'agg_report' in res.json_response.get('agg_report_url')
    assert 'valueRef' in res.json_response.get('agg_report_url')
    assert 'text_annotation/agg_report' in res.json_response.get('agg_report_url')
    assert res.json_response.get('confidence') is not None
    assert 'error_judgments' in res.json_response
    assert len(res.json_response.get('error_judgments')) == 0