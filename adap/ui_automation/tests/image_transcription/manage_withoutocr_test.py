"""
This test covers below:
1. manage transcription without ocr
"""
import time
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_image_transcription, pytest.mark.fed_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/image_transcription/receipts.csv")


@pytest.fixture(scope="module")
def tx_job(app):
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.image_transcription_withoutocr_cml,
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


def test_manage_transcription_without_ocr(app, tx_job):
    app.job.preview_job()
    time.sleep(5)
    app.image_transcription.activate_iframe_by_index(0)
    time.sleep(3)
    # create multiple text transcriptions
    app.image_transcription.full_screen()
    app.image_transcription.draw_box_with_coordination(100, 100, 20, 20)
    app.image_transcription.input_transcription_text('mlait1')
    app.image_transcription.select_ontology_class('total')
    app.image_transcription.draw_box_with_coordination(150, 150, 20, 20)
    app.image_transcription.input_transcription_text('mlait2')

    # get transcription text and edit it
    app.image_transcription.expand_category('price')
    shape_items_for_price_category = app.image_transcription.get_shape_items_for_category('price')
    app.image_transcription.collapse_open_category()
    assert len(shape_items_for_price_category) == 1

    app.image_transcription.expand_category('total')
    shape_items_for_total_category = app.image_transcription.get_shape_items_for_category('total')
    assert len(shape_items_for_total_category) == 1
    app.image_transcription.collapse_open_category()

    app.image_transcription.expand_category('price')
    text_for_mlait1 = app.image_transcription.get_transcription_text('price', 0)
    assert text_for_mlait1 == 'mlait1'
    app.image_transcription.collapse_open_category()

    app.image_transcription.expand_category('total')
    text_for_mlait2 = app.image_transcription.get_transcription_text('total', 0)
    assert text_for_mlait2 == 'mlait2'
    app.image_transcription.collapse_open_category()

    app.image_transcription.expand_category('price')
    app.image_transcription.edit_transcription_text('price', 0, 'editmlait1')
    text_edited = app.image_transcription.get_transcription_text('price', 0)
    assert text_edited == 'editmlait1'
    app.image_transcription.collapse_open_category()

    # delete transcriptions
    app.image_transcription.expand_category('price')
    app.image_transcription.delete_transcription('price', 0)
    app.image_transcription.collapse_open_category()

    app.image_transcription.expand_category('total')
    app.image_transcription.delete_transcription('total', 0)
    app.image_transcription.collapse_open_category()

    shape_items_after_delete_for_price = app.image_transcription.get_shape_count_for_category('price')
    assert shape_items_after_delete_for_price == '0'
    shape_items_after_delete_for_total = app.image_transcription.get_shape_count_for_category('total')
    assert shape_items_after_delete_for_total == '0'
    app.image_transcription.full_screen()
    app.image_transcription.deactivate_iframe()