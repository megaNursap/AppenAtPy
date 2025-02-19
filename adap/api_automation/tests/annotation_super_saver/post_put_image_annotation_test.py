"""
https://appen.atlassian.net/browse/QED-1699
SWAGGER:https://app.swaggerhub.com/apis/CrowdFlower/annotation-super-saver/1.0.0#/Annotations/get_annotations__id_
This tests implements
1. post image annotation api:
summary: Upload annotation images to s3 bucket
description: Given a base64 image payload, will store the image into the bucket. **IMPORTANT It overwrites the annotation content if an exsiting key is given.
2. put image annotation api:
summary: Get expiration link for the image annotation stored into the s3 bucket
description: Will return an expiring URL for the annotation. The expiration time is 5 minutes by default, the expiration params is optional and it is in seconds up to 7 days.
"""

import pytest
from adap.api_automation.services_config.supersaver import *
from adap.api_automation.utils.data_util import generate_random_string, generate_random_test_data

pytestmark = [pytest.mark.super_saver_api,pytest.mark.regression_image_annotation]

KEY = generate_random_string()
IMAGE = generate_random_string()
BUCKET_ID = generate_random_string()


@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.adap_api_uat
@pytest.mark.dependency()
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_post_image_annotation():
    payload = {
      "key": KEY,
      "bucket_id": BUCKET_ID,
      "image": IMAGE,
     }
    res = SuperSaver().post_image_annotation(payload)
    res.assert_response_status(200)
    assert res.json_response.get('aws_key') == KEY
    assert res.json_response.get('bucket_id') == "f8-annotation-super-saver-%s" % pytest.env

@pytest.mark.adap_api_uat
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")

@pytest.mark.parametrize('case_desc, key, bucket_id, image, expected_status, error_details',
                         [("missing key", "", "random_string", "random_string", 400, "Bad Request"),
                          ("missing bucket id", "random_string", "", "random_string", 200, ""),
                          ("missing image", "random_string", "random_string", "", 400, "Bad Request")
                          ])
def test_post_image_annotation_various_input(case_desc, key, bucket_id, image, expected_status, error_details):
    test_data = generate_random_test_data({'key': key,
                                           'bucket_id': bucket_id,
                                           'image': image
                                           })
    payload = {
        "key": test_data['key'],
        "bucket_id": test_data['bucket_id'],
        "image": test_data['image'],
    }
    res = SuperSaver().post_image_annotation(payload)
    res.assert_response_status(expected_status)
    if error_details:
        assert res.json_response.get("error") == error_details


@pytest.mark.dependency(name="test_post_image_annotation")
@pytest.mark.uat_api
@pytest.mark.adap_api_uat
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_put_image_annotation():
    payload = {
        "key": KEY,
        "bucket_id": BUCKET_ID,
        "expiration_time": 3000
    }

    res = SuperSaver().put_image_annotation(payload)
    res.assert_response_status(200)
    url = res.json_response.get('url')
    assert KEY in url
    assert "f8-annotation-super-saver" in url


@pytest.mark.dependency(name="test_post_image_annotation")
@pytest.mark.uat_api
@pytest.mark.adap_api_uat
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_put_image_annotation_nonmandatory_input():
    payload = {
        "key": KEY
    }

    res = SuperSaver().put_image_annotation(payload)
    res.assert_response_status(200)
    url = res.json_response.get('url')
    assert KEY in url
    assert "f8-annotation-super-saver" in url


@pytest.mark.parametrize('case_desc, key, bucket_id, expiration_time, expected_status, error_details',
                         [("missing key", "", "random_string","random_int", 400, "Bad Request"),
                          ("random bucket id", "random_string", "random_string", "random_int", 422, "AWS S3 Error"),
                          ("random key", "random_string", "", "", 422, "AWS S3 Error")
                          ])
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_put_image_annotation_invalid_input(case_desc, key, bucket_id, expiration_time, expected_status, error_details):
    test_data = generate_random_test_data({'key': key,
                                           'bucket_id': bucket_id,
                                           'expiration_time': expiration_time
                                           })
    payload = {
        "key": test_data['key'],
        "bucket_id": test_data['bucket_id'],
        "expiration_time": test_data['expiration_time'],
    }
    res = SuperSaver().put_image_annotation(payload)
    res.assert_response_status(expected_status)
    if expected_status == 422:
        assert error_details in str(res.json_response.get('errors'))
    else:
        assert res.json_response.get('error'), error_details
