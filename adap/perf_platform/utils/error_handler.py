"""
Counting errors until limit is reached (for Locust).
Sleep {wait_time} seconds after each error.
"""

from .logging import get_logger
import gevent

log = get_logger(__name__)

wait_time = 60
limit = 50


def init():
    global errors
    errors = []


def add(err):
    global errors
    try:
        errors.append(err)
    except NameError:
        init()
        add(err)


def check():
    global errors
    return len(errors) < limit


def handle(err):
    # log.error({'message': err})
    add(err)
    if not check():
        raise Exception(f'Max limit of errors handled exceeded!')
    gevent.sleep(wait_time)
