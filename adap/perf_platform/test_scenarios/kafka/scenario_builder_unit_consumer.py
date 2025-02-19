"""
======================== Load Test ========================
Measure max  throughput and latency of Builder Unit Creation consumer
time diff between message published to 'builder.units.from.external'
and new unit added to Builder DB 
Test 2 scenarios:
- units added to the first job (bulk unit upload)
- units added to the second job (1 unit at a time)
Note that these units also get launched

TODO: add a chart to grafana with a diff between unit created_at and 
time it was consumed from 'builder.units.from.external' to get a latency per unit
"""

from adap.perf_platform.test_scenarios import executor as se
import json


ENV = 'integration'
scenario=f"[{ENV}] Builder Unit Creation consumer load test"

with se.session(scenario, teardown=False) as session_id:

    TASK_ID = '1'

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

    # Monitoring unit counts in Builder for the first job in the WF
    wf_step = '1'
    job_units_monitor = {
        'name': f'monitor-wf-job-units-{session_id}-{TASK_ID}-{wf_step}',
        'filename': 'adap/perf_platform/units_state_monitor.py',
        'job_config': {
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'CAPTURE_RESULTS': 'true',
            'MAX_WAIT_TIME': '2700',  # 45 minutes
            'RUN_TIME': '10800',  # 3 hours
            'UNITS_MONITOR_TYPE': 'counts',
            'UNITS_MONITOR_SOURCE': 'task_info',
            'WORKFLOW_STEP': wf_step
        }
    }
    se.run_job(job_units_monitor)

    # Create and launch workflow
    wf = {
        'name': f'create-workflow-{session_id}-{TASK_ID}',
        'filename': 'adap/perf_platform/create_workflow.py',
        'job_config': {
            'ENV': ENV,
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'MAX_WAIT_TIME': '600',
            'CAPTURE_RESULTS': 'true',
            'LOG_HTTP': 'false',
            'NUM_UNITS': '100000'
        }
    }
    se.run_job(wf)
    se.wait_for_completion(wf, max_wait=15*60)
    se.wait(15*60)  # wait for the units to become added to Builder/ launched

