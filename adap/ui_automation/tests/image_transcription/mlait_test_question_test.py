"""
create multiple test questions for machine learning assisted image transcription job
"""
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_image_transcription, pytest.mark.fed_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/image_transcription/receipts.csv")


@allure.link("Bug ADAP-4931", "https://appen.atlassian.net/browse/ADAP-4931")
def test_create_multiple_tqs(app):
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.image_transcription_ocr_cml,
                                        job_title="Testing create image transcription job", units_per_page=5)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Transcription Ontology')

    ontology_file = get_data_file("/image_transcription/ontology.json")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created")

    app.job.open_tab('QUALITY')
    app.job.quality.click_to_create_tq()
    for i in range(2):
        app.job.quality.switch_to_tq_iframe()
        app.image_transcription.activate_iframe_by_xpath("//iframe[contains(@src, 'ImageTranscription')]")
        app.image_transcription.draw_box_with_coordination(300, 300, 100, 100)
        try:
            app.image_transcription.save_prediction()
        except Exception as r:
            try:
                app.image_transcription.input_transcription_text('no ocr text')
            except Exception as r:
                app.image_transcription.draw_box_with_coordination(10, 10, 20, 20)
                app.image_transcription.input_transcription_text('no ocr text')
        app.image_transcription.deactivate_iframe()
        app.job.quality.switch_to_tq_iframe()
        app.navigation.click_link("Save & Create Another")

    # verify the test questions count
    app.job.open_tab("QUALITY")
    tq_row_count = app.job.quality.get_number_of_active_tq()
    assert tq_row_count == 2
    app.user.logout()

