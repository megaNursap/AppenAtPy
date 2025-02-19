
from adap.api_automation.services_config.requestor_proxy import RP
from adap.api_automation.services_config.client import Client
from adap.api_automation.utils.data_util import get_user
from adap.api_automation.utils.helpers import (
    find_authenticity_token,
    retry
    )
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.db import DBUtils
from adap.perf_platform.utils import results_handler
from adap.perf_platform.utils.helpers import get_job_id_from_tasks_info

from adap.settings import Config

log = get_logger(__name__)

env = Config.ENV


def order_tqg(job_id, user, question_count, custom_channels):
    log.info(f"Order Test Question Generation for job_id {job_id}")

    # user credentials
    email = user.get('email')
    password = user.get('password')
    jwt_token = user.get('jwt_token')

    log.debug(f'sign in as a requester {email}')
    client = Client(env=env, session=True)
    sign_in_resp = client.sign_in(email=email, password=password)
    authenticity_token = find_authenticity_token(sign_in_resp.content)

    rp = RP(
        jwt_token=jwt_token,
        env=env,
        service=client.service
        )
    log.debug(f'ordering tqg for {question_count} units')
    resp = rp.order_test_questions(
        job_id=job_id,
        authenticity_token=authenticity_token,
        question_count=question_count,
        custom_channels=custom_channels
        )
    assert resp.status_code == 201, resp.text


def get_job_title(job_id):
    log.debug(f'get job title for the job_id {job_id}')
    sql = """
    SELECT title
    FROM jobs
    WHERE id = %(job_id)s
    """
    with DBUtils(**Config.BUILDER_DB_CONN) as db:
        row = db.fetch_one(
            sql,
            args={
                'job_id': str(job_id)
                }
            )
        title = row[0]
    return title


def get_tqg_job_id(tqg_job_title):
    log.debug(f'get job_id for the job title {tqg_job_title}')
    sql = """
    WITH latest_100 as (
        SELECT id
        FROM jobs
        ORDER BY id DESC
        LIMIT 1000
    )
    SELECT id
    FROM jobs
    WHERE title = %(job_title)s
    AND id > (SELECT min(id) FROM latest_100)
    """
    with DBUtils(**Config.BUILDER_DB_CONN) as db:
        rows = db.fetch_all(
            sql,
            args={
                'job_title': tqg_job_title
                }
            )
        assert rows, 'job not found'
        job_id = rows[0][0]
    return job_id


def main():
    job_id = get_job_id_from_tasks_info()
    user = get_user('perf_platform2', env=env)
    question_count = Config.NUM_TEST_QUESTION
    # custom_channels = [1182]  # for sandbox
    custom_channels = [1151]  # for integration
    order_tqg(
        job_id=job_id,
        user=user,
        question_count=question_count,
        custom_channels=custom_channels)
    original_job_title = get_job_title(job_id)
    tqg_job_title = f"Make Test Questions - {original_job_title}"
    log.info(f"tqg_job_title: {tqg_job_title}")
    tqg_job_id = retry(
        get_tqg_job_id,
        max_wait=Config.MAX_WAIT_TIME,
        tqg_job_title=tqg_job_title)
    task_info = results_handler.get_task_info()[0]
    task_info.update({
        'tqg_job_id': tqg_job_id
        })
    results_handler.update_task_info(task_info)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.error(e.__repr__())
        raise
