"""
https://appen.atlassian.net/browse/QED-1354
"""
import pytest
import random
from adap.api_automation.services_config.pointcloud import *
from adap.api_automation.utils.data_util import generate_random_string

pytestmark = pytest.mark.regression_lidar

TEST_DATA = pytest.data.predefined_data['pointcloud_api'].get(pytest.env)
if TEST_DATA:
     BASE_URL = TEST_DATA['base_url']
     INVALID_BASEURL = TEST_DATA['invalid_url']


@pytest.mark.lidar_pointcloud_api
@pytest.mark.pointcloud_api
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.parametrize('case_desc, base_url, image_id, frame_id, expected_status',
                         [("without frame id", "base_url", 0, None, 200),
                          ("with frame id", "base_url", 0, 1, 200)
                          ])
def test_get_callibration(case_desc, base_url, image_id, frame_id, expected_status):
    if base_url == "base_url":
        base_url = BASE_URL
    res = PointCloud().get_callibration(base_url, image_id, frame_id)
    res.assert_response_status(200)
    assert "message" in res.json_response
    assert "code" in res.json_response
    assert "data" in res.json_response


# case 4 bug? imageid is not provided, still return 200, expect error message
@pytest.mark.lidar_pointcloud_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.parametrize('case_desc, base_url, image_id, frame_id, expected_status, error_message',
                         [
                          ("both baseurl and imageid missing", "", "", None, 500, "Invalid URL"),
                          ("both missing, with frameid", "", "", 1, 500, "Invalid URL"),
                          ("only baseurl missing", "", 0, 1, 500, "Invalid URL"),
                          ("only imageid missing", "base_url", "", None, 200, None),
                          ("invalid input", "random_string", "random_int", None, 500, "Invalid URL")
                          ])
def test_get_callibration_various_input(case_desc, base_url, image_id, frame_id, expected_status, error_message):
    if base_url == "base_url":
        base_url = BASE_URL
    if base_url == "random_string":
        base_url = generate_random_string()
    if image_id == "random_int":
        image_id = random.randint(1, 10)
    res = PointCloud().get_callibration(base_url, image_id, frame_id)
    res.assert_response_status(expected_status)
    if error_message is not None:
        assert error_message in res.json_response.get('message')

