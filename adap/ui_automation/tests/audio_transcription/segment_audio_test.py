import time

from selenium.webdriver.common.keys import Keys

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

    app.audio_transcription.activate_iframe_by_index(0)

    return job_id


def test_play_icon(app, at_job):
    """
    Verify play icon is available in all segment bubbles and clicking on it plays the corresponding segment audio and stops at the end
    """
    checked_bubbels = {}
    bubbles = app.audio_transcription.get_bubbles_list()
    for bubble in bubbles:
        name = bubble['name']
        if checked_bubbels.get(name, False):
            checked_bubbels[name] = checked_bubbels[name] + 1
        else:
            checked_bubbels[name] = 1

        index = checked_bubbels[name] - 1

        app.audio_transcription.add_text_to_bubble(name, 'test', index)
        len_of = app.audio_transcription.get_audio_cursor_transform_info()
        print(len_of)
        app.audio_transcription.click_play_segment_for_bubble(name, index)
        len_of_active = app.audio_transcription.get_audio_cursor_transform_info()
        print(len_of_active)
        assert app.audio_transcription.get_active_layer_number() > 0
            # assert app.audio_transcription.get_active_layer().upper() == bubble['name'].upper()

        time.sleep(3)

@pytest.mark.skip(reason='Not working on docker')
def test_play_segment_by_hotkey(app, at_job):
    """
    Verify segment audio can be played using hotkey, CMD+P, when it is active
    """
    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(0)
    bubbles = app.audio_transcription.get_bubbles_list()

    _bubble = bubbles[1]

    init_cursor = app.audio_transcription.toolbar.get_audio_cursor_position()

    app.audio_transcription.add_text_to_bubble(_bubble['name'], "test")

    app.navigation.combine_hotkey(Keys.SHIFT, 'p')

    assert _bubble['color'].upper() == app.audio_transcription.get_active_layer().upper()

    time.sleep(10)

    stop_cursor = app.audio_transcription.toolbar.get_audio_cursor_position()

    assert int(init_cursor)<int(stop_cursor)


def test_segments_order(app, at_job):
    """
    Verify that the segment bubbles are displayed in the chronological order of segment start time
    """
    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(0)
    time.sleep(5)
    segments = app.audio_transcription.get_audio_layers_with_segments()
    ordered_seg = {}
    for bubble in segments.values():
        for c_seg in bubble:
            ordered_seg[float(c_seg['top'][:-2])] = c_seg['inactive_color']

    _bubbles = app.audio_transcription.get_bubbles_list()
    list_of_bubbles = [x['color'].lower() for x in _bubbles if x['color']]
    segments_by_color = list(dict(sorted(ordered_seg.items())).values())
    assert list_of_bubbles == segments_by_color


def test_bubbles_control_hotkey(app, at_job):
    """
    Verify hotkey ‘Enter’ moves control to next segment bubble --> UAT test
    Verify hotkey ‘Shift + Enter’ moves control to the previous segment bubble --> UAT test
    """

    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(0)

    _bubbles = app.audio_transcription.get_bubbles_list()

    first_bubble = _bubbles[0]
    app.audio_transcription.add_text_to_bubble(first_bubble['name'], "test")

    _first_info = app.audio_transcription.get_active_bubble()
    assert app.audio_transcription.get_active_layer().upper() == _first_info['color'].upper()

    app.navigation.hotkey(Keys.RETURN)

    _second_info = app.audio_transcription.get_active_bubble()
    assert app.audio_transcription.get_active_layer() == _second_info['color']
    assert _second_info['name'] != _first_info['name']

    app.navigation.combine_hotkey(Keys.SHIFT, Keys.RETURN)

    _current_info = app.audio_transcription.get_active_bubble()
    assert app.audio_transcription.get_active_layer().upper() == _current_info['color'].upper()
    assert _current_info['name'] == _first_info['name']
