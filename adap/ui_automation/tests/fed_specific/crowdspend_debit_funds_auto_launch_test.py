"""
This test covers 3 cases in https://appen.atlassian.net/browse/DED-2020
QA automation ticket https://appen.atlassian.net/browse/QED-1629
1. Choose host channel, enable auto launch on UI, add more data, call get balance api for team, make sure not fund debit.
We'll cover  the third cases with automation.
Above test will be run on both cf_internal user and non cf internal user who is in another team
"""

import time
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder as JobAPI

pytestmark = pytest.mark.fed_ui

CML = """
<cml:radios label="Ask question here:" validates="required" gold="true"><cml:radio label="First option" value="first_option" /><cml:radio label="Second option" value="second_option" /></cml:radios>
"""


def test_auto_launch_debit_funds(app):
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
        app.navigation.refresh_page()
        time.sleep(2)

        # enable auto launch
        app.job.open_settings_tab("API")
        app.navigation.click_checkbox_by_text('Turn on automatic launching of rows')
        app.job.input_automatic_launch_row_period(5)

        # check status
        job.wait_until_status('running', 60)
        res = job.get_json_job_status()
        res.assert_response_status(200)
        assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
            res.json_response['state'], "running")

        balance_after_launch = job.get_balance()
        assert balance_after_launch.status_code == 200
        assert balance_before_launch.json_response['balance'] == balance_after_launch.json_response['balance']

        app.user.logout()


def test_auto_launch_adding_more_data_debit_funds(app):
    for user in ["non_cf_team", "cf_internal_role"]:
        api_key = get_user_api_key(user)
        job = JobAPI(api_key)
        csv_file = get_data_file("/5rows.csv")
        job.create_job_with_csv(csv_file)
        updated_payload = {
            'key': api_key,
            'job': {
                'title': "Testing auto launch debit funds",
                'instructions': "Updated",
                'project_number': 'PN000112',
                'cml': CML,
                'units_per_assignment': 5
            }
        }
        job.update_job(payload=updated_payload)
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
        app.driver.find_elements('xpath',"//label[@class='b-Checkbox__icon']")[1].click()
        time.sleep(1)
        app.navigation.click_link('Ok')
        app.navigation.click_link('Save')
        time.sleep(2)
        app.navigation.refresh_page()
        time.sleep(2)

        # enable auto launch
        app.job.open_settings_tab("API")
        app.navigation.click_checkbox_by_text('Turn on automatic launching of rows')
        app.job.input_automatic_launch_row_period(5)

        # add more data
        app.job.open_tab("DATA")
        app.navigation.click_link("Add More Data")
        app.job.data.upload_file(csv_file)

        # check status
        job.wait_until_status('running', 60)
        res = job.get_json_job_status()
        res.assert_response_status(200)
        assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
            res.json_response['state'], "running")

        balance_after_launch = job.get_balance()
        assert balance_after_launch.status_code == 200
        assert balance_before_launch.json_response['balance'] == balance_after_launch.json_response['balance']

        app.user.logout()