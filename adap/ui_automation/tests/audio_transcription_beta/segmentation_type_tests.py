import time

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_audio_transcription_beta, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/AT-beta-source-data-one-unit.csv")


@pytest.fixture(scope="module")
def at_job_single_segment(tmpdir_factory, app):
    """
    Create Audio Tx beta='true' job with 2 data rows
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_one_segment_beta_segmentation,
                                        job_title="Testing audio transcription beta for one segment job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-new-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    app.job.preview_job()

    return job_id


def test_at_least_one_segments_require(at_job_single_segment, app):
    """
       Verify if type=['segmentation'] present then user should create at least one segment
    """

    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.deactivate_iframe()

    app.audio_transcription_beta.submit_test_validators()
    assert app.audio_transcription_beta.get_task_error_msg_by_index() == "You must create at least one segment before submitting since this is a segmentation type job."
    time.sleep(2)


def test_segmentation_require_attribute(app, at_job_single_segment):
    """
    Verify requestor can set up how many percent of audio should be segmented
    """
    type_transcription = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" 
    name="audio_transcription" type="['segmentation']" beta='true' segmentation-required="0.25"/> """

    job = Builder(API_KEY)

    job.job_id = at_job_single_segment

    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "Audio Transcription Test type=['transcription']",
            'instructions': "all fields CML",
            'cml': type_transcription,
            'project_number': 'PN000112'
        }
    }

    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)

    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.deactivate_iframe()

    app.audio_transcription_beta.submit_test_validators()
    assert app.audio_transcription_beta.get_task_error_msg_by_index() == "You must segment atleast 25 percent of the audio"
    time.sleep(2)


