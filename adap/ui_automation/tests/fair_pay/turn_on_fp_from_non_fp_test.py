import time

import pytest

from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.api_automation.utils.data_util import (
    get_user_email,
    get_user_password,
    get_user_team_id,
    get_user_api_key,
    get_data_file,
)


pytestmark = pytest.mark.regression_fair_pay_v2


EMAIL = get_user_email("fair_pay_account")
PASSWORD = get_user_password("fair_pay_account")
TEAM_ID = get_user_team_id("fair_pay_account")

API_KEY = get_user_api_key("fair_pay_account")
JOB = JobAPI(API_KEY)
SAMPLE_FILE = get_data_file("/fair_pay/sample_data_20_rows.json")
PRICE_PER_JUDGMENT = "0.45"


@pytest.fixture(scope="module", autouse=True)
def turn_off_fair_pay(app):
    app.user.login_as_customer(user_name=EMAIL, password=PASSWORD)
    app.mainMenu.account_menu("Customers")
    app.navigation.click_link("Teams")
    app.user.search_user_and_go_to_team_page(EMAIL, TEAM_ID)
    app.user.click_edit_team()
    app.fair_pay.change_team_roles_by_names(
        role_names=["Enhanced Launch Page UX + Fair Pay"], select=False
    )
    time.sleep(5)
    app.navigation.click_btn(btn_name="Save Changes", timeout=10)

    app.user.logout()
    time.sleep(10)


@pytest.fixture(scope="module", autouse=True)
def create_fp_job(app):
    resp = JOB.create_job_with_json(SAMPLE_FILE)
    resp.assert_response_status(200)
    return JOB.job_id


@pytest.mark.skip(reason="bug https://appen.atlassian.net/browse/ADAP-3394")
@pytest.mark.regression_fair_pay_v2
def test_turn_on_fp_from_non_fp(app, turn_off_fair_pay, create_fp_job):
    """
    Checks that changes implemented in the 'Launch' page for non Fair Pay roles
    are saved after Fair Pay 2 roles are turned on
    """

    app.user.login_as_customer(user_name=EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    assert app.verification.wait_untill_text_present_on_the_page(
        text="Jobs", max_time=10
    )

    app.job.open_job_with_id(create_fp_job)

    assert app.verification.wait_untill_text_present_on_the_page(
        text="Step 1: Data", max_time=10
    )

    app.job.open_tab("DESIGN")

    app.job.open_tab("LAUNCH")

    assert app.verification.wait_untill_text_present_on_the_page(
        text="Step 4: Launch a test run", max_time=60
    )

    assert app.verification.wait_untill_text_present_on_the_page(
        text="Crowd Channel", max_time=60
    )

    app.job.launch.click_edit_settings_section(name="Crowd Channel")
    app.fair_pay.crowd_settings.enable_disable_checkbox_by_name(
        checkbox_name="Internal", enable=False
    )
    app.navigation.click_btn(btn_name="Save & Close", timeout=10)

    app.job.launch.click_edit_settings_section(name="Crowd Settings (External)")
    app.job.launch.set_price_per_judgment(value=PRICE_PER_JUDGMENT)
    price_per_judgment = app.job.launch.get_price_per_judgment()
    assert price_per_judgment == PRICE_PER_JUDGMENT
    app.navigation.click_btn(btn_name="Save & Close", timeout=10)

    app.job.launch.click_edit_settings_section(name="Job Launch Settings")
    app.job.launch.enter_judgements_per_row_for_FP_jobs(judgements="1")
    app.job.launch.enter_row_per_page_FP(id="20")
    app.navigation.click_btn(btn_name="Save & Close", timeout=10)

    launch_page = app.driver.current_url

    app.mainMenu.account_menu("Customers")
    app.navigation.click_link("Teams")
    app.user.search_user_and_go_to_team_page(EMAIL, TEAM_ID)
    app.user.click_edit_team()
    app.fair_pay.change_team_roles_by_names(
        role_names=["Appen Connect Customer", "Enhanced Launch Page UX + Fair Pay"]
    )
    time.sleep(5)
    app.navigation.click_btn("Save Changes")

    app.user.logout()
    time.sleep(10)

    app.user.login_as_customer(user_name=EMAIL, password=PASSWORD)
    app.navigation.open_page(url=launch_page)

    assert app.verification.wait_untill_text_present_on_the_page(
        text="Step 4: Launch a test run", max_time=60
    )
    assert app.verification.wait_untill_text_present_on_the_page(
        text="Crowd Channel", max_time=60
    )

    app.verification.current_url_contains(appendix="/launch")

    app.job.launch.click_edit_settings_section(name="Crowd Channel")
    assert not app.fair_pay.crowd_settings.check_checkbox_is_selected_by_name(
        checkbox_name="Internal"
    )
    app.navigation.click_btn(btn_name="Cancel", timeout=10)

    app.verification.text_present_on_page(page_text="45.00")
    app.verification.text_present_on_page(page_text="1")
    app.verification.text_present_on_page(page_text="20")
    app.verification.text_present_on_page(page_text="$0.46")
    app.verification.text_present_on_page(page_text="$9.45")
    app.verification.text_present_on_page(page_text="$0.09")
    app.verification.text_present_on_page(page_text="$10.00")
    app.verification.text_present_on_page(page_text="Link for Internal Users: ", is_not=False)
