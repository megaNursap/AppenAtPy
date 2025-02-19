from adap.perf_platform.utils.logging import get_logger
from bs4 import BeautifulSoup
import time
from requests import get
import hashlib

log = get_logger(__name__)


def retry(func, max_wait=60, interval=5, wait_first=True, max_retries=None, exc=AssertionError, *args, **kwargs):
    """
    This will retry to execute fucntion `func`.
    Only exception `exc` is handled, others will immediately throw error.
    If `max_retries` is provided, it will be used instead of `max_wait`.

    Parameters:
    func (function): function to be executed
    max_wait (int): max number of seconds untill timeout
    interval (int): number of seconds to wait between each retry
    wait_first (bool): whether to wait before the first execution
    max_retries (int): max number of retries
    exc (subclass of BaseException): the exception type to be handled
    """

    if wait_first:
        time.sleep(interval)

    _c_wait = 0
    _c_retries = 0

    def waits():
        return _c_wait <= max_wait

    def retries():
        return _c_retries <= max_retries

    def check():
        if max_retries:
            return retries()
        else:
            return waits()

    _exceptions = []
    while check():
        try:
            return func(*args, **kwargs)
        except exc as e:
            log.debug(f"Caught exception in retry: {e.__repr__()}")
            _exceptions.append(e)
            _c_wait += interval
            _c_retries += 1
            time.sleep(interval)
            continue
    else:
        if max_retries:
            msg = f"Max number of retries ({max_retries}) exceeded!"
        else:
            msg = f"Max wait time ({max_wait} seconds) in retries exceeded!"
        e = _exceptions[-1]
        e.args = (msg, *e.args)
        raise e


def find_authenticity_token(page_text: bytes):
    """
    :param page_text: ApiResponse.content
    """
    try:
        soup = BeautifulSoup(page_text, 'html.parser')
        at_input = soup.find('input', {'name': 'authenticity_token'})
        csrf_token = soup.find('meta', {'name': 'csrf-token'})
        if at_input is not None:
            authenticity_token = at_input.get('value')
        elif csrf_token is not None:
            authenticity_token = csrf_token.get('content')
        return authenticity_token
    except Exception as e:
        raise Exception({
            'message': 'Error getting authenticity_token',
            'page_text': page_text,
            'exception': e.__repr__()
        })


def get_unit_markers_from_tasks(tasks: list) -> list:
    """
    Find unit markers from tasks html. Markers are expected in cml as
        <p>marker: {{marker}}</p>

    params:
    :type task: bs4.element.Tag
    """
    markers = []
    for task in tasks:
        p_tags = task.find_all('p')
        marker_tag = [p for p in p_tags if 'marker' in p.text]
        assert len(marker_tag) == 1, f'Marker not found in \n {task.text}'
        marker = marker_tag[0].text.split()[-1]
        markers.append(marker)

    return markers


def get_current_ip():
    try:
        return get('https://api.ipify.org').content.decode('utf8')
    except:
        return 'IP is not defined'


def hashed_unit_id(unit_id):
    return hashlib.sha1(unit_id.encode()).hexdigest()


def wait_until(predicate, timeout, period_sec=0.25, *args, **kwargs):
    must_end = time.time() + timeout
    while time.time() < must_end:
        if predicate(*args, **kwargs):
            return True
        time.sleep(period_sec)
    return False
