"""
This test covers below:
1. toolbar
"""
import time
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [
    pytest.mark.regression_image_transcription,
    pytest.mark.fed_ui,
    pytest.mark.adap_ui_uat,
    pytest.mark.adap_uat
]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/image_transcription/receipts.csv")


@pytest.fixture(scope="module")
def tx_job(app):
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
    return job_id


def test_toolbar_mlait(app, tx_job):
    app.job.preview_job()
    time.sleep(5)
    app.image_transcription.activate_iframe_by_index(0)
    time.sleep(2)
    assert app.image_transcription.button_is_disable('delete')
    assert app.image_transcription.button_is_disable('undo')
    assert app.image_transcription.button_is_disable('redo')
    assert app.image_transcription.button_is_disable('pan')
    assert not app.image_transcription.button_is_disable('zoom_in')
    assert not app.image_transcription.button_is_disable('zoom_out')
    assert app.image_transcription.button_is_disable('reframe')
    assert not app.image_transcription.button_is_disable('crosshair')
    assert app.image_transcription.button_is_disable('focus_mode')
    assert app.image_transcription.button_is_disable('hide_mode')
    assert not app.image_transcription.button_is_disable('shape_opacity')
    assert not app.image_transcription.button_is_disable('show_label')
    assert not app.image_transcription.button_is_disable('auto_enhance')
    assert not app.image_transcription.button_is_disable('help')
    assert not app.image_transcription.button_is_disable('full_screen')

    # verify labels menu
    app.image_transcription.click_toolbar_button('show_label')
    app.verification.text_present_on_page('Show labels for')
    app.verification.text_present_on_page('All')
    app.verification.text_present_on_page('Selected Class')
    app.verification.text_present_on_page('Selected Shape')
    app.verification.text_present_on_page('None')

    # verify help menu
    app.image_transcription.click_toolbar_button('help')
    app.verification.text_present_on_page('Using this tool')
    app.verification.text_present_on_page('CANVAS')
    app.verification.text_present_on_page('Toggle shape opacity')
    app.verification.text_present_on_page('TRANSCRIPTIONS')
    app.verification.text_present_on_page('Predict')
    app.verification.text_present_on_page('Apply Prediction')
    app.verification.text_present_on_page('DRAWING')
    app.verification.text_present_on_page('Delete Shape')
    app.verification.text_present_on_page('Next Shape')
    app.verification.text_present_on_page('Enable/disable hide mode')
    app.image_transcription.close_help_menu()
    app.verification.text_present_on_page('Using This Tool', is_not=False)

    # create ontology and delete it, verify toolbar
    app.image_transcription.select_ontology_class('total')
    assert app.image_transcription.button_is_disable('hide_mode')
    app.image_transcription.draw_box_with_coordination(100, 100, 20, 20)
    attemts = 0
    while app.image_annotation.button_is_disable('hide_mode') and attemts < 3:
        time.sleep(1)
        attemts += 1
        if not app.image_annotation.button_is_disable('hide_mode'):
            break

    assert not app.image_annotation.button_is_disable('hide_mode')
    assert app.image_transcription.find_labethisjob_floatingwrapper()
    assert not app.image_transcription.button_is_disable('delete')
    assert not app.image_transcription.button_is_disable('undo')
    assert not app.image_transcription.button_is_disable('focus_mode')

    app.image_transcription.click_toolbar_button('delete')
    assert not app.image_transcription.find_labethisjob_floatingwrapper()