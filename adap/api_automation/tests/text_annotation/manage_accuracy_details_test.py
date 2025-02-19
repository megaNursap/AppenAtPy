"""
EPIC:https://appen.atlassian.net/browse/QED-1334
JIRA:https://appen.atlassian.net/browse/QED-1337
SWAGGER:https://app.swaggerhub.com/apis/CrowdFlower/text-annotation/1.0.0#/Annotations/post_annotations
"""
import pytest
import random
from adap.api_automation.services_config.textannotation import *
from adap.api_automation.utils.data_util import generate_random_test_data
from adap.api_automation.utils.helpers import hashed_unit_id

pytestmark = [pytest.mark.regression_text_annotation, pytest.mark.textannotation_api]

TEST_DATA = pytest.data.predefined_data['data_validation_api'].get(pytest.env, {})
PREDEFINED_JOBS = pytest.data.predefined_data
TEAM_ID = TEST_DATA.get('team_id', "")
JOB_ID = PREDEFINED_JOBS['textannotation_api'].get(pytest.env, {}).get('id',"")
ANNOTATION_ID1 = PREDEFINED_JOBS['textannotation_api'].get(pytest.env,{}).get('annotation_1', "")
ANNOTATION_ID2 = PREDEFINED_JOBS['textannotation_api'].get(pytest.env, {}).get('annotation_2',"")

JOB_ID_SS = PREDEFINED_JOBS['textannotation_api'].get(pytest.env, {}).get('job_id_ss', "")
ANNOTATION_ID1_SS = PREDEFINED_JOBS['textannotation_api'].get(pytest.env, {}).get('annotation_1_ss', "")
ANNOTATION_ID2_SS = PREDEFINED_JOBS['textannotation_api'].get(pytest.env, {}).get('annotation_2_ss', "")
BUCKET_ID = PREDEFINED_JOBS['textannotation_api'].get(pytest.env, {}).get('bucket_id', "")


@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_accuracy_details_with_one_judgment_ta_storage():
    """
    Verify POST /accuracy_details endpoint is successful with one judgment (in Text Annotation storage)
    """
    unit_id = random.randint(1, 100000)
    payload = {
      "unit_id": unit_id,
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
               "annotation_id": ANNOTATION_ID2,
               "custom_bucket": False
         },
      "expiration_time": random.randint(1, 3000)
     }
    res = TextAnnotation().post_accuracy_details(payload)
    res.assert_response_status(200)
    accuracy_details = res.json_response.get('accuracy_details_url')
    assert str(JOB_ID) in accuracy_details
    assert hashed_unit_id(str(unit_id)) in accuracy_details


@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_accuracy_details_with_multiple_judgments():
    """
    Verify POST /accuracy_details endpoint is successful with multiple judgments
    """
    unit_id = random.randint(1, 100000)
    payload = {
      "unit_id": unit_id,
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
             },
            {
              "id": random.randint(1, 100000),
              "trust": 0.86,
              "data": {
                  "job_id": JOB_ID,
                  "annotation_id": ANNOTATION_ID2,
                  "custom_bucket": False
              }
            }
           ],
      "correct_response": {
               "job_id": JOB_ID,
               "annotation_id": ANNOTATION_ID2,
               "custom_bucket": False
         },
      "expiration_time": random.randint(1, 3000)
     }
    res = TextAnnotation().post_accuracy_details(payload)
    res.assert_response_status(200)
    accuracy_details = res.json_response.get('accuracy_details_url')
    assert str(JOB_ID) in accuracy_details
    assert 'error_judgments' in res.json_response
    assert hashed_unit_id(str(unit_id)) in accuracy_details


@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_accuracy_details_empty_judgments():
    """
    Verify POST /accuracy_details endpoint is successful with empty judgments
    """
    unit_id = random.randint(1, 100000)
    payload = {
      "unit_id": unit_id,
      "team_id": TEAM_ID,
      "job_id": JOB_ID,
      "judgments": [
           ],
      "correct_response": {
               "job_id": JOB_ID,
               "annotation_id": ANNOTATION_ID2,
               "custom_bucket": False
         },
      "expiration_time": random.randint(1, 3000)
     }
    res = TextAnnotation().post_accuracy_details(payload)
    res.assert_response_status(400)
    assert 'Bad Request' == res.json_response.get('error')


