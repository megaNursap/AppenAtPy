import time

import pytest

from adap.api_automation.services_config.builder import Builder as JobAPI, Builder
from adap.api_automation.utils.data_util import (
    get_user_email,
    get_user_password,
    get_user_api_key,
    get_data_file,
    get_user_info,
)


pytestmark = pytest.mark.regression_fair_pay_v2


EMAIL = get_user_email("fair_pay2_account")
PASSWORD = get_user_password("fair_pay2_account")
API_KEY = get_user_api_key("fair_pay2_account")
JOB = JobAPI(API_KEY)
SAMPLE_FILE = get_data_file("/fair_pay/bounding_box_10_sample_rows.csv")
ONTOLOGY_FILE = get_data_file("/fair_pay/bounding_box_10_sample_rows.json")
AUDIO_SAMPLE_FILE = get_data_file("/fair_pay/cf_115_audio_text_transcript_10_rows.csv")


@pytest.fixture()
def create_job_from_template(app_test):
    """
    Create a job from the template
    """

    app_test.user.login_as_customer(user_name=EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()

    app_test.job.create_new_job_from_template(
        template_type="Image Annotation",
        job_type="Annotate And Categorize Objects In An Image Using A Bounding Box",
    )

    app_test.job.data.upload_file(SAMPLE_FILE, wait_time=20)

    app_test.job.open_tab("DESIGN")
    app_test.navigation.click_btn("Skip")

    app_test.navigation.click_link("Manage Image Annotation Ontology")

    app_test.ontology.upload_ontology(file_name=ONTOLOGY_FILE, rebrand=True)
    app_test.verification.text_present_on_page("Classes Created")

    job_id = app_test.job.grab_job_id()
    return job_id


@pytest.mark.regression_fair_pay_v2
def test_fair_pay_template_job_shows_on_feca(app_test, create_job_from_template):
    """
    Checks that a Fair Pay 2 job created from the template shows on the FECA
    """

    app_test.mainMenu.jobs_page()
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Jobs", max_time=10
    )

    app_test.job.open_job_with_id(create_job_from_template)

    app_test.job.open_tab("DESIGN")
    time.sleep(2)

    cml_sample_updated = (
        """
        <cml:checkbox label="Nothing to box" aggregation="agg" gold="true" value="nothing_to_box" />
        <cml:shapes label="Draw Shapes" name="annotation" type="['box']" source-data="{{image-url}}" 
        box-threshold="0.7" class-threshold="0.7" ontology="true" validates="required" only-if="!nothing_to_box" 
        class-agg="agg" box-agg="0.7" allow-box-rotation="false" gold="true"></cml:shapes>
        """
    )

    cml_payload = {
        'job': {
            'cml': cml_sample_updated
        }}

    job = Builder(api_key=API_KEY, payload=cml_payload)
    resp = job.update_job(create_job_from_template)
    resp.assert_response_status(200)
    time.sleep(30)

    app_test.job.open_tab("LAUNCH")
    time.sleep(5)

    app_test.verification.text_present_on_page(page_text="Crowd Settings")

    app_test.fair_pay.crowd_settings.select_general_crowd_contributor_level(
        contributor_level="Unleveled"
    )
    app_test.verification.text_present_on_page(
        page_text="Includes new and unqualified contributors"
    )

    app_test.fair_pay.crowd_settings.enable_disable_checkbox_by_name(
        checkbox_name="Internal", enable=False
    )

    app_test.navigation.click_btn(btn_name="Save Crowd Settings")

    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Preview your job cost based on your price per judgment and row settings",
        max_time=10,
    )

    time.sleep(2)
    app_test.fair_pay.price_and_row_settings.set_price_slider_value(price_value="1.00")

    app_test.navigation.click_btn(btn_name="Save Prices & Rows Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Review settings and launch your job", max_time=10
    )

    app_test.navigation.click_btn(btn_name="Launch Job")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Trust/Untrusted Judgments", max_time=30
    )

    email = get_user_info("test_ui_account")["email"]
    password = get_user_password("test_ui_account")
    app_test.user.login_as_contributor(user_name=email, password=password)

    time.sleep(5)
    app_test.driver.switch_to.frame(0)

    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Available Jobs", max_time=60
    )

    app_test.user.task.click_on_sorting_desk_by_title(sorting_desk_title="Job")
    time.sleep(2)

    app_test.verification.text_present_on_page(create_job_from_template)
    app_test.verification.text_present_on_page(
        "Annotate And Categorize Objects In An Image Using A Bounding Box"
    )


@pytest.mark.regression_fair_pay_v2
def test_fair_pay_audio_template_job_has_tpj_box(app_test):
    """
    Checks that a Fair Pay 2 job created from the Audio template has Time Per Judgment box
    """

    new_time_per_judgment = "200"
    app_test.user.login_as_customer(user_name=EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()

    app_test.job.create_new_job_from_template(
        template_type="Transcription",
        job_type="Audio Transcription",
    )

    app_test.job.data.upload_file(AUDIO_SAMPLE_FILE, wait_time=20)

    app_test.job.open_tab("DESIGN")

    app_test.job.open_tab("LAUNCH")
    time.sleep(5)

    app_test.verification.text_present_on_page(page_text="Crowd Settings")

    app_test.fair_pay.crowd_settings.enable_disable_checkbox_by_name(
        checkbox_name="Internal", enable=False
    )

    app_test.navigation.click_btn(btn_name="Save Crowd Settings")

    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Preview your job cost based on your price per judgment and row settings",
        max_time=10,
    )

    app_test.fair_pay.price_and_row_settings.set_new_time_per_judgment(
        time_per_judgment_value=new_time_per_judgment
    )
    time.sleep(2)
    app_test.fair_pay.price_and_row_settings.set_price_slider_value(price_value="1.00")
    time.sleep(2)

    app_test.navigation.click_btn(btn_name="Save Prices & Rows Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Review settings and launch your job", max_time=10
    )

    app_test.navigation.click_link(link_name="Prices & Row Settings")
    assert app_test.verification.wait_untill_text_present_on_the_page(
        text="Preview your job cost based on your price per judgment and row settings",
        max_time=10,
    )

    assert app_test.fair_pay.price_and_row_settings.get_time_per_judgment() == new_time_per_judgment
