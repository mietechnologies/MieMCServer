"""
A simple but all-inclusive place to read and write data from and to files.

Methods
-------
"""

import json

def parse_json(file: str) -> dict:
    """
    Parses a given json file and returns the dictionary representing its contents.

    Parameters
    ----------
    file: str
        The absolute path to the json file to be parsed.
    """
    with open(file, 'r', encoding='utf8') as json_file:
        return json.load(json_file)
