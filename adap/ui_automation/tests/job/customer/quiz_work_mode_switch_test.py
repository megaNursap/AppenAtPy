"""
These tests check that Quiz mode enable/disable after launching the job, they cover:
https://appen.atlassian.net/browse/QED-3404
https://appen.atlassian.net/browse/QED-3448
"""

import time

import pytest

from adap.api_automation.utils.data_util import (
    get_data_file,
    get_user_api_key,
    get_user_email,
    get_user_password,
)
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.data import annotation_tools_cml as data


pytestmark = pytest.mark.regression_core

USER_EMAIL = get_user_email("test_ui_account")
PASSWORD = get_user_password("test_ui_account")
DATA_FILE = get_data_file("/quiz_work_mode_switch/whatisgreater.csv")
API_KEY = get_user_api_key("test_ui_account")


@pytest.fixture(autouse=True)
def create_job_with_quality_tqs(app_test):
    """
    Fixture creates job with 8 quality questions and logout after autotest ran
    """

    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    job_id = create_annotation_tool_job(
        API_KEY,
        DATA_FILE,
        data.quiz_work_mode_switch_cml,
        job_title="Testing quiz work mode switch",
        units_per_page=8,
    )

    assert job_id, "Job was not created"

    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(job_id)
    app_test.job.open_tab("DESIGN")
    app_test.navigation.click_btn("Save")

    app_test.job.open_tab("QUALITY")
    app_test.job.quality.create_random_tqs(number_tq=8)


@pytest.mark.regression_core
def test_job_goes_from_work_to_quiz_mode(app_test):
    """
    Checks that job goes from work to quiz mode after launch
    """

    app_test.job.open_tab("QUALITY")
    app_test.job.quality.disable_enable_last_tq_on_quality_page()  # turn off the last tq

    app_test.job.open_tab("LAUNCH")
    app_test.navigation.click_link("Launch Job")

    app_test.verification.wait_untill_text_present_on_the_page(
        text="Job link for your internal team", max_time=180
    )

    job_page_url = app_test.driver.current_url
    internal_link = app_test.job.monitor.get_internal_link_for_job_on_monitor_page()

    app_test.navigation.open_page(internal_link)
    app_test.verification.wait_untill_text_present_on_the_page(
        text="Testing Quiz Work Mode Switch", max_time=60
    )

    app_test.navigation.open_page(job_page_url)
    app_test.job.open_tab("QUALITY")
    app_test.job.quality.disable_enable_last_tq_on_quality_page()  # turn on the last tq

    app_test.navigation.open_page(internal_link)
    app_test.job.judgements.create_random_judgments_answer()

    app_test.navigation.open_page(job_page_url)
    app_test.job.open_tab("MONITOR")
    app_test.verification.wait_untill_text_present_on_the_page(
        text="8\nJudgments Collected", max_time=120
    )

    assert app_test.job.judgements.get_collected_judgments() == "8\nJudgments Collected"


@pytest.mark.regression_core
def test_job_goes_from_quiz_to_work_mode(app_test):
    """
    Checks that job goes from quiz to work mode after launch
    """

    app_test.job.open_tab("LAUNCH")
    app_test.navigation.click_link("Launch Job")

    app_test.verification.wait_untill_text_present_on_the_page(
        text="Job link for your internal team", max_time=180
    )

    job_page_url = app_test.driver.current_url
    internal_link = app_test.job.monitor.get_internal_link_for_job_on_monitor_page()

    app_test.navigation.open_page(internal_link)
    app_test.verification.wait_untill_text_present_on_the_page(
        text="Testing Quiz Work Mode Switch", max_time=60
    )

    app_test.navigation.open_page(job_page_url)
    app_test.job.open_tab("QUALITY")
    app_test.job.quality.disable_enable_last_tq_on_quality_page()  # turn off the last tq

    app_test.navigation.open_page(internal_link)
    app_test.verification.wait_untill_text_present_on_the_page(
        text="Testing Quiz Work Mode Switch", max_time=60
    )

    app_test.job.judgements.create_random_judgments_answer()

    app_test.navigation.open_page(job_page_url)
    app_test.job.open_tab("MONITOR")
    app_test.verification.wait_untill_text_present_on_the_page(
        text="8\nJudgments Collected", max_time=120
    )

    assert app_test.job.judgements.get_collected_judgments() == "8\nJudgments Collected"
