"""
This test covers:
1. create audio annotation job and launch it.
2. test nothing to annotate
3. test submit annotations
"""
import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.selenium_utils import *
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.data import annotation_tools_cml as data

pytestmark = [
    pytest.mark.regression_audio_annotation,
    pytest.mark.adap_ui_uat,
    pytest.mark.adap_uat
]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_annotation/audio_data.csv")


@pytest.fixture(scope="module")
def tx_job(app):
    """
    Create Audio Annotation job with 5 units, add 2 ontology classes and launch job
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE, data.audio_annotation_cml,
                                        job_title="Testing manage audio annotation", units_per_page=5)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Annotation Ontology')

    ontology_file = get_data_file("/audio_annotation/ontology.csv")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created", "//span[text()='2']")

    app.job.open_action("Settings")

    if pytest.env == 'fed':
        app.navigation.click_link("Select Contributor Channels")
        app.job.select_hosted_channel_by_index(save=True)

    # else:
    #     app.driver.find_element('xpath',"//label[@for='externalChannelsEnabled' and text()='External']").click()
    #     app.navigation.click_link('Save')

    job = JobAPI(API_KEY, job_id=job_id)
    job.launch_job()

    job.wait_until_status('running', 60)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    return job_id


@pytest.mark.dependency()
def test_nothing_to_annotate(app, tx_job):
    """
    Verify requestor can mark the data unit as "Nothing to Annotate" in preview page
    """
    job_link = generate_job_link(tx_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.close_guide()
    time.sleep(5)

    app.audio_annotation.activate_iframe_by_index(0)
    time.sleep(2)
    app.audio_annotation.begin_annotate(0)
    app.verification.text_present_on_page('No annotations have been made. Is there nothing to annotate?')
    app.navigation.click_link('Nothing to Annotate')
    app.verification.text_present_on_page('This question has been marked as Nothing to Annotate.')
    app.audio_annotation.save_for_nothing_annotate()
    app.audio_annotation.deactivate_iframe()


@pytest.mark.dependency(depends=["test_nothing_to_annotate"])
def test_submit_annotations(app, tx_job):
    """
    Verify validation fails until all units are annotated or marked as 'Nothing to Annotate' (in preview mode)
    """
    app.audio_annotation.submit_page()
    # app.verification.text_present_on_page('This question must be marked as Nothing to Annotate if there are no segments to create.')
    app.verification.text_present_on_page('Check below for errors!')
    time.sleep(2)
    for i in range(1, 5):
        app.audio_annotation.activate_iframe_by_index(i)
        app.audio_annotation.begin_annotate(0)
        app.navigation.click_link('Nothing to Annotate')
        app.audio_annotation.save_for_nothing_annotate()
        app.audio_annotation.deactivate_iframe()

    app.audio_annotation.submit_page()
    time.sleep(2)
    app.verification.text_present_on_page('There is no work currently available in this task.')

