"""
Test contributor can submit judgments
"""
import time
import pytest
import json
from adap.api_automation.utils.data_util import *
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.data import annotation_tools_cml as data
from adap.ui_automation.utils.selenium_utils import find_element

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')

pytestmark = [
    pytest.mark.fed_ui,
    pytest.mark.adap_ui_uat,
    pytest.mark.adap_uat,
    pytest.mark.cml_group_aggregation
]


@pytest.fixture(scope="module")
def tx_job(app):
    job = JobAPI(API_KEY)
    job.create_job_with_cml(data.cml_group_aggregation)
    job_id = job.job_id
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    data_file = get_data_file('/cml_group_aggregation/group_aggregation.csv')
    app.job.data.upload_file(data_file)

    if pytest.env == 'fed':
        app.job.open_action("Settings")
        app.navigation.click_link("Select Contributor Channels")
        app.job.select_hosted_channel_by_index(save=True)

    job.launch_job()
    job = JobAPI(API_KEY, job_id=job_id)
    job.wait_until_status('running', 80)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    app.user.logout()
    return job_id


def test_contributor_submit_judgement(app, tx_job):
    job_link = generate_job_link(tx_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    # app.user.close_guide()
    time.sleep(2)
    app.group_aggregation.add_another_by_index(0)
    app.group_aggregation.add_another_by_index(2)
    first_name_input = app.group_aggregation.get_input_text_field('output_first_name')
    last_name_input = app.group_aggregation.get_input_text_field('output_last_name')
    assert len(first_name_input) == 7
    assert len(last_name_input) == 7
    for i in range(0, 6):
        first_name_input[i].send_keys("first" + str(i))
        time.sleep(1)
        last_name_input[i].send_keys("last" + str(i))
        time.sleep(1)
    app.group_aggregation.submit_page()
    app.verification.text_present_on_page('This field is required.')

    first_name_input[6].send_keys("first6")
    last_name_input[6].send_keys("last6")
    app.group_aggregation.submit_page()
    app.verification.text_present_on_page('There is no work currently available in this task.')
