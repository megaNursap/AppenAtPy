import time
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_peer_review_job
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [
    pytest.mark.regression_audio_transcription_design,
    pytest.mark.audio_transcription_ui,
    pytest.mark.adap_ui_uat,
    pytest.mark.adap_uat
]

USER_EMAIL = get_user_email('test_predefined_jobs')
PASSWORD = get_user_password('test_predefined_jobs')
API_KEY = get_user_api_key('test_predefined_jobs')
DATA_FILE = get_data_file("/audio_transcription/f1606317.csv")
PREDEFINED_JOB_ID = pytest.data.predefined_data['audio_transcription'].get(pytest.env)


def test_create_peer_review_by_regenerating_report(tmpdir_factory, app):
    tmpdir = tmpdir_factory.mktemp('data')
    job_id = create_peer_review_job(tmpdir, API_KEY, PREDEFINED_JOB_ID, data.audio_transcription_subset_cml,
                                    units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')
    ontology_file = get_data_file('/audio_transcription/reviewdata_with_instances_ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)


def test_create_peer_review_by_uploading_file(app):
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE, data.audio_transcription_subset_cml,
                                        job_title="Testing audio transcription by uploading full report", units_per_page=2)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')
    ontology_file = get_data_file('/audio_transcription/reviewdata_with_instances_ontology.json')
    app.ontology.upload_ontology(ontology_file)