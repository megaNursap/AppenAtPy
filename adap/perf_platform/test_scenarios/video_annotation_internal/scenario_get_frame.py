from adap.perf_platform.test_scenarios import executor as se

with se.session(teardown=False) as session_id:

    # ------------------------- TASK I -------------------------
    TASK_ID = '1'

    # LOCUST
    locust_1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/locust_video_anno_internal.py',
      'num_slaves': 20,
      'num_clients': 200,
      'hatch_rate': 0.22,  # 100/300s=0.33
      'run_time': '20m',
      'locust_config': {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'LOCUST_TASK': 'get_frame'
      }
    }
    se.run_locust(locust_1)

    # ------------------------- END -------------------------
    se.wait_for_completion(locust_1, max_wait=35*60)
