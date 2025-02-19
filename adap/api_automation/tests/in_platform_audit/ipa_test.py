import random
import time

import pytest
import allure
from adap.settings import Config
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.in_platform_audit import IPA_API
from adap.api_automation.services_config.judgments import Judgments
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id
from adap.e2e_automation.services_config.job_api_support import generate_job_link

pytestmark = [
    pytest.mark.regression_ipa,
    pytest.mark.quality_audit_smoke
]

API_KEY = get_test_data('test_account', 'api_key')
EMAIL = get_test_data('test_account', 'email')
PASSWORD = get_test_data('test_account', 'password')
TEAM = get_user_team_id('test_account')
JWT = get_test_data('test_ui_account', 'jwt_token')

TEST_DATA = pytest.data.predefined_data['ipa_job']['what_is_greater'].get(pytest.env)
_ipa = IPA_API(API_KEY)


@pytest.fixture(scope="module")
def ipa_api_job():
    copied_job = Builder(API_KEY)

    copied_job_resp = copied_job.copy_job(TEST_DATA, "all_units")
    copied_job_resp.assert_response_status(200)

    job_id = copied_job_resp.json_response['id']
    copied_job.job_id = job_id
    copied_job.launch_job()
    copied_job.wait_until_status("running", max_time=60)
    time.sleep(120)

    j = Judgments(EMAIL, PASSWORD, env=pytest.env, internal=True)
    job_link = generate_job_link(job_id, API_KEY, pytest.env)

    Config.JOB_TYPE = 'what_is_greater'
    assignment_page = j.get_assignments(internal_job_url=job_link, job_id=job_id)
    j.contribute(assignment_page)
    time.sleep(60)
    return job_id


@pytest.mark.adap_api_uat
@allure.parent_suite('jobs/{job_id}/aggregations_distribution')
def test_get_aggregations_distribution_no_aggregation_ipa(ipa_api_job):
    res = _ipa.get_aggregations_distribution(ipa_api_job)
    res.assert_response_status(200)
    assert res.json_response == []


@pytest.mark.quality_audit_smoke
@pytest.mark.adap_api_uat
@allure.parent_suite('jobs/{job_id}/audit/units/aggregation')
def test_generate_aggregations_ipa(ipa_api_job):
    res = _ipa.generate_aggregation(ipa_api_job)
    res.assert_response_status(200)
    assert res.json_response == {'error': None, 'status': 'ok'}
    time.sleep(75)

@pytest.mark.adap_api_uat
@allure.parent_suite('jobs/{job_id}/aggregations_distribution')
def test_get_aggregations_distribution_ipa(ipa_api_job):
    res = _ipa.get_aggregations_distribution(ipa_api_job)
    res.assert_response_status(200)

    _max_retries = 100
    _try = 0
    content = res.json_response
    while str(content) == '[]' and _try < _max_retries:
        res = _ipa.get_aggregations_distribution(ipa_api_job)
        content = res.json_response
        time.sleep(2)
        _try += 1
    assert res.json_response[0]['name'] == 'what_is_greater'
    assert res.json_response[0]['aggregations_distribution']['total_count'] > 0
    assert int(res.json_response[0]['aggregations_distribution']['values'][0]['count']) + \
           int(res.json_response[0]['aggregations_distribution']['values'][1]['count']) == \
           res.json_response[0]['aggregations_distribution']['total_count']


@pytest.mark.adap_api_uat
@allure.parent_suite('jobs/{job_id}/search')
def test_search_units_for_audit_all_ipa(ipa_api_job):
    payload_all_units = {"filters":{"question":{"name":"what_is_greater","values":[]}},"pagination": {"page": 1, "per_page": 500}}
    res = _ipa.search_unit_for_audit(ipa_api_job, payload_all_units)
    res.assert_response_status(200)
    all_units = res.json_response

    assert all_units['pagination']['total_results'] == len(all_units['units'])
    assert all_units['units'][0].get('unit_id')
    assert all_units['units'][0]['audited'] is False
    assert all_units['units'][0].get('data')
    assert all_units['units'][0].get('fields')


@pytest.mark.adap_api_uat
@allure.parent_suite('jobs/{job_id}/audit/units/search')
def test_search_units_audited_filter_ipa(ipa_api_job):
    payload_audited = {"filters":{"question":{"name":"what_is_greater","values":[]},"audited": True}, "pagination": {"page": 1, "per_page": 100}}
    res = _ipa.search_unit_for_audit(ipa_api_job, payload_audited)
    res.assert_response_status(200)
    _units = res.json_response
    assert _units == {'pagination': {'per_page': 100, 'total_pages': 0, 'total_results': 0}, 'sda_columns': [],
                      'units': []}

    payload_not_audited = {"filters":{"question":{"name":"what_is_greater","values":[]}, "audited": False}, "pagination": {"page": 1, "per_page": 100}}
    res = _ipa.search_unit_for_audit(ipa_api_job, payload_not_audited)
    res.assert_response_status(200)
    all_units = res.json_response

    assert len(all_units['units']) == all_units['pagination']['total_results']

    assert all_units['units'][0].get('unit_id')
    assert all_units['units'][0]['audited'] is False
    assert all_units['units'][0].get('data')
    assert all_units['units'][0].get('fields')


