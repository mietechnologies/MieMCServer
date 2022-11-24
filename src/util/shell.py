"""
A simple module for working with shell commands.

Methods
-------
run(command: str)
    Executes a given command in the shell.
"""

import re
import shlex
from subprocess import check_output, Popen, PIPE
import psutil
from util.logger import log

def run(command: str, execute_in: str = None, stop_on_stdout_regex: str = None) -> str:
    """
    Executes a given command in the shell.

    Parameters
    ----------
    command: str
        The command to be executed.

    Returns
    -------
    str | None
        The output of the command.
    """

    lines = []
    command_parts = shlex.split(command)
    with Popen(command_parts, stdout=PIPE, universal_newlines=False, cwd=execute_in) as popen:
        if popen.stdout is not None:
            for stdout_line in iter(popen.stdout.readline, ''):
                stdout_line = stdout_line.decode('utf8').strip()

                if stdout_line != '':
                    lines.append(stdout_line)
                    log(stdout_line)
                if stop_on_stdout_regex and len(re.findall(stop_on_stdout_regex, stdout_line)) == 1:
                    break
                if popen.poll() == 0:
                    break

            popen.stdout.close()
            if popen.stdin is not None:
                popen.stdin.close()
            if popen.stderr is not None:
                popen.stderr.close()
            popen.kill()

    return lines

def kill_process(name: str):
    '''
    Terminates all processes and children proceses currently running with a given name.

    Parameters
    ----------
    name: str
        The name of the process to terminate.
    '''

    # Get the PIDs of any currently running processes
    pids = []
    for proc in psutil.process_iter():
        if name in proc.name():
            pids.append(proc.pid)

    # Kill the processes and all of their children
    for pid in pids:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
