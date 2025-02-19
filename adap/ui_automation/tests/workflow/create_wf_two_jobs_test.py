"""
    Refer to prod bug https://appen.atlassian.net/browse/ADAP-994
    Create a new WF using 2 cml:shapes tool jobs (annotation & QA review)
    Verify that data & jugdments from annotation job have routed to QA Review job
"""
import time

from adap.perf_platform.utils.logging import get_logger
from adap.data import annotation_tools_cml as data
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.workflow import Workflow
from adap.e2e_automation.services_config.workflow_api_support import api_create_wf_from_config
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.api_automation.services_config.builder import Builder as JobAPI
from datetime import datetime

LOG = get_logger(__name__)

pytestmark = [pytest.mark.wf_ui, pytest.mark.regression_wf]

USER_ACCOUNT = 'test_ui_account'
USER_EMAIL = get_user_email(USER_ACCOUNT)
PASSWORD = get_user_password(USER_ACCOUNT)
API_KEY = get_user_api_key(USER_ACCOUNT)
CURRENT_DATE = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
DATA_FILE = get_data_file("/image_annotation/catdog.csv")
JSON_ONTOLOGY_FILE = [{"description": "", "class_name": "cat", "display_color": "#FF1744"},
                      {"description": "", "class_name": "dog", "display_color": "#651FFF"}]
JWT_TOKEN = get_test_data('test_ui_account', 'jwt_token')
JOB_TITLE = f"Cat_Dog %s {CURRENT_DATE}"
CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')
TOKEN = get_test_data('test_ui_account', 'x_storage_refs_token')
JOB_INSTRUCTION = """
        <h1>Overview</h1>\n<p>In this task you will box tables and cells.</p>
        \n<hr />\n<h1>Steps</h1>\n<ol><li>Identify if there is a table on the receipt typically this will be items 
        ordered and prices.</li><li>Box the individual cells first.</li><li>Box the area of the table</li></ol>"""
PROJECT_NUMBER = "PN000115"

payload_job01 = {
    'job': {
        "title": JOB_TITLE % "1",
        "instructions": JOB_INSTRUCTION,
        "cml": data.image_annotation_cml_focus_to_review_data1,
        "judgments_per_unit": 1,
        "max_judgments_per_worker": 95,
        "project_number": PROJECT_NUMBER,
        "options": {
            "include_single_boxes": True,
        }
    }
}

payload_job02 = {
    'job': {
        "title": JOB_TITLE % "2",
        "instructions": JOB_INSTRUCTION,
        "cml": data.image_annotation_cml_focus_to_review_data2,
        "judgments_per_unit": 1,
        "max_judgments_per_worker": 95,
        "project_number": PROJECT_NUMBER,
        "options": {
            "include_single_boxes": True,
        }
    }
}

wf_config_2 = {
    "env": pytest.env,
    "user": {
        "api_key": API_KEY
    },
    "jobs": {
        "count": 2,
        "payloads": [payload_job01, payload_job02]
    },
    "workflow": {
        "payload": {
            'name': f'CML_Shapes_focus_review_data {CURRENT_DATE}', 'description': 'API create new wf'
        }
    },
    "routes": {
        "1": {
            "connect": (1, 2), "filter":
                {
                    "filter_rule": {"rule_connector": "all"}
                }
        }
    },
    "data_upload": [DATA_FILE],
    "launch": True,
    "row_order": 2,
    "ontology": JSON_ONTOLOGY_FILE,
    "jwt_token": JWT_TOKEN
}


@pytest.fixture(scope="module")
def set_up(app):
    """
    Refer to prod bug https://appen.atlassian.net/browse/ADAP-994
    Create a new wf and 2 jobs using predefined wf payload
    """
    wf_info = api_create_wf_from_config(wf_config_2, username=USER_EMAIL, password=PASSWORD)
    wf = Workflow(API_KEY)
    wf.wf_id = wf_info['id']
    jobs = wf_info['jobs']
    return jobs


