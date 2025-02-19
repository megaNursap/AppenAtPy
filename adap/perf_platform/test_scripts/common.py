from adap.settings import Config
from adap.e2e_automation.services_config.job_api_support import (
    create_job_from_config_api, generate_job_link
)
from adap.perf_platform.utils.data_feed import SourceDataReader
from adap.api_automation.services_config.judgments import Judgments
from adap.api_automation.services_config.workflow import Workflow
from adap.api_automation.services_config.builder import Builder
from adap.perf_platform.test_data.jobs_data import jobs_data
from adap.api_automation.utils.data_util import get_user
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.db import DBUtils
import random
from adap.api_automation.utils.data_util import *

log = get_logger(__name__)
env = Config.ENV
if env == 'integration':
    user = get_user('perf_platform2')
elif env == "fed":
    user = pytest.data.users['cf_internal_role']
else:
    user = get_user('perf_platform')

api_key = user['api_key']
JOB_TYPE = 'what_is_greater'
JOB_DATA = jobs_data.get(JOB_TYPE)
wf = Workflow(api_key, env=env)
worker = get_user('adap_integration_users_for_performance')
worker_password = worker['password']


def create_job(launch=False, num_units=0):
    job_config = {
        "job": {
            "title": f"QA WF Test {Config.SESSION_ID}.{Config.TASK_ID}",
            "instructions": "<h1>Overview</h1>",
            "cml": JOB_DATA['cml'],
            "units_per_assignment": 5,
            "gold_per_assignment": 0,
            "judgments_per_unit": 1,
            "max_judgments_per_worker": 1000,
            "project_number": "PN000112"
        },
        "level": Config.CROWD_LEVEL,
        "ontology": JOB_DATA.get('ontology'),
        "user_email": user['email'],
        "user_password": user['password'],
        "jwt_token": user['jwt_token']
    }
    if launch:
        data_generator = JOB_DATA['data_generator']
        job_config.update(
            {
                "data_upload": [data_generator(num_units)],
                "launch": True,
                "rows_to_launch": num_units,
            }
        )
    log.info(f"Creating a job, title {job_config['job']['title']}")
    job_id = create_job_from_config_api(
        job_config, env, api_key
    )
    return job_id

def create_jobs(num_jobs:int, launch=False, num_units=0) -> [int]:
    """ Create multiple jobs """
    job_ids = []
    for i in range(num_jobs):
        job_id = create_job(launch=launch, num_units=num_units)
        job_ids.append(job_id)
    return job_ids


def new_workflow():
    log.info("Creating Workflow")
    payload = {'name': 'QA WF test', 'description': 'API create new wf'}
    wf.create_wf(payload=payload)
    return wf.wf_id


def submit_judgments(job_id, num_assignments=None):
    log.info("Submitting Judgments (Internal)")
    workers_list = SourceDataReader(Config.DATA_SOURCE_PATH).read()
    worker_email = random.choice(workers_list).get('worker_email')
    j = Judgments(
        worker_email=random.choice(workers_list).get('worker_email'),
        worker_password=worker_password,
        env=env
    )
    # get internal job link
    job_link = generate_job_link(job_id, api_key, env)
    assignment_page = j.sign_in_internal(
        job_id=job_id,
        internal_job_url=job_link
    )
    j.contribute(assignment_page, num_assignments)


def verify_jobs_running(job_id):
    log.debug('verify job is in "running" state')
    b = Builder(api_key, env=env)
    resp = b.get_json_job_status(job_id)
    assert resp.json_response['state'] == 'running'

def fetch_finalized_units_from_builder(job_id):
    log.debug(f'fetch_finalized_units_from_builder for job {job_id}')
    with DBUtils(**Config.BUILDER_DB_CONN) as db:
        sql = """
        SELECT * FROM units
        WHERE job_id = %(job_id)s
        AND state = 9
        """
        return db.fetch_all(sql, args={'job_id': job_id}, include_column_names=True)

def get_msg_builder_topic(job_id, topic):
    """
    Fetch messages consumed from one of the "builder.*" topics,
    for the specified job_id
    """
    log.debug(f'fetch all messages from {topic} topic for job {job_id}')
    sql = """
    SELECT * FROM kafka_out 
    WHERE session_id = %(session_id)s
    AND details ->> 'topics' ~ %(topic)s
    AND value ->> 'job_id' = %(job_id)s
    """
    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        return db.fetch_all(
            sql,
            args={
                'session_id': Config.SESSION_ID,
                'topic': topic,
                'job_id': str(job_id)
            },
            include_column_names=True
        )

def get_count_msg_afu_topic(job_id):
    # Aggregated Finalized Units from Builder
    topic = 'builder.aggregated.finalized.units.from.builder'
    return len(get_msg_builder_topic(job_id, topic))

def get_count_msg_bu_topic(job_id):
    # New Units to Builder
    topic = 'builder.units.from.external'
    return len(get_msg_builder_topic(job_id, topic))
 

def get_msg_wf_topic(wf_id, step_id, topic):
    """
    Fetch messages consumed from one of the "wfp.*" topics,
    assuming they follow the format of having workflow_id and step_id
    in the message body.
    """
    log.debug(f'fetch all messages from {topic} topic for wf_id {wf_id}, step {step_id}')
    sql = """
    SELECT * FROM kafka_out 
    WHERE session_id = %(session_id)s
    AND details ->> 'topics' ~ %(topic)s
    AND value ->> 'workflow_id' = %(workflow_id)s
    AND value ->> 'step_id' = %(step_id)s
    """
    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        return db.fetch_all(
            sql,
            args={
                'session_id': Config.SESSION_ID,
                'topic': topic,
                'workflow_id': str(wf_id),
                'step_id': str(step_id)
            },
            include_column_names=True
        )

def get_count_msg_to_wf_topic(wf_id, step_id):
    # External (WBA) -> Workflows
    topic = 'wfp.datalines.from.external.to.workflows'
    return len(get_msg_wf_topic(wf_id, step_id, topic))

def get_count_msg_wf_to_ba_topic(wf_id, step_id):
    # Workflows -> WF Builder Adapter
    topic = 'wfp.builder.adapter.datalines.to.builder'
    return len(get_msg_wf_topic(wf_id, step_id, topic))
