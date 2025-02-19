import pytest
import allure
import random
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user_api_key, get_user_worker_id, generate_random_string


pytestmark = [pytest.mark.regression_core, pytest.mark.new_auth, pytest.mark.adap_api_uat]

predifined_jobs = pytest.data.predefined_data


# test is deprecated
# @allure.parent_suite('/jobs/{job_id}/workers/{contributor_id}/notify:post')
# @pytest.mark.uat_api
# @pytest.mark.skip_hipaa
# @allure.issue("https://appen.atlassian.net/browse/JW-1396", "BUG JW-1396")
# def test_notify_contributor():
#     api_key = get_user_api_key('test_predefined_jobs')
#     worker_id = pytest.data.predefined_data['notify_contributor'][pytest.env]
#     job_id = pytest.data.predefined_data['notify_contributor'][pytest.env]
#
#     job = Builder(api_key)
#     job.job_id =job_id
#
#     message = "Message to notify contributor" + generate_random_string(5)
#
#     resp = job.notify_contributor(message, worker_id)
#     resp.assert_response_status(200)
#     resp.assert_success_message_v2('Contributor was successfully notified.')


# # TODO: understand which channels allow bonuses for contributors. This may not be possible in sandbox and QA
# @allure.parent_suite('/jobs/{job_id}/workers/{contributor_id}/bonus:post')
# @pytest.mark.uat_api
# @pytest.mark.skip(reason='Only for local run')
# def test_pay_contributor_bonus():
#     """ amount is in cents. ie: 500 = $5 """
#     api_key = get_user_api_key('test_account')
#     worker_id = get_user_worker_id('test_contributor_task')
#
#     # Using the predefined job where the contributor has submitted a judgement
#     # If you try to give a bonus for a contributor that hasn't submitted a judgement in your job the
#     # the response if "{"error": {"message":"We couldn't find what you were looking for."}"
#     job_id = predifined_jobs['job_with_judgments'][pytest.env]
#     job = Job(api_key)
#     job.job_id = job_id
#
#     # random dollar amount between $5 - $20
#     # $20 seems to be the max you pay a contributor
#     amount = random.randint(500, 2000)
#
#     # This is the current result in sandbox & qa
#     resp = job.pay_bonus_to_contributor(worker_id, str(amount))
#     resp.assert_response_status(400)
#     resp.assert_error_message('Unable to bonus contributor: This channel does not support bonuses')


# Run this at your risk!! Skipping by default
# @allure.parent_suite('/jobs/{job_id}/workers/{contributor_id}/reject:put')
# @pytest.mark.uat_api
# @pytest.mark.skip(reason='Only for local run')
# def test_reject_contributor():
#     api_key = get_user_api_key('test_account')
#     worker_id = get_user_worker_id('test_contributor')
#
#     job_id = predifined_jobs['job_with_judgments'][pytest.env]
#     job = Job(api_key)
#     job.job_id = job_id
#
#     resp = job.reject_contributor(worker_id, "reason for rejecting contributor")
#     resp.assert_response_status(200)
#     resp.assert_success_message_v2("Rejecting contributor... this operation can take up to 10 minutes")


# TODO: Contributor account should be generated for FED and update the test_contributor_task information
@allure.severity(allure.severity_level.MINOR)
@allure.parent_suite('/jobs/{job_id}/workers/contributor_id:put')
@pytest.mark.uat_api
@pytest.mark.skip_hipaa
def test_flag_a_contributor():
    api_key = get_user_api_key('test_account')
    worker_id = get_user_worker_id('test_contributor_task')

    job_id = predifined_jobs['job_with_judgments'][pytest.env]
    job = Builder(api_key)
    job.job_id = job_id

    flag = "Flag on contributor" + generate_random_string(5)

    resp = job.flag_contributor(worker_id, flag)
    resp.assert_response_status(200)