@pytest.mark.prod_bug
@pytest.mark.dependency()
def test_launch_image_annotation_job_and_submit_judgments(app, set_up):
    """
    Refer to prod bug https://appen.atlassian.net/browse/ADAP-994
    Launch image annotation job, submit judgments. Launch QA review job
    """
    job1_id = set_up[0]
    job1_api = JobAPI(API_KEY, job_id=set_up[0])
    job1_api.wait_until_status('running', 200)
    res = job1_api.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    job_link = generate_job_link(job1_id, API_KEY, pytest.env)
    LOG.info(f"Generated job link {job_link}")
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link)
    LOG.info("Submit judgements")
    for i in range(2):
        app.image_annotation.activate_iframe_by_index(i)
        app.image_annotation.annotate_image(mode='ontology', value={"cat": 3})
        app.image_annotation.annotate_image(mode='ontology', value={"dog": 3})

        app.image_annotation.deactivate_iframe()

    app.image_annotation.submit_page()
    time.sleep(3)
    app.verification.text_present_on_page('There is no work currently available in this task.')
    app.user.logout()

    job2_id = set_up[1]
    LOG.info(f"Launch QA Review Job with id {job2_id}")
    job2_api = JobAPI(API_KEY, job_id=job2_id)
    job2_api.wait_until_status('running', 200)
    res = job2_api.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")


@pytest.mark.dependency("test_launch_image_annotation_job_and_submit_judgments")
@pytest.mark.prod_bug
def test_annotation_routes_to_qa_review_job(app, set_up):
    """
    Refer to prod bug https://appen.atlassian.net/browse/ADAP-994
    Verify data and judgments routed to QA Review job
    """
    job2_id = set_up[1]
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job2_id)
    # job opens on Data tab

    time.sleep(30)
    app.job.open_tab("RESULTS")
    report_type = 'Source'
    app.job.results.download_report(report_type, job2_id)
    file_name_zip = "/" + app.job.results.get_file_report_name(job2_id, report_type)
    full_file_name_zip = app.temp_path_file + file_name_zip
    unzip_file(full_file_name_zip)
    csv_name = str(full_file_name_zip)[:-4]

    _df = pd.read_csv(csv_name)
    assert 'annotation' in _df.columns

    expected_annotation01 = """
        {"average_trust"=>1.0, "class"=>{"cat"=>1.0}, "coordinates"=>{"h"=>573, "w"=>560, "x"=>1519, "y"=>143}, "type"=>"box"}
        {"average_trust"=>1.0, "class"=>{"cat"=>1.0}, "coordinates"=>{"h"=>934, "w"=>878, "x"=>1407, "y"=>654}, "type"=>"box"}
        {"average_trust"=>1.0, "class"=>{"cat"=>1.0}, "coordinates"=>{"h"=>891, "w"=>635, "x"=>1245, "y"=>1077}, "type"=>"box"}
        {"average_trust"=>1.0, "class"=>{"dog"=>1.0}, "coordinates"=>{"h"=>467, "w"=>847, "x"=>554, "y"=>971}, "type"=>"box"}
        """

    expected_annotation02 = """
        {"average_trust"=>1.0, "class"=>{"cat"=>1.0}, "coordinates"=>{"h"=>648, "w"=>497, "x"=>545, "y"=>1329}, "type"=>"box"}
        {"average_trust"=>1.0, "class"=>{"cat"=>1.0}, "coordinates"=>{"h"=>357, "w"=>555, "x"=>765, "y"=>803}, "type"=>"box"}
        {"average_trust"=>1.0, "class"=>{"dog"=>1.0}, "coordinates"=>{"h"=>539, "w"=>644, "x"=>1770, "y"=>607}, "type"=>"box"}
        {"average_trust"=>1.0, "class"=>{"dog"=>1.0}, "coordinates"=>{"h"=>478, "w"=>286, "x"=>329, "y"=>475}, "type"=>"box"}
        """
    exp_annotations = [expected_annotation01, expected_annotation02]

    total_rows = len(_df['_unit_id'])
    assert total_rows == 2, "Total rows cannot be less or bigger 2"

    unit_ids = []
    for item in _df['_unit_id'].items():
        unit_ids.append(item[1])

    LOG.info(f"UNIT IDS: {unit_ids}")

    annotations = []
    for elem in _df['annotation'].items():
        LOG.info(f"Annotation {elem}")
        annotations.append(elem[1])

    LOG.info(f"Annotation {annotations}")

    LOG.info("Delete downloaded csv file")
    os.remove(csv_name)
    os.remove(full_file_name_zip)
