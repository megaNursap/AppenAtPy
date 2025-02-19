import time

import pytest

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import (
    get_user_email,
    get_user_password,
    get_user_api_key,
)


pytestmark = pytest.mark.regression_fair_pay_v2


EMAIL = get_user_email("fair_pay2_account")
PASSWORD = get_user_password("fair_pay2_account")
API_KEY = get_user_api_key("fair_pay2_account")


@pytest.fixture(autouse=True)
def fair_pay_with_50_judgments():
    """
    Fixture copies job, adds 50 judgments
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
    copy_job = builder.copy_job(job_id, "all_units")
    copy_job.assert_response_status(200)
    copy_job_id = copy_job.json_response.get("id")

    return {"job_id": copy_job_id, "builder": builder}


@pytest.mark.regression_fair_pay_v2
def test_check_tq_graph(app_test, fair_pay_with_50_judgments):
    """
    Creates 1 test question, removes the golden unit on the 'Data' tab, creates 2 more test questions,
    navigates to the 'Monitor' tab and checks if the 'Test Questions Graph' shows 2 test questions
    """

    app_test.user.login_as_customer(user_name=EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    assert app_test.verification.wait_untill_text_present_on_the_page(text="Jobs", max_time=10)
    app_test.job.open_job_with_id(fair_pay_with_50_judgments["job_id"])
    app_test.user.close_guide()
    time.sleep(10)

    app_test.job.open_tab("DESIGN")
    app_test.navigation.click_btn("Save")
    app_test.navigation.click_link("Next: Create Test Questions")
    app_test.user.close_guide()

    app_test.job.quality.create_random_tqs()
    app_test.job.open_tab("DATA")

    tq_units = app_test.job.data.find_all_units_with_status("golden")
    assert len(tq_units) == 1, f"{len(tq_units)} rows were found, expected - 1"

    resp = fair_pay_with_50_judgments["builder"].delete_unit(tq_units['unit id'].values.tolist()[0])
    resp.assert_response_status(200)

    app_test.navigation.refresh_page()

    tq_units = app_test.job.data.find_all_units_with_status("golden")
    assert len(tq_units) == 0, f"{len(tq_units)} rows were found, expected - 0"

    app_test.job.open_tab("QUALITY")
    app_test.user.close_guide()

    app_test.job.quality.create_random_tqs(number_tq=2)

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
    app_test.navigation.click_btn(btn_name="Save Prices & Rows Settings")

    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Review settings and launch your job", max_time=10
    )

    app_test.navigation.click_btn(btn_name="Launch Job")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="2 total test questions.", max_time=10
    )
