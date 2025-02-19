"""
https://appen.atlassian.net/browse/QED-1665
https://appen.atlassian.net/browse/QED-1666
This test covers the nested span related test cases in above two tickets.
1. Create 8 test questions for a text annotation flat span job
2. Launch job
3. In Quiz mode, submit judgments for test questions(both correct and incorrect annotations)
4. Go to QUALITY tab, check below items for test question with both correct and incorrect annotation
5. Verify annotate page in the dropdown.
6. Click "Accuracy" in dropdown. Verify the accuracy details.
7. Click "Worker ID" in dropdown. Verify the Correct/Incorrect spans in test questions
"""
import time
from adap.api_automation.utils.data_util import *
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.ui_automation.services_config.text_annotation import copy_with_tq_and_launch_job

pytestmark = pytest.mark.regression_text_annotation

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')

CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')


NESTED_JOB_ID = pytest.data.predefined_data['text_annotation'].get(pytest.env)['tq_nest']


@pytest.fixture(scope="module", autouse=True)
def tx_job(app):
    """
    As a contributor, submit judgments for a predefined Text Annotation job with nested spans
    """
    job_id = copy_with_tq_and_launch_job(API_KEY, NESTED_JOB_ID)
    job_link = generate_job_link(job_id, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    # app.user.close_guide()
    time.sleep(2)

    for i in range(5):
        app.text_annotation.activate_iframe_by_index(i)
        merge_tokens = ["When", "Sebastian", "Thrun", "started", "working"]
        app.text_annotation.merge_token(merge_tokens)
        app.text_annotation.click_span('First 5 tokens merged')
        # make some incorrect annotation for first iframe
        if i == 0:
            app.text_annotation.click_token('people')
            app.text_annotation.click_span('9th token')

        if i > 0:
            app.text_annotation.select_gray_span(2)
            app.text_annotation.click_span('2nd token(of the 5)')

        app.text_annotation.click_token('Google')
        app.text_annotation.click_span('9th token')
        app.text_annotation.click_span('last token (of the 5)')
        app.text_annotation.click_span('7th and 8th tokens')

        app.text_annotation.deactivate_iframe()
        time.sleep(2)

    app.text_annotation.submit_page()
    time.sleep(9)
    app.text_annotation.submit_continue()
    return job_id


@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_review_judgments_for_nested_tq(app_test, tx_job):
    """
    Verify contributor judgments are shown in Quality page
    Verify 'Annotate' page shows all the set annotations for the Test question
    Verify the dropdown shows 'Annotate', 'Accuracy' and 'Contributor IDs' options
    Verify requestor can see "Accuracy" details for test question with judgements, for nested spans
    As a requestor, verify clicking on annotations in accuracy mode shows the corresponding spans accuracy (for nested spans)
    As a requestor, verify both passed and failed spans, corresponding to contributor ID, are shown (for nested spans)
    As a requestor, verify that clicking on correct contributor judgement shows the "Correct Annotation", for nested spans
    As a requestor, verify that clicking on incorrect contributor judgement shows the "Incorrect Annotation", for nested spans
    """
    CONTRIBUTOR_WORKER_ID = get_user_info('test_contributor_task')['worker_id']
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(tx_job)
    app_test.job.open_tab("QUALITY")
    # sort by %missed and get the first row(which has both correct and incorrect annotation)
    app_test.job.quality.click_sortable_header_by_name('% missed')
    app_test.job.quality.open_tq_unit_by_id('first row')

    app_test.job.quality.switch_to_tq_iframe()
    app_test.text_annotation.activate_iframe_by_index(0)

    # Verify default "Annotate" page
    when_label = app_test.text_annotation.get_word_count_with_label('First 5 tokens merged', 'When')
    assert when_label == 1
    sebastian_label = app_test.text_annotation.get_word_count_with_label('First 5 tokens merged', 'Sebastian')
    assert sebastian_label == 1
    google_label = app_test.text_annotation.get_word_count_with_label('last token (of the 5)', 'Google')
    assert google_label == 0
    google_label_latest = app_test.text_annotation.get_word_count_with_label('7th and 8th tokens', 'Google')
    assert google_label_latest == 1

    threshold = app_test.job.quality.get_passing_threshold()
    assert threshold.get_attribute('value') == '75'

    # In dropdown, we have "Annotate","Accuracy" and "Worker Id" three options
    app_test.job.quality.click_tq_dropdown()
    dropdown_list_items = app_test.job.quality.find_all_tq_dropdown_list_items()
    assert 'Annotate' in dropdown_list_items
    assert 'Accuracy' in dropdown_list_items
    assert CONTRIBUTOR_WORKER_ID in dropdown_list_items

    # https://appen.spiraservice.net/5/TestCase/2175.aspx
    # Click "Accuracy" in dropdown, verify requester can see "Accuracy" details
    app_test.job.quality.click_tq_dropdown_list_item('Accuracy')
    accuracy_status = app_test.job.quality.get_accuracy_status()
    assert "66.67% Passing" in accuracy_status
    assert "33.33% Missed" in accuracy_status

    # https://appen.spiraservice.net/5/TestCase/2170.aspx
    # In "Accuracy" mode, verify clicking on annotations shows the corresponding spans accuracy
    app_test.text_annotation.click_token('When')
    span_title = app_test.job.quality.get_span_title_in_accuracy_mode()
    assert 'When Sebastian Thrun started working' == span_title
    span_pass = app_test.job.quality.get_span_pass_in_accuracy_mode()
    assert '100%' == span_pass
    span_classname = app_test.job.quality.get_span_classname_in_accuracy_mode()
    assert '(First 5 tokens merged)' == span_classname

    app_test.text_annotation.click_token('Google')
    span_title = app_test.job.quality.get_span_title_in_accuracy_mode()
    assert 'Google' == span_title
    span_pass = app_test.job.quality.get_span_pass_in_accuracy_mode()
    assert '100%' == span_pass
    span_classname = app_test.job.quality.get_span_classname_in_accuracy_mode()
    assert '(7th and 8th tokens, last token (of the 5), 9th token)' == span_classname

    # Click "Worker ID' in dorpdown, verify requester can see judgment status and correct annotation, incorrect annotation
    app_test.job.quality.click_tq_dropdown()
    app_test.job.quality.click_tq_dropdown_list_item(CONTRIBUTOR_WORKER_ID)
    judgment_status = app_test.job.quality.get_tq_judgment_status()
    assert 'Not Passing' == judgment_status
    judgment_grade = app_test.job.quality.get_tq_judgment_grade()
    assert '50% correct' in judgment_grade
    assert '(75% required)' in judgment_grade

    app_test.verification.text_present_on_page('An annotation instance is correct if both the text string and assigned class are correct.')

    # Click on annotation will show "correct annotation" and "incorrect annotation"
    # https://appen.atlassian.net/browse/QED-1666
    app_test.text_annotation.click_token('When')
    span_status = app_test.job.quality.get_span_status()
    assert 'Correct Annotation' == span_status

    app_test.text_annotation.click_token('people')
    span_status = app_test.job.quality.get_span_status()
    assert 'Incorrect Annotation' == span_status
