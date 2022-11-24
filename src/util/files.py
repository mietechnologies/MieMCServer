"""
A simple module for working with files. This module also acts as a file url
provider to all other project files.
"""

import os
from util.logger import log
from util.path import project_path

def bootlog() -> str:
    return project_path('logs', 'bootlog.txt')

def add(lines: list, to_file_at_path: str) -> bool:
    '''
    Adds a list of lines as new lines to a specific file.

    Parameters
    ----------
    lines: list
        The lines to add to the file.

    to_file_at_path: str
        The absolute path to the file.
    '''

    existing = lines_from_file(to_file_at_path)

    new_lines = []
    for line in lines:
        new_line = line
        if '\n' not in new_line:
            new_line = f'{new_line}\n'
        if new_line not in existing:
            new_lines.append(new_line)

    with open(to_file_at_path, 'w', encoding='utf8') as file_out:
        for line in existing:
            if '\n' not in line:
                file_out.write(f'{line}\n')
            else:
                file_out.write(line)
        for line in new_lines:
            file_out.write(line)
        file_out.close()
    return True

def update(file_at_path: str, replacing_line: str, with_line: str) -> bool:
    '''
    Replaces a single line contained within a specific file with a different line.

    Paramters
    ---------
    file_at_path: str
        The absolute path to the file to update.

    replacing_line: str
        The line in the file to update.

    with_line: str
        The line to replace.

    Returns
    -------
    bool
        A bool value indicating success.
    '''

    lines = lines_from_file(file_at_path)
    with open(file_at_path, 'w', encoding='utf8') as file_out:
        for line in lines:
            if line is replacing_line:
                file_out.write(with_line)
            else:
                file_out.write(line)
    return True

def lines_from_file(file: str, delete_fetched: bool = False):
    '''
    Extracts the text from a file as a list of lines.

    Parameters
    ----------
    file: str
        The absolute path to the file to extract.

    delete_fetched: bool = False
        If True, removes all lines currently in the file.
    '''

    lines = []
    with open(file, 'r', encoding='utf8') as file_in:
        temp_lines = file_in.readlines()
        with open(file, 'w', encoding='utf8') as file_out:
            for line in temp_lines:
                # Always preserve all comments and empty lines when fetching commands from a file:
                if '#' in line:
                    file_out.write(line)
                elif line == '\n':
                    file_out.write(line)
                # If line is command and fetched commands should be kept:
                elif not delete_fetched:
                    lines.append(line.replace('\n', ''))
                    file_out.write(line)
                # If line is command and fetched commands should be removed:
                elif delete_fetched:
                    lines.append(line.replace('\n', ''))
                # Otherwise, the line is unhandled; log the line that was encountered and keep
                # it in the file
                else:
                    log('Line from {} not recognized [{}]'.format(file, line))
                    file_out.write(line)
    return lines

def write(lines: list, file: str):
    '''
    Writes a list of lines to a specific file. 

    Note
    ----
    This method overwrites the specified file. Only call this method if you are sure that
    the contents of the file are not needed.

    Parameters
    ----------
    lines: str
        The lines to write to the file.

    file: str
        The file to write to.
    '''

    new_lines = []
    for line in lines:
        if "\n" not in line:
            new_lines.append(f'{line}\n')
        else:
            new_lines.append(line)

    with open(file, 'w', encoding='utf8') as file_out:
        for line in new_lines:
            file_out.write(line)
        file_out.close()
