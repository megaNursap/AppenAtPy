"""
https://appen.atlassian.net/browse/QED-1942
"""

from adap.api_automation.utils.data_util import *
import time
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.data import annotation_tools_cml as data

pytestmark = pytest.mark.create_annotation_tools_job


@pytest.fixture(scope="module")
def create_new_user(app):
    app.user.login_as_customer(get_user_email('test_ui_account'), get_user_password('test_ui_account'))
    user_api_key = get_user_api_key('test_ui_account')
    return user_api_key


@pytest.mark.create_audio_annotation_job
def test_create_audio_annotation_job(app, create_new_user):
    job_id = create_annotation_tool_job(create_new_user, get_data_file("/audio_annotation/audio_data.csv"),
                                        data.audio_annotation_cml, job_title="Testing create audio annotation job for fed", units_per_page=5)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Annotation Ontology')
    ontology_file = get_data_file("/audio_annotation/ontology.csv")
    app.ontology.upload_ontology(ontology_file)
    app.verification.text_present_on_page("2/1000 Classes Created")


@pytest.mark.create_image_annotation_job
def test_create_image_annotation_job(app, create_new_user):
    job_id = create_annotation_tool_job(create_new_user, get_data_file("/image_annotation/catdog.csv"),
                                        data.image_annotation_cml,
                                        job_title="Testing create image annotation job for fed", units_per_page=2)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Annotation Ontology')
    ontology_file = get_data_file("/image_annotation/ontology.json")
    app.ontology.upload_ontology(ontology_file)
    app.verification.text_present_on_page("2/1000 Classes Created")


@pytest.mark.create_image_transcription_job
def test_create_image_transcription_job(app, create_new_user):
    job_id = create_annotation_tool_job(create_new_user, get_data_file("/image_transcription/receipts.csv"),
                                        data.image_transcription_ocr_cml,
                                        job_title="Testing create image transcription job", units_per_page=5)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Transcription Ontology')
    ontology_file = get_data_file("/image_transcription/ontology.json")
    app.ontology.upload_ontology(ontology_file)
    app.verification.text_present_on_page("2/1000 Classes Created")


@pytest.mark.create_plss_job
def test_create_plss_job(app, create_new_user):
    job_id = create_annotation_tool_job(create_new_user, get_data_file("/plss/catdog.csv"), data.plss_cml,
                                        job_title="Testing plss annotation tool", units_per_page=2)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Segmentation Ontology')
    ontology_file = get_data_file("/plss/ontology.json")
    app.ontology.upload_ontology(ontology_file)
    app.verification.text_present_on_page("2/1000 Classes Created")


@pytest.mark.create_text_annotation_job
def test_create_text_annotation_job(app, create_new_user):
    job_id = create_annotation_tool_job(create_new_user, get_data_file("/text_annotation/multiplelinesdata.csv"), data.text_annotation_cml,
                                        job_title="Testing text annotation tool", units_per_page=5)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Text Annotation Ontology')
    ontology_file = get_data_file("/text_annotation/ontology.json")
    app.ontology.upload_ontology(ontology_file)
    app.verification.text_present_on_page("3/1000 Classes Created")


@pytest.mark.create_video_annotation_job
def test_create_video_annotation_job(app, create_new_user):
    job_id = create_annotation_tool_job(create_new_user, get_data_file("/video_annotation/video.csv"),
                                        data.video_annotation_linear_interpolation_cml, job_title="Testing video annotation tool", units_per_page=5)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Video Shapes Ontology')
    ontology_file = get_data_file("/video_annotation/ontology.json")
    app.ontology.upload_ontology(ontology_file)
    app.verification.text_present_on_page("2/1000 Classes Created")

    app.job.open_action("Settings")
    if pytest.env == 'fed':
        app.navigation.click_link("Select Contributor Channels")
        app.job.select_hosted_channel_by_index(save=True)
    else:
        app.driver.find_element('xpath',"//label[@for='externalChannelsEnabled' or text()='External']").click()
        app.navigation.click_link('Save')
    app.job.open_tab('LAUNCH')
    app.navigation.click_link("Launch Job")