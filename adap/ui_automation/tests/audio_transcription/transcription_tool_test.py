
import time
import allure
from selenium.webdriver.support.color import Color

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

    ontology_file = get_data_file('/audio_transcription/AT-ontology-more-group-labels.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    return job_id

@pytest.fixture(autouse=True)
def close_preview_job(app, at_job):
    yield
    if len(app.driver.window_handles) > 1:
        app.driver.close()
        app.navigation.switch_to_window(app.driver.window_handles[0])


@pytest.mark.dependency()
def test_enable_one_layer(app, at_job):
    """
    Verify ontology can be saved, when ‘Transcribe the layer’ is enabled for at least one class
    Verify one segment layer is shown in tool preview mode
    """
    app.user.close_guide()
    assert app.verification.checkbox_by_text_background_color('Transcribe the layer') == 'rgba(255, 255, 255, 1)'

    app.navigation.click_checkbox_by_text('Transcribe the layer')
    color = app.verification.checkbox_by_text_background_color('Transcribe the layer')
    assert color != 'rgba(255, 255, 255, 1)'
    app.navigation.click_link('Save')

    app.job.preview_job()
    time.sleep(2)
    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(0)
    time.sleep(5)

    all_layers = app.audio_transcription.get_audio_layers()
    all_bubbles = app.audio_transcription.get_bubbles_list()
    app.audio_transcription.select_bubble_by_index(index=1)
    all_transcribe_label = app.audio_transcription.group_labels.the_list_of_transcribe_labels()

    assert len(all_layers) == 5
    assert all_bubbles[0]['name'] =='Person'
    assert all_transcribe_label[0].lower() == 'transcribable'
    # assert len(all_transcribe_label) == 5

    app.image_annotation.deactivate_iframe()


def test_enable_all_layers(app, at_job):
    """
    Verify requester can enable transcription for all available ontology classes
    Verify only a mx of 8 layers can be displayed in tool
    """
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(at_job)

    app.navigation.click_link('Manage Audio Transcription Ontology')

    all_classes = app.ontology.get_all_group_audio_tx_labels()

    for ontology_class in range(0, int(all_classes)):
        if not app.verification.checkbox_by_text_is_selected('Transcribe the layer', index=ontology_class):
           app.navigation.click_checkbox_by_text('Transcribe the layer', index=ontology_class)
           assert app.verification.checkbox_by_text_is_selected('Transcribe the layer', index=ontology_class)
           time.sleep(2)
    app.navigation.click_link('Save')

    app.job.preview_job()
    app.audio_transcription.activate_iframe_by_index(0)
    time.sleep(5)

    all_bubbles = app.audio_transcription.get_bubbles_list()

    assert all_bubbles[0]['name'] == 'Segment 1'

    app.audio_transcription.select_bubble_by_name('Person')
    app.audio_transcription.add_text_to_bubble('Person', 'test ignore')
    all_transcribe_label = app.audio_transcription.group_labels.the_list_of_transcribe_labels()

    assert ['TRANSCRIBABLE', 'NOISE', 'PERSON VOICE'] == all_transcribe_label

    # app.audio_transcription.close_at_tool_without_saving()
    app.image_annotation.deactivate_iframe()


def test_info_icon(app, at_job):
    """
    Verify tool info panel contents
    """
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(at_job)
    # job_window = app.driver.window_handles[0]
    app.job.preview_job()
    app.audio_transcription.activate_iframe_by_index(0)

    time.sleep(5)

    app.audio_transcription.toolbar.click_btn_right_panel('ButtonInfo')

    app.verification.text_present_on_page('Using this tool')
    app.verification.text_present_on_page('Play Active Segment')
    app.verification.text_present_on_page('Place Event')
    app.verification.text_present_on_page('Next Segment')
    app.verification.text_present_on_page('Redo')

    app.audio_transcription.toolbar.close_info_panel()

    app.verification.text_present_on_page('Using this tool', is_not=False)
    # app.audio_transcription.close_at_tool_without_saving()
    app.image_annotation.deactivate_iframe()


def test_click_bubble(app, at_job):
    """
    Verify user can make a segment bubble active by clicking it
    """
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(at_job)
    # job_window = app.driver.window_handles[0]
    app.job.preview_job()
    app.audio_transcription.activate_iframe_by_index(0)

    # app.navigation.click_btn("Open Transcription Tool")
    # app.audio_transcription.toolbar.full_screen()
    time.sleep(3)

    app.audio_transcription.select_bubble_by_name('Segment 1', index=0)
    app.audio_transcription.get_active_bubble()
    assert app.audio_transcription.get_active_layer().upper() == app.audio_transcription.get_active_bubble()['color'].upper()

    app.audio_transcription.select_bubble_by_name('Segment 2', index=0)
    assert app.audio_transcription.get_active_layer().upper() == app.audio_transcription.get_active_bubble()['color'].upper()

    app.image_annotation.deactivate_iframe()
    # app.driver.close()
    #
    # app.navigation.switch_to_window(job_window)


# # TODO: https://appen.spiraservice.net/5/TestCase/1232.aspx - Verify that user can scroll information panel when description is long → Regression test
# # TODO https://appen.spiraservice.net/5/TestCase/1233.aspx - Verify that info icon is no longer available, after deleting previously saved description → Regression test
def test_toolbar_is_available(app, at_job):
    """
    Verify play/pause button is available on the tool bar
    """
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(at_job)
    # job_window = app.driver.window_handles[0]
    app.job.preview_job()
    app.audio_transcription.activate_iframe_by_index(0)
    time.sleep(1)

    assert app.audio_transcription.toolbar.get_tooltip_for_btn("play") == 'Play/Pause (Tab)'
    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(0)
    time.sleep(1)

    assert app.audio_transcription.toolbar.get_tooltip_for_btn("back") == 'Nudge back(Cmd/Ctrl+K)'
    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(0)
    time.sleep(1)

    assert app.audio_transcription.toolbar.get_tooltip_for_btn("forward") == 'Nudge forward(Cmd/Ctrl+L)'

    # play speed check
    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(0)
    assert app.audio_transcription.toolbar.get_play_speed() == '1X'
    app.audio_transcription.toolbar.click_btn('play')
    time.sleep(3)
    app.audio_transcription.toolbar.click_btn('pause')
    first_speed_time = app.audio_transcription.toolbar.get_displayed_time().split(':')[2]

    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(0)
    app.audio_transcription.toolbar.click_btn_right_panel('DropdownButton')
    app.audio_transcription.toolbar.select_play_speed("2X")
    assert app.audio_transcription.toolbar.get_play_speed() == '2X'
    app.audio_transcription.toolbar.click_btn('play')
    time.sleep(3)
    app.audio_transcription.toolbar.click_btn('pause')
    second_speed_time = app.audio_transcription.toolbar.get_displayed_time().split(':')[2]
    # even though it is 2X, the play time is not exactly *2, so we use abs
    assert abs(int(first_speed_time) * 2 - int(second_speed_time)) < 3
    app.image_annotation.deactivate_iframe()



def test_audio_cursor_is_available(app, at_job):
    """
    Verify audio cursor is shown on waveform and moves accordingly when played
    """
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(at_job)
    # job_window = app.driver.window_handles[0]
    app.job.preview_job()
    app.audio_transcription.activate_iframe_by_index(0)

    # app.navigation.click_btn("Open Transcription Tool")
    # app.audio_transcription.toolbar.full_screen()
    time.sleep(1)

    assert app.audio_transcription.toolbar.audio_cursor_is_displayed()
    assert app.audio_transcription.toolbar.get_audio_cursor_position() == '0'

    app.audio_transcription.toolbar.click_btn('play')
    time.sleep(3)
    assert int(app.audio_transcription.toolbar.get_audio_cursor_position()) > 0

    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(0)
    # app.audio_transcription.close_at_tool_without_saving()
    # app.navigation.click_btn("Open Transcription Tool")
    # app.audio_transcription.toolbar.full_screen()
    time.sleep(1)

    assert app.audio_transcription.toolbar.audio_cursor_is_displayed()
    assert app.audio_transcription.toolbar.get_audio_cursor_position() == '0'

    # app.audio_transcription.close_at_tool_without_saving()
    app.image_annotation.deactivate_iframe()
    # app.driver.close()
    # app.navigation.switch_to_window(job_window)


def test_audio_cursor_move(app, at_job):
    """
    Verify audio cursor moves accordingly on the waveform when play/pause/forward/backward icons are used
    """
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(at_job)
    app.job.preview_job()
    app.audio_transcription.activate_iframe_by_index(0)
    time.sleep(1)

    assert app.audio_transcription.toolbar.get_audio_cursor_position() == '0'

    app.audio_transcription.toolbar.click_btn('play')
    time.sleep(30)

    stop_position = app.audio_transcription.toolbar.get_audio_cursor_position()
    int_stop_position = int(stop_position)
    assert int_stop_position > 0
    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(0)
    time.sleep(1)

    app.audio_transcription.toolbar.click_btn('play')
    time.sleep(5)
    app.audio_transcription.toolbar.click_btn('pause')
    app.audio_transcription.toolbar.click_btn('back', index=1)
    int_current_position_pause = int(app.audio_transcription.toolbar.get_audio_cursor_position())
    assert 0 < int_current_position_pause < int_stop_position

    app.audio_transcription.toolbar.click_btn('back', index=1)
    int_current_position_back = int(app.audio_transcription.toolbar.get_audio_cursor_position())
    assert 0 < int_current_position_back < int_current_position_pause

    app.audio_transcription.toolbar.click_btn('forward', index=2)
    current_position_forward = int(app.audio_transcription.toolbar.get_audio_cursor_position())
    assert int_current_position_pause-1 <= current_position_forward <= int_current_position_pause + 1

    app.audio_transcription.toolbar.click_btn('play')
    time.sleep(30)

    assert int_stop_position - 100 <= int(app.audio_transcription.toolbar.get_audio_cursor_position()) <= int_stop_position + 100
    assert int_stop_position == int(app.audio_transcription.toolbar.get_audio_cursor_position())
