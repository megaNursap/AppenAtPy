import time

import pytest

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import (
    get_user_email,
    get_user_password,
    get_user_api_key,
    get_user_info,
)


pytestmark = pytest.mark.regression_fair_pay_v2


EMAIL = get_user_email("fair_pay2_account")
PASSWORD = get_user_password("fair_pay2_account")
API_KEY = get_user_api_key("fair_pay2_account")


@pytest.fixture(autouse=True)
def fair_pay_copy_two_jobs():
    """
    Fixture copies two jobs
    """

    predefined_jobs = pytest.data.predefined_data.get("fair_pay_job_for_copying")
    job_id = predefined_jobs.get(pytest.env)
    resp = Builder(API_KEY).get_json_job_status(job_id)
    assert resp.status_code == 200, (
        f"Failed to get job status for job {job_id}"
        f"Status code: {resp.status_code}"
        f"Response: {resp.text}"
    )

    builder = Builder(API_KEY)
    copy_job_1 = builder.copy_job(job_id, "all_units")
    copy_job_1.assert_response_status(200)
    copy_job_id_1 = copy_job_1.json_response.get("id")

    copy_job_2 = builder.copy_job(job_id, "all_units")
    copy_job_2.assert_response_status(200)
    copy_job_id_2 = copy_job_2.json_response.get("id")

    return {"job_id_1": copy_job_id_1, "job_id_2": copy_job_id_2}


def _external_internal_job(app_test, job_id, external, internal, text_on_monitor_tab):
    """
    Helper launches job with External, Internal channels and checks that the Monitor tab is opened
    """

    app_test.user.customer.open_home_page()
    app_test.mainMenu.jobs_page()
    assert app_test.verification.wait_untill_text_present_on_the_page(text="Jobs", max_time=10)
    app_test.job.open_job_with_id(job_id)
    app_test.user.close_guide()
    time.sleep(10)

    app_test.job.open_tab("QUALITY")
    app_test.job.open_tab("LAUNCH")
    time.sleep(5)

    app_test.navigation.click_link(link_name="Crowd Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Setup your crowd channel and target settings", max_time=30
    )

    app_test.fair_pay.crowd_settings.enable_disable_checkbox_by_name(
        checkbox_name="External", enable=external
    )
    app_test.fair_pay.crowd_settings.enable_disable_checkbox_by_name(
        checkbox_name="Internal", enable=internal
    )

    app_test.navigation.click_btn(btn_name="Save Crowd Settings")

    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Preview your job cost based on your price per judgment and row settings",
        max_time=20,
    )
    app_test.navigation.click_btn(btn_name="Save Prices & Rows Settings")

    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Review settings and launch your job", max_time=10
    )

    app_test.navigation.click_btn(btn_name="Launch Job")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text=text_on_monitor_tab, max_time=240
    )


def _external_multiple_assignments(app_test, fair_pay_copy_two_jobs):
    """
    Helper checks that the contributor can't work on two External jobs at the same time
    """

    email = get_user_info("test_ui_account")["email"]
    password = get_user_password("test_ui_account")
    app_test.user.login_as_contributor(user_name=email, password=password)

    time.sleep(10)
    app_test.driver.switch_to.frame(0)

    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Available Jobs", max_time=60
    )

    app_test.user.task.click_on_sorting_desk_by_title(sorting_desk_title="Job")

    job_link_1 = app_test.user.task.find_job_link_by_job_id(
        job_id=fair_pay_copy_two_jobs["job_id_1"]
    )

    job_link_2 = app_test.user.task.find_job_link_by_job_id(
        job_id=fair_pay_copy_two_jobs["job_id_2"]
    )

    app_test.navigation.open_page(job_link_1)
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Fair Pay 2 Job [Do Not Remove]", max_time=30
    )

    app_test.navigation.open_page(job_link_2)
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Fair Pay 2 Job [Do Not Remove]", max_time=30
    )

    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Concurrent tasks are not allowed. Please complete the current task.",
        max_time=30
    )


@pytest.mark.regression_fair_pay_v2
def test_check_internal_multiple_assignments(app_test, fair_pay_copy_two_jobs):
    """
    Checks that the contributor can work on two Internal jobs at the same time
    """

    app_test.user.login_as_customer(user_name=EMAIL, password=PASSWORD)

    for job_id in fair_pay_copy_two_jobs:
        _external_internal_job(
            app_test=app_test,
            job_id=fair_pay_copy_two_jobs[job_id],
            external=False,
            internal=True,
            text_on_monitor_tab="Job link for your internal team"
        )

        internal_link = app_test.job.monitor.get_internal_link_for_job_on_monitor_page()
        app_test.navigation.open_page(internal_link)

        assert app_test.verification.wait_untill_text_present_on_the_page(
            text="Fair Pay 2 Job [Do Not Remove]", max_time=30
        )

    assert not app_test.verification.wait_untill_text_present_on_the_page(
        text="Concurrent tasks are not allowed. Please complete the current task.",
        max_time=30
    )


@pytest.mark.regression_fair_pay_v2
def test_check_external_multiple_assignments(app_test, fair_pay_copy_two_jobs):
    """
    Checks that the contributor can't work on two External jobs at the same time
    """

    app_test.user.login_as_customer(user_name=EMAIL, password=PASSWORD)

    for job_id in fair_pay_copy_two_jobs:
        _external_internal_job(
            app_test=app_test,
            job_id=fair_pay_copy_two_jobs[job_id],
            external=True,
            internal=False,
            text_on_monitor_tab="Trust/Untrusted Judgments"
        )

    _external_multiple_assignments(
        app_test=app_test,
        fair_pay_copy_two_jobs=fair_pay_copy_two_jobs
    )


@pytest.mark.regression_fair_pay_v2
def test_check_internal_external_multiple_assignments(app_test, fair_pay_copy_two_jobs):
    """
    Checks that the contributor can work on two Internal and External jobs at the same time
    """

    app_test.user.login_as_customer(user_name=EMAIL, password=PASSWORD)

    for job_id in fair_pay_copy_two_jobs:
        _external_internal_job(
            app_test=app_test,
            job_id=fair_pay_copy_two_jobs[job_id],
            external=True,
            internal=True,
            text_on_monitor_tab="Job link for your internal team"
        )

        internal_link = app_test.job.monitor.get_internal_link_for_job_on_monitor_page()
        app_test.navigation.open_page(internal_link)

        assert app_test.verification.wait_untill_text_present_on_the_page(
            text="Fair Pay 2 Job [Do Not Remove]", max_time=30
        )

    assert not app_test.verification.wait_untill_text_present_on_the_page(
        text="Concurrent tasks are not allowed. Please complete the current task.",
        max_time=30
    )


@pytest.mark.regression_fair_pay_v2
def test_check_external_internal_multiple_assignments(app_test, fair_pay_copy_two_jobs):
    """
    Checks that the contributor can't work on two External and Internal jobs at the same time
    """

    app_test.user.login_as_customer(user_name=EMAIL, password=PASSWORD)

    for job_id in fair_pay_copy_two_jobs:
        _external_internal_job(
            app_test=app_test,
            job_id=fair_pay_copy_two_jobs[job_id],
            external=True,
            internal=True,
            text_on_monitor_tab="Trust/Untrusted Judgments"
        )

    _external_multiple_assignments(
        app_test=app_test,
        fair_pay_copy_two_jobs=fair_pay_copy_two_jobs
    )
