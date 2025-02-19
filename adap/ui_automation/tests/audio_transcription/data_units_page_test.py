"""
https://appen.atlassian.net/browse/QED-1947
"""
import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.selenium_utils import go_to_page
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

mark_only_sandbox = pytest.mark.skipif(not pytest.running_in_preprod_sandbox, reason="Only sandbox has multiple contributors configured")
pytestmark = [pytest.mark.regression_audio_transcription_design, pytest.mark.audio_transcription_ui, mark_only_sandbox]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/AT-newdata-dv.csv")
CONTRIBUTORS = ['test_contributor_task', 'test_multiple_contributors_task']


@pytest.fixture(scope="module")
def at_job(app):
    """
    Create Audio Tx job with 2 data rows, upload ontology and add span/event
    Add spell check data validation rule
    Launch job
    """
    target_mode = 'AT'
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

    app.ontology.add_tag("Span", "Cat span", "span 1 description")
    app.ontology.add_tag("Event", "Cat event", "event with description")

    # add spell check rule
    url = "https://client.%s.cf3.us/jobs/%s/data_validation" % (pytest.env, job_id)
    go_to_page(app.driver, url)
    app.user.close_guide()
    app.navigation.click_btn('Add rules')
    app.audio_transcription.data_validation.enter_language_check_rule_info(language='English', locale='American')
    app.navigation.click_btn('Save')
    time.sleep(3)

    # launch job
    app.job.open_action("Settings")
    if pytest.env == 'fed':
        app.navigation.click_link("Select Contributor Channels")
        app.job.select_hosted_channel_by_index(save=True)
    else:
        app.driver.find_element('xpath',"//label[@for='externalChannelsEnabled' or text()='External']").click()
        app.navigation.click_link('Save')

    app.job.open_tab('LAUNCH')
    app.navigation.click_link("Launch Job")

    job = JobAPI(API_KEY, job_id=job_id)

    job.wait_until_status('running', 150)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    return job_id


# https://appen.spiraservice.net/5/TestCase/3034.aspx
@pytest.mark.dependency()
def test_no_judgment_no_dropdown(app, at_job):
    """
    When judgments are not available, verify dropdown is not shown in toolbar
    """
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(at_job)
    app.job.open_tab('Data')
    units = app.job.data.find_all_units_with_status('judgable')
    first_unit = units['unit id'][0]
    app.job.data.open_unit_by_id(first_unit)
    app.verification.current_url_contains("/units/%s" % first_unit)
    app.audio_transcription.data_unit.activate_iframe_on_unit_page()
    app.audio_transcription.data_unit.worker_id_dropdown_button_is_displayed(is_not=False)
    time.sleep(2)
    app.audio_transcription.deactivate_iframe()
    app.user.logout()


@pytest.mark.dependency(depends=["test_no_judgment_no_dropdown"])
def test_add_judgments_from_multiple_contributors(app, at_job):
    """
    Submit multiple judgments as a contributor
    """
    for contributor in CONTRIBUTORS:
        job_link = generate_job_link(at_job, API_KEY, pytest.env)
        app.navigation.open_page(job_link)
        app.user.task.login(get_user_email(contributor), get_user_password(contributor))
        app.user.close_guide()
        time.sleep(2)
        app.user.task.wait_until_job_available_for_contributor(job_link)
        for i in range(2):
            app.audio_transcription.activate_iframe_by_index(i)
            checked_bubbles = {}
            bubbles = app.audio_transcription.get_bubbles_list()
            for bubble in bubbles:
                name = bubble['name']
                if checked_bubbles.get(name, False):
                    checked_bubbles[name] = checked_bubbles[name] + 1
                else:
                    checked_bubbles[name] = 1

                index = checked_bubbles[name] - 1
                app.audio_transcription.add_text_to_bubble(name, "test data validation eror " + get_user_worker_id(contributor), index)

                # add span and event for 'Cat'
                if name == 'Cat':
                    app.audio_transcription.span.highlight_text_in_bubble(span_text='data', bubble_name='Cat', index=index)
                    app.audio_transcription.span.add_span('Cat span')
                    app.audio_transcription.event.move_cursor_to_text_in_bubble('validation', 'Cat', index=0)
                    app.audio_transcription.event.click_event_marker('Cat', index=index)
                    app.audio_transcription.event.add_event('Cat event')

            app.audio_transcription.deactivate_iframe()
        app.audio_transcription.submit_page()
        time.sleep(5)
        app.verification.text_present_on_page('There is no work currently available in this task.')
        app.user.task.logout()


@pytest.mark.skip
@pytest.mark.dependency(depends=["test_add_judgments_from_multiple_contributors"])
def test_data_unit_page_with_multiple_contributors_judgments(app, at_job):
    """
    Verify judgments are shown as per the selected contributor ID, in data unit page
    Verify number of judgments are shown on Data unit page, with a dropdown when 2+ contributor judgments are available
    Verify transcription text, spans, events and validation errors are all available in judgments
    """
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(at_job)
    app.job.open_tab('Data')
    units = app.job.data.find_all_units_with_status('judgable')
    first_unit = units['unit id'][0]
    app.job.data.open_unit_by_id(first_unit)
    app.audio_transcription.data_unit.activate_iframe_on_unit_page()
    app.audio_transcription.data_unit.worker_id_dropdown_button_is_displayed()
    app.audio_transcription.data_unit.click_worker_id_dropdown_button()
    assert app.audio_transcription.data_unit.get_number_of_contributors_from_dropdown_list() == len(CONTRIBUTORS)
    contributor_index = random.randint(0, 1)
    contributor = CONTRIBUTORS[contributor_index]
    app.audio_transcription.data_unit.click_worker_id_from_dropdown_list(worker_id=get_user_worker_id(contributor))
    # verify span and event
    span_info = app.audio_transcription.span.get_text_with_spans('Cat')
    assert span_info[0]['span_name'] == 'Cat span'

    _events = app.audio_transcription.get_span_event('Cat')
    assert _events['event_name'] == ['<cat_event/>']
    # verify text and validation errors available
    assert app.audio_transcription.get_text_from_bubble('Person') == "test data validation eror " + get_user_worker_id(contributor)
    app.audio_transcription.event.move_cursor_to_the_end_of_text_in_bubble('Person', additional_space=True)
    time.sleep(3)
    assert app.audio_transcription.btn_is_displayed('IGNORE')
    app.audio_transcription.deactivate_iframe()