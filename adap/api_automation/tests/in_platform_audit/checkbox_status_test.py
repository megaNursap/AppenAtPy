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

TEST_DATA_CHECKBOX = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('checkbox', "")
TEST_DATA_CHECKBOX_VALUE_ATT = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('checkbox_value_att', "")

@pytest.fixture(scope="module")
def rp():
    username = get_test_data('test_ui_account', 'email')
    password = get_test_data('test_ui_account', 'password')

    rp = RP()
    rp.get_valid_sid(username, password)

    return rp


@pytest.mark.quality_audit_smoke
@pytest.mark.parametrize('cml_type, job_id, name',
                         [("checkbox", TEST_DATA_CHECKBOX, "is_fruit"),
                          ("checkbox_value_att", TEST_DATA_CHECKBOX, "is_number")]
                         )
@allure.parent_suite('jobs/{job_id}/audit/status')
def test_generate_aggregations_checkbox(rp, cml_type, job_id, name):
    payload = {"filters": {"question": {"name": name, "values": []}}, "per_page": 500}
    rp_search = rp.search_unit_for_audit(job_id, payload)
    rp_search.assert_response_status(200), f"The filter doesn't work for name {name}"
    rp_res = rp.generate_aggregation(job_id)
    rp_res.assert_response_status(200), "Aggregation NOT generated"
    assert rp_res.json_response == {'error': None, 'status': 'ok'}
    rp.wait_until_regenerate_aggregation("in_progress_version", job_id)
    rp_res_status = rp.get_ipa_audit_aggregation_status(job_id)
    rp_res_status.assert_response_status(200)
    assert "current_version" in rp_res_status.json_response, "The current version absent in response body "
    assert rp_res_status.json_response['flash_message'] is None, f"The Job with cml_type {cml_type} not generate aggregation"


@pytest.mark.parametrize('cml_type, job_id, unit_id, unit_id_no_answer',
                         [("checkbox", TEST_DATA_CHECKBOX, 2295310306, 2295310305)])
@allure.parent_suite('jobs/{job_id}/audit/units/audit')
def test_view_details_checkbox(rp, cml_type, job_id, unit_id, unit_id_no_answer):
    rp_res = rp.get_audit_info_for_unit(job_id, unit_id)
    rp_res.assert_response_status(200), "The unit with judgment not response for /audit "
    assert job_id == rp_res.json_response["job_id"]
    assert cml_type in rp_res.json_response["nodes"]["nodes"][1]["tag"]
    assert unit_id == rp_res.json_response["unit_id"]
    rp_res_without_judgment = rp.get_audit_info_for_unit(job_id, unit_id_no_answer)
    rp_res_without_judgment.assert_response_status(200), "The unit without judgment not response for /audit "
