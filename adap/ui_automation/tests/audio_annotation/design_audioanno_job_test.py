"""
https://appen.atlassian.net/browse/QED-1647
Design audio annotation job using CML
"""

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
import time
from adap.data import annotation_tools_cml as data

pytestmark = [pytest.mark.regression_audio_annotation, pytest.mark.fed_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')


@pytest.mark.dependency()
def test_create_job_from_cml(app):
    """
    Verify requestor can create job using cml and upload ontology successfully
    """
    job = Builder(API_KEY)
    job.create_job_with_cml(data.audio_annotation_cml)
    job_id = job.job_id
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    data_file = get_data_file("/audio_annotation/audio_data.csv")
    app.job.data.upload_file(data_file)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Annotation Ontology')

    ontology_file = get_data_file("/audio_annotation/ontology.csv")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created", "//span[text()='2']")


# TODO: Update test to verify data is shown in unit page. Test questions are not supported in Audio Annotation job
@pytest.mark.dependency(depends=["test_create_job_from_cml"])
def test_preview_data_unit(app):
    app.job.open_tab('DATA')
    units = app.job.data.find_all_units_with_status('new')
    first_unit = units['unit id'][0]

    app.job.data.open_unit_by_id(first_unit)
    app.verification.current_url_contains("/units/%s" % first_unit)
    time.sleep(2)
    app.navigation.click_btn("Make Test Question")
    app.verification.text_present_on_page("Test Question Stats")
    app.verification.text_present_on_page("Total Judgments")
    app.verification.text_present_on_page("Missed")
    app.verification.text_present_on_page("Contentions")
    app.job.open_tab('DATA')
    golden = app.job.data.find_all_units_with_status('golden')
    assert len(golden) == 1
