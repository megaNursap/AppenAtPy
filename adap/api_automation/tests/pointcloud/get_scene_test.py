"""
EPIC:https://appen.atlassian.net/browse/QED-1353
JIRA:https://appen.atlassian.net/browse/QED-1354
POSTMAN COLLECTION:https://figure-eight-eng.postman.co/collections/5577736-f0ba2f20-ef5d-4749-bff0-7807d0d62e13?version=latest&workspace=4faa266b-bc41-4b48-8f9a-f1dac4b33281#e780378d-e98a-4a13-a695-7d864dc8e7dc
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
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")# Spira Testcase: https://appen.spiraservice.net/5/TestCase/1036.aspx
def test_get_scene_valid_baseurl():
    res = PointCloud().get_scene(BASEURL)
    res.assert_response_status(200)
    res.assert_job_message('success')
    data_dict = res.json_response.get('data')
    # 26 frames is specific to the BASEURL being used for this test case
    assert len(data_dict['frames']) == 168

# @pytest.mark.lidar_pointcloud_api
# Spira Testcase: https://appen.spiraservice.net/5/TestCase/1037.aspx
# Test fails - Bug reported in CTT-32
# TODO: Change status code and error message assertion according to bug fix
# def test_get_scene_invalid_baseurl():
#     res = PointCloud().get_scene(INVALID_BASEURL)
#     res.assert_response_status(400)

@pytest.mark.lidar_pointcloud_api
# Spira Test case: https://appen.spiraservice.net/5/TestCase/1107.aspx
# TODO: Confirm the status code (maybe 400/422?)
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_get_scene_no_baseurl():
    res = PointCloud().get_scene('')
    res.assert_response_status(500)
    res.assert_job_message('baseUrl is required')

