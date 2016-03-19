import contextlib
import time


clock = time.perf_counter


@contextlib.contextmanager
def timed(verbose=False, start_text=None, stop_text=None):
    started = clock()
    if verbose and start_text:
        print(start_text)

    yield

    elapsed = clock() - started
    if verbose and stop_text:
        print(stop_text.format(elapsed))
