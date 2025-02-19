"""
1. Create a job
2. Order Test Questions -> TQG Job created | how fast units are moved to the TQG
3. Submit Judgments -> finalized units are published to buidlder.agg.finalized.units -> wfp.datalines.to.tqg |
4. Finalized units consumed by TQG convert_listener -> converts units into TQs
5. TQ units are routed to the Original job -> wfp.datalines.from.external
6. -> builder.units.from.external TQs are added to the original job
"""

from adap.perf_platform.test_scenarios import executor as se
import json

with se.session(teardown=False) as session_id:

    # ------------------------- TASK I -------------------------

    TASK_IDS = ['1', '2', '3']
    JOB_TYPE = 'what_is_greater'

    # KAFKA CONSUMERS

    kafka_topics = [
        'wfp.datalines.from.external.to.workflows',
        'wfp.datalines.to.tqg',
        'wfp.builder.adapter.datalines.to.builder',
        'builder.units.from.external',
    ]
    rs_configs = []
    for i, topic in enumerate(kafka_topics):
        rs_config = {
              'name': f'kafka-consumers-{session_id}-{i}',
              'command': 'python',
              'args': ['adap/perf_platform/kafka_consumers_tqg.py'],
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

    def part1(TASK_ID):
        # MONITORING UNITS IN BUILDER
        job_units_monitor = {
          'name': f'monitor-original-job-units-{session_id}-{TASK_ID}',
          'filename': 'adap/perf_platform/units_state_monitor.py',
          'job_config': {
              'SESSION_ID': session_id,
              'TASK_ID': TASK_ID,
              'CAPTURE_RESULTS': 'true',
              'MAX_WAIT_TIME': '2700',
              'RUN_TIME': '10800',  # 3 hours
              'UNITS_MONITOR_TYPE': 'counts'
          }
        }
        se.run_job(job_units_monitor)

        # CREATE A JOB
        job = {
          'name': f'create-job-{session_id}-{TASK_ID}',
          'filename': 'adap/perf_platform/create_job.py',
          'job_config': {
              'JOB_TYPE': JOB_TYPE,
              'SESSION_ID': session_id,
              'TASK_ID': TASK_ID,
              'MAX_WAIT_TIME': '1800',
              'CAPTURE_RESULTS': 'true',
              'LOG_HTTP': 'false',
              'NUM_UNITS': '10000',
              'NUM_TEST_QUESTION': '0',
              'UNITS_PER_ASSIGNMENT': '5',
              'GOLD_PER_ASSIGNMENT': '1',
              'JUDGMENTS_PER_UNIT': '2',
              'MAX_JUDGMENTS_PER_WORKER': '100',
              'LAUNCH_JOB': 'false'
          }
        }
        se.run_job(job)
        se.wait_for_completion(job, max_wait=30*60)

        # ORDER TEST QUESTIONS GENERATION
        order_tqg = {
          'name': f'order-tqg-{session_id}-{TASK_ID}',
          'filename': 'adap/perf_platform/order_tqg.py',
          'job_config': {
              'SESSION_ID': session_id,
              'TASK_ID': TASK_ID,
              'CAPTURE_RESULTS': 'true',
              'LOG_HTTP': 'false',
              'MAX_WAIT_TIME': '300',
              'NUM_TEST_QUESTION': '10000'
          }
        }
        se.run_job(order_tqg)
        se.wait_for_completion(order_tqg, max_wait=10*60)
        # wait for TQG job to get launched

        # MONITORING UNITS IN BUILDER
        job_units_monitor = {
          'name': f'monitor-tqg-job-units-{session_id}-{TASK_ID}',
          'filename': 'adap/perf_platform/units_state_monitor.py',
          'job_config': {
              'SESSION_ID': session_id,
              'TASK_ID': TASK_ID,
              # 'TASK_ID_DATA': '1',
              'JOB_TYPE': f"TQG_{JOB_TYPE}",  # monitor for the TQG job
              'CAPTURE_RESULTS': 'true',
              'MAX_WAIT_TIME': '2700',
              'RUN_TIME': '10800',  # 3 hours
              'UNITS_MONITOR_TYPE': 'counts',
              'UNITS_MONITOR_SOURCE': 'task_info'
          }
        }
        se.run_job(job_units_monitor)

    se.execute_concurrent(part1, TASK_IDS)

    se.wait(600)

    def part2(TASK_ID):
        # LOCUST SUBMIT JUDGMENTS ON TQG JOB
        workload = [
            {
                'start_at': '0:0:1',
                'target_count': 20,
                'finish_at': '0:10:0'
            }
        ]
        locust = {
          'suffix': f'{session_id}-{TASK_ID}',
          'filename': 'adap/perf_platform/locust_judge.py',
          'num_slaves': 2,
          'num_clients': 1,
          'hatch_rate': 1,
          'run_time': '15m',
          'locust_config': {
            'JOB_TYPE': f"TQG_{JOB_TYPE}",
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'EXTERNAL': 'false',
            'CAPTURE_RESULTS': 'true',
            'WAIT_ON_ASSIGNMENT': '3',
            'WORKLOAD': json.dumps(workload),
            'MAX_WAIT_TIME': '600',
          }
        }
        se.run_locust(locust)

    se.execute_concurrent(part2, TASK_IDS)

    se.wait(90*60)
    # ------------------------- END -------------------------
    # se.wait_for_completion(locust_1, max_wait=65*60)