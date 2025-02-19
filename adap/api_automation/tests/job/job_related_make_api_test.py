"""
https://appen.atlassian.net/browse/QED-2511
"""
import allure
import pytest
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.make import Make
from adap.api_automation.utils.data_util import *

API_KEY = get_user_api_key('test_account')
users = pytest.data.users
pytestmark = [pytest.mark.regression_core, pytest.mark.make, pytest.mark.adap_api_uat]


@pytest.fixture(scope="module")
def create_sample_job():
    job = Builder(API_KEY)
    resp = job.create_simple_job()
    assert resp is True
    job_id = job.job_id
    return job_id


@allure.severity(allure.severity_level.NORMAL)
def test_get_cml_tag(create_sample_job):
    make = Make(API_KEY)
    resp = make.get_jobs_cml_tag(create_sample_job)
    resp.assert_response_status(200)
    assert "name" in resp.json_response[0]
    assert "label" in resp.json_response[0]
    assert "type" in resp.json_response[0]
    assert "attributes" in resp.json_response[0]
    assert "aggregations" in resp.json_response[0]


@allure.severity(allure.severity_level.NORMAL)
def test_job_setting(create_sample_job):
    make = Make(API_KEY)
    resp = make.get_jobs_setting(create_sample_job)
    resp.assert_response_status(200)
    assert "webhook_uri" in resp.json_response
    assert "auto_order" in resp.json_response
    assert "auto_order_timeout" in resp.json_response
    assert "bypass_estimated_fund_limit" in resp.json_response
    assert "bypass_estimated_fund_limit_updatable" in resp.json_response
    assert "auto_order_timeout" in resp.json_response
    assert "units_remain_finalized" in resp.json_response
    assert "schedule_fifo" in resp.json_response


@allure.severity(allure.severity_level.NORMAL)
def test_job_dashboard(create_sample_job):
    make = Make(API_KEY)
    resp = make.get_dashboard(create_sample_job)
    resp.assert_response_status(200)
    assert "tq_candidate_state" in resp.json_response
    assert "internal_channel_link" in resp.json_response
    assert "progress_info" in resp.json_response
