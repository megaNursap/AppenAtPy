import time

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.workflow import Workflow
from adap.perf_platform.utils.logging import get_logger
from adap.settings import Config
from adap.api_automation.services_config.requestor_proxy import RP

log = get_logger(__name__)

def api_create_wf_from_config(wf_config: dict, username=None, password=None):
    log.info({
        'message': 'Create Workflow',
        'wf_config': wf_config
        })
    env = wf_config['env']
    api_key = wf_config['user']['api_key']

    status=''

    # CREATE WORKFLOW
    wf = Workflow(api_key, env=env)
    res = wf.create_wf(payload=wf_config['workflow']['payload'])
    assert res.status_code == 201, f"Workflow not created: {res.content}"

    # CREATE STEPS
    job_ids = wf_config.get('job_ids')
    if job_ids :
        log.info({
            'message': 'Create Steps',
            'job_ids': job_ids
            })
        _steps = wf.create_job_step(job_ids)
    else:
        log.info({'message': 'Create New Jobs'})
        job_ids = []
        for job_index in range(wf_config['jobs']['count']):
            # todo check that len(payloads) ==  jobs num
            job_payload = wf_config['jobs']['payloads'][job_index]

            new_job = Builder(api_key, payload=job_payload, api_version='v2', env=env)
            res = new_job.create_job()
            assert res.status_code == 200

            ontology_details = wf_config.get('ontology')
            if ontology_details:
                rp = RP()
                rp.get_valid_sid(username, password)
                resp = rp.update_ontology(new_job.job_id, ontology_details)
                assert resp.status_code == 200, f"Actual status code: {resp.status_code}, content {resp.text}"
            job_ids.append(new_job.job_id)

        log.info({
            'message': 'Create Steps',
            'job_ids': job_ids
            })
        _steps = wf.create_job_step(job_ids)

    log.info({'message': 'Create Routes'})
    _routes = []
    for route_config in wf_config['routes'].values():
        step_id = _steps[route_config['connect'][0]-1]['step_id']
        destination_step_id = _steps[route_config['connect'][1]-1]['step_id']
        route_id = wf.create_route(step_id, destination_step_id, wf.wf_id).json_response['id']

        # _routes.append({"step_id": step_id, "route_id": route_id})
        wf.create_filter_rule(step_id, route_id, route_config['filter'], wf.wf_id)

    # UPLOAD UNITS
    for filename in wf_config['data_upload']:
        log.info({'message': 'Upload Units'})
        res = wf.upload_data(filename)
        #  wait untill data uploaded is completed
        data_upload_id = res.json_response['id']

        c_wait = interwal = 10
        c_rows = 0
        while c_wait < Config.MAX_WAIT_TIME:
            res = wf.get_data_upload_info(data_upload_id, filename, wf.wf_id)
            state = res.json_response['state']
            if state == 'completed':
                break
            elif state == 'failed':
                raise Exception(f'Data upload failed: {res.content}')
            else:
                c_wait += interwal
                time.sleep(interwal)
        else:
            err = f"Data upload {data_upload_id} takes too long, " \
                  f"max wait time exceeded: {c_wait} seconds"
            raise Exception(err)

    # LAUNCH WORKFLOW
    if wf_config['launch']:
        log.info({'message': 'Launch Workflow'})
        row_order = wf_config['row_order']
        res = wf.launch(row_order)
        res.assert_response_status(202)

        c_wait = interwal = 10
        c_rows = 0
        while c_wait < Config.MAX_WAIT_TIME:
            res = wf.get_info(wf.wf_id)
            status = res.json_response['status']
            if status == 'running':
                break
            elif status == 'failed':
                raise Exception(f'Workflow launch failed: {res.content}')
            else:
                c_wait += interwal
                time.sleep(interwal)
        else:
            err = f"Workflow {wf.wf_id} take too long to launch, " \
                  f"max wait time exceeded: {c_wait} seconds"
            raise Exception(err)
    return {
        "id": wf.wf_id,
        "jobs": job_ids,
        "steps": _steps,
        "status": status
    }
