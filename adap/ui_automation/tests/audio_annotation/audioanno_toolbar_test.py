"""
This test covers toolbar validation for audio annotation
play, pause, zoom in, zoom out, reframe, help menu, save and  close
"""
import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.selenium_utils import *
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.data import annotation_tools_cml as data

pytestmark = [pytest.mark.regression_audio_annotation, pytest.mark.fed_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_annotation/audio_data.csv")


@pytest.fixture(scope="module")
def tx_job(app):
    """
    Create Audio Annotation test job with 2 data units and 2 ontology classes
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE, data.audio_annotation_cml,
                                        job_title="Testing audio annotation toolbar", units_per_page=5)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')

    app.navigation.click_link('Manage Audio Annotation Ontology')

    ontology_file = get_data_file("/audio_annotation/ontology.csv")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created", "//span[text()='2']")
    return job_id


def test_toolbar_audio_annotation(app, tx_job):
    """
     1. Verify 'Begin Annotation' button is shown for data unit in preview page
     2. When tool is opened, verify below toolbar icons are enabled by default:
        a. zoom in
        b. previous
        c. play/pause
        d. snap mode
        e. help
        f. volume
        g. save and close
     3. When tool is opened, verify below toolbar icons are disabled by default:
        a. zoom out
        b. reframe
     4. Verify user can play and pause audio using 'Play/pause' toolbar icon
     5. Verify clicking on 'previous' icon plays audio from beginning
     6. Verify clicking on zoom in icon, shows the mini map on top of the audio waveform and zoom out is now enabled
     7. Verify user can reframe the waveform after zooming in
     8. Verify text in help menu
    """
    app.job.preview_job()
    time.sleep(5)
    app.audio_annotation.activate_iframe_by_index(0)
    time.sleep(1)
    app.audio_annotation.begin_annotate(0)
    assert not app.audio_annotation.button_is_disable('zoom_in')
    assert app.audio_annotation.button_is_disable('zoom_out')
    assert app.audio_annotation.button_is_disable('reframe')
    assert not app.audio_annotation.button_is_disable('previous')
    assert not app.audio_annotation.button_is_disable('play_pause')
    assert not app.audio_annotation.button_is_disable('snap_mode')
    assert not app.audio_annotation.button_is_disable('help')
    assert not app.audio_annotation.button_is_disable('volume')
    assert not app.audio_annotation.button_is_disable('save_close')

    # play and pause audio
    before_play_cursor = app.audio_annotation.get_current_cursor()
    app.audio_annotation.click_toolbar_button('play_pause')
    time.sleep(3)
    after_play_cursor = app.audio_annotation.get_current_cursor()
    assert after_play_cursor > before_play_cursor
    app.audio_annotation.click_toolbar_button('play_pause')
    app.audio_annotation.click_toolbar_button('previous')
    start_cursor = app.audio_annotation.get_current_cursor()
    assert start_cursor == before_play_cursor

    # zoom in and zoom out, verify mini map visible
    assert app.audio_annotation.mini_map_visible() is False
    app.audio_annotation.click_toolbar_button('zoom_in')
    assert not app.audio_annotation.button_is_disable('zoom_out')
    assert app.audio_annotation.mini_map_visible() is True
    app.audio_annotation.click_toolbar_button('zoom_out')
    assert app.audio_annotation.mini_map_visible() is False

    # play with zoom in and reframe
    app.audio_annotation.click_toolbar_button('zoom_in')
    assert not app.audio_annotation.button_is_disable('reframe')
    assert app.audio_annotation.mini_map_visible() is True
    app.audio_annotation.click_toolbar_button('reframe')
    assert app.audio_annotation.mini_map_visible() is False

    # check help menu
    app.audio_annotation.click_toolbar_button('help')
    app.verification.text_present_on_page('Using This Tool')
    app.verification.text_present_on_page('PLAYING')
    app.verification.text_present_on_page('Play/Pause')
    app.verification.text_present_on_page('Nudge Forward')
    app.verification.text_present_on_page('Nudge Back')
    app.verification.text_present_on_page('Play Active Segment')
    app.verification.text_present_on_page('DRAWING')
    app.verification.text_present_on_page('Delete Segment')
    app.verification.text_present_on_page('Undo')
    app.verification.text_present_on_page('Redo')
    app.verification.text_present_on_page('Snap Mode')
    app.verification.text_present_on_page('CANVAS')
    app.verification.text_present_on_page('Zoom In')
    app.verification.text_present_on_page('Zoom Out')
    app.verification.text_present_on_page('Zoom to 100%')
    app.audio_annotation.close_help_menu()
    app.verification.text_present_on_page('Using This Tool', is_not=False)


