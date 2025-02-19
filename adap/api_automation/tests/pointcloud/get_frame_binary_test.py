"""
POSTMAN COLLECTION: https://figure-eight-eng.postman.co/collections/5577736-f0ba2f20-ef5d-4749-bff0-7807d0d62e13?version=latest&workspace=4faa266b-bc41-4b48-8f9a-f1dac4b33281#16103582-6b1e-4e38-b66e-f4823d515fe3
"""
import pytest
from adap.api_automation.services_config.pointcloud import *

pytestmark = pytest.mark.regression_lidar

# Test data
TEST_DATA = pytest.data.predefined_data['pointcloud_api'].get(pytest.env)
if TEST_DATA:
     BASEURL = TEST_DATA['base_url']
     INVALID_BASEURL = TEST_DATA['invalid_url']


@pytest.mark.lidar_pointcloud_api
@pytest.mark.pointcloud_api
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")# Spira Testcase: https://appen.spiraservice.net/5/TestCase/1038.aspx
def test_get_frame_valid_baseurl():
    res = PointCloud().get_frame_binary(BASEURL)
    res.assert_response_status(200)
    res.assert_job_message('success')
    data_dict = res.json_response.get('data')
    assert len(data_dict['points']['default']) == 168
    assert len(data_dict['points']['vertical']) == 168
    assert len(data_dict['images']) == 168

# @pytest.mark.lidar_pointcloud_api
# Spira Testcase: https://appen.spiraservice.net/5/TestCase/1109.aspx
# Test fails - Bug reported in CTT-44
# TODO: Change status code and error message assertion according to bug fix
# def test_get_frame_no_baseurl():
#     res = PointCloud().get_frame_binary('')
#     res.assert_response_status(400)
#     res.assert_job_message('baseUrl is required')

# @pytest.mark.lidar_pointcloud_api
# Spira Testcase: https://appen.spiraservice.net/5/TestCase/1039.aspx
# Test fails - Bug reported in CTT-45
# TODO: Change/Add status error code and message assertions according to bug fix
# def test_get_frame_invalid_baseurl():
#     res = PointCloud().get_frame_binary(INVALID_BASEURL)
#     res.assert_response_status(400)
