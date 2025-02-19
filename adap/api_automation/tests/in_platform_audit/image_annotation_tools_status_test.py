import random
import time

import pytest
import allure
from adap.api_automation.services_config.requestor_proxy import RP
from adap.api_automation.utils.data_util import get_test_data

pytestmark = [
    pytest.mark.regression_ipa,
    pytest.mark.quality_audit_smoke
]


TEST_DATA_SHAPE = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('image_annotation', "")
TEST_DATA_SHAPE_WITHOUT_ONTOLOGY = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('image_annotation_without_ontology', "")
TEST_DATA_SHAPE_OUTPUT_URL = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('image_annotation_output_url', "")
TEST_DATA_IMAGE_TRANSCRIPTION = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('image_transcription', "")
TEST_DATA_IMAGE_TRANSCRIPTION_WITHOUT_ONTOLOGY = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('image_transcription_without_ontology', "")
TEST_DATA_IMAGE_TRANSCRIPTION_OUTPUT_UTL = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('image_transcription_output_url', "")



@pytest.fixture(scope="module")
def rp():
    username = get_test_data('test_ui_account', 'email')
    password = get_test_data('test_ui_account', 'password')

    rp = RP()
    rp.get_valid_sid(username, password)

    return rp


@pytest.mark.quality_audit_smoke
@pytest.mark.parametrize('cml_type, job_id',
                         [("image_annotation", TEST_DATA_SHAPE),
                          ("image_annotation_without_ontology", TEST_DATA_SHAPE_WITHOUT_ONTOLOGY),
                          ("image_annotation_output_url", TEST_DATA_SHAPE_OUTPUT_URL),
                          ("image_transcription", TEST_DATA_IMAGE_TRANSCRIPTION),
                          ("image_transcription_output_url", TEST_DATA_IMAGE_TRANSCRIPTION_OUTPUT_UTL),
                          ("image_transcription_without_ontology", TEST_DATA_IMAGE_TRANSCRIPTION_WITHOUT_ONTOLOGY)])
@allure.parent_suite('jobs/{job_id}/audit/units/aggregation')
def test_generate_aggregations_image_annotations_tools(rp, cml_type, job_id):
    rp_res = rp.generate_aggregation(job_id)
    rp_res.assert_response_status(200)
    assert rp_res.json_response == {'error': None, 'status': 'ok'}
    rp.wait_until_regenerate_aggregation("in_progress_version", job_id)
    rp_res_status = rp.get_ipa_audit_aggregation_status(job_id)
    rp_res_status.assert_response_status(200)
    assert "current_version" in rp_res_status.json_response, "The current version absent in response body "
    assert rp_res_status.json_response['flash_message'] is None, f"The Job with cml_type {cml_type} not generate aggregation"


@pytest.mark.parametrize('cml_type, job_id, unit_id, unit_id_without_judgment, node_position',
                         [("shapes", TEST_DATA_SHAPE, 2301904908, 2301904906, 0),
                          ("shapes", TEST_DATA_SHAPE_WITHOUT_ONTOLOGY, 2459821830, 2459821831, 0),
                          ("shapes", TEST_DATA_SHAPE_OUTPUT_URL, 2459821809, 2459821808, 1),
                          ("image_transcription", TEST_DATA_IMAGE_TRANSCRIPTION, 2458390124, 2458390123, 0),
                          ("image_transcription", TEST_DATA_IMAGE_TRANSCRIPTION_WITHOUT_ONTOLOGY, 2459821814, 2459821813, 1),
                          ("image_transcription", TEST_DATA_IMAGE_TRANSCRIPTION_OUTPUT_UTL, 2458390118, 2458390115, 0)])
@allure.parent_suite('jobs/{job_id}/audit/units/aggregation')
def test_view_details_image_annotations_tools(rp, cml_type, job_id, unit_id, unit_id_without_judgment, node_position):
    rp_res = rp.get_audit_info_for_unit(job_id, unit_id)
    rp_res.assert_response_status(200), "The unit with judgment not response for /audit "
    assert job_id == rp_res.json_response["job_id"]
    assert cml_type in rp_res.json_response["nodes"]["nodes"][node_position]["tag"]
    assert int(unit_id) == rp_res.json_response["unit_id"]
    rp_res_without_judgment = rp.get_audit_info_for_unit(job_id, unit_id_without_judgment)
    rp_res_without_judgment.assert_response_status(200), "The unit without judgment not response for /audit "
