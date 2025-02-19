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

TEST_DATA_TEXT = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('text', "")
TEST_DATA_TEXTAREA = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('textarea', "")
TEST_DATA_CHECKBOXES = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('checkboxes', "")
TEST_DATA_SELECT = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('select', "")
TEST_DATA_RADIO = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('radio')
TEST_DATA_RATINGS = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('ratings')


@pytest.fixture(scope="module")
def rp():
    username = get_test_data('test_ui_account', 'email')
    password = get_test_data('test_ui_account', 'password')

    rp = RP()
    rp.get_valid_sid(username, password)

    return rp


@pytest.mark.quality_audit_smoke
@pytest.mark.parametrize('cml_type, job_id',
                         [("text", TEST_DATA_TEXT),
                          ("textarea", TEST_DATA_TEXTAREA),
                          ("checkboxes", TEST_DATA_CHECKBOXES),
                          ("select", TEST_DATA_SELECT),
                          ("radio", TEST_DATA_RADIO),
                          ("ratings", TEST_DATA_RATINGS)
                         ])
@allure.parent_suite('jobs/{job_id}/audit/status')
def test_generate_aggregations_text_select_checkboxes(rp, cml_type, job_id):
    rp_res = rp.generate_aggregation(job_id)
    rp_res.assert_response_status(200)
    assert rp_res.json_response == {'error': None, 'status': 'ok'}
    rp.wait_until_regenerate_aggregation("in_progress_version", job_id)
    rp_res_status = rp.get_ipa_audit_aggregation_status(job_id)
    rp_res_status.assert_response_status(200)
    assert "current_version" in rp_res_status.json_response, "The current version absent in response body "
    assert rp_res_status.json_response['flash_message'] is None, f"The Job with cml_type {cml_type} not generate aggregation"


@pytest.mark.parametrize('cml_type, job_id, unit_id, unit_id_no_answer, node_position',
                         [("text", TEST_DATA_TEXT, 2296277230, 2296277229, 1),
                          ("textarea", TEST_DATA_TEXTAREA, 2459920847, 2459920843, 4),
                          ("checkboxes", TEST_DATA_CHECKBOXES, 2303860175, 2303860174, 1),
                          ("select", TEST_DATA_SELECT, 2296277183, 2296277182, 1),
                          ("radio", TEST_DATA_RADIO, 2459919796, 2459919797, 2),
                          ("ratings", TEST_DATA_RATINGS, 2296277210, 2296277209, 1),
                          ])
@allure.parent_suite('jobs/{job_id}/audit/units/audit')
def test_view_details_text_select_checkboxes(rp, cml_type, job_id, unit_id, unit_id_no_answer, node_position):
    rp_res = rp.get_audit_info_for_unit(job_id, unit_id)
    rp_res.assert_response_status(200),  "The unit with judgment not response for /audit "
    assert job_id == rp_res.json_response["job_id"]
    assert cml_type in rp_res.json_response["nodes"]["nodes"][node_position]["tag"]
    assert unit_id == rp_res.json_response["unit_id"]
    rp_res_without_judgment = rp.get_audit_info_for_unit(job_id, unit_id_no_answer)
    rp_res_without_judgment.assert_response_status(200), "The unit without judgment not response for /audit "
