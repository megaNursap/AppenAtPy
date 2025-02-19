"""
AT - UI Automation - Nothing to transcribe
https://appen.atlassian.net/browse/QED-1386
"""

import time
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_audio_transcription_design, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/AT-newdata-segments.csv")


@pytest.fixture(scope="module")
def at_job(tmpdir_factory, app):
    """
    Create Audio Tx job with 2 data rows and upload ontology
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_cml,
                                        job_title="Testing audio transcription job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    app.job.preview_job()

    return job_id


def test_nothing_transcribe_tool_level(app, at_job):
    """
    Verify tool level “Nothing to transcribe” prompt and checkbox are displayed when the tool is initially opened for each data row and remains in place until a transcription has been made
    """
    app.audio_transcription.activate_iframe_by_index(0)

    app.verification.text_present_on_page("Empty Segments")
    app.verification.text_present_on_page("No Transcriptions have been made. Is there nothing to transcribe?")
    assert app.audio_transcription.nothing_to_transcribe_checkbox_is_displayed()

    app.audio_transcription.add_text_to_bubble("Noise", "test")
    # dev updated the code, it will always show there
    # app.verification.text_present_on_page("Empty Segments", is_not=False)
    # app.verification.text_present_on_page("No Transcriptions have been made. Is there nothing to transcribe?", is_not=False)
    # assert not app.audio_transcription.nothing_to_transcribe_checkbox_is_displayed()

    # tear down
    app.audio_transcription.delete_text_from_bubble("Noise")


def test_nothing_transcribe_checked_tool_level(app, at_job):
    """
    Verify that if tool level “Nothing to transcribe” is checked, all the segments bubbles are marked as “Nothing to transcribe”
    Verify user can uncheck “Nothing to transcribe” checkbox to enable transcription again
    """
    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(0)

    app.audio_transcription.click_nothing_to_transcribe_for_task()

    checked_bubbles = {}
    bubbles = app.audio_transcription.get_bubbles_list()

    for bubble in bubbles:
        name = bubble['name']
        if checked_bubbles.get(name, False):
            checked_bubbles[name] = checked_bubbles[name] + 1
        else:
            checked_bubbles[name] = 1

        index = checked_bubbles[name] - 1

        assert app.audio_transcription.get_text_from_bubble(name, index) == 'Nothing to Transcribe'

    app.audio_transcription.click_nothing_to_transcribe_for_task()
    app.audio_transcription.add_text_to_bubble("Noise", "test")
    assert app.audio_transcription.get_text_from_bubble('Noise') == 'test'

    # tear down
    app.audio_transcription.delete_text_from_bubble("Noise")


@pytest.mark.dependency()
def test_nothing_transcribe_btn_available_for_each_bubble(app, at_job):
    """
    Verify that nothing to transcribe icon is available for each transcription bubble and is disabled by default
    """
    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(0)
    # app.navigation.click_btn("Open Transcription Tool")
    time.sleep(5)

    checked_bubbles = {}
    bubbles = app.audio_transcription.get_bubbles_list()
    for bubble in bubbles:
        name = bubble['name']
        if checked_bubbles.get(name, False):
            checked_bubbles[name] = checked_bubbles[name]+1
        else:
            checked_bubbles[name] = 1

        index = checked_bubbles[name] - 1

        assert not app.audio_transcription.nothing_to_transcribe_btn_is_disable_for_bubble(name, index)

    # app.audio_transcription.close_at_tool_without_saving()
    # app.audio_transcription.toolbar.click_btn('save')
    app.audio_transcription.deactivate_iframe()


@pytest.mark.dependency(depends=["test_nothing_transcribe_btn_available_for_each_bubble"])
def test_nothing_to_transcribe_btn(app, at_job):
    """
    Verify user can mark segment as 'Nothing to transcribe'
    """
    app.audio_transcription.activate_iframe_by_index(0)
    # app.navigation.click_btn("Open Transcription Tool")
    time.sleep(5)

    app.audio_transcription.click_nothing_to_transcribe_for_bubble('Pet')
    assert app.audio_transcription.get_nothing_to_transcribe_status_for_bubble('Pet')

    # app.verification.text_present_on_page('Empty Segments', is_not=False)
    # app.verification.text_present_on_page('No Transcriptions have been made. Is there nothing to transcribe?',
    #                                       is_not=False)
    #
    #
    # app.audio_transcription.click_nothing_to_transcribe_for_bubble('Cat')
    # assert not app.audio_transcription.get_nothing_to_transcribe_status_for_bubble('Cat')
    # tool level nothing to transcribe is still displayed
    app.verification.text_present_on_page('Empty Segments')
    app.verification.text_present_on_page('No Transcriptions have been made. Is there nothing to transcribe?')

    # app.audio_transcription.close_at_tool_without_saving()
    app.image_annotation.deactivate_iframe()


@pytest.mark.dependency(depends=["test_nothing_to_transcribe_btn"])
def test_nothing_to_transcribe_disable(app, at_job):
    """
    Verify that ‘Nothing to transcribe' icon is disabled when text is entered and re-enabled when text is deleted
    """
    app.audio_transcription.activate_iframe_by_index(0)
    time.sleep(2)

    app.audio_transcription.add_text_to_bubble("Person", "test")
    assert app.audio_transcription.nothing_to_transcribe_btn_is_disable_for_bubble("Person")
    assert not app.audio_transcription.get_nothing_to_transcribe_status_for_bubble('Person')

    app.audio_transcription.delete_text_from_bubble("Person")
    app.audio_transcription.click_nothing_to_transcribe_for_bubble('Person')

    assert not app.audio_transcription.nothing_to_transcribe_btn_is_disable_for_bubble("Person")
    assert app.audio_transcription.get_nothing_to_transcribe_status_for_bubble('Person')

    app.audio_transcription.click_nothing_to_transcribe_for_bubble('Person')
    app.audio_transcription.add_text_to_bubble("Person", "new test")

    assert app.audio_transcription.get_text_from_bubble('Person') == "new test"

    # tear down
    app.audio_transcription.delete_text_from_bubble('Person')
    app.image_annotation.deactivate_iframe()