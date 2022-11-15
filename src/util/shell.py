"""
A simple module for working with shell commands.

Methods
-------
run(command: str)
    Executes a given command in the shell.
"""

import os

def run(command: str):
    """
    Executes a given command in the shell.

    Parameters
    ----------
    command: str
        The command to be executed.
    """

    os.system(command)
