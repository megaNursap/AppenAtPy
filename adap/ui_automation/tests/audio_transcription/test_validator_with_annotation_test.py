"""
AT - UI Automation - "Test Validators" functionality
https://appen.atlassian.net/browse/QED-1692
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

    ontology_file = get_data_file('/audio_transcription/AT-new-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    app.job.preview_job()

    return job_id


@pytest.mark.dependency()
def test_validation_no_transcription(app, at_job):
    """
    Verify "Test Validators" throws an error when segment bubbles are either left empty, or not marked “Nothing to transcribe' or contain only white space
    """
    app.navigation.refresh_page()

    global min_task, max_task
    page_task = []
    for iframe in range(2):
        app.text_relationship.activate_iframe_by_index(iframe)

        segments = app.audio_transcription.get_bubbles_list()
        page_task.append(len(segments))

        app.audio_transcription.deactivate_iframe()

    min_task = page_task.index(min(page_task))
    max_task = page_task.index(max(page_task))

    app.text_relationship.activate_iframe_by_index(min_task)

    skipped_transcription = False
    checked_bubbles = {}
    bubbles = app.audio_transcription.get_bubbles_list()
    i = 0
    for bubble in bubbles:

        name = bubble['name']

        if checked_bubbles.get(name, False):
            checked_bubbles[name] = checked_bubbles[name] + 1
        else:
            checked_bubbles[name] = 1
        index = checked_bubbles[name] - 1

        if skipped_transcription:
            app.audio_transcription.select_bubble_by_name(name, index)
            app.audio_transcription.add_text_to_bubble(name, "test", index)
            app.audio_transcription.group_labels.close_label_panel()
            i += 1
        skipped_transcription = True

    app.audio_transcription.deactivate_iframe()
    app.audio_transcription.submit_test_validators()
    assert app.audio_transcription.get_task_error_msg_by_index(min_task) == "Error: All segments have to be transcribed or marked as nothing to transcribe."


@pytest.mark.dependency(depends=["test_validation_no_transcription"])
def test_validation_empty_transcription(app, at_job):
    """
    Verify "Test Validators" throws an error when segment bubbles are either left empty, or not marked “Nothing to transcribe' or contain only white space
    """
    app.text_relationship.activate_iframe_by_index(min_task)

    bubbles = app.audio_transcription.get_bubbles_list()

    app.audio_transcription.add_text_to_bubble(bubbles[0]['name'], '   ')

    app.audio_transcription.deactivate_iframe()
    app.audio_transcription.submit_test_validators()
    assert app.audio_transcription.get_task_error_msg_by_index(min_task) == "Error: All segments have to be transcribed or marked as nothing to transcribe."


@pytest.mark.dependency(depends=["test_validation_empty_transcription"])
def test_validation_passed(app, at_job):
    """
    Verify "Test Validators" passes when all transcription bubbles either have transcription or marked as “Nothing to transcribe”
    """
    app.text_relationship.activate_iframe_by_index(min_task)

    bubbles = app.audio_transcription.get_bubbles_list()

    app.audio_transcription.delete_text_from_bubble(bubbles[0]['name'])
    app.audio_transcription.click_nothing_to_transcribe_for_bubble(bubbles[0]['name'])
    app.audio_transcription.deactivate_iframe()

    app.audio_transcription.submit_test_validators()
    assert not app.audio_transcription.get_task_error_msg_by_index(min_task)


@pytest.mark.dependency(depends=["test_validation_passed"])
def test_validation_edit_transcription(app, at_job):
    """
    Verify validation error is thrown when requestor clicks 'Test Validators' when a previously saved transcription is deleted --> UAT test
    """
    app.audio_transcription.activate_iframe_by_index(min_task)

    bubbles = app.audio_transcription.get_bubbles_list()
    app.audio_transcription.delete_text_from_bubble(bubbles[1]['name'])
    app.audio_transcription.deactivate_iframe()
    app.audio_transcription.submit_test_validators()

    # assert app.audio_transcription.get_task_error_msg_by_index(min_task) == "Error: All segments have to be transcribed or marked as nothing to transcribe."


@pytest.mark.dependency(depends=["test_validation_edit_transcription"])
def test_validation_nothing_to_transcribe(app, at_job):
    """
    Verify ‘Test Validators’ pass after user chooses “Nothing to transcribe” at tool level
    """
    app.audio_transcription.activate_iframe_by_index(max_task)
    app.audio_transcription.click_nothing_to_transcribe_for_task()
    app.audio_transcription.deactivate_iframe()
    app.audio_transcription.submit_test_validators()
    assert not app.audio_transcription.get_task_error_msg_by_index(max_task)
