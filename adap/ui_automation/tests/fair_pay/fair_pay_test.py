import time

import pytest

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.make import Make
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
UPDATED_TIME_PER_JUDGMENT = "30"


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
def test_check_fair_pay_average_tpj(app_test, fair_pay_with_50_judgments):
    """
    Checks that 'average_tpj' appears for job with 50 judgments
    """

    app_test.user.login_as_customer(user_name=EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    assert app_test.verification.wait_untill_text_present_on_the_page(text="Jobs", max_time=10)
    app_test.job.open_job_with_id(fair_pay_with_50_judgments["job_id"])
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

    app_test.navigation.click_btn(btn_name="Save Prices & Rows Settings")

    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Review settings and launch your job", max_time=10
    )

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
        job_id=fair_pay_with_50_judgments["job_id"]
    )

    app_test.navigation.open_page(job_link)
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Fair Pay 2 Job [Do Not Remove]", max_time=5
    )

    app_test.job.judgements.create_random_judgments_answer(var_numbers=2, wait_time=60)
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Wait! Before you go!", max_time=10
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

    make = Make(api_key=API_KEY)
    resp = make.get_json_workers(fair_pay_with_50_judgments["job_id"])
    make_job_info = resp.json_response
    assert make_job_info["worksets"][0]["judgments_count"] == 50
    assert make_job_info["worksets"][0]["average_tpj"]


@pytest.mark.regression_fair_pay_v2
def test_fp_recommended_price_not_zero(app_test, fair_pay_with_50_judgments):
    """
    Checks that recommended price is not zero
    """

    app_test.user.login_as_customer(user_name=EMAIL, password=PASSWORD)

    fair_pay_with_50_judgments["builder"].launch_job(
        external_crowd=True, channel="feca"
    )
    fair_pay_with_50_judgments["builder"].wait_until_status("running", max_time=120)

    email = get_user_info("test_ui_account")["email"]
    password = get_user_password("test_ui_account")
    app_test.user.login_as_contributor(user_name=email, password=password)

    app_test.driver.switch_to.frame(0)

    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Available Jobs", max_time=60
    )

    app_test.user.task.click_on_sorting_desk_by_title(sorting_desk_title="Job")
    job_link = app_test.user.task.find_job_link_by_job_id(
        job_id=fair_pay_with_50_judgments["job_id"]
    )

    app_test.navigation.open_page(job_link)
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Fair Pay 2 Job [Do Not Remove]", max_time=5
    )

    app_test.job.judgements.create_random_judgments_answer(var_numbers=2)
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Wait! Before you go!", max_time=10
    )

    app_test.user.task.logout()

    app_test.user.task.logout()
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Login", max_time=10
    )

    app_test.user.login_as_customer(user_name=EMAIL, password=PASSWORD)

    app_test.mainMenu.jobs_page()
    assert app_test.verification.wait_untill_text_present_on_the_page(text="Jobs", max_time=10)
    app_test.job.open_job_with_id(fair_pay_with_50_judgments["job_id"])
    app_test.user.close_guide()

    app_test.job.open_tab("LAUNCH")
    time.sleep(5)
    app_test.navigation.click_link(link_name="Prices & Row Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Preview your job cost based on your price per judgment and row settings",
        max_time=10
    )

    time.sleep(5)
    app_test.verification.text_present_on_page(page_text="$0.00", is_not=False)


