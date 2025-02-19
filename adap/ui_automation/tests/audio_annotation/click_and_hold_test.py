import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.selenium_utils import *
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.data import annotation_tools_cml as data

pytestmark = [pytest.mark.regression_audio_annotation, pytest.mark.fed_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_annotation/audio_data.csv")


def test_click_and_hold(app):
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE, data.audio_annotation_cml,
                                        job_title="Testing manage audio annotation", units_per_page=5)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Annotation Ontology')

    ontology_file = get_data_file("/audio_annotation/ontology.csv")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created", "//span[text()='2']")

    app.job.preview_job()
    app.audio_annotation.activate_iframe_by_index(0)
    time.sleep(2)
    app.audio_annotation.begin_annotate(0)
    app.audio_annotation.annotate_audio()
    time.sleep(5)