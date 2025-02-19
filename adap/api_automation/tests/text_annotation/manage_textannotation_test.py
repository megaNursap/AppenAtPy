"""
EPIC:https://appen.atlassian.net/browse/QED-1334
JIRA:https://appen.atlassian.net/browse/QED-1335
     https://appen.atlassian.net/browse/QED-1336
SWAGGER:https://app.swaggerhub.com/apis/CrowdFlower/text-annotation/1.0.0#/Annotations/post_annotations
"""
import pytest
import random
from adap.api_automation.services_config.textannotation import *
from adap.api_automation.utils.data_util import generate_random_string, generate_random_test_data

pytestmark = [pytest.mark.regression_text_annotation, pytest.mark.textannotation_api]

JOB_ID = random.randint(1, 100000)
ANNOTATION_ID = generate_random_string()


@pytest.mark.dependency()
@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_manage_post_annotation():
    """
    Verify POST /annotations is successful with valid payload
    """
    payload = {
        "id": ANNOTATION_ID,
        "job_id": JOB_ID,
        "payload": {
            "key": "value"
        }
    }
    res = TextAnnotation().post_annotation(payload)
    res.assert_response_status(200)
    assert res.json_response.get('job_id') == JOB_ID
    assert res.json_response.get('annotation_id') == ANNOTATION_ID


""" 
bucket_id and payload is not mandatory at this moment.
Per dev,it defaults to the text annotation bucket assigned for each environment, 
so no matter what you add there or if you don’t add it, it will go to the same place. 
It was intended to have a feature that will store in different buckets in the future, 
but it is not yet developed and there are no plans to do it in the near future.
"""


@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.parametrize('id, job_id, key, expected_status',
                         [("random_string", "random_int", "random_string", 200),
                          ("random_string", "random_int", "", 200)])
def test_post_annotation_nonmandatory_input(id, job_id, key, expected_status):
    """
    Verify POST /annotations is successful with valid payload (using all non-mandatory fields as well)
    """
    test_data = generate_random_test_data({'id': id,
                                           'job_id': job_id,
                                           'key': key
                                           })
    payload = {
        "id": test_data['id'],
        "job_id": test_data['job_id'],
        "payload": {
            "key": test_data['key']
        }
    }
    res = TextAnnotation().post_annotation(payload)
    res.assert_response_status(expected_status)
    assert res.json_response.get('job_id') == test_data['job_id']
    assert res.json_response.get('annotation_id') == test_data['id']


# id, job_id is mandatory per design
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.parametrize('id, job_id, bucket_id, key, expected_status',
                         [("", "random_int", "random_string", "random_string", 400),
                          ("random_string", "", "random_string", "random_string", 400),
                          ("", "", "random_string", "random_string", 400)])
def test_post_annotation_invalid_input(id, job_id, bucket_id, key, expected_status):
    """
    Verify POST /annotations fails with invalid payload
    """
    test_data = generate_random_test_data({'id': id,
                                           'job_id': job_id,
                                           'bucket_id': bucket_id,
                                           'key': key
                                           })
    payload = {
        "id": test_data['id'],
        "job_id": test_data['job_id'],
        "bucket_id": test_data['bucket_id'],
        "payload": {
            "key": test_data['key']
        }
    }
    res = TextAnnotation().post_annotation(payload)
    res.assert_response_status(expected_status)


@pytest.mark.dependency(name="test_manage_post_annotation")
@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_manage_get_annotation():
    """
    Verify GET /annotations/%s?job_id=%s&expiration_time=%s is successful with valid parameters
    """
    res = TextAnnotation().get_annotation(ANNOTATION_ID, JOB_ID)
    res.assert_response_status(200)
    url = res.json_response.get('url')
    assert ANNOTATION_ID in url
    assert "f8-text-annotation" in url


@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.dependency(name="test_manage_post_annotation")
@pytest.mark.parametrize('annotation_id, job_id, expected_status, error_message',
                         [("random_string", "random_int", 404, "Not found"),
                          ("random_string", "", 400, ""),
                          ("", "random_int", 404, None)
                          ])
def test_get_annotation_invalid_input(annotation_id, job_id, expected_status, error_message):
    """
    Verify GET /annotations/%s?job_id=%s&expiration_time=%s fails when invalid parameters are passed
    """
    test_data = generate_random_test_data({'annotation_id': annotation_id,
                                           'job_id': job_id
                                           })
    res = TextAnnotation().get_annotation(test_data['annotation_id'], test_data['job_id'])
    res.assert_response_status(expected_status)
    if expected_status == 404 and error_message is not None:
        assert error_message in res.json_response.get('errors')
