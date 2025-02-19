"""
https://appen.atlassian.net/browse/QED-1764
"""

import time
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder as JobAPI

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')

CML = """
<cml:radios label="Ask question here:" validates="required" gold="true"><cml:radio label="First option" value="first_option" /><cml:radio label="Second option" value="second_option" /></cml:radios>
"""

pytestmark = [
    pytest.mark.regression_core,
    pytest.mark.ui_smoke,
    pytest.mark.ui_uat,
    pytest.mark.adap_ui_uat,
    pytest.mark.adap_uat,
    pytest.mark.fed_ui
]


def test_job_alerts_page(app):
    job = JobAPI(API_KEY)
    csv_file = get_data_file("/5rows.csv")
    job.create_job_with_csv(csv_file)
    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "Testing job alerts page",
            'instructions': "Updated",
            'project_number': 'PN000112',
            'cml': CML,
            'units_per_assignment': 5
        }
    }
    job.update_job(payload=updated_payload)
    job_id = job.job_id

    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    time.sleep(2)

    # choose host channel
    if pytest.env == "fed":
        app.job.open_action("Settings")
        app.navigation.click_link("Select Contributor Channels")
        app.job.select_hosted_channel_by_index(save=True)
        time.sleep(2)

    # use api to launch the job
    job.launch_job()

    job.wait_until_status('running', 120)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    # go to monitor->alerts page
    app.navigation.refresh_page()
    app.user.close_guide()
    app.job.open_tab('MONITOR')
    app.navigation.click_link('Alerts')

    app.verification.current_url_contains("/jobs/%s/alerts" % job_id)
    app.verification.text_present_on_page("We found 1 possible issue with your job.")
    app.verification.text_present_on_page("Alert")
    app.verification.text_present_on_page("Fix")
    app.verification.text_present_on_page("Please create the recommended number of test questions.")
    app.navigation.click_btn("Fix it now")
    app.verification.current_url_contains("/jobs/%s/test_questions" % job_id)
    app.verification.text_present_on_page("Test Questions")
    app.verification.text_present_on_page("Total Active:")
