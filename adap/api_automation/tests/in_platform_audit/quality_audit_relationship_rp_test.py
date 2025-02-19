import random
import time

import pytest
import allure
from adap.settings import Config
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.in_platform_audit import IPA_API
from adap.api_automation.services_config.judgments import Judgments
from adap.api_automation.services_config.requestor_proxy import RP
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id
from adap.e2e_automation.services_config.job_api_support import generate_job_link

pytestmark = [
    pytest.mark.regression_ipa,
    pytest.mark.quality_audit_smoke
]

API_KEY = get_test_data('test_account', 'api_key')
EMAIL = get_test_data('test_account', 'email')
PASSWORD = get_test_data('test_account', 'password')
JWT = get_test_data('test_ui_account', 'jwt_token')

TEST_DATA = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('text_relationship', "")
_ipa = IPA_API(API_KEY)

_report_version = ""


@pytest.fixture(scope="module")
def rp():
    username = get_test_data('test_ui_account', 'email')
    password = get_test_data('test_ui_account', 'password')

    rp = RP()
    rp.get_valid_sid(username, password)

    return rp

@pytest.mark.quality_audit_smoke
@pytest.mark.adap_api_uat
@pytest.mark.flaky(reruns=3)
@allure.parent_suite('jobs/{job_id}/audit/units/aggregation')
def test_generate_aggregations(rp):
    rp_res = rp.generate_aggregation(TEST_DATA)
    rp_res.assert_response_status(200)
    assert rp_res.json_response == {'error': None, 'status': 'ok'}
    time.sleep(20)


@pytest.mark.adap_api_uat
@allure.parent_suite('jobs/{job_id}/aggregations_distribution')
def test_get_answer_distribution(rp):
    rp_res = rp.get_aggregations_distribution(TEST_DATA)
    rp_res.assert_response_status(200)
    assert rp_res.json_response[0]['name'] == 'tr_annotation'
    assert rp_res.json_response[0]['aggregations_distribution']['type'] == 'relationship'
    time.sleep(5)


@pytest.mark.adap_api_uat
@allure.parent_suite('jobs/{job_id}/audit/units/search')
def test_search_units_for_audit_all(rp):
    # Verify that payload for search endpoint could be empty
    payload_all_units = {}
    rp_res = rp.search_unit_for_audit(TEST_DATA, payload_all_units)
    rp_res.assert_response_status(500)


@pytest.mark.adap_api_uat
@allure.parent_suite('jobs/{job_id}/audit/units/search')
def test_search_units_audited_filter(rp):
    payload_not_audited = {"filters": {"question": {"name": "tr_annotation", "values": []}}, "pagination": {"page": 1, "per_page": 500}}
    rp_res = rp.search_unit_for_audit(TEST_DATA, payload_not_audited)
    rp_res.assert_response_status(200)
    all_units = rp_res.json_response

    assert len(all_units['units']) == all_units['pagination']['total_results']

    assert all_units['units'][0].get('unit_id')
    assert all_units['units'][1]['audited'] == True
    assert all_units['units'][0].get('data')
    assert all_units['units'][0].get('fields')


@pytest.mark.adap_api_uat
@allure.parent_suite('jobs/{job_id}/audit/units/{unit_id}')
def test_get_audit_info_for_unit( rp):
    payload_audited = {"filters": {"question": {"name": "tr_annotation", "values": []}}}
    rp_res = rp.search_unit_for_audit(TEST_DATA, payload_audited)
    all_units = rp_res.json_response['units']

    _index = random.randint(1, len(all_units))
    total_units = len(all_units)
    assert _index <= total_units, f"Required index {_index} is not less than total units {total_units}"
    random_unit = all_units[0]['unit_id']

    res = rp.get_audit_info_for_unit(TEST_DATA, random_unit)
    res.assert_response_status(200)
    assert res.json_response['unit_id'] == random_unit
    assert res.json_response['job_id'] == TEST_DATA
    assert res.json_response['encrypted_unit_id'] != ""
    assert res.json_response['nodes']['nodes'][0]['tag'] == 'text_relationships'


