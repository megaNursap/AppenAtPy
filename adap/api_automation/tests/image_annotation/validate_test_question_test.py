"""
https://appen.atlassian.net/browse/QED-1613
"""

import pytest
import json
from adap.api_automation.services_config.image_annotation import Image_Annotation_Internal
from adap.data.image_annotation import internal_service_data as data

pytestmark = pytest.mark.regression_image_annotation


@pytest.mark.imageannotation_api
@pytest.mark.smoke
@pytest.mark.adap_api_uat
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_validate_test_question():
    request_body = data.validate
    res = Image_Annotation_Internal(env=pytest.env).validate(json.dumps(request_body))
    res.assert_response_status(200)
    assert "annotations" in res.json_response
    assert "grades" in res.json_response
    assert "scores" in res.json_response
    assert "status" in res.json_response
    assert "class" in res.json_response.get("annotations")[0]
    assert "coordinates" in res.json_response.get("annotations")[0]
    assert "expected_class" in res.json_response.get("annotations")[0]
    assert "expected_id" in res.json_response.get("annotations")[0]
    assert "id" in res.json_response.get("annotations")[0]
    assert "score" in res.json_response.get("annotations")[0]
    assert "status" in res.json_response.get("annotations")[0]
    assert "type" in res.json_response.get("annotations")[0]
    assert "h" in res.json_response.get("annotations")[0].get("coordinates")
    assert "w" in res.json_response.get("annotations")[0].get("coordinates")
    assert "x" in res.json_response.get("annotations")[0].get("coordinates")
    assert "y" in res.json_response.get("annotations")[0].get("coordinates")


@pytest.mark.imageannotation_api
@pytest.mark.parametrize('case_desc, request_body',
                         [
                          ("invalid input", data.validate_invalidinput),
                          ("missing input", data.validate_missing_input)
                          ])
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_validate_test_question_negative(case_desc, request_body):
    res = Image_Annotation_Internal(env=pytest.env).validate(json.dumps(request_body))
    res.assert_response_status(500)
