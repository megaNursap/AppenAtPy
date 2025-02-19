"""
https://appen.atlassian.net/browse/QED-1612
"""

import pytest
import json
from adap.api_automation.services_config.image_annotation import Image_Annotation_Internal
from adap.data.image_annotation import internal_service_data as data

pytestmark = pytest.mark.regression_image_annotation


@pytest.mark.imageannotation_api
@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.adap_api_uat
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_generate_aggregate_report():
    request_body = data.aggregate
    res = Image_Annotation_Internal(env=pytest.env).aggregate(json.dumps(request_body))
    res.assert_response_status(200)
    assert len(res.json_response) == 2
    assert "average_trust" in res.json_response[0]
    assert "class" in res.json_response[0]
    assert "coordinates" in res.json_response[0]
    assert "type" in res.json_response[0]
    assert "h" in res.json_response[0].get("coordinates")
    assert "w" in res.json_response[0].get("coordinates")
    assert "x" in res.json_response[0].get("coordinates")
    assert "y" in res.json_response[0].get("coordinates")


@pytest.mark.imageannotation_api
@pytest.mark.parametrize('case_desc, request_body, response_status',
                         [
                          ("invalid input", data.aggregate_invalid_input, 422),
                          ("missing input", data.aggregate_missing_thresholds, 500),
                          ("missing trust", data.aggregate_missing_trust, 422)
                          ])
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_generate_aggregate_report_negative(case_desc, request_body, response_status):
    res = Image_Annotation_Internal(env=pytest.env).aggregate(json.dumps(request_body))
    res.assert_response_status(response_status)
