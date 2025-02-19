"""
https://appen.atlassian.net/browse/QED-1354
"""
import pytest
from adap.api_automation.services_config.pointcloud import *
from adap.api_automation.utils.data_util import generate_random_string

pytestmark = pytest.mark.regression_lidar

TEST_DATA = pytest.data.predefined_data['pointcloud_api'].get(pytest.env)
if TEST_DATA:
     INVALID_BASEURL = TEST_DATA['invalid_url']
     RESULT_URL = TEST_DATA['result_url']


@pytest.mark.lidar_pointcloud_api
@pytest.mark.pointcloud_api
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_get_result():
    res = PointCloud().get_result(RESULT_URL)
    res.assert_response_status(200)
    res.assert_job_message('success')
    assert "code" in res.json_response
    assert len(res.json_response.get('data').get('baseUrl')) > 0


# https://appen.atlassian.net/browse/CTT-58 for case 3
@pytest.mark.lidar_pointcloud_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.parametrize('case_desc, result_url, expected_status, error_message',
                         [
                          ("resulturl is missing", "", 500, "resultUrl is required"),
                          ("random resulturl", "random_string", 500, "Invalid URL"),
                          ("invalid resulturl", "invalid_url", 500, "Access Denied")
                          ])
def test_get_result_various_input(case_desc, result_url, expected_status, error_message):
    if result_url == "random_string":
        result_url = generate_random_string()
    if result_url == "invalid_url":
        result_url = INVALID_BASEURL
    res = PointCloud().get_result(result_url)
    res.assert_response_status(expected_status)
    if error_message is not None:
        assert error_message in res.json_response.get('message')