@allure.parent_suite('jobs/{job_id}/audit/units/search')
def test_search_units_per_page_filter_ipa(ipa_api_job):
    for i in [1, 5, 10, 100]:
        payload_audited = {"filters":{"question": {"name":"what_is_greater","values":[]}}, "pagination": {"page": 1, "per_page": i}}

        res = _ipa.search_unit_for_audit(ipa_api_job, payload_audited)
        res.assert_response_status(200)
        _units = res.json_response
        assert len(_units['units']) == min(i, 15)


@allure.parent_suite('jobs/{job_id}/audit/units/{unit_id}')
def test_get_audit_info_for_unit_ipa(ipa_api_job):
    payload_audited = {"filters": {"question": {"name":"what_is_greater","values":[]}, "audited": False}, "pagination": {"page": 1, "per_page": 10}}
    res = _ipa.search_unit_for_audit(ipa_api_job, payload_audited)
    all_units = res.json_response['units']

    _index = random.randint(1, 9)
    total_all_units = len(all_units)
    assert total_all_units > _index, f"Random index {_index} is not less than total number of all units {total_all_units}"
    random_unit = all_units[_index]['unit_id']

    res = _ipa.get_audit_info_for_unit(ipa_api_job, random_unit)
    res.assert_response_status(200)
    assert res.json_response['unit_id'] == random_unit
    assert res.json_response['job_id'] == ipa_api_job


@pytest.mark.adap_api_uat
@pytest.mark.dependency()
@allure.parent_suite('jobs/{job_id}/audit/units/{unit_id}')
def test_add_audit_info_for_unit_correct_ipa(ipa_api_job):
    payload_find_units = {"filters": {"question":{"name":"what_is_greater", "values": ["col1", "col2"]}, "audited": False}, "pagination": {"page": 1, "per_page": 10}}

    res = _ipa.search_unit_for_audit(ipa_api_job, payload_find_units)

    all_units = res.json_response['units']

    _index = random.randint(0, len(all_units) - 1)
    random_unit = all_units[_index]['unit_id']
    payload = {
        "fields":
            {
                "what_is_greater": {
                    "correct": False,
                    "answers": ["col2"],
                    "reason": "Audited by api",
                    "custom_answers": [],
                    "fixed_reasons": []
                }
            }
    }

    res = _ipa.add_audit(ipa_api_job, random_unit, payload)  # 201
    res.assert_response_status(201)
    assert res.json_response == {'status': 'ok', 'error': None}

    res = _ipa.get_audit_info_for_unit(ipa_api_job, random_unit)
    res.assert_response_status(200)
    assert res.json_response['unit_id'] == random_unit
    assert res.json_response['team_id'] == TEAM
    assert res.json_response['job_id'] == ipa_api_job
    assert res.json_response.get('encrypted_unit_id')
    assert res.json_response.get('audited_at')

    assert res.json_response['fields']['what_is_greater']['audit'] == {
        "correct": False,
        "answers": ["col2"],
        "reason": "Audited by api",
        "custom_answers": [],
        "fixed_reasons": []
    }


@pytest.mark.dependency(depends=["test_add_audit_info_for_unit_correct_ipa"])
@allure.parent_suite('jobs/{job_id}/audit/units/search')
def test_search_units_audited_filter_true_ipa(ipa_api_job):
    payload_audited = {"filters": {"question":{"name":"what_is_greater", "values": ["col1", "col2"]}, "audited": True},  "pagination": {"page": 1, "per_page": 100}}

    res = _ipa.search_unit_for_audit(ipa_api_job, payload_audited)
    res.assert_response_status(200)
    _units = res.json_response
    assert len(_units['units']) == 1
    assert len(_units['units']) == _units['pagination']['total_results']

    assert _units['units'][0].get('unit_id')
    assert _units['units'][0]['audited'] is True


@pytest.mark.adap_api_uat
@pytest.mark.dependency(depends=["test_add_audit_info_for_unit_correct_ipa"])
@allure.parent_suite('')
def test_generate_report_ipa(ipa_api_job):
    res = _ipa.generate_ipa_report(ipa_api_job)
    res.assert_response_status(200)
    report_json = res.json_response

    assert report_json['version'] is not None
    assert report_json['status'] == 'generating'
    assert report_json['file_url'] is None
