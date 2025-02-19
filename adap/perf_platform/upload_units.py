from adap.perf_platform.utils.results_handler import get_task_info
from adap.perf_platform.test_data.jobs_data import jobs_data
from adap.perf_platform.utils.logging import get_logger
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user
from adap.settings import Config
import time

log = get_logger(__name__)
user = get_user('perf_platform')

job_data = jobs_data.get(Config.JOB_TYPE)
assert job_data, f'Config for JOB_TYPE {Config.JOB_TYPE}, ' \
                f'available types are: {jobs_data.keys()}'

data_generator = job_data['data_generator']


def get_job_id():
    try:
        info = get_task_info()
        log.debug(f"Current task info: {info}")
        if step := Config.WORKFLOW_STEP:
            job_id = info[0]['workflow_job_ids'][step-1]
        else:
            job_id = info[0]['job_id']
        return job_id
    except Exception as e:
        log.error(e.__repr__())
        raise


def main():
    num_units = Config.NUM_UNITS
    num_unit_uploads = Config.NUM_UNIT_UPLOADS
    job_id = get_job_id()
    builder = Builder(user['api_key'], env=Config.ENV, job_id=job_id)
    for i in range(num_unit_uploads):
        log.info(f"Adding {num_units} units to the job {job_id}")
        t0 = time.time()
        units_fp = data_generator(num_units, filename='/tmp/units.csv')
        res = builder.upload_data(units_fp, data_type='csv')
        assert res.status_code == 200, res.content
        t1 = time.time()
        t_delta = Config.WAIT - (t1 - t0)
        if t_delta > 0.1:
            time.sleep(t_delta)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.error(e.__repr__())
        raise