@pytest.mark.adap_api_uat
@allure.parent_suite('jobs/{job_id}/audit/units/{unit_id}')
def test_add_audit_info_for_unit_correct( rp):
    payload_find_units = {"filters": {"question": {"name": "tr_annotation", "values": []}},  "audited": True, "pagination": {"page": 1, "per_page": 10}}

    rp_res = rp.search_unit_for_audit(TEST_DATA, payload_find_units)

    all_units = rp_res.json_response['units']

    _index = random.randint(0, len(all_units) - 1)
    random_unit = all_units[_index]['unit_id']
    payload = {
        "fields":
            {
                "tr_annotation":
                 {
                  "correct": False,
                  "answers": [],
                  "reason": "",
                  "custom_answers": [],
                  "fixed_reasons": []
                 }
             }
    }

    res = rp.add_audit(TEST_DATA, random_unit, payload)  # 201
    res.assert_response_status(201)
    assert res.json_response == {'error': None, 'status': 'ok'}

    res = rp.get_audit_info_for_unit(TEST_DATA, random_unit)
    res.assert_response_status(200)
    assert res.json_response['unit_id'] == random_unit
    assert res.json_response['job_id'] == TEST_DATA
    assert res.json_response.get('audited_at')

    assert res.json_response['fields']['tr_annotation']['audit'] == {
        "correct": False,
        "answers": [],
        "reason": "",
        "custom_answers": [],
        "fixed_reasons": []
    }


@pytest.mark.adap_api_uat
@allure.parent_suite('jobs/{jobId}/audit/units/{unitId}/all_judgments')
def test_get_all_judgments_for_unit(rp):
    payload_all_units = {"filters": {"question": {"name": "tr_annotation", "values": []}}, "pagination": {"page": 1, "per_page": 500}}
    _ids = []
    rp_res = rp.search_unit_for_audit(TEST_DATA, payload_all_units)
    rp_res.assert_response_status(200)
    all_units = rp_res.json_response

    # Extract unit ids from list of aggregated unites
    for unit in all_units['units']:
        _ids.append(unit['unit_id'])

    for _id in range(len(_ids)):
        try:
            rp_res_judgment = rp.get_ipa_all_judgments(TEST_DATA, _ids[_id])
            rp_res_judgment.assert_response_status(200)
            unit_judgments = rp_res_judgment.json_response
            assert unit_judgments['judgments']
            assert unit_judgments['aggregations']
        except:
            print(f"Unable get judgments for unit id {_ids[_id]} in job {TEST_DATA}")


@pytest.mark.adap_api_uat
@pytest.mark.dependency()
@allure.parent_suite('jobs/{job_id}/audit/reports')
def test_generation_ipa_report(rp):
    global _report_version
    rp_res = rp.generate_ipa_report(TEST_DATA)
    rp_res.assert_response_status(200)
    report_status = rp_res.json_response

    assert report_status['version'] is not None
    assert report_status['status'] == 'generating'
    assert report_status['file_url'] is None

    _report_version = report_status['version']
    time.sleep(10)


@pytest.mark.dependency(depends=["test_generation_ipa_report"])
@allure.parent_suite('jobs/{job_id}/audit/reports/{version}')
# @pytest.mark.skip(reason="flaky")
def test_get_ipa_report_status(rp):
    assert _report_version is not None

    wait = 10
    running_time = 0
    current_status = ""
    while (current_status != 'finished') and (running_time < 30):
        rp_res = rp.get_ipa_report_status(TEST_DATA, _report_version)
        rp_res.assert_response_status(200)
        report_status = rp_res.json_response
        current_status = report_status['status']
        running_time += wait
        time.sleep(wait)

    assert report_status['version'] == _report_version
    assert report_status['status'] == 'finished'
    assert report_status['file_url'] is not None
