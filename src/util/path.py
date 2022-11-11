"""
A simple module for working with local paths.

Methods
-------
project_path(to_dir: str, filename: str = None, create: bool = True) -> str
    Creates a path to the designated directory in the project's root.

system_path(to_dir: str, filename: str = None) -> str
    Creates a path to the designated directory on the disk.

is_file(directory: str) -> bool
    Determines if the object located at a specific directory is a file or not.
"""

import os
import shutil
import sys
sys.path.append('..')

def project_path(to_dir: str, filename: str = None, create: bool = True) -> str:
    """
    Creates a path to the designated directory in the project's root. By default, if the
    directory does not exist, this method will create it automatically.

    Parameters
    ----------
    to_dir: str
        The project directory to point to.
    filename: str | None
        An optional filename to point to.

    Returns
    -------
    str
        The constructed path pointing to the desired directory/file.
    """

    # Construct the path to the directory.
    root = os.path.dirname(__file__)
    project = os.path.join(root, '..')
    directory = os.path.join(project, to_dir)

    # Create the directory if it doesn't already exist.
    if create and not os.path.exists(directory):
        os.makedirs(directory)

    # Add the filename if given.
    if filename:
        return os.path.join(directory, filename)
    return directory

def system_path(to_dir: str, filename: str = None) -> str:
    """
    Creates a path to the designated directory on the disk.
    Note: This method does NOT create the directory if it doesn't already
    exist.

    Parameters
    ----------
    to_dir: str
        The project directory to point to.
    filename: str | None
        An optional filename to point to.

    Returns
    -------
    str
        The constructed path pointing to the desired directory/file.
    """
    root = os.path.expanduser('~/')
    directory = os.path.join(root, to_dir)
    if filename:
        return os.path.join(directory, to_dir)
    return directory

def isfile(directory: str) -> bool:
    """
    Determines if the object located at a specific directory is a file or not.

    Parameters
    ----------
    directory: str
        The full path to the directory/file to be checked.
    """
    return os.path.isfile(directory)

def remove(project_directory: str = None, system_directory: str = None) -> bool:
    """
    Deletes an entire directory, if possible.

    Warning
    -------
    This method is designed to be very unforgiving. Only use this if you are **absolutely**
    certain you no longer need the supplied directory.

    Parameters
    ----------
    project_directory: str | None
        The path relative to the project you wish to remove.
    system_directory: str | None
        The path relative to the system you wish to remove.

    Returns
    -------
    bool
        A bool indicating if the process was successful.
    """

    if project_directory:
        path = project_path(project_directory, create=False)
        shutil.rmtree(path)
    if system_directory:
        path = system_path(system_directory)
        shutil.rmtree(path)

    return False
