"""
https://appen.atlassian.net/browse/QED-1633
"""

import pytest
from adap.api_automation.services_config.video_annotation import Video_Annotation_Internal
from adap.api_automation.services_config.requestor_proxy import RP
from adap.api_automation.utils.data_util import generate_random_string, get_test_data
import random

TEST_DATA = pytest.data.predefined_data['video_annotation_api'].get(pytest.env)
if TEST_DATA:
     VIDEO_ID = TEST_DATA['video_id']

pytestmark = [pytest.mark.regression_video_annotation, pytest.mark.adap_api_uat]


# @pytest.mark.videoannotation_api
# @pytest.mark.smoke
# @pytest.mark.uat_api
# @pytest.mark.skip(reason='Need check data')
# def test_get_frame_internal():
#     frame_id = random.choice(range(1, 246))
#     resp = Video_Annotation_Internal(env=pytest.env).get_frame(VIDEO_ID, frame_id)
#     assert resp.status_code == 200, resp.content


# need to check if we need jwt in userid
@pytest.mark.videoannotation_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_get_frame_request_proxy():
    frame_id = random.choice(range(1, 246))

    username = get_test_data('test_ui_account', 'email')
    password = get_test_data('test_ui_account', 'password')

    rp = RP()
    rp.get_valid_sid(username, password)
    resp = rp.get_video_frame(video_id=VIDEO_ID, frame_id=frame_id)
    assert resp.status_code == 404, resp.content


@pytest.mark.videoannotation_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.parametrize('case_desc, video_id, frame_id, expected_status',
                         [
                           ("missing video id", "", "100", 404),
                           ("missing frame id", VIDEO_ID, "", 404),
                           ("invalid video id", "random_string", "100", 404),
                           ("invalid frame id", VIDEO_ID, "random_int", 404)
                         ])
def test_get_frame_invalid_input(case_desc, video_id, frame_id, expected_status):
    if video_id == "random_string":
        video_id = generate_random_string()
    if frame_id == "random_int":
        frame_id = random.choice(range(247, 300))
    resp = Video_Annotation_Internal(env=pytest.env).get_frame(video_id, frame_id)
    assert resp.status_code == expected_status, resp.content


