"""
https://appen.atlassian.net/browse/QED-1699
SWAGGER:https://app.swaggerhub.com/apis/CrowdFlower/annotation-super-saver/1.0.0#/Annotations/get_annotations__id_
This tests implements
1. post annotation api:
summary: Upload contributor/gold data to s3 bucket
description: Uploads contributor responses or gold data into the S3 bucket. **IMPORTANT It overwrites the annotation content if an exsiting `job_id` and `annotation_id` combination is given.**
2. get annotation api:
summary: Get expiration link for the annotation stored into the s3 bucket
description: Will return an expiring URL for the annotation. The expiration time is 60 seconds by default, the expiration params is optional and it is in seconds up to 7 days.
"""

import pytest
import random
from adap.api_automation.services_config.supersaver import *
from adap.api_automation.utils.data_util import generate_random_string, generate_random_test_data

pytestmark = [pytest.mark.super_saver_api,pytest.mark.regression_core]

JOB_ID = random.randint(1, 100000)
ANNOTATION_ID = generate_random_string()


@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.adap_api_uat
@pytest.mark.dependency()
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_post_annotation():
    payload = {
      "id": ANNOTATION_ID,
      "job_id": JOB_ID,
      "payload": {
          "key": generate_random_string(),
          "key1": generate_random_string()
      }
     }
    res = SuperSaver().post_annotation(payload)
    res.assert_response_status(200)
    assert res.json_response.get('job_id') == JOB_ID
    assert res.json_response.get('annotation_id') == ANNOTATION_ID
    # later, if we enable it for other env, this assert needs to be updated.
    assert res.json_response.get('bucket_id') == "f8-annotation-super-saver-%s" % pytest.env


@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.parametrize('case_desc, annotation_id, job_id, key, key1, expected_status, error_details',
                         [("missing annotation id", "", "random_int", "", "random_string", 400, "Bad Request"),
                          ("missing job id", "random_string", "", "random_string", "", 400, "Bad Request")])
def test_post_annotation_invalid_input(case_desc, annotation_id, job_id, key, key1, expected_status, error_details):
    test_data = generate_random_test_data({'id': annotation_id,
                                           'job_id': job_id,
                                           'key': key,
                                           'key1': key1
                                           })
    payload = {
      "id": test_data['id'],
      "job_id": test_data['job_id'],
      "payload": {
          "key": test_data['key'],
          "key1": test_data['key1']
      }
     }
    res = SuperSaver().post_annotation(payload)
    res.assert_response_status(expected_status)
    assert res.json_response.get("error") == error_details


@pytest.mark.dependency(name="test_post_annotation")
@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.adap_api_uat
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_get_annotation():
    res = SuperSaver().get_annotation(ANNOTATION_ID, JOB_ID)
    res.assert_response_status(200)
    url = res.json_response.get('url')
    assert ANNOTATION_ID in url
    assert str(JOB_ID) in url
    assert "f8-annotation-super-saver" in url


@pytest.mark.parametrize('case_desc, annotation_id, job_id, expected_status, error_details',
                         [
                          ("random annotation id and job id", "random_string", "random_int", 422, "AWS S3 Error"),
                          ("missing job id", "random_string", "", 400, "Bad Request"),
                          ("missing annotation id", "", "random_int", 404, "Not Found")
                          ])
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_get_annotation_invalid_input(case_desc, annotation_id, job_id, expected_status, error_details):
    test_data = generate_random_test_data({'annotation_id': annotation_id,
                                           'job_id': job_id
                                           })
    res = SuperSaver().get_annotation(test_data['annotation_id'], test_data['job_id'])
    res.assert_response_status(expected_status)
    if expected_status == 422:
        assert error_details in str(res.json_response.get('errors'))
    else:
        assert res.json_response.get('error'), error_details