# TODO: Check the response code when empty string is provided for annotation_id param. 500 is not the expected code, hence disabling
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only QA and Sandbox has data configured")
@pytest.mark.parametrize('case_desc, unit_id, judgment_id, job_id, annotation_id1, '
                         'annotation_id2, expiration_time, expected_status, error_message',
                         [("missing unit id", "", "random_int", "predefine_job", "predefine_annotation", "predefine_annotation",  "random_int", 400, None),
                          ("missing judgment id", "random_int", "", "predefine_job", "predefine_annotation", "predefine_annotation",  "random_int", 200, None),
                          #("missing judgment annotation id", "random_int", "random_int", "predefine_job", "", "predefine_annotation", "random_int", 500, None),
                          ("missing job id", "random_int", "random_int", "", "random_string", "random_string",  "random_int", 422, "Gold response not found in storage"),
                          ("invalid random job id", "random_int", "random_int", "random_int", "", "random_string",  "random_int", 422, "Gold response not found in storage"),
                          ("missing response annotation id", "random_int", "random_int", "random_int", "random_string", "",  "random_int", 422, "Gold response not found in storage"),
                          ("missing response annotation id and expiration time, random job id", "random_int", "random_int", "random_int", "random_string", "",  "", 422, "Gold response not found in storage"),
                          ("correct judgment, incorrect response annotation id", "random_int", "random_int", "predefine_job", "predefine_annotation", "random_string",  "random_int", 422, "Gold response not found in storage"),
                          ("incorrect annotation id in judgments, correct response", "random_int", "random_int", "predefine_job", "random_string", "predefine_annotation",  "random_int", 200, "empty accuracy details url"),
                          ])
def test_accuracy_details_various_input(case_desc, unit_id, judgment_id, job_id, annotation_id1, annotation_id2,
                                        expiration_time, expected_status, error_message):
    """
    Verify POST /accuracy_details endpoint fails, when invalid payload is passed
    """
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
        "job_id": JOB_ID,
        "judgments": [
            {
                "id": test_data['judgment_id'],
                "trust": 0.86,
                "data": {
                    "job_id": test_data['job_id'],
                    "annotation_id": test_data['annotation_id1'],
                    "custom_bucket": False
                }
            }
        ],
        "correct_response": {
            "job_id": test_data['job_id'],
            "annotation_id": test_data['annotation_id2'],
            "custom_bucket": False
        },
        "expiration_time": test_data['expiration_time']
     }
    res = TextAnnotation().post_accuracy_details(payload)
    res.assert_response_status(expected_status)
    if error_message == "empty accuracy details url":
        assert res.json_response.get('accuracy_details_url') == ''
    elif error_message is not None:
        assert error_message in res.json_response.get('errors')


@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_accuracy_details_with_one_judgment_ss_storage():
    """
    Verify POST /accuracy_details endpoint is successful with one judgment (in Super Saver storage)
    """
    unit_id = random.randint(1, 100000)
    payload = {
      "unit_id": unit_id,
      "team_id": TEAM_ID,
      "job_id": JOB_ID,
      "judgments": [
            {
              "id": random.randint(1, 100000),
              "trust": 0.86,
              "data": {
                   "job_id": JOB_ID_SS,
                   "annotation_id": ANNOTATION_ID1_SS,
                   "bucket_id": BUCKET_ID
                }
             }
           ],
      "correct_response": {
               "job_id": JOB_ID_SS,
               "annotation_id": ANNOTATION_ID2_SS,
               "bucket_id": BUCKET_ID
         }
     }
    res = TextAnnotation().post_accuracy_details(payload)
    res.assert_response_status(200)
    accuracy_details = res.json_response.get('accuracy_details_url')
    assert str(JOB_ID) in accuracy_details
    assert hashed_unit_id(str(unit_id)) in accuracy_details
    assert '/accuracy_details' in accuracy_details
