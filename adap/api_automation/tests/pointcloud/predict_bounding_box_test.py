"""
https://appen.atlassian.net/browse/QED-1354
"""
import pytest
from adap.api_automation.services_config.pointcloud import *
from adap.api_automation.utils.data_util import generate_random_test_data

pytestmark = pytest.mark.regression_lidar

TEST_DATA = pytest.data.predefined_data['pointcloud_api'].get(pytest.env)
if TEST_DATA:
     BASE_URL = TEST_DATA['base_url']
     INVALID_BASEURL = TEST_DATA['invalid_url']


@pytest.mark.lidar_pointcloud_api
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_predict_bounding_box():
    payload = {
       "baseUrl": BASE_URL,
       "frameId": 0,
       "pointFormat": {
           "format": "bin",
           "x": 1,
           "y": 2,
           "z": 0
       },
       "point": {
           "x": 2.619772309224496,
           "y": -0.5557852494296549,
           "z": 9.439513897223218
       },
       "plane": True
    }
    res = PointCloud().post_predict_bounding_box(payload)
    res.assert_response_status(200)
    assert "position" in res.json_response
    assert "rotation" in res.json_response
    assert "scale" in res.json_response
    assert len(res.json_response.get('position')) == 3
    assert len(res.json_response.get('rotation')) == 3
    assert len(res.json_response.get('scale')) == 3


@pytest.mark.lidar_pointcloud_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_predict_bounding_box_missingbaseurl():
    payload = {
       "frameId": 0,
       "pointFormat": {
           "format": "bin",
           "x": 1,
           "y": 2,
           "z": 0
       },
       "point": {
           "x": 2.619772309224496,
           "y": -0.5557852494296549,
           "z": 9.439513897223218
       },
       "plane": True
    }
    res = PointCloud().post_predict_bounding_box(payload)
    res.assert_response_status(500)
    assert "baseUrl' not found in request" in res.json_response.get('message')


@pytest.mark.lidar_pointcloud_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_predict_bounding_box_missingframeid():
    payload = {
       "baseUrl": BASE_URL,
       "pointFormat": {
           "format": "bin",
           "x": 1,
           "y": 2,
           "z": 0
       },
       "point": {
           "x": 2.619772309224496,
           "y": -0.5557852494296549,
           "z": 9.439513897223218
       },
       "plane": True
    }
    res = PointCloud().post_predict_bounding_box(payload)
    res.assert_response_status(500)
    assert "frameId' not found in request" in res.json_response.get('message')

# error message should be missing pointFormat
@pytest.mark.lidar_pointcloud_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_predict_bounding_box_missingpointformat():
    payload = {
       "baseUrl": BASE_URL,
       "frameId": 0,
       "point": {
           "x": 2.619772309224496,
           "y": -0.5557852494296549,
           "z": 9.439513897223218
       },
       "plane": True
    }
    res = PointCloud().post_predict_bounding_box(payload)
    res.assert_response_status(500)
    assert "point' not found in request" in res.json_response.get('message')


@pytest.mark.lidar_pointcloud_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_predict_bounding_box_missingpoint():
    payload = {
       "baseUrl": BASE_URL,
       "frameId": 0,
       "pointFormat": {
           "format": "bin",
           "x": 1,
           "y": 2,
           "z": 0
       },
       "plane": True
    }
    res = PointCloud().post_predict_bounding_box(payload)
    res.assert_response_status(500)
    assert "point' not found in request" in res.json_response.get('message')


@pytest.mark.lidar_pointcloud_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_predict_bounding_box_missingplane():
    payload = {
        "baseUrl": BASE_URL,
        "frameId": 0,
        "pointFormat": {
            "format": "bin",
            "x": 1,
            "y": 2,
            "z": 0
        },
        "point": {
            "x": 2.619772309224496,
            "y": -0.5557852494296549,
            "z": 9.439513897223218
        }
    }
    res = PointCloud().post_predict_bounding_box(payload)
    res.assert_response_status(200)
    assert "position" in res.json_response
    assert "rotation" in res.json_response
    assert "scale" in res.json_response


@pytest.mark.lidar_pointcloud_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.parametrize('case_desc, base_url, frame_id, pointformat_x, pointformat_y, pointformat_z, '
                         'point_x, point_y, point_z, plane, expected_status, error_message',
                         [
                           ("baseurl missing", "", 0, 1, 2, 0, 2.6, -0.5, 9.3, True, 500, "baseUrl and frameId are required"),
                           ("frameid missing", BASE_URL, "", 1, 2, 0, 2.6, -0.5, 9.3, True, 500, None),
                           ("xyz missing for pointformat", BASE_URL, 0, "", "", "", 2.6, -0.5, 9.3, True, 500, None),
                           ("xyz missing for point", BASE_URL, 0, 1, 2, 0, "", "", "", True, 500, None),
                           ("invalid url", INVALID_BASEURL, 0, 1, 2, 0, 2.6, -0.5, 9.3, True, 500, "Access Denied"),
                           ("frameid out of range", BASE_URL, 1000, 1, 2, 0, 2.6, -0.5, 9.3, True, 500, "list index out of range"),
                          ])
def test_predict_bounding_box_various_input(case_desc, base_url, frame_id, pointformat_x, pointformat_y, pointformat_z,
                                            point_x, point_y, point_z, plane, expected_status, error_message):
    payload = {
        "baseUrl": base_url,
        "frameId": frame_id,
        "pointFormat": {
            "format": "bin",
            "x": pointformat_x,
            "y": pointformat_y,
            "z": pointformat_z
        },
        "point": {
            "x": point_x,
            "y": point_y,
            "z": point_z
        },
        "plane": plane
    }
    res = PointCloud().post_predict_bounding_box(payload)
    res.assert_response_status(expected_status)
    if error_message is not None:
        assert error_message in res.json_response.get('message')
