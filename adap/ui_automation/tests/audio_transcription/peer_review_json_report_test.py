"""
https://appen.atlassian.net/browse/QED-2233
"""
import time

import requests

from adap.api_automation.services_config.requestor_proxy import RP
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_peer_review_job
from adap.ui_automation.utils.selenium_utils import go_to_page
import json

pytestmark = [pytest.mark.regression_audio_transcription_subset, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_predefined_jobs')
PASSWORD = get_user_password('test_predefined_jobs')
API_KEY = get_user_api_key('test_predefined_jobs')

PREDEFINED_JOB_ID = pytest.data.predefined_data['audio_transcription'].get(pytest.env)
RULE_DESCRIPTION = 'Do not enter two punctuation mark'


@pytest.fixture(scope="module", autouse=True)
def peer_review_job(tmpdir_factory, app):
    tmpdir = tmpdir_factory.mktemp('data')
    job_id = create_peer_review_job(tmpdir, API_KEY, PREDEFINED_JOB_ID, data.audio_transcription_peer_review_report_cml, units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')
    ontology_file = get_data_file('/audio_transcription/reviewdata_with_instances_ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    # add regex rule
    url = "https://client.%s.cf3.us/jobs/%s/data_validation" % (pytest.env, job_id)
    go_to_page(app.driver, url)
    app.user.close_guide()
    app.navigation.click_btn('Add rules')
    app.audio_transcription.data_validation.add_regex_search_rule(regular_expression='[,.!?]{2,}',
                                                                  error_description=RULE_DESCRIPTION,
                                                                  enable_fix_suggestion=True, empty_string=False,
                                                                  replace_string='.')
    app.navigation.click_btn('Save')
    time.sleep(3)
    assert app.verification.text_present_on_page(RULE_DESCRIPTION)

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

    # job_id = 2117710
    return job_id


@pytest.mark.dependency()
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="only enabled in preprod")
def test_update_peer_review_transcription(app, peer_review_job):
    job_link = generate_job_link(peer_review_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.close_guide()
    time.sleep(5)

    for i in range(0, 2):
        app.audio_transcription.activate_iframe_by_index(i)
        app.audio_transcription.review_all_segments()
        bubbles = app.audio_transcription.get_bubbles_list()
        for bubble in bubbles:
            name = bubble['name']
            # When original text was marked as ‘Nothing to transcribe’, and then transcribed in review job
            if name == "Segment 3":
                app.audio_transcription.select_bubble_by_name(name, default_name=name)
                app.audio_transcription.click_nothing_to_transcribe_for_bubble(name)
                app.audio_transcription.add_text_to_bubble(name, "transcribe noise.,.")
                assert app.audio_transcription.review_btn_is_disable_for_bubble(name)
                app.navigation.click_btn('CORRECT')
                assert not app.audio_transcription.review_btn_is_disable_for_bubble(name)
            #  Delete original text and mark as 'Nothing to transcribe'
            elif name == "Segment 1":
                app.audio_transcription.delete_text_from_bubble(name)
                app.audio_transcription.click_nothing_to_transcribe_for_bubble(name)
            # update original transcription
            elif name == "Segment 2":
                app.audio_transcription.edit_text_from_bubble(name, "edit text")
        app.audio_transcription.deactivate_iframe()

    app.audio_transcription.submit_page()
    time.sleep(5)
    app.verification.text_present_on_page('There is no work currently available in this task.')


@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="only enabled in preprod")
@pytest.mark.dependency(depends=["test_update_peer_review_transcription"])
def test_json_output_reports(app_test, peer_review_job):
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(peer_review_job)

    app_test.job.open_tab("RESULTS")
    app_test.navigation.click_link("Advanced Report Settings")
    app_test.navigation.click_checkbox_by_text("Include Unfinished Rows")
    app_test.navigation.click_link("Save")
    app_test.job.results.download_report("Full", peer_review_job)
    file_name_zip = "/" + app_test.job.results.get_file_report_name(peer_review_job, "Full")
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
    rp = RP()
    cookie = rp.get_valid_sid(USER_EMAIL, PASSWORD)
    result = requests.get(json_value, cookies=cookie)
    annotation_data = json.loads(result.text)
    assert "ableToAnnotate" in annotation_data
    assert "nothingToTranscribe" in annotation_data
    annotation_data_ann = annotation_data.get('annotation')
    for i in range(0, len(annotation_data_ann.get("segments"))):
        assert "id" in annotation_data_ann.get("segments")[i]
        assert "layerId" in annotation_data_ann.get("segments")[i]
        assert "startTime" in annotation_data_ann.get("segments")[i]
        assert "endTime" in annotation_data_ann.get("segments")[i]
        assert "transcription" in annotation_data_ann.get("segments")[i]

    assert annotation_data_ann.get("segments")[3].get("transcription").get(
            "text") == "transcribe noise."
    os.remove(csv_name)
    os.remove(full_file_name_zip)
