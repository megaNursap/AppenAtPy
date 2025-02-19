import logging
import time

import allure
import pytest

from adap.api_automation.utils.data_util import get_test_data

pytestmark = pytest.mark.regression_gap

log = logging.getLogger(__name__)

PM_USER = 'gap_pm1'
WORKER_USER = 'gap_worker2'
data_file_path = "/upload_files/lidar_data_records/lidar_data_honda_samples.csv"
WORKERS_FILE_PATH = "/upload_files/worker_management/workers_worker2.csv"


# @pytest.mark.skip
@pytest.mark.dependency()
def test_gap_create_project(app):
    with allure.step("Test create project"):
        project_name = app.g_project.gap_generate_project_name()
        presales = "yes"
        cost_center = 'Engineering USA'
        customer_code = "123"
        description = "123"

        app.g_user.gap_login_as(PM_USER)
        app.g_nav.open_page_projects()

        app.g_project.gap_project_create_new()
        time.sleep(2)
        app.g_verify.gap_verify_modal_window()

        app.g_project.gap_project_create_populate_form(name=project_name, presales=presales, cost_center=cost_center,
                                                       customer_code=customer_code, descr=description)
        time.sleep(1)
        # search for new project
        assert app.g_project.gap_project_search_by_params(name=project_name), f"Project {project_name} not found"
        project_display_id = app.g_project.get_project_displayid()
        log.info(f"Project display id {project_display_id}")
        # app.g_project.gap_project_modify(project_name=project_name, do_delete=True)
        # assert not app.g_project.gap_project_search_by_params(name=project_name, proceed=False), "Project exists!!"
        app.g_nav.gap_click_btn('View')
        app.g_verify.current_url_contains('data-center')
        app.g_project.gap_project_parse_id_from_current_url()


# @pytest.mark.skip
@pytest.mark.dependency("test_gap_create_project")
def test_gap_upload_data(app):
    with allure.step(f"Test upload data record to {app.g_project.current_project_name}"):
        # project_name = "AutoTest_33599"
        # project_display_id = "A77"
        # # projectid = "140037d3-318b-45b4-932b-68a354139ecf"
        # cuboid_template_name = "LiDAR Cuboid Annotation"
        app.g_user.gap_login_as(PM_USER)
        app.g_project.gap_project_open_by_name(app.g_project.current_project_name)
        # upload data

        record_id = app.g_project.gap_project_data_record_upload(file_path=data_file_path)
        app.g_data.gap_search_data_list(record_id=record_id)


# @pytest.mark.skip
@pytest.mark.dependency("test_gap_create_project")
def test_gap_create_template(app):
    with allure.step("Test create template"):
        template_name = app.gap_generate_test_uniq_mark()
        app.g_user.gap_login_as(PM_USER)
        app.g_project.gap_project_open_by_name(app.g_project.current_project_name)
        new_template_title = app.g_template.gap_template_create(title=template_name)
        log.info(f"Created template name {new_template_title}")
        app.g_verify.gap_verify_template_exist(new_template_title)


# @pytest.mark.skip
@pytest.mark.dependency("test_gap_create_template")
def test_gap_create_workflow_with_jobs(app):
    with allure.step("Test create workflow"):
        log.info("Predefined data")
        project_name = app.g_project.current_project_name
        project_id = app.g_project.current_projectid
        project_display_id = app.g_project.current_project_displayid

        cuboid_template_name = "LiDAR Cuboid Annotation"

        app.g_workflow.gap_workflow_set_current_project(project_name=project_name, projectid=project_id,
                                                        project_displayid=project_display_id)

        app.g_user.gap_login_as(PM_USER)
        app.g_project.gap_project_open_by_name(project_name)

        app.g_workflow.create_gap_workflow(template_name=cuboid_template_name)

        expected_workflow_name = app.g_workflow.current_workflow.get("workflow_name")
        log.info(f"Expected workflow name: {expected_workflow_name}")
        expected_workflow_displayid = app.g_workflow.current_workflow.get("workflow_display_id")
        log.info(f"Expected workflow displayid: {expected_workflow_displayid}")

        assert app.g_verify.text_present_on_page(expected_workflow_name), "Workflow name not displayed"
        assert app.g_verify.text_present_on_page(expected_workflow_displayid), "Workflow displayid not found"
        assert app.g_verify.text_present_on_page(cuboid_template_name), "Template name not displayed"

        # create jobs in workflow
        app.g_workflow.gap_workflow_open_existing(expected_workflow_name, project_display_id)
        labelind_job_name = app.g_job.gap_job_create(contact_email=app.g_user.current_user)
        log.info(f"Labeling Job name: {labelind_job_name}")
        # invite worker
        job_lst = app.g_workflow.gap_workflow_get_job_list(expected_workflow_name)
        app.g_job.gap_job_invite_workers_to_job_list(job_lst, WORKERS_FILE_PATH)

        app.g_workflow.gap_workflow_open_existing(expected_workflow_name, project_display_id)
        job_name_01 = app.g_job.gap_job_create(contact_email=app.g_user.current_user)
        log.info(f"QA Around Job name: {job_name_01}")
        # gap_workflow_search


# @pytest.mark.skip
@pytest.mark.dependency("test_gap_create_workflow")
def test_gap_invite_worker_to_job(app):
    with allure.step("Test invite workers to job"):
        project_id = app.g_project.current_projectid
        project_name = app.g_project.current_project_name
        workflow = app.g_project.current_project_workflows[0]
        workflow_name = workflow.get('workflow_name')

        worker_email = get_test_data(WORKER_USER, 'email')

        app.g_user.gap_login_as(PM_USER)
        app.g_nav.open_page_projects()
        app.g_project.gap_project_set_current_id(project_id)
        app.g_nav.open_project_details(project_id)

        job_lst = app.g_workflow.gap_workflow_get_job_list(workflow_name)
        app.g_job.gap_job_invite_workers_to_job_list(job_lst, WORKERS_FILE_PATH)

        job_lst = app.g_workflow.gap_workflow_get_job_list(workflow_name)
        for index in range(1, len(job_lst)):
            app.g_job.gap_job_invite_workers_from_internal_pool(job=job_lst[index], worker_email=worker_email)


# @pytest.mark.skip
@allure.link("Bug CTT-2593", "https://appen.atlassian.net/browse/CTT-2593")
@pytest.mark.dependency("test_gap_create_workflow")
def test_assign_data_to_workflow(app):
    with allure.step("Assign data record to workflow"):
        project_name = app.g_project.current_project_name
        project_id = app.g_project.current_projectid
        project_display_id = app.g_project.current_project_displayid
        workflow_data = app.g_project.current_project_workflows[0]

        assert len(app.g_project.data_records_batch_list) > 0, f"Data record not uploaded to project {project_name}"
        data_record_id = app.g_project.data_records_batch_list[0]

        app.g_user.gap_login_as(PM_USER)
        app.g_nav.open_page_projects()
        app.g_project.gap_project_set_current_id(project_id)
        app.g_nav.open_project_details(project_id)

        app.g_data.gap_set_current_project(name=project_name, displayid=project_display_id, projectid=project_id)
        app.g_data.gap_data_assign_to_workflow(dataid=data_record_id, workflow_data=workflow_data)
