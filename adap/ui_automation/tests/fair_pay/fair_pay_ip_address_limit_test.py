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
URL = f"https://api.{pytest.env}.cf3.us"
MAX_JUDGMENTS = 25


@pytest.fixture(autouse=True)
def fair_pay_job():
    """
    Fixture copies job
    """

    predefined_jobs = pytest.data.predefined_data.get("fair_pay_job_for_copying")
    job_id = predefined_jobs.get(pytest.env)
    resp = Builder(API_KEY).get_json_job_status(job_id)
    assert resp.status_code == 200, (
        f"Failed to get job status for job {job_id}"
        f"Status code: {resp.status_code}"
        f"Response: {resp.text}"
    )

    builder = Builder(API_KEY, custom_url=URL)
    copy_job = builder.copy_job(job_id, "all_units")
    copy_job.assert_response_status(200)
    copy_job_id = copy_job.json_response.get("id")

    return {"job_id": copy_job_id, "builder": builder}


@pytest.mark.regression_fair_pay_v2
def test_check_ip_address_limit_for_workers(app_test, fair_pay_job):
    """
    Checks that 'max_judgments_per_ip' changed and the Contributor can't add more than 25 judgments
    """

    max_judgments_per_ip_1 = fair_pay_job['builder'].get_json_job_status().json_response.get("max_judgments_per_ip")
    assert not max_judgments_per_ip_1

    max_judgments_param = {'job[max_judgments_per_ip]': MAX_JUDGMENTS}
    fair_pay_job['builder'].update_job_settings(max_judgments_param)
    max_judgments_per_ip_2 = fair_pay_job['builder'].get_json_job_status().json_response.get("max_judgments_per_ip")
    assert max_judgments_per_ip_2 == MAX_JUDGMENTS
    assert not max_judgments_per_ip_1 == max_judgments_per_ip_2

    app_test.user.login_as_customer(user_name=EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    assert app_test.verification.wait_untill_text_present_on_the_page(text="Jobs", max_time=10)
    app_test.job.open_job_with_id(fair_pay_job["job_id"])
    app_test.user.close_guide()
    time.sleep(10)

    app_test.job.open_tab("QUALITY")
    app_test.job.open_tab("LAUNCH")
    time.sleep(5)

    app_test.navigation.click_link(link_name="Crowd Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Setup your crowd channel and target settings", max_time=30
    )
    app_test.navigation.click_btn(btn_name="Save Crowd Settings")

    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Preview your job cost based on your price per judgment and row settings",
        max_time=10,
    )

    time.sleep(5)
    app_test.job.launch.enter_row_per_page_FP(MAX_JUDGMENTS)

    app_test.navigation.click_btn(btn_name="Save Prices & Rows Settings")

    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Review settings and launch your job", max_time=10
    )

    time.sleep(5)
    app_test.job.launch.enter_rows_to_order(MAX_JUDGMENTS)

    app_test.navigation.click_btn(btn_name="Launch Job")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Trust/Untrusted Judgments", max_time=240
    )

    monitor_page = app_test.driver.current_url

    email = get_user_info("test_ui_account")["email"]
    password = get_user_password("test_ui_account")
    app_test.user.login_as_contributor(user_name=email, password=password)

    time.sleep(10)
    app_test.driver.switch_to.frame(0)

    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Available Jobs", max_time=60
    )

    app_test.user.task.click_on_sorting_desk_by_title(sorting_desk_title="Job")
    job_link = app_test.user.task.find_job_link_by_job_id(
        job_id=fair_pay_job["job_id"]
    )

    app_test.navigation.open_page(job_link)
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Fair Pay 2 Job [Do Not Remove]", max_time=5
    )

    app_test.job.judgements.create_random_judgments_answer(var_numbers=2, wait_time=60)
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="There is no work currently available in this task.", max_time=10
    )

    app_test.user.task.logout()
    time.sleep(5)

    app_test.user.task.logout()
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Login", max_time=10
    )

    app_test.user.login_as_customer(user_name=EMAIL, password=PASSWORD)

    app_test.navigation.open_page(url=monitor_page)
    time.sleep(5)

    app_test.verification.current_url_contains("/dashboard")

    assert app_test.verification.wait_untill_text_present_on_the_page(
        text=str(MAX_JUDGMENTS), max_time=10
    )

    judgments_count = fair_pay_job['builder'].get_json_job_status().json_response.get("judgments_count")

    assert judgments_count == MAX_JUDGMENTS
