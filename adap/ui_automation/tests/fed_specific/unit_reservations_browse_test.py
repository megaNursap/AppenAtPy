"""
https://appen.atlassian.net/browse/QED-1214
This is fed specific, to check unit reservations tab.
"""
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder

pytestmark = pytest.mark.fed_ui

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')


def test_unit_reservations_browse(app):
    job = Builder(API_KEY)
    job.create_simple_job_with_test_questions()
    job.launch_job()
    json_status = job.get_json_job_status()
    json_status.assert_response_status(200)
    assert 'running' == json_status.json_response['state']

    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job.job_id)
    app.job.open_tab("MONITOR")
    app.verification.current_url_contains("/dashboard")
    app.verification.text_present_on_page("Job link for your internal team")
    app.job.monitor.get_internal_link_for_job_on_monitor_page()
    app.job.monitor.tab_present('Alerts')
    app.job.monitor.tab_present('Advanced Analytics')
    app.job.monitor.tab_present('Contributors')
    app.job.monitor.tab_present('History')
    app.job.monitor.tab_present('Unit Reservations')
    app.job.monitor.open_tab("Unit Reservations")
    app.verification.text_present_on_page('Unit Reservations')
    app.verification.text_present_on_page('No current reservations')
    app.job.monitor.tab_present('Dashboard')
    app.job.monitor.tab_present('Alerts')
    app.job.monitor.tab_present('Advanced Analytics')
    app.job.monitor.tab_present('Contributors')
    app.job.monitor.tab_present('History')