@pytest.mark.regression_fair_pay_v2
def test_fp_time_per_judgment(app_test, fair_pay_with_50_judgments):
    """
    Checks that 'Time Per Judgment' can be only integer and can be changed
    """

    app_test.user.login_as_customer(user_name=EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    assert app_test.verification.wait_untill_text_present_on_the_page(text="Jobs", max_time=10)
    app_test.job.open_job_with_id(fair_pay_with_50_judgments["job_id"])
    app_test.user.close_guide()

    app_test.job.open_tab("DESIGN")
    time.sleep(2)

    app_test.job.open_tab("LAUNCH")
    time.sleep(5)

    app_test.navigation.click_link(link_name="Crowd Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Setup your crowd channel and target settings", max_time=30
    )
    app_test.navigation.click_btn(btn_name="Save Crowd Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Preview your job cost based on your price per judgment and row settings", max_time=10
    )

    app_test.fair_pay.price_and_row_settings.set_new_time_per_judgment(
        time_per_judgment_value="a!@ #$%^&*()-3.0"
    )

    time.sleep(2)
    app_test.fair_pay.price_and_row_settings.set_price_slider_value(price_value="1.00")
    time.sleep(2)

    assert app_test.fair_pay.price_and_row_settings.get_time_per_judgment() == UPDATED_TIME_PER_JUDGMENT

    app_test.navigation.click_btn(btn_name="Save Prices & Rows Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Review settings and launch your job", max_time=10
    )

    app_test.navigation.click_btn(btn_name="Prices & Row Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Preview your job cost based on your price per judgment and row settings",
        max_time=10
    )

    assert app_test.fair_pay.price_and_row_settings.get_time_per_judgment() == UPDATED_TIME_PER_JUDGMENT


@pytest.mark.regression_fair_pay_v2
def test_fp_tpj_seconds_minutes_hours(app_test, fair_pay_with_50_judgments):
    """
    Checks that 'Time Per Judgment' can be changed to seconds, minutes, hours
    """

    app_test.user.login_as_customer(user_name=EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    assert app_test.verification.wait_untill_text_present_on_the_page(text="Jobs", max_time=10)
    app_test.job.open_job_with_id(fair_pay_with_50_judgments["job_id"])
    app_test.user.close_guide()

    app_test.job.open_tab("DESIGN")
    time.sleep(2)

    app_test.job.open_tab("LAUNCH")
    time.sleep(5)

    app_test.navigation.click_link(link_name="Crowd Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Setup your crowd channel and target settings", max_time=30
    )
    app_test.navigation.click_btn(btn_name="Save Crowd Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Preview your job cost based on your price per judgment and row settings", max_time=10
    )

    app_test.fair_pay.price_and_row_settings.set_tpj_seconds_minutes_hours(
        seconds_minutes_hours="Minutes"
    )
    assert app_test.verification.wait_untill_text_present_on_the_page(text="Minutes", max_time=5)

    app_test.fair_pay.price_and_row_settings.set_tpj_seconds_minutes_hours(
        seconds_minutes_hours="Hours"
    )
    assert app_test.verification.wait_untill_text_present_on_the_page(text="Hours", max_time=5)

    app_test.fair_pay.price_and_row_settings.set_tpj_seconds_minutes_hours(
        seconds_minutes_hours="Seconds"
    )
    assert app_test.verification.wait_untill_text_present_on_the_page(text="Seconds", max_time=5)


@pytest.mark.regression_fair_pay_v2
def test_max_hourly_pay_is_not_validated(app_test, fair_pay_with_50_judgments):
    """
    Checks that Max Hourly Pay is not validated upon Country removal
    """

    app_test.user.login_as_customer(user_name=EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    assert app_test.verification.wait_untill_text_present_on_the_page(text="Jobs", max_time=10)
    app_test.job.open_job_with_id(fair_pay_with_50_judgments["job_id"])
    app_test.user.close_guide()

    app_test.job.open_tab("DESIGN")
    time.sleep(2)

    app_test.job.open_tab("LAUNCH")
    time.sleep(5)

    app_test.navigation.click_link(link_name="Crowd Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Setup your crowd channel and target settings", max_time=30
    )

    app_test.fair_pay.crowd_settings.add_remove_general_crowd_geography_countries(
        country_names=["Finland"], select_countries=True
    )

    app_test.navigation.click_btn(btn_name="Save Crowd Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Preview your job cost based on your price per judgment and row settings", max_time=10
    )

    fair_pay_price_finland = app_test.fair_pay.price_and_row_settings.get_fair_pay_price()

    app_test.job.open_tab("LAUNCH")
    time.sleep(5)

    app_test.navigation.click_link(link_name="Crowd Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Setup your crowd channel and target settings", max_time=30
    )

    app_test.fair_pay.crowd_settings.add_remove_general_crowd_geography_countries(
        all_countries=True, select_all_countries=True
    )

    app_test.navigation.click_btn(btn_name="Save Crowd Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Preview your job cost based on your price per judgment and row settings", max_time=10
    )

    assert not app_test.fair_pay.price_and_row_settings.get_fair_pay_price() == fair_pay_price_finland


@pytest.mark.skip(reason="bug https://appen.atlassian.net/browse/ADAP-3919")
@pytest.mark.regression_fair_pay_v2
def test_switch_general_custom_channels_managed_crowd(app_test, fair_pay_with_50_judgments):
    """
    Checks that correct channels number appear on UI when the user switch between 'General',
    'Custom Channels', and 'Managed Crowd'
    """

    app_test.user.login_as_customer(user_name=EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    assert app_test.verification.wait_untill_text_present_on_the_page(text="Jobs", max_time=10)
    app_test.job.open_job_with_id(fair_pay_with_50_judgments["job_id"])
    app_test.user.close_guide()

    app_test.job.open_tab("DESIGN")
    time.sleep(2)

    app_test.job.open_tab("LAUNCH")
    time.sleep(5)

    app_test.navigation.click_link(link_name="Crowd Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Setup your crowd channel and target settings", max_time=30
    )

    app_test.fair_pay.crowd_settings.add_remove_general_crowd_contributor_channels(
        contributor_channels=['BitcoinGet', 'CapeStart'], select_channels=True
    )

    app_test.verification.text_present_on_page(page_text="2 contributor channels selected.")

    app_test.navigation.click_btn(btn_name="Save Crowd Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Preview your job cost based on your price per judgment and row settings", max_time=10
    )

    app_test.navigation.click_btn(btn_name="Save Prices & Rows Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Review settings and launch your job", max_time=10
    )

    app_test.fair_pay.review_and_launch.click_on_box(box_title="Crowd Settings")
    app_test.verification.text_present_on_page(page_text="2 channels selected")

    app_test.job.open_tab("LAUNCH")
    time.sleep(5)

    app_test.navigation.click_link(link_name="Crowd Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Setup your crowd channel and target settings", max_time=30
    )
    app_test.verification.text_present_on_page(page_text="2 contributor channels selected.")

    app_test.fair_pay.select_radio_button_by_name(radio_button_name="Custom Channels")
    app_test.fair_pay.crowd_settings.create_custom_channel()

    app_test.navigation.click_btn(btn_name="Save Crowd Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Preview your job cost based on your price per judgment and row settings", max_time=10
    )

    app_test.navigation.click_btn(btn_name="Save Prices & Rows Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Review settings and launch your job", max_time=10
    )

    app_test.fair_pay.review_and_launch.click_on_box(box_title="Crowd Settings")
    app_test.verification.text_present_on_page(page_text="1 channel selected")

    app_test.job.open_tab("LAUNCH")
    time.sleep(5)

    app_test.navigation.click_link(link_name="Crowd Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Setup your crowd channel and target settings", max_time=30
    )
    app_test.fair_pay.select_radio_button_by_name(radio_button_name="General")

    app_test.verification.text_present_on_page(page_text="2 contributor channels selected.")

    app_test.navigation.click_btn(btn_name="Save Crowd Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Preview your job cost based on your price per judgment and row settings", max_time=10
    )

    app_test.navigation.click_btn(btn_name="Save Prices & Rows Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Review settings and launch your job", max_time=10
    )

    app_test.fair_pay.review_and_launch.click_on_box(box_title="Crowd Settings")
    app_test.verification.text_present_on_page(page_text="2 channels selected")

    app_test.job.open_tab("LAUNCH")
    time.sleep(5)

    app_test.navigation.click_link(link_name="Crowd Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Setup your crowd channel and target settings", max_time=30
    )
    app_test.verification.text_present_on_page(page_text="2 contributor channels selected.")

    app_test.fair_pay.select_radio_button_by_name(radio_button_name="Managed Crowd")

    app_test.fair_pay.crowd_settings.set_ac_project_id(project_id='324')
    app_test.navigation.click_btn(btn_name="Save Crowd Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Preview your job cost based on your price per judgment and row settings", max_time=10
    )

    app_test.navigation.click_btn(btn_name="Save Prices & Rows Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Review settings and launch your job", max_time=10
    )

    app_test.fair_pay.review_and_launch.click_on_box(box_title="Crowd Settings")
    app_test.verification.text_present_on_page(page_text="All Appen Connect contributors")

    app_test.job.open_tab("LAUNCH")
    time.sleep(5)

    app_test.navigation.click_link(link_name="Crowd Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Setup your crowd channel and target settings", max_time=30
    )

    app_test.fair_pay.select_radio_button_by_name(radio_button_name="Custom Channels")
    app_test.navigation.click_btn(btn_name="Save Crowd Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Select a channel before continuing", max_time=10
    )

    app_test.fair_pay.select_radio_button_by_name(radio_button_name="General")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        "No contributor channels selected.", max_time=10
    )


@pytest.mark.regression_fair_pay_v2
def test_check_fair_pay_internal(app_test, fair_pay_with_50_judgments):
    """
    Checks that the job with the 'Internal' channel can be launched
    """

    app_test.user.login_as_customer(user_name=EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    assert app_test.verification.wait_untill_text_present_on_the_page(text="Jobs", max_time=10)
    app_test.job.open_job_with_id(fair_pay_with_50_judgments["job_id"])
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
        checkbox_name="External", enable=False
    )

    app_test.fair_pay.crowd_settings.enable_disable_checkbox_by_name(
        checkbox_name="Internal", enable=True
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

    app_test.fair_pay.review_and_launch.click_on_box(box_title="Crowd Settings")
    app_test.verification.text_present_on_page(page_text="Internal")

    app_test.navigation.click_btn(btn_name="Launch Job")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Trust/Untrusted Judgments", max_time=240
    )

    app_test.verification.current_url_contains(appendix="/dashboard")


@pytest.mark.regression_fair_pay_v2
def test_check_fair_pay_external_internal(app_test, fair_pay_with_50_judgments):
    """
    Checks that the job with the 'External' and the 'Internal' channels can be launched
    """

    app_test.user.login_as_customer(user_name=EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    assert app_test.verification.wait_untill_text_present_on_the_page(text="Jobs", max_time=10)
    app_test.job.open_job_with_id(fair_pay_with_50_judgments["job_id"])
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
        checkbox_name="External", enable=True
    )

    app_test.fair_pay.crowd_settings.enable_disable_checkbox_by_name(
        checkbox_name="Internal", enable=True
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

    app_test.fair_pay.review_and_launch.click_on_box(box_title="Crowd Settings")
    app_test.verification.text_present_on_page(page_text="External (General), Internal")

    app_test.navigation.click_btn(btn_name="Launch Job")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Trust/Untrusted Judgments", max_time=240
    )

    app_test.verification.current_url_contains(appendix="/dashboard")


@pytest.mark.regression_fair_pay_v2
def test_managed_crowd_user_groups_locales(app_test, fair_pay_with_50_judgments):
    """
    Checks that the 'Save Crowd Settings' button on the 'Managed Crowd' tab is not clickable if
    Locales or User groups are not selected
    """

    app_test.user.login_as_customer(user_name=EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    assert app_test.verification.wait_untill_text_present_on_the_page(text="Jobs", max_time=10)
    app_test.job.open_job_with_id(fair_pay_with_50_judgments["job_id"])
    app_test.user.close_guide()

    app_test.job.open_tab("DESIGN")
    time.sleep(2)

    app_test.job.open_tab("LAUNCH")
    time.sleep(5)

    app_test.fair_pay.select_radio_button_by_name(radio_button_name="Managed Crowd")
    time.sleep(2)

    app_test.fair_pay.crowd_settings.set_ac_project_id(project_id='324')
    time.sleep(5)

    app_test.fair_pay.select_radio_button_by_name(radio_button_name="Target specific Appen Connect locales")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="No Locales selected", max_time=10
    )
    app_test.navigation.click_btn(btn_name="Save Crowd Settings")
    app_test.verification.current_url_contains(appendix="/crowd-settings")

    app_test.fair_pay.select_radio_button_by_name(radio_button_name="Target specific Appen Connect user groups")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="No User groups selected", max_time=10
    )
    app_test.navigation.click_btn(btn_name="Save Crowd Settings")
    app_test.verification.current_url_contains(appendix="/crowd-settings")
