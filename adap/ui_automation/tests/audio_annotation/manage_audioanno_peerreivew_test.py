"""
https://appen.atlassian.net/browse/QED-1650
This test covers:
1. create peer review job
2. manage annotations for peer review job by deleting it. Undo delete and Redo delete
2. test validator peer review job for audio annotation
"""
import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.annotation import create_peer_review_job
from selenium.webdriver.common.keys import Keys
from adap.data import annotation_tools_cml as data

# skip on staging due to https://appen.atlassian.net/browse/DO-10791
pytestmark = pytest.mark.regression_audio_annotation

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
PREDEFINED_JOB_ID = pytest.data.predefined_data['audio_annotation'].get(pytest.env)


@pytest.fixture(scope="module", autouse=True)
def audio_job_peer(tmpdir_factory, app):
    """
    Create Audio Annotation(AA) review job using the output of a predefined AA job and upload ontology
    """
    tmpdir = tmpdir_factory.mktemp('data')
    job_id = create_peer_review_job(tmpdir, API_KEY, PREDEFINED_JOB_ID, data.audio_annotation_peer_review_cml)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Annotation Ontology')

    ontology_file = get_data_file("/audio_annotation/ontology.csv")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created", "//span[text()='2']")
    return job_id


# @pytest.mark.dependency()
# @pytest.mark.skipif(not pytest.running_in_preprod_sandbox, reason="Only Sandbox has correct data configured")
# def test_delete_annotation_for_peer_review(app, audio_job_peer):
#     """
#     In preview mode, verify requestor can delete existing annotation, along with undo and redo of deletion using hotkeys 'z' and 'y'
#     """
#     app.job.preview_job()
#     time.sleep(3)
#
#     # update annotate by deleting one
#     rows_on_page = app.annotation.get_number_iframes_on_page()
#     assert rows_on_page == 5
#     app.audio_annotation.activate_iframe_by_index(0)
#     app.audio_annotation.edit_annotate(0)
#     before_delete_segment = app.audio_annotation.get_segment_count()
#     assert before_delete_segment > 0
#     app.audio_annotation.single_hotkey(Keys.DELETE)
#     after_delete_segment = app.audio_annotation.get_segment_count()
#     assert after_delete_segment == before_delete_segment - 1
#     # undo delete
#     app.audio_annotation.combine_hotkey(Keys.COMMAND, 'z')
#     undo_delete_segment = app.audio_annotation.get_segment_count()
#     assert undo_delete_segment == before_delete_segment
#     # redo delete
#     app.audio_annotation.combine_hotkey(Keys.COMMAND, 'y')
#     redo_delete_segment = app.audio_annotation.get_segment_count()
#     assert redo_delete_segment == after_delete_segment
#
#     app.audio_annotation.click_toolbar_button('save_close')
#     app.audio_annotation.deactivate_iframe()
#
#
# @pytest.mark.dependency(depends=["test_delete_annotation_for_peer_review"])
# # @pytest.mark.skipif(pytest.env not in ["sandbox"], reason="configured predefined job for sandbox")
# def test_submit_validator_for_peer_review(app, audio_job_peer):
#     """
#     In preview mode, verify validation passes after deleting existing annotation
#     """
#     # browse other iframes, make sure annotations are being displayed on it
#     for i in range(1, 5):
#         app.audio_annotation.activate_iframe_by_index(i)
#         app.audio_annotation.edit_annotate(0)
#         segment_count = app.audio_annotation.get_segment_count()
#         assert segment_count > 0
#         app.audio_annotation.click_toolbar_button('save_close')
#         app.audio_annotation.deactivate_iframe()
#
#     # submit validator
#     app.audio_annotation.submit_test_validators()
#     time.sleep(8)
#     app.verification.text_present_on_page("Validation succeeded")
