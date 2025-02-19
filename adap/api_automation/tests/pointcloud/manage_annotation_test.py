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
     FILE_NAME = TEST_DATA['file_name']


@pytest.mark.lidar_pointcloud_api
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.skip(reason="AT-3909")
def test_submit_annotation():
    payload = {
        "fileName": FILE_NAME,
        "baseUrl": BASE_URL
    }
    res = PointCloud().submit_annotation(payload)
    res.assert_response_status(200)
    assert res.json_response.get('message') == 'success'
    assert "code" in res.json_response
    assert "data" in res.json_response
    assert "f8-pc-annotations-" + pytest.env in res.json_response.get('data')
    assert FILE_NAME in res.json_response.get('data')


@pytest.mark.dependency()
@pytest.mark.lidar_pointcloud_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_submit_annotation_withnonmandatoryfield():
    payload = {
        "fileName": FILE_NAME,
        "baseUrl": BASE_URL,
        "result": [
            {
                "frameId": 0,
                "items": [
                    {
                        "id": "a72fda80-df12-4f10-b780-138307285b37",
                        "category": "Vehicle",
                        "interpolated": False,
                        "occlusion": "",
                        "truncation": "null",
                        "position": {
                            "x": 2.619772309224496,
                            "y": -0.5557852494296549,
                            "z": 9.439513897223218
                        },
                        "rotation": {
                            "x": 0,
                            "y": 0,
                            "z": 0
                        },
                        "dimension": {
                            "x": 2,
                            "y": 2,
                            "z": 4
                        }
                    }
                ],
                "images": [
                    {
                        "image": "",
                        "items": []
                    }
                ]
            }
        ]

    }
    res = PointCloud().submit_annotation(payload)
    res.assert_response_status(200)
    assert res.json_response.get('message') == 'success'
    assert "code" in res.json_response
    assert "data" in res.json_response
    print("data is:", res.json_response.get('data'))
    assert "f8-pc-annotations-" + pytest.env in res.json_response.get('data')
    assert FILE_NAME in res.json_response.get('data')


# please confirm, case 1, 2, 3 error message can be improved.
# Case 5 random file name also return 200, any check needed?
# https://appen.atlassian.net/browse/CTT-56
@pytest.mark.lidar_pointcloud_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.parametrize('case_desc, file_name, base_url, expected_status, error_message',
                         [
                           ("both mandatory fields missing", "", "", 500, "baseUrl is required"),
                           ("only filename missing", "", "base_url", 500, "Failed to save annotation: baseUrl and fileName are required"),
                           ("only baseurl missing", "file_name", "", 500, "baseUrl is required"),
                           ("invalid baseurl", "file_name", "random_string", 500, "Failed to save annotation: Invalid URL"),
                           ("invalid filename", "random_string", "base_url", 200, None)
                         ])
def test_submit_annotation_invalid_input(case_desc, file_name, base_url, expected_status, error_message):
    if base_url == "base_url":
        base_url = BASE_URL
    if file_name == "file_name":
        file_name = FILE_NAME
    test_data = generate_random_test_data({'file_name': file_name,
                                           'base_url': base_url
                                           })

    payload = {
        "fileName": test_data['file_name'],
        "baseUrl": test_data['base_url']
    }
    res = PointCloud().submit_annotation(payload)
    res.assert_response_status(expected_status)
    if error_message is not None:
        assert error_message in res.json_response.get('message')


@pytest.mark.dependency(name="test_submit_annotation_withnonmandatoryfield")
@pytest.mark.lidar_pointcloud_api
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.skip(reason="AT-3909")
def test_get_annotation_text():
    res = PointCloud().get_annotation(BASE_URL, FILE_NAME)
    res.assert_response_status(200)
    res.assert_job_message('success')
    assert "code" in res.json_response
    data_dict = res.json_response.get('data')
    assert data_dict.get('baseUrl') == BASE_URL
    assert len(data_dict['frames']) == 168
    assert data_dict['frames'][0].get('frameId') == 0
    # item is not on integration
    # item = data_dict['frames'][0].get('items')[0]
    # assert item.get('id') == 'a72fda80-df12-4f10-b780-138307285b37'
    # assert item.get('category') == 'Vehicle'
    # assert item.get('interpolated') is False
    # assert item.get('occlusion') == ''
    # assert item.get('truncation') == 'null'
    # assert item.get('position').get('x') == 2.619772309224496
    # assert item.get('position').get('y') == -0.5557852494296549
    # assert item.get('position').get('z') == 9.439513897223218
    # assert item.get('rotation').get('x') == 0
    # assert item.get('rotation').get('y') == 0
    # assert item.get('rotation').get('z') == 0
    # assert item.get('dimension').get('x') == 2
    # assert item.get('dimension').get('y') == 2
    # assert item.get('dimension').get('z') == 4


# pls confirm, case 2,3 error message can be improved.
# case 4,5,  invalid baseurl and invalid filename, return 200, bug?
# https://appen.atlassian.net/browse/CTT-57
@pytest.mark.lidar_pointcloud_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.parametrize('case_desc, base_url, file_name, expected_status, error_message',
                         [
                          ("baseurl and filename missing", "", "", 500, "baseUrl and fileName are required"),
                          ("only baseurl missing", "", "file_name", 500, "baseUrl and fileName are required"),
                          ("only filename missing", "base_url", "", 500, "baseUrl and fileName are required"),
                          ("invalid baseurl", "random_string", "file_name", 200, None),
                          ("invalid filename", "base_url", "random_string", 200, None)
                          ])
def test_get_annotation_invalid_input(case_desc, base_url, file_name, expected_status, error_message):
    if base_url == "base_url":
        base_url = BASE_URL
    if file_name == "file_name":
        file_name = FILE_NAME
    test_data = generate_random_test_data({'base_url': base_url,
                                           'file_name': file_name,
                                           })

    res = PointCloud().get_annotation(test_data['base_url'], test_data['file_name'])
    res.assert_response_status(expected_status)
    if error_message is not None:
        assert error_message == res.json_response.get('message')

