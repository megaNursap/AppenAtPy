import pytest
import allure
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.webhook import Webhook
from adap.api_automation.utils.data_util import *
import logging
import time

LOGGER = logging.getLogger(__name__)
# disable test from regression until it's fixed
# pytestmark = [pytest.mark.regression_core, pytest.mark.adap_api_uat]
default_user = 'test_account'


def create_job(api_key):
    # create job
    new_job = Builder(api_key)
    res = new_job.create_job()
    res.assert_response_status(200)
    job_id = new_job.job_id
    assert job_id > 0, "Job ID cannot be null"
    return job_id


#@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_create_webhook():
    api_key = get_user_api_key(default_user)
    team_id = get_user_team_id(default_user)
    job_id = create_job(api_key)
    # print(f"Team ID {team_id}")
    webhooks = Webhook(api_key)
    webhooks.make_webhook(job_id, team_id).assert_response_status(201)
    webhooks.check_job_hooked(job_id).assert_response_status(200)
    webhooks.ignit_webhook().assert_response_status(200)



