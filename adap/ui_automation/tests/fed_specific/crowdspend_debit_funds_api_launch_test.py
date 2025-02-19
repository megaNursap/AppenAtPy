"""
This test covers 3 cases in https://appen.atlassian.net/browse/DED-2020
QA automation ticket https://appen.atlassian.net/browse/QED-1628
1. Choose host channel, launch job via API with on demand, call get balance api for team, make sure no fund debit.
Above test will be run on both cf_internal user and non cf internal user who is in another team
"""

import time
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder as JobAPI

pytestmark = pytest.mark.fed_ui


def test_launch_via_api_debit_funds(app):
    for user in ["non_cf_team", "cf_internal_role"]:
        job = JobAPI(get_user_api_key(user))
        job.create_simple_job_with_test_questions()
        job_id = job.job_id

        # call get balance api to get current balance
        balance_before_launch = job.get_balance()
        assert balance_before_launch.status_code == 200

        app.user.login_as_customer(user_name=get_user_email(user), password=get_user_password(user))
        app.mainMenu.jobs_page()
        app.job.open_job_with_id(job_id)
        time.sleep(2)

        # choose host channel
        app.job.open_action("Settings")
        app.navigation.click_link("Select Contributor Channels")
        app.job.select_hosted_channel_by_index(save=True)
        time.sleep(2)

        # use api to launch the job
        job.launch_job(rows=37, channel="on_demand")

        job.wait_until_status('running', 60)
        res = job.get_json_job_status()
        res.assert_response_status(200)
        assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
            res.json_response['state'], "running")

        balance_after_launch = job.get_balance()
        assert balance_after_launch.status_code == 200
        assert balance_before_launch.json_response['balance'] == balance_after_launch.json_response['balance']

        app.user.logout()