"""
https://appen.atlassian.net/browse/QED-2232
https://appen.atlassian.net/browse/QED-2234
"""
import time
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.data import annotation_tools_cml as data
from adap.api_automation.services_config.builder import Builder
from adap.ui_automation.services_config.annotation import create_peer_review_job
import urllib
import json

pytestmark = [pytest.mark.regression_audio_transcription_subset, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_predefined_jobs')
PASSWORD = get_user_password('test_predefined_jobs')
API_KEY = get_user_api_key('test_predefined_jobs')

PREDEFINED_JOB_ID = pytest.data.predefined_data['audio_transcription'].get(pytest.env)


@pytest.fixture(scope="module", autouse=True)
def subset_job(tmpdir_factory, app):
    target_mode = 'AT'
    tmpdir = tmpdir_factory.mktemp('data')
    job_id = create_peer_review_job(tmpdir, API_KEY, PREDEFINED_JOB_ID, data.audio_transcription_subset_cml,
                                    units_per_page=2)

    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')
    ontology_file = get_data_file('/audio_transcription/reviewdata_with_instances_ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

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

    job.wait_until_status('running', 120)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    return job_id


@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_subset_outof_range_error_message(app, subset_job):
    """
    https://appen.atlassian.net/browse/QED-2231
    """
    updated_payload = {
        'key': API_KEY,
        'job': {
            'cml': data.audio_transcription_subset_cml_outside_range
        }
    }
    job = Builder(API_KEY)
    job.job_id = subset_job
    resp = job.update_job(payload=updated_payload)
    assert "subset should be a number between 0.01 and 1" in resp.json_response.get("errors")[0]


@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_subset_without_review_from_error_message(app, subset_job):
    """
    https://appen.atlassian.net/browse/QED-2231
    """
    updated_payload = {
        'key': API_KEY,
        'job': {
            'cml': data.audio_transcription_subset_cml_without_review_from
        }
    }
    job = Builder(API_KEY)
    job.job_id = subset_job
    resp = job.update_job(payload=updated_payload)
    assert "subset attribute can only be used with review-from" in resp.json_response.get("errors")[0]


# https://appen.spiraservice.net/5/TestCase/3243.aspx
# https://appen.spiraservice.net/5/TestCase/3244.aspx
@pytest.mark.dependency()
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_subset_of_segments(app, subset_job):
    """
    Verify that a subset of segments are shown in the review job based on the subset attribute value defined in job CML
    """
    job_link = generate_job_link(subset_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.close_guide()
    time.sleep(5)

    app.audio_transcription.activate_iframe_by_index(0)
    bubbles = app.audio_transcription.get_bubbles_list()
    assert len(bubbles) == 2
    bubbles_name = app.audio_transcription.get_bubbles_name()
    bubbles_name.sort()
    app.audio_transcription.deactivate_iframe()
    app.navigation.refresh_page()

    # refresh page, verify same bubbles display
    app.audio_transcription.activate_iframe_by_index(0)
    bubbles_name_after_refresh = app.audio_transcription.get_bubbles_name()
    bubbles_name_after_refresh.sort()
    assert bubbles_name == bubbles_name_after_refresh
    app.audio_transcription.deactivate_iframe()
    app.user.task.logout()
    # logout and login again, verify same bubbles display
    app.navigation.open_page(job_link)
    app.user.task.login(USER_EMAIL, PASSWORD)
    app.user.close_guide()
    time.sleep(2)
    app.audio_transcription.activate_iframe_by_index(0)
    bubbles_name_after_relogin = app.audio_transcription.get_bubbles_name()
    bubbles_name_after_relogin.sort()
    assert bubbles_name == bubbles_name_after_relogin
    app.audio_transcription.deactivate_iframe()


# https://appen.spiraservice.net/5/TestCase/3245.aspx
@pytest.mark.dependency(depends=["test_subset_of_segments"])
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="only enabled in preprod")
def test_segments_subset_change(app, subset_job):
    updated_payload = {
        'key': API_KEY,
        'job': {
            'cml': data.audio_transcription_subset_cml_2
        }
    }
    job = Builder(API_KEY)
    job.job_id = subset_job
    job.update_job(payload=updated_payload)

    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(0)
    bubbles = app.audio_transcription.get_bubbles_list()
    assert len(bubbles) == 3
    app.audio_transcription.deactivate_iframe()


@pytest.mark.dependency(depends=["test_subset_of_segments"])
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="only enabled in preprod")
def test_submit_judgements_with_review(app, subset_job):
    app.audio_transcription.submit_page()
    app.verification.text_present_on_page("Error: There are some missing reviews. Please check.")

    for i in range(0, 2):
        app.audio_transcription.activate_iframe_by_index(i)
        bubbles = app.audio_transcription.get_bubbles_list()
        checked_bubbels = {}
        for bubble in bubbles:
            name = bubble['name']
            if checked_bubbels.get(name, False):
                checked_bubbels[name] = checked_bubbels[name] + 1
            else:
                checked_bubbels[name] = 1

            index = checked_bubbels[name] - 1
            assert app.audio_transcription.review_button_is_displayed(name)
            app.audio_transcription.click_review_for_bubble(name)
            app.audio_transcription.reviewed_icon_is_displayed(name)

        app.audio_transcription.deactivate_iframe()
    # https://appen.spiraservice.net/5/TestCase/3254.aspx
    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(0)
    bubbles = app.audio_transcription.get_bubbles_list()
    app.audio_transcription.reviewed_icon_is_displayed(bubbles[0]['name'])
    app.audio_transcription.deactivate_iframe()
    app.audio_transcription.submit_page()
    time.sleep(5)
    app.verification.text_present_on_page('There is no work currently available in this task.')


# Todo, add report check for case https://appen.spiraservice.net/5/TestCase/3246.aspx  once https://appen.atlassian.net/browse/AT-3819 is resolved
@pytest.mark.dependency(depends=["test_submit_judgements_with_review"])
@pytest.mark.skip
def test_review_status_in_reports(app_test, subset_job):
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(subset_job)

    app_test.job.open_tab("RESULTS")
    app_test.job.results.download_report("Full", subset_job)
    file_name_zip = "/" + app_test.job.results.get_file_report_name(subset_job, "Full")
    full_file_name_zip = app_test.temp_path_file + file_name_zip

    unzip_file(full_file_name_zip)
    csv_name = str(full_file_name_zip)[:-4]

    _df = pd.read_csv(csv_name)
    assert 'new_audio_transcription' in _df.columns
    assert 'annotate_the_thing' in _df.columns
    assert 'audio_transcription' in _df.columns

    random_row = random.randint(0, _df.shape[0] - 1)
    annotate_result = _df['new_audio_transcription'][random_row]
    assert 'type' in annotate_result
    assert 'valueRef' in annotate_result
    assert 'url' in annotate_result

    json_value = json.loads(annotate_result).get('url')
    response = urllib.request.urlopen(json_value)
    annotation_data = json.loads(response.read())
    assert "id" in annotation_data.get("annotation")[0][0]
    assert "layerId" in annotation_data.get("annotation")[0][0]
    assert "startTime" in annotation_data.get("annotation")[0][0]
    assert "endTime" in annotation_data.get("annotation")[0][0]
    assert "ontologyName" in annotation_data.get("annotation")[0][0]
    assert "annotatedBy" in annotation_data.get("annotation")[0][0]
    assert "nothingToTranscribe" in annotation_data.get("annotation")[0][0]
    assert "metadata" in annotation_data.get("annotation")[0][0]
    # somehow, some report does not have reviewed status, need check
    assert annotation_data.get("annotation")[0][0].get("reviewStatus") == "reviewed"
    os.remove(csv_name)
    os.remove(full_file_name_zip)
