import time

import functools


def time_execution(f):
    @functools.wraps(f)
    def timed(*args, **kw):
        start = time.time()
        result = f(*args, **kw)
        end = time.time()

        print('%r - %2.2f seconds' % (f.__name__, abs(start - end)))

        return result

    return timed
