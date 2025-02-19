""" Create QA Performance Test Job """

from adap.e2e_automation.services_config.job_api_support import create_job_from_config_api
from adap.perf_platform.utils.db import DBUtils
from adap.api_automation.utils.data_util import get_user
from adap.perf_platform.test_data.jobs_data import jobs_data
from adap.perf_platform.utils.results_handler import add_task_info
from adap.perf_platform.utils.logging import get_logger
from adap.settings import Config

log = get_logger(__name__)
if Config.ENV == 'integration':
    # DO-9589
    user = get_user('perf_platform2')
elif Config.ENV == 'fed':
    user = get_user('cf_internal_role')
else:
    user = get_user('perf_platform')


job_data = jobs_data.get(Config.JOB_TYPE)
assert job_data, f'Config for JOB_TYPE {Config.JOB_TYPE}, ' \
                f'available types are: {jobs_data.keys()}'

data_generator = job_data['data_generator']
config = {
    "job": {
        "title": "QA Performance Test "
        f"{Config.SESSION_ID}.{Config.TASK_ID} - {Config.JOB_TYPE}",
        "instructions": "<h1>Overview</h1>",
        "cml": job_data['cml'],
        "units_per_assignment": Config.UNITS_PER_ASSIGNMENT,
        "gold_per_assignment": Config.GOLD_PER_ASSIGNMENT,
        "judgments_per_unit": Config.JUDGMENTS_PER_UNIT,
        "project_number": "PN000112"
    },
    "data_upload": [data_generator(
        Config.NUM_UNITS,
        filename='/tmp/units.csv')],
    "launch": Config.LAUNCH_JOB,
    "rows_to_launch": Config.LAUNCH_NUM_UNITS,
    "external_crowd": Config.EXTERNAL,
    "channels": Config.CHANNELS,
    "level": Config.CROWD_LEVEL,
    "ontology": job_data.get('ontology'),
    "user_email": user['email'],
    "user_password": user['password'],
    "jwt_token": user['jwt_token']
}
if Config.MAX_JUDGMENTS_PER_WORKER > 0:
    config['job']['max_judgments_per_worker'] = Config.MAX_JUDGMENTS_PER_WORKER
if Config.NUM_TEST_QUESTION > 0:
    config['test_questions'] = [data_generator(
        Config.NUM_TEST_QUESTION,
        gold=True,
        filename='/tmp/tq.csv')]
if Config.DYNAMIC_JUDGMENT_COLLECTION:
    config['dynamic_judgment_collection'] = {
        'max_judgments_per_unit': Config.MAX_JUDGMENTS_PER_UNIT,
        'min_unit_confidence': Config.MIN_UNIT_CONFIDENCE,
        'dynamic_judgment_fields': job_data['fields']
    }
if Config.AUTO_ORDER:
    config['auto_order'] = {
        'bypass_estimated_fund_limit': Config.BYPASS_ESTIMATED_FUND_LIMIT,
        'units_remain_finalized': Config.UNITS_REMAIN_FINALIZED,
        'schedule_fifo': Config.SCHEDULE_FIFO,
        'auto_order_timeout': Config.AUTO_ORDER_TIMEOUT
    }


def main():
    log.info(f"Creating the job, title {config['job']['title']}")
    job_id = create_job_from_config_api(config, Config.ENV, user['api_key'], env_fed=Config.ENV_FED)

    log.debug("Add job_id to `tasks` table in Results DB")
    info = {'job_id': job_id}
    add_task_info(info)

    if Config.ENABLE_JUDGMENT_LOADER:
        log.info("Enabling Judgment Loader")
        with DBUtils(**Config.BUILDER_DB_CONN) as db:
            db.execute(
                """
                UPDATE jobs SET options = (options::jsonb || '{"kafka_judgments_loading": "enabled"}'::jsonb)::text
                WHERE id = %(job_id)s;
                """,
                args={'job_id': job_id}
            )


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.error(e.__repr__())
        raise
