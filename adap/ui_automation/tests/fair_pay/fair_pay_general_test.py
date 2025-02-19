import time

import pytest

from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.api_automation.utils.data_util import (
    get_user_email,
    get_user_password,
    get_user_api_key,
    get_data_file,
)


pytestmark = pytest.mark.regression_fair_pay_v2


EMAIL = get_user_email("fair_pay2_account")
PASSWORD = get_user_password("fair_pay2_account")
API_KEY = get_user_api_key("fair_pay2_account")
JOB = JobAPI(API_KEY)
SAMPLE_FILE = get_data_file("/fair_pay/sample_data_20_rows.json")


@pytest.fixture(scope="module", autouse=True)
def create_fp_job():
    resp = JOB.create_job_with_json(SAMPLE_FILE)
    resp.assert_response_status(200)
    return JOB.job_id


@pytest.mark.regression_fair_pay_v2
@pytest.mark.dependency()
def test_launch_fair_pay_and_check(app, create_fp_job):
    """
    Checks that 'Crowd Settings', 'Prices & Row Settings' and 'Review & Launch' are shown
    on 'LAUNCH' tab after launching all needed roles for Fair Pay 2
    """

    app.user.login_as_customer(user_name=EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    assert app.verification.wait_untill_text_present_on_the_page(text="Jobs", max_time=10)

    app.job.open_job_with_id(create_fp_job)

    assert app.verification.wait_untill_text_present_on_the_page(
        text="Step 1: Data", max_time=10
    )

    app.job.open_tab("DESIGN")

    app.job.open_tab("LAUNCH")
    time.sleep(5)

    app.verification.text_present_on_page(page_text="Crowd Settings")
    app.verification.text_present_on_page(page_text="Prices & Row Settings")
    app.verification.text_present_on_page(page_text="Review & Launch")


@pytest.mark.regression_fair_pay_v2
@pytest.mark.dependency(depends=["test_launch_fair_pay_and_check"])
def test_check_fair_pay_crowd_settings(app):
    """
    Changes 'Contributor Level', 'Contributor Channels' and 'Geography Countries' for Fair Pay 2 'Crowd Settings' and
    check that all fields is changed. Saves all changes and checks that user is navigated to 'Prices & Row Settings' tab
    """

    app.fair_pay.crowd_settings.select_general_crowd_contributor_level(
        contributor_level="Level 3"
    )
    app.verification.text_present_on_page(page_text="Highest Quality:")
    app.verification.text_present_on_page(page_text="Smallest group of most experienced, highest accuracy contributors")

    app.fair_pay.crowd_settings.select_general_crowd_contributor_level(
        contributor_level="Level 2"
    )
    app.verification.text_present_on_page(page_text="Higher Quality:")
    app.verification.text_present_on_page(page_text="Smaller group of more experienced, higher accuracy contributors")

    app.fair_pay.crowd_settings.select_general_crowd_contributor_level(
        contributor_level="Level 1"
    )
    app.verification.text_present_on_page(page_text="Fastest Throughput:")
    app.verification.text_present_on_page(page_text="All qualified contributors")

    app.fair_pay.crowd_settings.select_general_crowd_contributor_level(
        contributor_level="Unleveled"
    )
    app.verification.text_present_on_page(page_text="Open to all:")
    app.verification.text_present_on_page(page_text="Includes new and unqualified contributors")

    app.fair_pay.crowd_settings.add_remove_general_crowd_contributor_channels(
        all_channels=True, select_all_channels=True
    )

    app.fair_pay.crowd_settings.add_remove_general_crowd_geography_countries(
        country_names=["Finland", "Fiji"], select_countries=True
    )

    app.fair_pay.crowd_settings.select_general_crowd_language(language="English")

    assert app.fair_pay.crowd_settings.check_checkbox_is_selected_by_name(
        checkbox_name="Internal"
    )

    app.fair_pay.crowd_settings.enable_disable_checkbox_by_name(
        checkbox_name="Internal", enable=False
    )

    app.verification.text_present_on_page(
        page_text="Includes new and unqualified contributors"
    )

    app.verification.text_present_on_page(
        page_text=f"2 contributor channels selected."
    )
    app.verification.text_present_on_page(page_text="2 countries selected")
    app.verification.text_present_on_page(page_text="English")

    app.navigation.click_btn(btn_name="Save Crowd Settings")

    assert app.verification.wait_untill_text_present_on_the_page(
        text="Preview your job cost based on your price per judgment and row settings",
        max_time=10,
    )
    app.verification.current_url_contains(appendix="/prices-and-row-settings")


@pytest.mark.regression_fair_pay_v2
@pytest.mark.dependency(depends=["test_check_fair_pay_crowd_settings"])
def test_check_fair_pay_prices_and_row_settings(app):
    """
    Changes slider value and check that it is changed. Saves all changes and checks that user is navigated
    to 'Review & Launch' tab
    """

    time.sleep(2)
    fair_pay_price = app.fair_pay.price_and_row_settings.get_fair_pay_price()
    price_slider_value = app.fair_pay.price_and_row_settings.get_price_slider_value()

    assert fair_pay_price == price_slider_value

    time.sleep(2)
    app.fair_pay.price_and_row_settings.set_price_slider_value(price_value="1.00")
    time.sleep(2)

    app.verification.text_present_on_page(page_text="$73.44")

    app.navigation.click_btn(btn_name="Save Prices & Rows Settings")
    assert app.verification.wait_untill_text_present_on_the_page(
        text="Review settings and launch your job", max_time=10
    )
    app.verification.current_url_contains(appendix="/review-launch")


@pytest.mark.regression_fair_pay_v2
@pytest.mark.dependency(depends=["test_check_fair_pay_prices_and_row_settings"])
def test_check_fair_pay_review_and_launch(app):
    """
    Changes 'Rows to Order' value and check that it is changed and the user can see all previous changes.
    Saves all changes and checks that user is navigated to 'MONITOR' tab
    """

    app.fair_pay.review_and_launch.set_rows_to_order(rows_to_order="0")
    app.verification.text_present_on_page(page_text="Must be greater than 0")

    app.fair_pay.review_and_launch.set_rows_to_order(rows_to_order="1")
    app.verification.text_present_on_page(
        page_text="Must be greater than 0", is_not=False
    )

    app.fair_pay.review_and_launch.set_rows_to_order(rows_to_order="21")
    app.verification.text_present_on_page(page_text="Job has 20 unordered rows")

    app.fair_pay.review_and_launch.set_rows_to_order(rows_to_order="20")
    app.verification.text_present_on_page(
        page_text="Must be greater than 0", is_not=False
    )

    app.verification.text_present_on_page(page_text="$73.44")
    app.verification.text_present_on_page(page_text="$61.20")
    app.verification.text_present_on_page(page_text="$0.00")
    app.verification.text_present_on_page(page_text="$12.24")

    app.verification.text_present_on_page(page_text="Page Expiration Time")

    app.fair_pay.review_and_launch.click_on_box(box_title="Crowd Settings")

    # change "targeted" to "selected" when 'https://appen.atlassian.net/browse/ADAP-3876' will be done
    app.verification.text_present_on_page(page_text="2 countries targeted")
    app.verification.text_present_on_page(page_text="1 language selected")
    app.verification.text_present_on_page(
        page_text="Unleveled (Open to all: Includes new and unqualified contributors)"
    )
    app.verification.text_present_on_page(page_text=f"2 channels selected")

    app.fair_pay.review_and_launch.click_on_box(box_title="Prices & Rows Settings")
    app.verification.text_present_on_page(page_text="$1.00")

    app.job.open_tab("LAUNCH")
    time.sleep(5)

    app.navigation.click_btn(btn_name="Launch Job")
    assert app.verification.wait_untill_text_present_on_the_page(
        text="Trust/Untrusted Judgments", max_time=240
    )
    app.verification.current_url_contains(appendix="/dashboard")
