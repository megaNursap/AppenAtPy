import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.annotation import create_peer_review_job
from adap.data import annotation_tools_cml as data
from adap.api_automation.services_config.builder import Builder

pytestmark = [pytest.mark.regression_image_transcription]

USER_EMAIL = get_user_email('test_predefined_jobs')
PASSWORD = get_user_password('test_predefined_jobs')
API_KEY = get_user_api_key('test_predefined_jobs')
ONTOLOGY_MISMATCH_PREDEFINED_JOB_ID = pytest.data.predefined_data['ontology_mismatch'].get(pytest.env)


@pytest.fixture(scope="module")
def tx_job2(tmpdir_factory, app):
    tmpdir = tmpdir_factory.mktemp('data')
    job_id = create_peer_review_job(tmpdir, API_KEY, ONTOLOGY_MISMATCH_PREDEFINED_JOB_ID, data.image_transcription_peer_review_cml_ontology_mismatch)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Transcription Ontology')

    ontology_file = get_data_file("/image_transcription/table-ontology2.json")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created")
    return job_id

@pytest.mark.skipif(not pytest.running_in_preprod, reason="only run on Sandbox and Integration")
@allure.issue("https://appen.atlassian.net/browse/AT-5444", "BUG AT-5444")
@pytest.mark.dependency()
def test_ontology_mismatch_peer_review(app, tx_job2):
    app.job.preview_job()
    time.sleep(3)
    app.image_transcription.activate_iframe_by_index(0)
    sidebar_table1_value = app.image_transcription.get_instance_limits_sidebar("Table_1")
    assert sidebar_table1_value == "1 /1"
    sidebar_table2_value = app.image_transcription.get_instance_limits_sidebar("Cell_1")
    assert sidebar_table2_value == "1"