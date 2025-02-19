"""
======================== Functional Test ========================
Integration testing of Workflows Builder Adapter
1. Create a workflow with 2 steps, upload 50 units and launch
3. Start submitting judgments on the job1 (units get finalized and routed to job2)
4. After all assignments are complete from Step 3, start submitting judgments on the job2

Concurrently create another Job (not part of any workflow) and start submitting
judgments on that job.

Verify that all units from job1(WF) are finalized and routed to job2(WF)
Verify that all units from job3(non-WF) are finalized and ignored by the Builder Adapter
"""

from adap.perf_platform.test_scenarios import executor as se
import json


ENV = 'integration'
scenario = f"[{ENV}] Workflows Builder Adapter functional test"
data_source_env_paths = {
    'integration': 'appen_connect/data/adap_integration_users.csv'
}
with se.session(scenario, teardown=False) as session_id:

    # Start Kafka consumers for each topic
    kafka_topics = [
        'builder.aggregated.finalized.units.from.builder',
        'wfp.datalines.from.external.to.workflows',
        'wfp.builder.adapter.datalines.to.builder',
        'builder.units.from.external',
        'builder.units.creation.dead.letters',
        'raw.judgments.from.workerui',
        'db.builder.units',
    ]
    rs_configs = []
    for i, topic in enumerate(kafka_topics):
        rs_config = {
              'name': f'kafka-consumers-{session_id}-{i}',
              'command': 'python',
              'args': ['adap/perf_platform/kafka_consumers.py'],
              'num_replicas': 1,
              'cmap_data': {
                'SESSION_ID': session_id,
                'TASK_ID': '0',
                'CAPTURE_RESULTS': 'true',
                'KAFKA_BOOTSTRAP_SERVER': '1.kafka.integration.cf3.us:9092,'
                                          '2.kafka.integration.cf3.us:9092,'
                                          '3.kafka.integration.cf3.us:9092',
                'KAFKA_TEST_TOPICS': topic,
              }
            }
        se.deploy_replicaset(rs_config)

    se.wait(10)

    def task1():
      TASK_ID = '1'
      se.init_task(TASK_ID)
      test_job = {
        'name': f'workflows-test-{session_id}-{TASK_ID}',
        'filename': 'adap/perf_platform/test_scripts/WBA_wf.py',
        'job_config': {
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'CAPTURE_RESULTS': 'true',
            'MAX_WAIT_TIME': '300',
            'LOG_HTTP': 'false',
            'DATA_SOURCE_PATH': data_source_env_paths[ENV],
        }
      }
      se.run_job(test_job)
      se.wait_for_completion(test_job, max_wait=15*60)

    def task2():
      TASK_ID = '2'
      se.init_task(TASK_ID)
      test_job = {
        'name': f'workflows-test-{session_id}-{TASK_ID}',
        'filename': 'adap/perf_platform/test_scripts/WBA_non_wf.py',
        'job_config': {
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'CAPTURE_RESULTS': 'true',
            'MAX_WAIT_TIME': '300',
            'LOG_HTTP': 'false'
        }
      }
      se.run_job(test_job)
      se.wait_for_completion(test_job, max_wait=15*60)

    se.execute_concurrent_func(task1, task2)
