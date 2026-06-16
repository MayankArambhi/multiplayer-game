import time

class TimerError:
    """A custom exception used to report errors in use of Timer class"""

class Timer:
    def __init__(self):
        self._start_time = None
        self._elapsed_time = None
    
    def start(self):
        if self._start_time != None:
            raise TimerError("Timer is running")
        self._start_time = time.perf_counter()

    def stop(self):
        if self._start_time == None:
            raise TimerError("Timer is not running")
        self._elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None

    def elapsed(self):
        if self._elapsed_time == None:
            raise TimerError("Timer has not run yet")
        return self._elapsed_time
    
    def __str__(self):
        return str(self._elapsed_time)