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


TEST_DATA_AUDIO_ANNOTATION = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('audio_annotation', "")
TEST_DATA_AUDIO_TRANSCRIPTION = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('audio_transcription', "")
TEST_DATA_TEXT_ANNOTATION = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('text_annotation', "")
TEST_DATA_TEXT_RELATIONSHIP = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('text_relationship',"")
TEST_DATA_VIDEO_SHAPE = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('video_annotation', "")
TEST_DATA_TAXONOMY = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('taxonomy', "")


@pytest.fixture(scope="module")
def rp():
    username = get_test_data('test_ui_account', 'email')
    password = get_test_data('test_ui_account', 'password')

    rp = RP()
    rp.get_valid_sid(username, password)

    return rp


@pytest.mark.quality_audit_smoke
@pytest.mark.parametrize('cml_type, job_id',
                         [("audio_annotation", TEST_DATA_AUDIO_ANNOTATION),
                          ("text_annotation", TEST_DATA_TEXT_ANNOTATION),
                          ("text_relationship", TEST_DATA_TEXT_RELATIONSHIP),
                          ("video_annotation", TEST_DATA_VIDEO_SHAPE),
                          ("audio_transcription", TEST_DATA_AUDIO_TRANSCRIPTION),
                          ("taxonomy_tool", TEST_DATA_TAXONOMY)])
@allure.parent_suite('jobs/{job_id}/audit/units/aggregation')
def test_generate_aggregations_annotations_tools(rp, cml_type, job_id):
    rp_res = rp.generate_aggregation(job_id)
    rp_res.assert_response_status(200)
    assert rp_res.json_response == {'error': None, 'status': 'ok'}
    rp.wait_until_regenerate_aggregation('in_progress_version', job_id)
    rp_res_status = rp.get_ipa_audit_aggregation_status(job_id)
    rp_res_status.assert_response_status(200)
    assert "current_version" in rp_res_status.json_response, "The current version absent in response body "
    assert rp_res_status.json_response['flash_message'] is None, f"The Job with cml_type {cml_type} not generate aggregation"


@pytest.mark.parametrize('cml_type, job_id, unit_id, unit_id_without_judgment, node_position',
                         [("audio_annotation", TEST_DATA_AUDIO_ANNOTATION, 2459821793, 2459821792, 2),
                          ("text_annotation", TEST_DATA_TEXT_ANNOTATION, 2324281481, 2324281480, 0),
                          ("text_relationships", TEST_DATA_TEXT_RELATIONSHIP, 2482821213, 2482821212, 0),
                          ("video_shapes", TEST_DATA_VIDEO_SHAPE, 2459821530, 2459821529, 1),
                          ("audio_transcription", TEST_DATA_AUDIO_TRANSCRIPTION, 2546943975, 2546943976, 1),
                          ("taxonomy_tool", TEST_DATA_TAXONOMY, 2492672762, 2492672765, 1)])
@allure.parent_suite('jobs/{job_id}/audit/units/aggregation')
def test_view_details_annotations_tools(rp, cml_type, job_id, unit_id, unit_id_without_judgment, node_position):
    rp_res = rp.get_audit_info_for_unit(job_id, unit_id)
    rp_res.assert_response_status(200), "The unit with judgment not response for /audit "
    assert job_id == rp_res.json_response["job_id"]
    assert cml_type in rp_res.json_response["nodes"]["nodes"][node_position]["tag"]
    assert int(unit_id) == rp_res.json_response["unit_id"]
    rp_res_without_judgment = rp.get_audit_info_for_unit(job_id, unit_id_without_judgment)
    rp_res_without_judgment.assert_response_status(200), "The unit without judgment not response for /audit "
