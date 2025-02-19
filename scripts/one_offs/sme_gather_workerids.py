from appen_connect.api_automation.services_config.ac_sme import SME
from adap.settings import Config
from adap.perf_platform.utils.db import DBUtils
import gevent

env = 'stage'
concurrency = 10

rows_w_projects = []

def _findproj(worker_id):
    sme = SME(env=env)
    data = {
        "workerId": worker_id,
        "rankFactor":"bestMatch",
        "maxReturnCount":20,
        "hireGapThreshold":0.0001,
        "useCase":"allWorkers"
    }
    resp = sme.find_projects(data)
    if projects := resp.json_response.get('projects'):
        rows_w_projects.append((resp.json_response['workerId'], len(projects)))


def findproj(worker_ids):
    print(f"Checking {worker_ids}")
    gevent.joinall([gevent.spawn(_findproj, worker_id) for worker_id in worker_ids])


def main():
    worker_ids_csv = f"{Config.APP_DIR}/../appen_connect/data/sme_data/workerids.csv"
    with open(worker_ids_csv, 'r') as f:
        worker_ids = f.read()
    worker_ids = worker_ids.split('\n')[1:1000]
    while worker_ids:
        c_jobs = []
        for i in range(concurrency):
            try:
                c_jobs.append(worker_ids.pop())
            except IndexError:
                break
        findproj(c_jobs)
    


def save_to_resultsdb():
    print('saving_results')
    db = DBUtils(**Config.RESULTS_DB_CONN)
    db.connect()
    sql_insert_worker_data = """
    INSERT INTO sme_workers (worker_id, projects_num)
    VALUES (%s, %s)
    """
    db.execute_batch(
        sql_insert_worker_data,
        (m for m in rows_w_projects),
        page_size=1000
        )

if __name__ == "__main__":
    main()
    save_to_resultsdb()