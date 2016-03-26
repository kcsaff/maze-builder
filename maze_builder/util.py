import contextlib
import time


clock = time.perf_counter


_verbosities = [0]


@contextlib.contextmanager
def verbosity(verbose):
    _verbosities.append(verbose)
    try:
        yield
    finally:
        _verbosities.pop()


def is_verbose(verbose):
    return _verbosities[-1] >= verbose


@contextlib.contextmanager
def timed(verbose, start_text=None, stop_text=None):
    started = clock()
    if verbose and start_text:
        print(start_text)

    yield

    elapsed = clock() - started
    if verbose and stop_text:
        print(stop_text.format(elapsed))
