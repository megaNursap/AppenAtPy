from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.client import Client
from adap.api_automation.services_config.requestor_proxy import RP
from adap.perf_platform.utils.logging import get_logger
from adap.settings import Config
from urllib.parse import quote
import time
import pytest


log = get_logger(__name__)


def generate_job_link(job_id, api_key, env):
    job = Builder(api_key, env=env)
    job.job_id = job_id

    res = job.get_json_job_status()
    res.assert_response_status(200)
    secret = quote(res.json_response['secret'], safe='')

    if env == 'fed':
        job_link = "https://app.%s.secure.cf3.us/worker-ui/channels/cf_internal/jobs/%s/work?secret=%s" % (pytest.env_fed, res.json_response['id'], secret)
    else:
        job_link = "https://account.%s.cf3.us/channels/cf_internal/jobs/%s/work?secret=%s" % (env, res.json_response['id'], secret)
    print(f"Internal Job Link: %s" % job_link)

    return job_link


def create_job_from_config_api(config, env, api_key, env_fed=None):
    log.info({
        'message': 'Creating job from config',
        'config': config
        })
    job_payload = {
        "key": api_key,
        "job": config['job']
    }
    user_email = config.get('user_email')
    user_password = config.get('user_password')
    jwt_token = config.get('jwt_token')

    new_job = Builder(api_key, payload=job_payload, api_version='v1', env=env, env_fed=env_fed)
    res = new_job.create_job()
    assert res.status_code == 200, f"{res.status_code} :: {res.text}"
    log.info({
        'message': 'New job created',
        'job_id': new_job.job_id
        })

    # UNITS
    data_files = config.get('data_upload')
    if data_files:
        log.info({
            'message': 'Starting data upload',
            'job_id': new_job.job_id
            })
        for filepath in data_files:
            file_ext = filepath.rpartition(".")[-1]
            if file_ext in ['json', 'csv']:
                data_res = new_job.upload_data(filepath, data_type=file_ext)
                assert data_res.status_code == 200, data_res.content
            else:
                raise Exception("Data format %s is not supported" % file_ext)

    # wait until required number of rows is loaded
    rows = config.get('rows_to_launch')
    if rows:
        log.info(f"Checking that required number of rows ({rows}) has been uploaded")
        interwal = 10
        c_rows = 0
        c_wait = interwal
        while c_rows < rows and c_wait < Config.MAX_WAIT_TIME:
            resp = new_job.count_rows(delay=interwal)
            if resp.status_code == 500:
                log.error({
                    'message': 'Got 500 response code',
                    'info': f'retry in {interwal} seconds'
                    })
                c_wait += interwal
                continue
            c_rows = int(resp.json_response['count'])
            if c_rows >= rows:
                break
            log.info({
                'message': 'Current number of units uploaded',
                'num_units': c_rows,
                'num_units_req': rows,
                'info': f'retry in {interwal} seconds'
                })
            c_wait += interwal
        else:
            raise Exception({
                'message': 'Required number of units has not been uploaded before timeout',
                'info': f"waited {c_wait} seconds"
            })

    # TEST QUESTIONS
    tq_files = config.get('test_questions')
    if tq_files:
        log.info(f"Uploading test test questions")
        for filepath in tq_files:
            file_ext = filepath.rpartition(".")[-1]
            assert file_ext in ['json', 'csv'], f"Data format {file_ext} is not supported"
            resp = new_job.upload_data(filepath, data_type=file_ext)
            assert resp.status_code == 200, 'Data upload failed'
            time.sleep(5)
            resp = new_job.convert_uploaded_tq(max_retries=5)
            assert resp.status_code == 200, 'Test questions conversion failed'

    # ONTOLOGY
    ontology = config.get('ontology')
    if ontology:
        log.info(f"Adding Ontology")
        assert jwt_token, "'jwt_token' is required to add ontology to a job"
        rp = RP(jwt_token, env=env)
        resp = rp.update_ontology(new_job.job_id, ontology)
        assert res.status_code == 200, f"Actual status code: {res.status_code}, content {res.text}"

    # DYNAMIC JUDGMENT COLLECTION
    dynamic_judgment_collection = config.get('dynamic_judgment_collection')
    if dynamic_judgment_collection:
        log.info(f"Setting Dynamic Judgment Collection")
        client = Client()
        client.sign_in(
            email=user_email,
            password=user_password
            )
        client.update_job_judgment_settings(
            data=dynamic_judgment_collection,
            job_id=new_job.job_id)

    # AUTO_ORDER
    auto_order = config.get('auto_order')
    if auto_order:
        log.info("Setting Auto Order")
        client = Client()
        client.sign_in(
            email=user_email,
            password=user_password
            )
        client.update_job_api_settings(
            data=auto_order,
            job_id=new_job.job_id)

    # LAUNCH JOB
    if config.get('launch'):
        log.info({
            'message': "Launching job",
            'job_id': new_job.job_id,
            'num_rows': rows
            })
        res = new_job.launch_job(
            rows=rows,
            external_crowd=config.get('external_crowd'))
        assert res.status_code == 200, f"Actual status code: {res.status_code}, content {res.text}"

    # CHANNELS
    channels = config.get('channels')
    if channels:
        if type(channels) != list:
            channels = [channels]
        for channel in channels:
            log.info(f"Adding channel '{channel}'")
            resp = new_job.add_channel_to_job(channel)
            assert resp.status_code == 200, f"Actual status code: {resp.status_code}, content {resp.text}"

    # LEVELS
    level = config.get('level')
    if level:
        log.info(f"Updating required contributor level to '{level}'")
        assert jwt_token, "'jwt_token' is required to update contributor level on a job"

        rp = RP(env=env)
        rp.get_valid_sid(user_email, user_password)

        resp = rp.update_job_contributor_level(new_job.job_id, level)
        assert resp.status_code == 200, f"Actual status code: {resp.status_code}, content {resp.text}"

    return new_job.job_id
