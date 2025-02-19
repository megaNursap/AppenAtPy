"""
https://appen.atlassian.net/browse/QED-1583
This test covers:
1. create image annotation job from template
2. create image annotation job from cml
3. upload ontology for image annotation job
"""

from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [
    pytest.mark.regression_image_annotation,
    pytest.mark.fed_ui,
    pytest.mark.adap_ui_uat,
    pytest.mark.adap_uat
]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/image_annotation/catdog.csv")


def test_create_job_from_cml_image_annotation(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE, data.image_annotation_cml, job_title="Testing image annotation tool",
                                         units_per_page=2)
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Annotation Ontology')
    ontology_file = get_data_file("/image_annotation/ontology.json")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created")


def test_create_job_from_template_image_anno(app_test):
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.create_new_job_from_template(template_type="Image Annotation",
                                              job_type="Image Categorization")
    app_test.navigation.click_btn("Next: Design your job")
    app_test.job.open_tab("DATA")
    data_file = get_data_file("/image_annotation/catdog.csv")
    app_test.job.data.upload_file(data_file, wait_time=10)


