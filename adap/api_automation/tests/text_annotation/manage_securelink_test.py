"""
EPIC:https://appen.atlassian.net/browse/QED-1334
JIRA:https://appen.atlassian.net/browse/QED-1341
     https://appen.atlassian.net/browse/QED-1342
SWAGGER:https://app.swaggerhub.com/apis/CrowdFlower/text-annotation/1.0.0#/Annotations/post_annotations
"""
import pytest
import random
from adap.api_automation.services_config.textannotation import *
from adap.api_automation.utils.data_util import generate_random_string, generate_random_test_data

pytestmark = [pytest.mark.regression_text_annotation, pytest.mark.textannotation_api]

JOB_ID = random.randint(1, 100000)
ANNOTATION_ID = generate_random_string()
TOKEN = None


@pytest.mark.dependency()
@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_post_annotation_securelink():
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


@pytest.mark.dependency()
@pytest.mark.dependency(name="test_post_annotation_securelink")
@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_put_securelink():
    """
    Verify PUT /secure_links/expiring_url is successful with valid payload, using required fields only
    """
    payload = {
        "id": ANNOTATION_ID,
        "job_id": JOB_ID,
        "annotation_type": "json"
    }
    res = TextAnnotation().put_securelink(payload)
    res.assert_response_status(200)
    url = res.json_response.get('url')
    assert 'token' in url
    index = url.index('token')
    global TOKEN
    TOKEN = url[index+6:len(url)]


# per design, bucket_id and annotation_type not mandatory at this moment
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.parametrize('annotation_type, expected_status',
                         [("json", 200),
                          ("", 200)])
def test_put_securelink_nonmandatory_input(annotation_type, expected_status):
    """
    Verify PUT /secure_links/expiring_url is successful with valid payload using non-mandatory input as well
    """
    id = generate_random_string()
    job_id = generate_random_string()
    post_payload = {
        "id": id,
        "job_id": job_id,
        "payload": {
            "key": "value"
        }
    }
    res = TextAnnotation().post_annotation(post_payload)
    res.assert_response_status(200)

    put_payload = {
        "id": id,
        "job_id": job_id,
        "annotation_type": annotation_type
    }
    res = TextAnnotation().put_securelink(put_payload)
    res.assert_response_status(expected_status)
    url = res.json_response.get('url')
    assert "token" in url


@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.parametrize('id, job_id, bucket_id, annotation_type, expected_status, error_message',
                         [("", "random_int", "random_string", "json", 400, None),
                          ("random_string", "", "random_string", "xml", 400, None),
                          ("random_string", "random_int", "", "json", 404, "Annotation not found")])
def test_put_securelink_invalid_input_manage(id, job_id, bucket_id, annotation_type, expected_status, error_message):
    """
    Verify PUT /secure_links/expiring_url fails with invalid payload
    """
    test_data = generate_random_test_data({'id': id,
                                           'job_id': job_id,
                                           'bucket_id': bucket_id
                                           })
    payload = {
        "id": test_data['id'],
        "job_id": test_data['job_id'],
        "bucket_id": test_data['bucket_id'],
        "annotation_type": annotation_type
    }
    res = TextAnnotation().put_securelink(payload)
    res.assert_response_status(expected_status)
    if expected_status == 404 and error_message is not None:
        assert error_message in res.json_response.get('errors')


@pytest.mark.dependency(name="test_put_securelink")
@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_manage_get_securelink():
    """
    Verify GET /secure_links?token=%s is successful with valid token
    """
    res = TextAnnotation().get_securelink(TOKEN)
    res.assert_response_status(200)

@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
@pytest.mark.parametrize('token, expected_status, error_message',
                         [("", 400, None),
                          ("random_string", 403, "Invalid Token")
                          ])
def test_get_securelink_invalid_input(token, expected_status, error_message):
    """
    Verify GET /secure_links?token=%s fails with invalid token
    """
    if token == "random_string":
        token = generate_random_string()
    res = TextAnnotation().get_securelink(token)
    res.assert_response_status(expected_status)
    if error_message is not None:
        assert error_message in res.json_response.get('errors')
