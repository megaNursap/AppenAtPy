""" Application configuration. """

import os
from decouple import config

def to_bool(s: str) -> bool:
    return str(s).lower() in ['true', 't']

def to_list(s: str) -> list:
    return [i.strip() for i in s.split(',') if i]

def init_global():
    # list of messages published to kafka topic
    # used by locust producers for batch inserts into resultsdb
    global produced_messages_list
    produced_messages_list = list()


init_global()


class Config(object):
    """Config

    The configuration for the application. Each configuration option is specified as a class
    constant with a value derived from the environment using the :meth:`decouple.config` function.

    """

    ##
    #: The `APP_DIR` points to the location of the Flask app on the local
    #: filesystem.
    #:
    #: This value is not configurable as it derives itself from the path of this
    #: settings file, as it is assumed to be in the `APP_DIR`.
    #:
    APP_DIR: str = os.path.abspath(os.path.dirname(__file__))

    ##
    #: The `PROJECT_ROOT` specifies the path to the project (the directory
    #: containing migrations, tests, configurations, etc).
    #:
    #: This value is not configurable as it derives itself from the parent
    #: directory of the `APP_DIR`.
    #:
    PROJECT_ROOT: str = os.path.abspath(os.path.join(APP_DIR, os.pardir))

    ENV: str = str.lower(config('ENV', ''))
    ENV_FED: str = str.lower(config('ENV_FED', ''))
    HOSTNAME: str = config('HOSTNAME', '')
    KEY: str = config('KEY', '')

    LOG_LEVEL: str = config('LOG_LEVEL', 'DEBUG')
    LOG_HTTP: bool = to_bool(config('LOG_HTTP', True))
    LOG_TO_STDOUT: bool = to_bool(config('LOG_TO_STDOUT', True))
    LOG_TO_DB_LEVEL: str = config('LOG_TO_DB_LEVEL', 'INFO')

    # PSYCOPG2_POOL
    MIN_POOL: int = config('MIN_POOL', '1')
    MAX_POOL: int = config('MAX_POOL', '100')

    ECR_URL: str = config('ECR_URL', '411719562396.dkr.ecr.us-east-1.amazonaws.com')
    IMAGE_NAME: str = config('IMAGE_NAME', 'qa-automation')
    IMAGE_TAG: str = config('IMAGE_TAG', 'latest')
    IMAGE = f'{ECR_URL}/{IMAGE_NAME}:{IMAGE_TAG}'
    NAMESPACE: str = config('NAMESPACE', 'default')

    SESSION_ID: int = config('SESSION_ID', '')
    TASK_ID: int = config('TASK_ID', '')
    # TASK_ID_DATA is used when locusts have to work on a job_id created
    # within a different task, e.g. scenario:
    # TASK 1 :
    # create_job_conf = {
    #     $task_id: 1
    # }
    # locust_conf = {
    #     $task_id: 1
    # }
    # ...
    # TASK 3
    # add more locusts to the job from task 1
    # locust_conf = {
    #     $task_id: 3
    #     $task_id_data: 1
    # }
    TASK_ID_DATA: int = config('TASK_ID_DATA', '')

    FEEDER_HOST: str = config("FEEDER_HOST", f"locust-master{TASK_ID}")
    FEEDER_BIND_PORT: int = config("FEEDER_BIND_PORT", 5555)
    FEEDER_ADDR: str = f"tcp://{FEEDER_HOST}:{FEEDER_BIND_PORT}"
    MASTER_HOST: str = config("MASTER_HOST", f"locust-master-{SESSION_ID}-{TASK_ID}")
    MASTER_PORT: int = config("MASTER_PORT", 5556)

    DATA_SOURCE_FILE: str = config("DATA_SOURCE_FILE", "default")
    if DATA_SOURCE_FILE == 'default':
        env_data_source_file = {
            'qa': 'qa_contributor_emails.py',
            'integration': 'integration_contributor_emails.py',
            'staging': 'staging_contributor_emails.py'
        }
        DATA_SOURCE_FILE = env_data_source_file.get(ENV)
    dsfp = f"{APP_DIR}/perf_platform/test_data/{DATA_SOURCE_FILE}" if DATA_SOURCE_FILE else ""
    DATA_SOURCE_PATH: str = config("DATA_SOURCE_PATH", dsfp)

    WORKLOAD: str = config("WORKLOAD", '')  # JSON
    LOCUST_TASK: str = config("LOCUST_TASK", '')
    RUN_TIME: int = config("RUN_TIME", 300)

    DB_NAME: str = config('DB_NAME', '')
    DB_USER: str = config('DB_USER', '')
    DB_PASSWORD: str = config('DB_PASSWORD', '')
    DB_HOST: str = config('DB_HOST', '')
    DB_PORT: int = config('DB_PORT', '5432')

    RESULTS_DB_NAME: str = config('RESULTS_DB_NAME', '')
    RESULTS_DB_USER: str = config('RESULTS_DB_USER', '')
    RESULTS_DB_PASSWORD: str = config('RESULTS_DB_PASSWORD', '')
    RESULTS_DB_HOST: str = config('RESULTS_DB_HOST', '')
    RESULTS_DB_PORT: int = config('RESULTS_DB_PORT', '5432')
    RESULTS_DB_CONN = {
        'host': RESULTS_DB_HOST,
        'port': RESULTS_DB_PORT,
        'user': RESULTS_DB_USER,
        'dbname': 'platform_performance',  # TODO: find a better place for this
        'password': RESULTS_DB_PASSWORD,
    }

    BUILDER_DB_NAME: str = config(f'{ENV.upper()}_BUILDER_DB_NAME', '')
    BUILDER_DB_USER: str = config(f'{ENV.upper()}_BUILDER_DB_USER', '')
    BUILDER_DB_PASSWORD: str = config(f'{ENV.upper()}_BUILDER_DB_PASSWORD', '')
    BUILDER_DB_HOST: str = config(f'{ENV.upper()}_BUILDER_DB_HOST', '')
    BUILDER_DB_PORT: int = config(f'{ENV.upper()}_BUILDER_DB_PORT', '5432')
    BUILDER_DB_CONN = {
        'host': BUILDER_DB_HOST,
        'port': BUILDER_DB_PORT,
        'user': BUILDER_DB_USER,
        'dbname': BUILDER_DB_NAME,
        'password': BUILDER_DB_PASSWORD,
    }

    # CAPTURE_RESULTS: send results to Results DB (when run in Kubernetes)
    CAPTURE_RESULTS: bool = to_bool(config('CAPTURE_RESULTS', False))
    BATCHED_SAVE_RESULTS_SIZE: int = int(config('BATCHED_SAVE_RESULTS_SIZE', 0))
    CAPTURE_PAYLOAD: bool = to_bool(config('CAPTURE_PAYLOAD', False))
    # CAPTURE_RESPONSE: include HTTP json_response in results
    CAPTURE_RESPONSE: bool = to_bool(config('CAPTURE_RESPONSE', True))

    MAX_WAIT_TIME: int = int(config('MAX_WAIT_TIME', 120))

    JOB_TYPE: str = config('JOB_TYPE', 'what_is_greater')
    EXTERNAL: bool = to_bool(config('EXTERNAL', True))
    LAUNCH_JOB: bool = to_bool(config('LAUNCH_JOB', True))
    NUM_UNITS: int = int(config('NUM_UNITS', 300))
    VIDEO_SIZE: int = int(config('VIDEO_SIZE', 0))
    UNITS_PER_ASSIGNMENT: int = int(config('UNITS_PER_ASSIGNMENT', 5))
    GOLD_PER_ASSIGNMENT: int = int(config('GOLD_PER_ASSIGNMENT', 1))
    JUDGMENTS_PER_UNIT: int = int(config('JUDGMENTS_PER_UNIT', 5))
    MAX_JUDGMENTS_PER_WORKER: int = int(config('MAX_JUDGMENTS_PER_WORKER', 0))
    # tq_num = (MAX_JUDGMENTS_PER_WORKER / UNITS_PER_ASSIGNMENT) * GOLD_PER_ASSIGNMENT
    # tq_num = (tq_num + 10) * 2
    # NUM_TEST_QUESTION:  int = int(config('NUM_TEST_QUESTION', tq_num))
    NUM_TEST_QUESTION:  int = int(config('NUM_TEST_QUESTION', 0))
    LAUNCH_NUM_UNITS:  int = int(config('LAUNCH_NUM_UNITS', NUM_UNITS))
    CHANNELS: list = to_list(config('CHANNELS', 'vcare,listia'))
    CROWD_LEVEL: str = config('CROWD_LEVEL', 'unleveled')
    # DYNAMIC JUDGMENT COLLECTION
    DYNAMIC_JUDGMENT_COLLECTION: bool = to_bool(config('DYNAMIC_JUDGMENT_COLLECTION', False))
    MAX_JUDGMENTS_PER_UNIT: int = int(config('MAX_JUDGMENTS_PER_UNIT', 3))
    MIN_UNIT_CONFIDENCE: float = config('MIN_UNIT_CONFIDENCE', 0.7)
    JOB_SETTINGS_UPDATE: str = config('JOB_SETTINGS_UPDATE', '')
    # AUTO ORDER
    AUTO_ORDER: bool = to_bool(config('AUTO_ORDER', False))
    BYPASS_ESTIMATED_FUND_LIMIT: bool = to_bool(config('BYPASS_ESTIMATED_FUND_LIMIT', False))
    UNITS_REMAIN_FINALIZED: bool = to_bool(config('UNITS_REMAIN_FINALIZED', False))
    SCHEDULE_FIFO: bool = to_bool(config('SCHEDULE_FIFO', False))
    AUTO_ORDER_TIMEOUT: int = config('AUTO_ORDER_TIMEOUT', None)
    # ADDITIONAL UNITS
    NUM_UNIT_UPLOADS: int = int(config('NUM_UNIT_UPLOADS', 1))
    WAIT: int = int(config('WAIT', 10))

    # JUDGMENT SUBMISSION
    WAIT_IDLE_TIME: int = int(config('WAIT_IDLE_TIME', 0))
    WAIT_ON_ASSIGNMENT: int = int(config('WAIT_ON_ASSIGNMENT', 11))
    WORKFLOW_STEP: int = int(config('WORKFLOW_STEP', 0))
    # percentage of videos for which predict_box will be called
    PREDICT_BOX_RATE: float = config('PREDICT_BOX_RATE', 0.5)
    WORKER_RANDOM_EXIT: float = config('WORKER_RANDOM_EXIT', None)
    RANDOM_JUDGMENT: bool = to_bool(config('RANDOM_JUDGMENT', False))
    ANSWER_TYPE: int = int(config('ANSWER_TYPE', 0))
    JUDGMENT_ACCURACY: float = float(config('JUDGMENT_ACCURACY', 0))
    # for image annotation judgments
    NUM_ANNOTATIONS_PER_UNIT: int = int(config('NUM_ANNOTATIONS_PER_UNIT', 1))

    INTERVAL: int = int(config('INTERVAL', 0))
    UNITS_MONITOR_TYPE: str = config('UNITS_MONITOR_TYPE', 'counts')
    UNITS_MONITOR_SOURCE: str = config('UNITS_MONITOR_SOURCE', '')
    MONITOR_JOB_ID: str = config('MONITOR_JOB_ID', '')
    WF_JOB_ID: str = config('WF_JOB_ID', '')
    # KAFKA
    KAFKA_BOOTSTRAP_SERVER: str = config('KAFKA_BOOTSTRAP_SERVER', 'default')
    if KAFKA_BOOTSTRAP_SERVER == 'default':
        kafka_bootstrap_servers = {
            'integration': '1.kafka.integration.cf3.us:9092'
            }
        KAFKA_BOOTSTRAP_SERVER = kafka_bootstrap_servers.get(ENV)
    KAFKA_USERNAME: str = config('KAFKA_USERNAME', 'kafka')
    KAFKA_PASSWORD: str = config('KAFKA_PASSWORD', '')
    KAFKA_TEST_TOPICS: str = config('KAFKA_TEST_TOPICS', '')
    KAFKA_CONSUMER_TOPICS: list = to_list(
        config('KAFKA_CONSUMER_TOPICS', KAFKA_TEST_TOPICS))
    KAFKA_GROUP_ID: str = config('KAFKA_GROUP_ID', 'platform-perftest-group')
    MLAPI_MODEL_ID: int = int(config('MLAPI_MODEL_ID', 7))
    produced_messages_list = globals()['produced_messages_list']

    SLACK_NOTIFY: bool = to_bool(config('SLACK_NOTIFY', True))
    SLACK_TOKEN: str = config('SLACK_TOKEN', '')
    SLACK_CHANNEL: str = config('SLACK_CHANNEL', '')

    ENABLE_JUDGMENT_LOADER: bool = to_bool(config('ENABLE_JUDGMENT_LOADER', False))

    IPQS_RANDOM_IP: bool = to_bool(config('IPQS_RANDOM_IP', False))
