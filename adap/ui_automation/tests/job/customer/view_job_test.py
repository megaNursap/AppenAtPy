import time

from adap.api_automation.utils.data_util import *

pytestmark = [
    pytest.mark.regression_core,
    pytest.mark.adap_ui_uat,
    pytest.mark.adap_uat
]

user_email = get_user_email('view_job_ui')
password = get_user_password('view_job_ui')
api_key = get_user_api_key('view_job_ui')
team_id = get_user_team_id('view_job_ui')
team_name = get_user_team_name('view_job_ui')


# comment it out till https://appen.atlassian.net/browse/CW-8013 fixed.
@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.br_wip
@pytest.mark.flaky(reruns=2)
def test_view_my_jobs(app_test):
    """
    Customer should be able to view my jobs
    """
    app_test.user.login_as_customer(user_name=user_email, password=password)

    app_test.mainMenu.jobs_page()
    app_test.verification.current_url_contains("/jobs")
    app_test.verification.text_present_on_page("Jobs")
    app_test.verification.text_present_on_page("Projects")
    app_test.verification.tab_with_columns_present_on_page("JOB TITLE,ROWS,COST,DATE CREATED")
    _api_jobs = app_test.user.get_jobs_by_api_key(api_key)
    _ui_jobs = app_test.job.get_user_jobs_ui()
    assert len(_api_jobs) == len(_ui_jobs), "len not equal, you may check sleep time in job.py"
    assert sorted(_ui_jobs) == sorted(_api_jobs)


# comment it out till https://appen.atlassian.net/browse/CW-8013 fixed.
@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.flaky(reruns=2)
def test_view_teams_jobs(app_test):
    """
    Customer should be able to view team jobs
    """
    app_test.user.login_as_customer(user_name=user_email, password=password)

    app_test.mainMenu.jobs_page()
    app_test.verification.current_url_contains("/jobs")
    app_test.job.open_team_jobs(team_name)

    _api_jobs = app_test.user.get_jobs_by_api_key(api_key, team_id)
    _ui_jobs = app_test.job.get_user_jobs_ui()
    assert sorted(_api_jobs) == sorted(_ui_jobs)