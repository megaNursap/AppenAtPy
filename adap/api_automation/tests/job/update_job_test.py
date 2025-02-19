import time

import pytest
import allure
import logging
from dictor import dictor
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user_api_key, get_data_file, count_row_in_file
from adap.api_automation.utils.helpers import retry

LOGGER = logging.getLogger(__name__)

pytestmark = [pytest.mark.regression_core, pytest.mark.new_auth, pytest.mark.adap_api_uat]

USERS = pytest.data.users
API_KEY = get_user_api_key('test_account')


@pytest.fixture(scope="module")
def create_simple_job():
    global job_id

    job = Builder(API_KEY)
    job.create_simple_job()
    job_id = job.job_id


@allure.severity(allure.severity_level.CRITICAL)
@allure.parent_suite('/jobs/{job_id}:put')
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.flaky(reruns=3)
@pytest.mark.devspace
def test_update_job_title():
    payload = {
        'job': {
            'title': "Job for updated",
            'instructions': "Test jobInstructions TB updated"}
    }
    new_job = Builder(api_key=API_KEY, payload=payload)
    new_job.create_job()
    _job_id = new_job.job_id

    cml_sample_updated = '''<cml:text label="Please enter the correct ZIP in 5-letter format." validates="required maxLength:5 clean:['uppercase']" />'''

    updated_payload = {
        'job': {
            'title': "Updated",
            'instructions': "Updated",
            'cml': cml_sample_updated
        }
    }
    job = Builder(api_key=API_KEY, payload=updated_payload)
    resp = job.update_job(_job_id)
    resp.assert_job_title("Updated")
    assert resp.json_response['instructions'] == updated_payload['job'][
        'instructions'], "Expected title: %s \n Actual status: " \
                         "%s" % (updated_payload['job']['instructions'], resp.json_response['title'])


@allure.severity(allure.severity_level.CRITICAL)
@allure.parent_suite('/jobs/{job_id}:put')
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.builder
@pytest.mark.flaky(reruns=3)
def test_update_job_cml():
    cml_sample = '''<cml:text label="Please enter the correct ZIP in 2-letter format." validates="required maxLength:2 clean:['uppercase']" />'''
    cml_sample_updated = '''<cml:text label="Please enter the correct ZIP in 5-letter format." validates="required maxLength:5 clean:['uppercase']" />'''

    payload = {
        'job': {
            'title': "Job for updated",
            'instructions': "Test job Instructions TB updated",
            'cml': cml_sample

        }
    }
    new_job = Builder(api_key=API_KEY, payload=payload)
    new_job.create_job()
    _job_id = new_job.job_id

    time.sleep(1)

    cml_payload = {
        'job': {
            'title': "TB updated",
            'instructions': "TB updated",
            'cml': cml_sample_updated

        }}

    job = Builder(api_key=API_KEY, payload=cml_payload)
    resp = job.update_job(_job_id)

    resp.assert_response_status(200)
    assert resp.json_response['cml'] == cml_sample_updated


# TODO force verification
@allure.severity(allure.severity_level.BLOCKER)
@allure.parent_suite('/jobs/{job_id}/upload:put')
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.builder
@pytest.mark.flaky(reruns=3)
@pytest.mark.devspace
def test_upload_json():
    sample_file = get_data_file('/sample_data.json')
    rows_in_json = count_row_in_file(sample_file)

    job = Builder(API_KEY)
    resp = job.create_job_with_json(sample_file)
    resp.assert_response_status(200)

    time.sleep(3)

    add_file = get_data_file("/add_sample_data.json")
    new_rows = count_row_in_file(add_file)

    upload_data_rest = job.upload_data(add_file)
    upload_data_rest.assert_response_status(200)

    job_status = job.get_job_status(job.job_id).json_response
    assert (rows_in_json + new_rows) == job_status['all_units']


@allure.severity(allure.severity_level.NORMAL)
@allure.parent_suite('/jobs/{job_id}/upload:put')
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.flaky(reruns=3)
def test_upload_empty_json():
    sample_file = get_data_file('/sample_data.json')
    rows_in_json = count_row_in_file(sample_file)

    job = Builder(API_KEY)
    resp = job.create_job_with_json(sample_file)
    resp.assert_response_status(200)

    time.sleep(3)

    add_file = get_data_file("/empty_json.json")

    upload_data_rest = job.upload_data(add_file)
    upload_data_rest.assert_response_status(200)

    job_status = job.get_job_status(job.job_id).json_response

    assert rows_in_json == job_status['all_units']


@allure.severity(allure.severity_level.BLOCKER)
@allure.parent_suite('/jobs/{job_id}/upload:put')
# @allure.issue("https://crowdflower.atlassian.net/browse/EE-1149")
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.builder
# @pytest.mark.bug
# @pytest.mark.skip(reason='BUG')
@pytest.mark.flaky(reruns=3)
@pytest.mark.skipif(pytest.flaky == "false", reason="Flaky test")
def test_upload_csv():
    job = Builder(API_KEY)
    resp = job.create_job()
    resp.assert_response_status(200)

    sample_file = get_data_file("/dod_data.csv")

    upload_data_rest = job.upload_data(sample_file, data_type='csv')
    upload_data_rest.assert_response_status(200)

    time.sleep(5)
    count_res = job.count_rows()
    assert 5 == count_res.json_response['count'], "Expected number of rows: 5 \n Actual number: %s" % \
                                                  count_res.json_response['count']


@allure.severity(allure.severity_level.CRITICAL)
@allure.parent_suite('/jobs/{job_id}/upload:put')
@pytest.mark.uat_api
@pytest.mark.parametrize('file_type, file, num_rows',
                         [("96K", "Appen_Tagging_100_200k_6_17_2021.csv", 96853),
                          ("250K", "large_file_numbers_250K.csv", 256169)])
