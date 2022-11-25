'''
Handy custom functions for executing specific tasks.
'''

import re
from typing import List

def clean_string(haystack: str, needles: List[str]) -> str:
    '''Finds and removes the needles from the haystack string if they exist'''
    cleaned = haystack
    for needle in needles:
        cleaned = cleaned.replace(needle, '')
    return cleaned

def string_contains(haystack: str, needle_pattern: str) -> bool:
    '''Searches the given str for any instance of the given regex pattern'''
    return len(re.findall(needle_pattern, haystack)) >= 1

def string_contains_any_case(haystack: str, needles: List[str]) -> bool:
    '''Searches a given str for a match from a list of str'''
    lower = haystack.lower()
    for needle in needles:
        if needle.lower() in lower:
            return True
    return False

def lines_from_file(file: str, delete_fetched: bool = False) -> list[str]:
    '''
    Fetches all lines from a specific file, ignoring any lines that are comments
    (begins with '#') and any new lines.
    Parameters:
        file (str): The file to fetch lines from.
        delete_fetched (bool): Determines if the lines fetched from the file
        should be deleted as they are fetched from the file. Defaults to False.
    Returns:
        list[str]: A list of lines from the given file.
    '''
    lines = []
    with open(file, 'r', encoding='utf-8') as file_in:
        tmp = file_in.readlines()
        with open(file, 'w', encoding='utf-8') as file_out:
            for line in tmp:
                # Always preserve all comments and empty lines when fetching
                # commands from a file:
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
                # Otherwise, the line is unhandled; log the line that was 
                # encountered and keep it in the file
                else:
                    file_out.write(line)
    return lines
