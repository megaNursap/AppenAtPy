"""
https://appen.atlassian.net/browse/QED-1631
"""

import pytest
import json
import uuid
from adap.api_automation.services_config.video_annotation import Video_Annotation_Internal
from adap.data.units import hands_vid_annotation as hva

ANNOTATIONS = [hva.frame_annotation for f in range(25)]

pytestmark = [pytest.mark.regression_video_annotation, pytest.mark.adap_api_uat]


@pytest.mark.videoannotation_api
@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_save_annotation():
    annotation_data = {
        'annotation': ANNOTATIONS,
        'job_id': 1000,
        'annotation_id': uuid.uuid4().__str__()
    }
    res = Video_Annotation_Internal(env=pytest.env).save_annotation(json.dumps(annotation_data))
    res.assert_response_status(200)
    assert res.json_response.get('url'), "'url' not found in response payload: "


@pytest.mark.videoannotation_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.parametrize('case_desc, annotation, job_id, annotation_id, expected_status',
                         [
                           ("missing annotation", "", "1000", "uuid.uuid4().__str__()", 500),
                           ("missing job id", ANNOTATIONS, "", "uuid.uuid4().__str__()", 500),
                           ("missing annotation id", ANNOTATIONS, "1000", "", 500)
                          ])
def test_save_annotation_invalid_input(case_desc, annotation, job_id, annotation_id, expected_status):
    annotation_data = {
        'annotation': annotation,
        'job_id': job_id,
        'annotation_id': annotation_id
    }
    res = Video_Annotation_Internal(env=pytest.env).save_annotation(json.dumps(annotation_data))
    res.assert_response_status(expected_status)
