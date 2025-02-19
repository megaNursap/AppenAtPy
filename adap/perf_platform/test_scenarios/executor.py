from contextlib import contextmanager
from adap.settings import Config
from adap.perf_platform.utils import slack
from gevent import monkey
from ..utils.results_handler import (
    init_session,
    finilize_session,
    add_task_info
    )
from ..utils.logging import get_logger
from ..utils import k8
import gevent
import time

monkey.patch_all(ssl=False)
log = get_logger(__name__)


def run_job(config: dict):
    """ Kick off a K8s job """
    k8.create_job(
        job_name=config['name'],
        args=[config['filename']],
        cmap_data=config['job_config'])


def run_locust(config: dict):
    """ Kick off locust deployment """
    k8.deploy_locusts(
        suffix=config['suffix'],
        cmap_data=config['locust_config'],
        command='locust',
        filename=config['filename'],
        num_slaves=config['num_slaves'],
        num_clients=config['num_clients'],
        hatch_rate=config['hatch_rate'],
        run_time=config['run_time'])


def deploy_replicaset(config: dict):
    k8.deploy_replicaset(**config)


def wait(num_seconds):
    log.info(f"Sleep {num_seconds} seconds")
    time.sleep(num_seconds)


def wait_for_completion(config: dict, max_wait: int):
    if name := config.get('name'):
        if 'job_config' in config:
            return k8.wait_for_job_completion(name, max_wait)
    elif suffix := config.get('suffix'):
        if 'locust_config' in config:
            master_name = f'locust-master-{suffix}'
            return k8.wait_for_job_completion(master_name, max_wait)
    raise Exception(f"Dont know what resource this is: {config}")


def session_teardown():
    """ Delete all k8s reources that were created during the seesion """

    k8.delete_all_labelled_resources()


def get_session(env=None):
    """ Strart a new session or use existing one """
    session_id = Config.SESSION_ID
    if session_id:
        log.info(f"Existing session_id: {session_id}")
    else:
        session_id = init_session(env)
        Config.SESSION_ID = session_id
        k8.labels['session_id'] = str(session_id)
        log.info(f"New session_id: {session_id}, env: {env}")
    return session_id


def slack_notify_session_intiated(session_id, scenario) -> str:
    """
    Post slack notification when session is started.
    Returns timestamp of the posted message to be used for the message thread.
    """
    text = slack.text_template.format(
        env=Config.ENV,
        message=f"""
    Session #{session_id}
    Scenario: {scenario}
    Status: Running :loading:
        """)
    resp = slack.post_performance_results(text=text)
    return resp


def slack_update_session_status(status):
    """
    Update initial session slack message with the satus
    """
    global current_session_info
    initial_message = current_session_info.get('init_slack_message')
    assert initial_message is not None
    ts = initial_message.json()['ts']
    channel = initial_message.json()['channel']
    text = slack.text_template.format(
        env=Config.ENV,
        message=f"""
    Session #{current_session_info['session_id']}
    Scenario: {current_session_info['scenario']}
    Status: {status}
        """)
    resp = slack.update_message(
        text=text,
        ts=ts,
        channel=channel)
    return resp


def post_performance_results(text):
    """
    Post to a thread under the initial slack session message
    """
    initial_message = globals()['current_session_info'].get('init_slack_message')
    assert initial_message is not None
    thread_ts = initial_message.json()['ts']
    slack.post_performance_results(text=text, thread_ts=thread_ts)


@contextmanager
def session(scenario='Noname', teardown=True, env=Config.ENV):
    try:
        session_id = get_session(env)
        if Config.SLACK_NOTIFY:
            initial_message = slack_notify_session_intiated(
                session_id, scenario)
            global current_session_info
            current_session_info = {
                'session_id': session_id,
                'scenario': scenario,
                'init_slack_message': initial_message
            }
        yield session_id
    except Exception as e:
        log.error(e.__repr__())
        finilize_session(session_id, 'failed')
        if Config.SLACK_NOTIFY:
            slack_update_session_status(status='Failed :rotating_light:')
        raise e
    else:
        finilize_session(session_id, 'complete')
        if Config.SLACK_NOTIFY:
            slack_update_session_status(status='Complete :checkered_flag:')
        if teardown:
            session_teardown()


def init_task(task_id, info={}):
    session_id = get_session()
    add_task_info(
        info=info,
        session_id=session_id,
        task_id=task_id)


def execute_concurrent(func, params: list):
    tasks = [gevent.spawn(func, param) for param in params]
    return gevent.joinall(tasks)

def execute_concurrent_func(*args):
    """
    args is a list of functions to be called
    """
    tasks = [gevent.spawn(func) for func in args]
    return gevent.joinall(tasks, raise_error=True)
