import time
import os


def measure_time(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if eval(os.getenv('VERBOSE', 'False')):
            print('{} took {:.2f} s'.format(method.__name__,
                                            (te - ts)))
        return result

    return timed
