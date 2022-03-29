# pylint: disable=not-callable

'''
A module for monitoring the data stream from the project.
'''

from asyncio import subprocess
from threading import Event, Thread

from util.extension import lines_from_file, string_contains
from util.files import bootlog

class RepeatingTimer(Thread):
    '''
    As the name indicates, this is a repeating timer that executes the supplied
    method at each interval until stopped.
    '''
    def __init__(self, interval_seconds, callback):
        super().__init__()
        self.stop_event = Event()
        self.interval_seconds = interval_seconds
        self.callback = callback

    def run(self):
        while not self.stop_event.wait(self.interval_seconds):
            self.callback()

    def stop(self):
        self.stop_event.set()

class MonitorItem:
    elapsed = 0
    timeout = 10
    finished = False
    timer: RepeatingTimer
    on_finish = None

    def __init__(self, timer: RepeatingTimer, timeout: int = 10):
        self.elapsed = 0
        self.timeout = timeout
        self.timer = timer

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def completed(self) -> bool:
        if self.finished:
            return self.finished
        if self.timedout():
            self.stop()
            return self.timedout()

    def timedout(self) -> bool:
        return self.elapsed >= self.timeout

class Monitor:
    '''
    The main Monitor class. Houses several methods to monitor various statistics
    related to the project and the current run.
    '''
    DEBUG = False
    DEBUG_BOOTLOG = None
    STARTUP_SUCCESSFUL = False

    __LOG = None

    __STARTUP: MonitorItem

    @classmethod
    def start_server_start_monitor(cls, timeout: int = 10, log = None):
        '''
        Starts monitoring the server's bootlog file for relevant data to
        indicate that the server has started. After a specific amount of time,
        this method will "timeout" and the server will be considered as not
        having started. To keep this a valid statement, if this method ever
        "detects" a failure to start, it should also call the command to stop
        the server.

        Parameters:
          - timeout (int): The number of seconds before the application
          determines that too much time has passed for this to be a successful
          launch.
          - log (void): A reference to the method for logging information.
        '''
        cls.__LOG = log
        cls.__STARTUP = MonitorItem(RepeatingTimer(1, cls.__check_startup), timeout)
        cls.__STARTUP.start()

    @classmethod
    def stop_all_monitors(cls):
        cls.__STARTUP.stop()

    @classmethod
    def __check_startup(cls):
        cls.__STARTUP.elapsed += 1

        # Decide file to use.
        # If we're in DEBUG and a debuggable bootlog file has been provided, use
        # that one. Otherwise, use the default bootlog file created and used by
        # the server code.
        file = bootlog()
        if cls.DEBUG and cls.DEBUG_BOOTLOG:
            file = cls.DEBUG_BOOTLOG

        for line in lines_from_file(file):
            if string_contains(line, r'Done \(\d.\d+s\)!'):
                cls.STARTUP_SUCCESSFUL = True
                break

        if cls.__STARTUP.completed():
            if cls.__STARTUP.timedout():
                cls.__LOG('Could not start the server in a reasonable amount of ' \
                'time! Is something wrong?')
            else:
                cls.__LOG('Startup successful!')
            cls.__STARTUP.stop()
