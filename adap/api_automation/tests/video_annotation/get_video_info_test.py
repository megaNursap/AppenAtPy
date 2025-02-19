"""
https://appen.atlassian.net/browse/QED-1630
curl -X GET \
  'https://video-annotation.internal.qa.cf3.us/api/video_info?row_id=77745d1f5b85ede62a770b0849f9b73747c9e2b6d8f690cf74a899d8b49ef0d9' \
  -H 'cache-control: no-cache' \
  -H 'postman-token: 8a024989-20cc-2e39-9e0c-feff98061635'
"""

import pytest
from adap.api_automation.services_config.video_annotation import Video_Annotation_Internal
from adap.api_automation.utils.data_util import generate_random_string

TEST_DATA = pytest.data.predefined_data['video_annotation_api'].get(pytest.env)
if TEST_DATA:
     UNIT_ID = TEST_DATA['unit_id']

pytestmark = pytest.mark.regression_video_annotation


@pytest.mark.videoannotation_api
@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.skip(reason='Need check data')
def test_get_video_info():
    res = Video_Annotation_Internal(env=pytest.env).get_video_info(unit_id=UNIT_ID)
    res.assert_response_status(200)
    assert "frame_count" in res.json_response


@pytest.mark.videoannotation_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.parametrize('case_desc, unit_id, expected_status',
                         [
                           ("missing unit id", "", 404),
                           ("invalid unit id", "random_string", 404)
                         ])
def test_get_video_info_invalid_input(case_desc, unit_id, expected_status):
    if unit_id == "random_string":
        unit_id = generate_random_string()
    res = Video_Annotation_Internal(env=pytest.env).get_video_info(unit_id=unit_id)
    res.assert_response_status(404)
    assert res.content
