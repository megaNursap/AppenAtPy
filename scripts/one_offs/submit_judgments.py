"""
Submit judgments on a given job using internal channel.
Using gevent to run multiple workers concurrently.
Runs until there is no more work left on the job or canceled by user (ctr-C).

Note: QA_AUTOMATION_KEY is required to decrypt data using get_user,
the key can be found in LastPass.
"""

from adap.settings import Config
Config.JOB_TYPE = 'what_is_greater'

from adap.api_automation.services_config.judgments import Judgments
from adap.api_automation.utils.data_util import get_user
from adap.perf_platform.test_data import integration_contributor_emails
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.perf_platform.utils.logging import get_logger
import random
import gevent
import sys

log = get_logger(__name__)

env = 'integration'
concurrency = 3

# pool of worker emails
worker_emails = [i['worker_email'] for i in integration_contributor_emails.get()]
# password is the same for all accounts
worker_password = get_user('perf_platform', env=env)['worker_password']

job_id = 1586758

api_key = get_user('perf_platform', env=env)['api_key']

def task(worker_email):
    j = Judgments(
        worker_email=worker_email,
        worker_password=worker_password,
        env=env,
        internal=True
    )
    resp = j.get_assignments(
        job_id=job_id,
        internal_job_url=generate_job_link(job_id, api_key, env)
    )
    j.contribute(resp)

def main_loop():
    ok = True
    while ok:
        # select batch of emails from the pool
        emails = random.choices(worker_emails, k=concurrency)
        # schedule gevent tasks
        gevent_tasks = [gevent.spawn(task, email) for email in emails]
        # run gevent_tasks through completion
        gevent.joinall(gevent_tasks)
        # validate status of each task
        for _task in gevent_tasks:
            if not _task.successful():
                out_of_work_msg = 'There is no work currently available in this task'
                if out_of_work_msg in _task.exc_info.__str__():
                    log.info("Quit due to: " + out_of_work_msg)
                    ok = False
                else:
                    log.error("Quit due to an unhandled exception")
                    sys.exit(1)


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print('Interrupted')
        
