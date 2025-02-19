
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.db import DBUtils
from adap.perf_platform.utils import helpers
from adap.settings import Config
import json

log = get_logger(__name__)

if Config.ENV == 'integration':
    # DO-9589
    user = get_user('perf_platform2')
else:
    user = get_user('perf_platform')


def update_dynamic_judgment_fields(job_id: int, fields: list):
    with DBUtils(**Config.BUILDER_DB_CONN) as db:
        job = db.fetch_one(
            'select * from jobs where id = %(job_id)s',
            args={'job_id': job_id},
            include_column_names=1)
        job_options = json.loads(job['options'])
        job_options['dynamic_judgment_fields'] = fields
        db.execute(
            'update jobs set options = %(options)s where id = %(job_id)s',
            args={
                'job_id': job_id,
                'options': json.dumps(job_options)}
            )


def main():
    job_id = helpers.get_job_id_from_tasks_info()
    builder = Builder(
        api_key=user['api_key'],
        env=Config.ENV,
        job_id=job_id)
    payload = json.loads(Config.JOB_SETTINGS_UPDATE)
    if payload.get('_dynamic_judgment_fields'):
        dynamic_judgment_fields = payload.pop('_dynamic_judgment_fields')
        update_dynamic_judgment_fields(job_id, dynamic_judgment_fields)
    resp = builder.update_job_settings(payload)
    assert resp.status_code == 200, f"{resp.status_code} :: {resp.text}"


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.error(e.__repr__())
        raise
