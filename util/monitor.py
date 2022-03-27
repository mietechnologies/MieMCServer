'''
A module for monitoring the data stream from the project.
'''

import os
from threading import Event, Thread

from util.extension import lines_from_file, string_contains, strings_contain
from util.files import bootlog

class RepeatingTimer(Thread):
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

class Monitor:
    DEBUG = False
    DEBUG_BOOTLOG = None

    __STARTUP = None
    __STARTUP_ELAPSED = 0
    __STARTUP_SUCCESSFUL = False
    __STARTUP_TIMEOUT = 10

    @classmethod
    def start_server_start_monitor(cls, timeout: int = 10):
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
        '''
        cls.__STARTUP_TIMEOUT = timeout
        cls.__STARTUP = RepeatingTimer(1, cls.__check_startup)
        cls.__STARTUP.start()

    @classmethod
    def __check_startup(cls):
        cls.__STARTUP_ELAPSED += 1
        
        # Decide file to use.
        # If we're in DEBUG and a debuggable bootlog file has been provided, use
        # that one. Otherwise, use the default bootlog file created and used by
        # the server code.
        file = bootlog()
        if cls.DEBUG and cls.DEBUG_BOOTLOG:
            file = cls.DEBUG_BOOTLOG

        for line in lines_from_file(file):
            if string_contains(line, r'Done \(\d.\d+s\)!'):
                cls.__STARTUP_SUCCESSFUL = True
                break

        print('check startup', cls.__STARTUP_ELAPSED, cls.__STARTUP_SUCCESSFUL)
        if cls.__STARTUP_SUCCESSFUL:
            # Should this be logged?
            print('startup successful; stopping monitor!')
            cls.__STARTUP.stop()
        elif cls.__STARTUP_ELAPSED >= cls.__STARTUP_TIMEOUT:
            # Should this be logged?
            print('startup timeout; stopping server and monitor!')
            cls.__STARTUP.stop()
            # stop server