@pytest.mark.skipif(pytest.flaky == "false", reason="Flaky test")
def test_upload_large_csv(file_type, file, num_rows):
    job = Builder(API_KEY)
    resp = job.create_job()
    resp.assert_response_status(200)

    sample_file = get_data_file("/large_files/" + file)

    upload_data_rest = job.upload_data(sample_file, data_type='csv', large_file=True)
    assert upload_data_rest.status_code == 200

    time.sleep(10)
    current = 0
    times = 0
    count_res = job.count_rows()

    while num_rows != current and times <= 500:
        count_res = job.count_rows()
        current = count_res.json_response['count']
        times += 1

    assert num_rows == count_res.json_response[
        'count'], "Expected number of rows: {num_rows} \n Actual number: {actual}".format(num_rows=num_rows, actual=
    count_res.json_response['count'])


@allure.severity(allure.severity_level.NORMAL)
@allure.parent_suite('/jobs/{job_id}/gold:put')
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.flaky(reruns=3)
@pytest.mark.skipif(pytest.flaky == "false", reason="Flaky test")
# @pytest.mark.skip(reason='bug CW-7687')
def test_convert_uploaded_tq():
    job = Builder(API_KEY)
    job.create_simple_job()

    job_status = job.get_job_status().json_response
    assert job_status['golden_units'] == 0

    resp_convert_tq = job.convert_uploaded_tq()
    resp_convert_tq.assert_response_status(200)
    assert {'success': {'message': 'The job will be updated in the background.'}} == resp_convert_tq.json_response

    def check_units():
        job_status = job.get_job_status().json_response
        assert job_status['golden_units'] == 8

    retry(check_units, max_retries=3)


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.fed_api
@pytest.mark.flaky(reruns=3)
@pytest.mark.devspace(reruns=3)
def test_set_task_payment(create_simple_job):
    update_job = Builder(API_KEY)
    update_job.job_id = job_id
    res = update_job.set_job_task_payment(20)

    assert res.json_response['payment_cents'] == 20


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.fed_api
@pytest.mark.flaky(reruns=3)
@pytest.mark.devspace(reruns=3)
@pytest.mark.parametrize('param_name, payload, value',
                         [
                             ("judgments_per_unit", {"job[judgments_per_unit]": 6}, 6),
                             ("quiz_length_configured", {"job[quiz_length_configured]": True}, True),
                             ("quiz_length", {"job[quiz_length]": 5}, 5),
                             ("options.req_ttl_in_seconds", {"job[options][req_ttl_in_seconds]": 5000}, 5000),
                             ("units_per_assignment", {"job[units_per_assignment]": 1}, 1),
                             ("variable_judgments_mode", {"job[variable_judgments_mode]": "auto_confidence"},
                              "auto_confidence"),
                             ("options.dynamic_judgment_fields", "job[options][dynamic_judgment_fields][]=question", ["question"]),
                             ("max_judgments_per_unit", {"job[max_judgments_per_unit]": 2}, 2),
                             ("min_unit_confidence", {"job[min_unit_confidence]": 0.5}, 0.5),
                             ("units_remain_finalized", {"job[units_remain_finalized]": True}, True),
                             ("units_remain_finalized", {"job[units_remain_finalized]": False}, False),
                             ("schedule_fifo", {"job[schedule_fifo]": True}, None),
                             ("schedule_fifo", {"job[schedule_fifo]": True}, None)
                         ])
def test_update_job(param_name, payload, value, create_simple_job):
    """
    note: schedule_fifo is not returned in the job json from builder
    """
    update_job = Builder(API_KEY)
    update_job.job_id = job_id

    res = update_job.update_job_settings(payload)
    assert dictor(res.json_response, param_name) == value


@allure.severity(allure.severity_level.MINOR)
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.fed_api
@pytest.mark.flaky(reruns=3)
@pytest.mark.devspace(reruns=3)
def test_get_legend(create_simple_job):
    job = Builder(API_KEY)
    job.job_id = job_id
    res = job.get_legend()
    assert res.json_response == {
        'is_this_funny_or_not': {'Is this funny or not?': {'funny': 'funny', 'not_funny': 'not funny'}}}


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.flaky(reruns=3)
@pytest.mark.devspace(reruns=3)
@pytest.mark.parametrize('param_name',
                         ["included_countries", "excluded_countries"])
def test_set_countries(param_name):
    _job = Builder(API_KEY)
    _resp = _job.create_simple_job()
    assert _resp, "Job was not created"
    countries_codes = "[\"US\", \"CX\", \"GH\"]"

    _resp_job = _job.update_job_settings_list(param_name, countries_codes)
    _resp_job.assert_response_status(200)

    _resp_included_countries = dictor(_resp_job.json_response, param_name)

    for code in _resp_included_countries:
        assert code['code'] in countries_codes
        LOGGER.info("{code} is in the list of countries".format(code=code['code']))


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.flaky(reruns=3)
@pytest.mark.devspace(reruns=3)
@pytest.mark.parametrize('param_name, countries_codes',
                         [("included_countries", "[US, CX, GH]"),
                          ("included_countries", []),
                          ("included_countries", 3),
                          ("excluded_countries", "[US, CX, GH]"),
                          ("excluded_countries", []),
                          ("excluded_countries", 3)
                          ])
def test_set_countries_with_invalid_param(param_name, countries_codes):
    _job = Builder(API_KEY)
    _resp = _job.create_simple_job()
    assert _resp, "Job was not created"

    _resp_job = _job.update_job_settings_list(param_name, countries_codes)
    _resp_job.assert_response_status(422)
    _resp_job.assert_error_message_v2(f"Invalid format of {param_name} attribute")