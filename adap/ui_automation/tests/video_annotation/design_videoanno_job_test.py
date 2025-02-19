"""
https://appen.atlassian.net/browse/QED-1634
This test covers:
1. create video annotation job with object_tracking assistant
2. create video annotation job with linear_interpolation assistant
3. upload ontology for video annotation job, launch the job and check status
4. create job with invalid cml, validate error message on design page
5. also include create nested ontology for video annotation job.
Sandbox and QA has bug https://appen.atlassian.net/browse/AT-2868, once it is fixed, we'll change to non-peer review version
"""

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder as JobAPI
import time
from adap.data import annotation_tools_cml as data

pytestmark = [pytest.mark.regression_video_annotation,
              pytest.mark.adap_ui_uat,
              pytest.mark.adap_uat
              ]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')


@pytest.fixture(scope="module")
def login_at(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)


# https://appen.atlassian.net/browse/QED-2331
def test_create_job_with_linear_interpolation_and_nested_ontology(app, login_at):
    job = JobAPI(API_KEY)
    job.create_job_with_cml(data.video_annotation_linear_interpolation_cml)
    job_id = job.job_id
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    data_file = get_data_file("/video_annotation/video.csv")
    app.job.data.upload_file(data_file)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Video Shapes Ontology')
    ontology_file = get_data_file("/video_annotation/nested_ontology.json")
    app.ontology.upload_ontology(ontology_file)
    app.ontology.search_class_by_name("Nest1", found=True)
    app.ontology.search_class_by_name("Nest2", found=False)
    app.ontology.search_class_by_name("Nest3", found=False)
    app.ontology.search_class_by_name("Nest4", found=False)
    app.ontology.expand_nested_ontology_by_name("Nest1")
    app.ontology.search_class_by_name("Nest1", found=True)
    app.ontology.search_class_by_name("Nest2", found=True)
    app.ontology.search_class_by_name("Nest3", found=False)
    app.ontology.search_class_by_name("Nest4", found=False)
    app.ontology.expand_nested_ontology_by_name("Nest2")
    app.ontology.search_class_by_name("Nest1", found=True)
    app.ontology.search_class_by_name("Nest2", found=True)
    app.ontology.search_class_by_name("Nest3", found=True)
    app.ontology.search_class_by_name("Nest4", found=False)
    app.ontology.expand_nested_ontology_by_name("Nest3")
    app.ontology.search_class_by_name("Nest1", found=True)
    app.ontology.search_class_by_name("Nest2", found=True)
    app.ontology.search_class_by_name("Nest3", found=True)
    app.ontology.search_class_by_name("Nest4", found=True)
    time.sleep(3)


def test_create_with_object_tracking_and_launch(app, login_at):
    job = JobAPI(API_KEY)
    job.create_job_with_cml(data.video_annotation_object_tracking_cml)
    job_id = job.job_id
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    data_file = get_data_file("/video_annotation/video.csv")
    app.job.data.upload_file(data_file)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Video Shapes Ontology')

    ontology_file = get_data_file("/video_annotation/ontology.json")
    app.ontology.upload_ontology(ontology_file)
    # app.verification.text_present_on_page("2/1000 Classes Created")
    time.sleep(3)
    # need to select hosted channel if it is fed env
    if pytest.env == 'fed':
        app.job.open_action("Settings")
        app.navigation.click_link("Select Contributor Channels")
        app.job.select_hosted_channel_by_index(save=True)

    job.launch_job()

    job = JobAPI(API_KEY, job_id=job_id)

    job.wait_until_status('running', 60)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

#
# def test_create_job_with_invalid_cml(app, login_at):
#     job = JobAPI(API_KEY)
#     job.create_job_with_cml(data.video_annotation_invalid_cml)
#     job_id = job.job_id
#     app.mainMenu.jobs_page()
#     app.job.open_job_with_id(job_id)
#     app.job.open_tab("DATA")
#     data_file = get_data_file("/video_annotation/video.csv")
#     app.job.data.upload_file(data_file)
#
#     app.job.open_tab('DESIGN')
#     app.navigation.click_btn("Save")
#     alert_message = app.job.design.get_alert_message()
#     error1 = "Please change to 'linear_interpolation'"
#     error2 = "'object_tracking' assistant is only supported for"
#     assert error1 in alert_message[0].text
#     assert error2 in alert_message[0].text
