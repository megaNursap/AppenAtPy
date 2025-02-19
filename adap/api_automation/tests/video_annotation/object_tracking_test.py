"""
https://appen.atlassian.net/browse/QED-1632
"""

import pytest
import json
import random
from adap.api_automation.services_config.video_annotation import Video_Annotation_Internal

TEST_DATA = pytest.data.predefined_data['video_annotation_api'].get(pytest.env)
if TEST_DATA:
     VIDEO_ID = TEST_DATA['video_id']


pytestmark = [pytest.mark.regression_video_annotation, pytest.mark.adap_api_uat]


# @pytest.mark.videoannotation_api
# @pytest.mark.smoke
# @pytest.mark.uat_api
# @pytest.mark.skip(reason='Need check data')
# def test_object_tracking():
#     frame_id = random.choice(range(1, 236))
#     data = {
#         'video_id': VIDEO_ID,
#         'start_frame': 73,
#         'tracked_frame_count': 10,
#         'object_id': 1,
#         'x': 1022,
#         'y': 430,
#         'width': 49,
#         'height': 36
#     }
#     resp = Video_Annotation_Internal(env=pytest.env).object_tracking(data=json.dumps(data))
#     resp.assert_response_status(200)
#     assert "object_id" in resp.json_response[0]
#     assert "x" in resp.json_response[0]
#     assert "y" in resp.json_response[0]
#     assert "width" in resp.json_response[0]
#     assert "height" in resp.json_response[0]
#     assert "frame_num" in resp.json_response[0]


# different behavior for case missing track frame count on QA and Sandbox, so comment it out
# https://appen.atlassian.net/browse/AT-2858 created
@pytest.mark.videoannotation_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.parametrize('case_desc, video_id, frame_id, tracked_frame_count, '
                         'object_id, x, y, width, height, expected_status',
                         [
                             ("missing video id", "", "random_int", 10, 1, 1022, 430, 49,  36, 422),
                             ("missing start frame id", VIDEO_ID, "", 10, 1, 1022, 430, 49,  36, 200),
                            # ("missing track frame count", VIDEO_ID, "random_int", "", 1, 1022, 430, 49,  36, 200),
                             ("missing various input", VIDEO_ID, "random_int", 10, "", "", "", "",  "", 422)
                         ])
def test_object_tracking_various_input(case_desc, video_id, frame_id, tracked_frame_count, object_id, x, y, width, height, expected_status):
    if frame_id == "random_int":
        frame_id = random.choice(range(1, 236))
    data = {
        'video_id': video_id,
        'start_frame': frame_id,
        'tracked_frame_count': tracked_frame_count,
        'object_id': object_id,
        'x': x,
        'y': y,
        'width': width,
        'height': height
    }
    resp = Video_Annotation_Internal(env=pytest.env).object_tracking(data=json.dumps(data))
    resp.assert_response_status(expected_status)



