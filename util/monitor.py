# pylint: disable=not-callable


'''
A module for monitoring the data stream from the project.
'''

import os
from threading import Event, Thread
from time import sleep

from pendulum import time

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
    '''
    A class representing a task that the system should monitor in the
    background.

    Examples are system startup, player logs, etc.
    '''
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
        '''
        Starts the MonitorItem.
        '''
        self.timer.start()

    def stop(self):
        '''
        Stops the MonitorItem from running.
        '''
        self.timer.stop()

    def completed(self) -> bool:
        '''
        Determines if the MonitorItem has finished running.

        NOTE: This method should only be used on time-sensitive monitors
        (i.e., the server startup monitor). Other monitors will run
        indefinitely.
        '''
        if self.finished:
            return self.finished
        if self.timedout():
            self.stop()
            return self.timedout()
        return False

    def is_running(self) -> bool:
        '''
        Determines if the MonitorItem is running by checking to see if it hasn't
        completed or if the elapsed time is less that it's timeout value.
        '''
        return not self.completed() or self.elapsed < self.timeout

    def timedout(self) -> bool:
        '''
        Determines if the MonitorItem's elapsed time is greater that it's
        timeout value.
        '''
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

    startup: MonitorItem

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
        cls.startup = MonitorItem(RepeatingTimer(1, cls.__check_startup), timeout)
        cls.startup.start()

    @classmethod
    def stop_all_monitors(cls):
        '''
        Stops all currently running MonitorItem's that are running.
        '''
        cls.startup.stop()

    @classmethod
    def __check_startup(cls):
        cls.startup.elapsed += 1

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

        if cls.startup.completed():
            if cls.startup.timedout():
                cls.__LOG('Could not start the server in a reasonable amount of ' \
                'time! Is something wrong?')

                # This technically shouldn't be needed and should actually cause
                # an error, but in case the server has started up (after
                # timeout), we're going to call the quit command so that we're
                # absolutely sure that the server isn't running anymore.
                sleep(10)
                this_dir = os.path.dirname(__file__)
                root_dir = os.path.join(this_dir, '..')
                os.system(f'python3 { root_dir }/main.py -q')

            else:
                cls.__LOG('Startup successful!')
            cls.startup.stop()
