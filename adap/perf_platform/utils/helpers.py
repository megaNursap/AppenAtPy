from adap.perf_platform.utils.results_handler import get_task_info
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.db import DBUtils
from adap.settings import Config
import time

log = get_logger(__name__)


def get_job_id_from_tasks_info(interval=5):
    try:
        job_id = None
        _wait = 0
        while not job_id and _wait < Config.MAX_WAIT_TIME:

            if Config.TASK_ID_DATA:
                task_id = Config.TASK_ID_DATA
            else:
                task_id = Config.TASK_ID

            info = get_task_info(task_id=task_id, accept_null=True)

            if info:
                if step := Config.WORKFLOW_STEP:
                    workflow_job_ids = info[0].get('workflow_job_ids')
                    job_id = workflow_job_ids[step-1]
                elif Config.JOB_TYPE.startswith('TQG'):
                    job_id = info[0].get('tqg_job_id')
                else:
                    job_id = info[0].get('job_id')
                log.debug({
                    'get_job_id_from_tasks_info_new: job_id': job_id
                    })
                return job_id
            else:
                log.debug(f'task info not found, retry in {interval} seconds')
                time.sleep(interval)
                _wait += interval

    except Exception as e:
        log.error(e.__repr__())
        raise

def get_job_unit_ids(job_id, state=None) -> [int]:
    log.debug(f'Fetch all unit ids for job {job_id}')
    with DBUtils(**Config.BUILDER_DB_CONN) as db:
        sql = """
        SELECT id FROM units
        WHERE job_id = %(job_id)s
        """
        if state is None:
            rows = db.fetch_all(sql, args={'job_id': job_id})
        else:
            sql += " AND state = %(state)s "
            rows = db.fetch_all(
                sql,
                args={
                    'job_id': job_id,
                    'state': state
                }
            )
    return [i[0] for i in rows]