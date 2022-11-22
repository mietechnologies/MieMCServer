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

def project_path(to_dir: str = None, filename: str = None, create: bool = True) -> str:
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
    if to_dir is not None:
        directory = os.path.join(project, to_dir)
    else:
        directory = project

    # Create the directory if it doesn't already exist.
    if create and not os.path.exists(directory):
        os.makedirs(directory)

    # Add the filename if given.
    if filename:
        return os.path.join(directory, filename)
    return directory.replace(' ', '\\ ')

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

def remove(project_directory: str = None, system_directory: str = None, file: str = None) -> bool:
    """
    Deletes an entire directory, if possible. Alternatively, you can remove a
    single file from this directory by designating a specific file to delete.

    Warning
    -------
    This method is designed to be very unforgiving. Only use this if you are
    **absolutely** certain you no longer need the supplied directory.

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

    if project_directory is not None and file is not None:
        project_file_path = project_path(project_directory, file)
        if isfile(project_file_path):
            os.remove(project_file_path)
        return True
    if project_directory is not None:
        project_directory_path = project_path(project_directory)
        shutil.rmtree(project_directory_path)
        return True
    if system_directory is not None and file is not None:
        system_file_path = system_path(system_directory, file)
        if isfile(system_file_path):
            os.remove(system_file_path)
        return True
    if system_directory is not None:
        system_directory_path = system_path(system_directory)
        shutil.rmtree(system_directory_path)
        return True
    # If only file is given, assume it is an absolute path
    if file is not None:
        if isfile(file):
            os.remove(file)
        return True
    return False
    
def move(from_dir: str, to_dir: str, file: str = None):
    """
    """

    if file:
        source = project_path(from_dir, file)
        destination = project_path(to_dir, file)
        os.rename(source, destination)
    else:
        source = project_path(from_dir)
        destination = project_path(to_dir)
        os.rename(source, destination)

def list_dir(directory: str) -> list:
    '''
    Returns a list of file paths in a given directory.

    Parameters
    ----------
    directory: str
        The directory to list.

    Returns
    -------
    list(str)
        A list of file paths in the given directory.
    '''

    contents = []
    for filename in os.listdir(directory):
        file = f'{directory}/{filename}'
        contents.append(file)
    return contents

def file_name(from_dir: str) -> str:
    '''
    '''

    if isfile(from_dir):
        parts = from_dir.split('/')
        return parts[len(parts) - 1]
    return None
