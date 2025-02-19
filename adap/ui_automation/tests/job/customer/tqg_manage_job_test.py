"""
Test Questions Generator
"""
import time

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.workflow import Workflow
from adap.api_automation.utils.data_util import *

from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.ui_automation.services_config.job.job_quality import find_tq_job, generate_tq_for_job
from adap.ui_automation.utils.pandas_utils import collect_data_from_ui_table

pytestmark = pytest.mark.regression_tq

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')


@pytest.mark.tqg
def test_order_tq_for_running_job(app_test):
    job = Builder(API_KEY)
    job.create_simple_job()
    res = job.launch_job()
    res.assert_response_status(200)

    res = job.get_json_job_status()
    res.assert_response_status(200)

    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(job.job_id)

    app_test.job.open_tab("QUALITY")

    app_test.job.quality.click_generate_tq()
    app_test.job.quality.order_tq(5, "Appen Trusted Contributors")
    app_test.navigation.click_link('Order')


@pytest.mark.tqg
def test_order_tq_for_canceled_job(app_test):
    job = Builder(API_KEY)

    job.create_simple_job()
    job.launch_job()

    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    job.cancel_job()

    res = job.get_json_job_status()
    res.assert_response_status(200)

    assert 'canceled' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "canceled")

    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(job.job_id)

    app_test.job.open_tab("QUALITY")

    app_test.verification.text_present_on_page("Currently Unavailable")

