"""
https://appen.atlassian.net/browse/QED-1654
This test covers:
1. create peer review job
2. edit/delete transcription for peer review job
3. test validator peer review job
"""
import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.annotation import create_peer_review_job
from adap.data import annotation_tools_cml as data
from adap.api_automation.services_config.builder import Builder

pytestmark = [pytest.mark.regression_image_transcription]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
PREDEFINED_JOB_ID = pytest.data.predefined_data['mlait'].get(pytest.env)


# staging depend on this https://appen.atlassian.net/browse/DO-10801 to submit judgments for job 1423210, then use it to create peer review job
@pytest.fixture(scope="module", autouse=True)
def tx_job(tmpdir_factory, app):
    tmpdir = tmpdir_factory.mktemp('data')
    job_id = create_peer_review_job(tmpdir, API_KEY, PREDEFINED_JOB_ID, data.image_transcription_peer_review_cml)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Transcription Ontology')

    ontology_file = get_data_file("/image_transcription/ontology.json")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created")
    return job_id


@pytest.mark.skipif(not pytest.running_in_preprod, reason="only enabled in preprod")
@allure.issue("https://appen.atlassian.net/browse/AT-5444", "BUG AT-5444")
@pytest.mark.dependency()
def test_manage_peer_review(app, tx_job):
    app.job.preview_job()
    time.sleep(3)

    rows_on_page = app.annotation.get_number_iframes_on_page()
    assert rows_on_page == 5

    app.image_transcription.activate_iframe_by_index(0)

    # user is able to edit transcription for peer review job

    app.image_transcription.expand_category('price')
    shape_items_for_price_category = app.image_transcription.get_shape_items_for_category('price')
    assert len(shape_items_for_price_category) == 2
    app.image_transcription.collapse_open_category()

    shape_count_for_total_category = app.image_transcription.get_shape_count_for_category('total')
    assert shape_count_for_total_category == '0'

    app.image_transcription.expand_category('price')
    app.image_transcription.edit_transcription_text('price', 0, 'edittext')
    text_edited = app.image_transcription.get_transcription_text('price', 0)
    assert text_edited == 'edittext'

    # user is able to delete transcription
    app.image_transcription.delete_transcription('price', 1)
    shape_items_after_delete = app.image_transcription.get_shape_items_for_category('price')
    assert len(shape_items_after_delete) == 1
    app.image_transcription.deactivate_iframe()

    # submit validator
    app.image_transcription.submit_test_validators()
    time.sleep(2)
    app.verification.text_present_on_page("Validation succeeded")


@pytest.mark.skipif(not pytest.running_in_preprod, reason="only enabled in preprod")
@pytest.mark.dependency(depends=["test_manage_peer_review"])
def test_mlait_image_rotation_peer_review_job_error_tile(app, tx_job):
    # update cml and verify scenario in https://appen.atlassian.net/browse/AT-3478
    # The job does have allow-image-rotation=true but the data read in view review-from does not have rotation values, then read in the data with rotation value of 0.
    updated_payload = {
        'key': API_KEY,
        'job': {
            'cml': data.image_transcription_rotation_peer_review_cml
        }
    }

    job = Builder(API_KEY)
    job.job_id = tx_job
    job.update_job(payload=updated_payload)

    app.navigation.refresh_page()
    app.image_transcription.activate_iframe_by_index(0)
    app.image_transcription.click_image_rotation_button()
    app.image_transcription.image_rotation_slider_bar_available()
    assert app.image_transcription.get_image_rotation_degree() == "0°"
    app.image_transcription.close_image_rotation_bar()
    app.image_transcription.image_rotation_slider_bar_available(is_not=False)
    app.image_transcription.deactivate_iframe()