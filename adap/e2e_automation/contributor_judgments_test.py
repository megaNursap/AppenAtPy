import time

import pytest

from adap.e2e_automation.services_config.contributor_ui_support import get_judgments, generate_judgments_for_job
from adap.api_automation.utils.data_util import *
from adap.e2e_automation.services_config.job_api_support import create_job_from_config_api, generate_job_link
from adap.e2e_automation.job_examples.simple_job import config

pytestmark = [pytest.mark.e2e_submit_judgments, pytest.mark.ui_uat]

api_key = get_user_api_key('test_ui_account')
customer_name = get_user_email('test_ui_account')
customer_password = get_user_password('test_ui_account')


@pytest.fixture(scope="module")
def create_simple_job():
    global job_id
    job_id = create_job_from_config_api(config, pytest.env, api_key)


@pytest.mark.skipif(pytest.flaky == "false", reason="Flaky test")
def test_contributor_submit_judgments(app_test, create_simple_job):
    email = get_user_info('test_contributor_task')['email']
    password = get_user_password('test_contributor_task')
    user_name = get_user_info('test_contributor_task')['user_name']
    worker_id = get_user_info('test_contributor_task')['worker_id']
    job_link = generate_job_link(job_id, api_key, pytest.env)
    generate_judgments_for_job(pytest.env,job_link, email, password)
    app_test.driver.delete_all_cookies()
    app_test.user.logout()

    app_test.user.login_as_customer(user_name=customer_name, password=customer_password)
    app_test.verification.current_url_contains("client")

    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(job_id)
    app_test.job.open_tab("MONITOR")

    app_test.job.monitor.open_tab("Contributors")
    time.sleep(10)
    app_test.verification.text_present_on_page(worker_id)
