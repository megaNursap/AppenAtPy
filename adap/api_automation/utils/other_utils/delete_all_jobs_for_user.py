# todo find all jobs
from adap.api_automation.services_config.builder import Builder
import time
import gevent
import urllib3
urllib3.disable_warnings()
# "https://api.nxxgpxhq0rum22cd.staging.cf3.us/v1"
# api_key = ""
url = "https://api.integration.cf3.us/v1"
api_key = ""
exclude_job_ids = []  # these won't be deleted
# integration - [1679124, 1679123, 1679122,1674908, 1674861]

states_to_cancel = ('running', 'paused', 'finished')

# url = "https://api.figure-eight.com/v1"

# this will limit number of coroutines (greenlets)
concurrency = 4


#  user can find only 10 jobs
def find_jobs():
    jobs = Builder(api_key, custom_url=url).get_jobs_for_user().json_response
    ids = [job['id'] for job in jobs]
    return ids


def delete_job(job_id):
    # check status if it is running or paused  - cancel it first
    _job = Builder(api_key, custom_url=url)
    _job.job_id = job_id

    status = _job.get_json_job_status().json_response
    if status['state'] in states_to_cancel:
        _job.cancel_job()
        gevent.sleep(2)

    api = Builder(api_key, api_version='v2', custom_url=url)
    res = api.delete_job(job_id)
    if res.status_code == 200:
        print("Job %s was deleted" % job_id)
    else:
        print("Job - %s. Something went wrong. Error: %s" % (job_id, res.json_response))


def delete_jobs(jobs):
    print(f"Deleting {jobs}")
    gevent.joinall([gevent.spawn(delete_job, job_id) for job_id in jobs])


def main():
    while True:
        jobs = find_jobs()
        jobs = [j for j in jobs if j not in exclude_job_ids]
        if not jobs:
            break
        while jobs:
            c_jobs = []
            for i in range(concurrency):
                try:
                    c_jobs.append(jobs.pop())
                except IndexError:
                    break
            delete_jobs(c_jobs)


if __name__ == "__main__":
    main()
