"""
https://appen.atlassian.net/browse/QED-1699
SWAGGER:https://app.swaggerhub.com/apis/CrowdFlower/annotation-super-saver/1.0.0#/Annotations/get_annotations__id_
This tests implements
1. put secure link api:
summary: Generates an expiring URL including token with encrypted data.
description: The expiring url has encrypted within the token the annotation data. The default expiration time is 14 days.
2. get secure link api:
summary: Generates a short-lived s3 URL
description: Generates an s3 URL decrypting the token within the parameters
"""


import pytest
import random
from adap.api_automation.services_config.supersaver import *
from adap.api_automation.utils.data_util import generate_random_string, generate_random_test_data

pytestmark = [pytest.mark.super_saver_api,pytest.mark.regression_core]

JOB_ID = random.randint(1, 100000)
ANNOTATION_ID = generate_random_string()
BUCKET_ID = generate_random_string()


@pytest.mark.dependency()
@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.adap_api_uat
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_put_secure_link():
    # test setup-create annotation for put secure link testing
    payload = {
        "id": ANNOTATION_ID,
        "job_id": JOB_ID,
        "bucket_id": BUCKET_ID,
        "payload": {
            "key": "value"
        }
    }
    res = SuperSaver().post_annotation(payload)
    res.assert_response_status(200)
    assert res.json_response.get('job_id') == JOB_ID
    assert res.json_response.get('annotation_id') == ANNOTATION_ID
    assert res.json_response.get('bucket_id') == BUCKET_ID

    # start test put secure link
    payload = {
        "id": ANNOTATION_ID,
        "job_id": JOB_ID,
        "bucket_id": BUCKET_ID,
        "annotation_type": "json"
    }
    res = SuperSaver().put_securelink(payload)
    res.assert_response_status(200)
    url = res.json_response.get('url')
    assert 'secure_redirect?token' in url
    assert 'requestor-proxy' in url
    assert 'annotations' in url
    index = url.index('token')
    global TOKEN
    TOKEN = url[index + 6:len(url)]


# https://appen.atlassian.net/browse/QED-2654 update code based on this jira
@pytest.mark.parametrize('case_desc, id, job_id, bucket_id, annotation_type, expected_status, error_details',
                         [("missing annotation id", "", "random_int", "random_string", "json", 400, "Bad Request"),
                          ("missing job id", "random_string", "", "random_string", "json", 400, "Bad Request"),
                          ("invalid annotation type", "random_string", "random_int", "random_string", "xml", 400, "Bad Request"),
                          ("random annotation id and job id", "random_string", "random_int", "random_string", "json", 200, "")
                         ])
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_put_securelink_invalid_input(case_desc, id, job_id, bucket_id, annotation_type, expected_status, error_details):
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
    res = SuperSaver().put_securelink(payload)
    if expected_status == 400:
        assert res.json_response.get('error'), error_details


@pytest.mark.dependency(name="test_put_secure_link")
@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.adap_api_uat
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_get_securelink():
    res = SuperSaver().get_securelink(TOKEN)
    res.assert_response_status(200)
    assert res.json_response.get('key'), 'value'


@pytest.mark.parametrize('case_desc, token, expected_status, error_details',
                         [
                          ("missing token", "", 400, "Bad Request"),
                          ("random token", "random_string", 403, "Invalid Token"),
                          ("expired token", "expired_token", 403, "Expired Token")
                          ])
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_get_securelink_invalid_input(case_desc, token, expected_status, error_details):
    if token == "random_string":
        token = generate_random_string()
    if token == "expired_token":
        token = "CxRkhCiquzP2k5Lr7GKEWJGG3k%2BjK7brV%2BuAVa9br/Boe6agBCx8g2h9RXlM%2BjAufub8PxYP0ZdoxtLKgPUOwPo4xGwLr/5qYLa4AljuWLU6PN7POwaZEmmG8/iZtP19LYw6XLSjkYHIXjvyfbRvYLQDzL3F6r9lZWe4/rqSrYwzW0zjiiu%2BkMx1NwsyGSsp0qqR%2BKzzmwmTvH4pG6GWcdGkTHyOutVuCsaE0%2BnQDJAgZnwlJ%2Bv6294Lb/ZKcnU62W4a--iTYi7L3czfwMV/rv--vhY6bTERuz%2BOAJdvlLmVvQ=="
    res = SuperSaver().get_securelink(token)
    res.assert_response_status(expected_status)
    if expected_status == 400:
        assert res.json_response.get('error'), error_details
    else:
        assert error_details in str(res.json_response.get('errors'))

