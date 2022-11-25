"""
A simple but all-inclusive place to read and write data from and to files.

Methods
-------
"""

import json
import yaml
import zipfile
from util import path

def parse_json(file: str) -> dict:
    """
    Parses a given json file and returns the dictionary representing its contents.

    Parameters
    ----------
    file: str
        The absolute path to the json file to be parsed.

    Returns
    -------
    dict | None
        Returns a dict representing the json file if the file exists or None.
    """

    with open(file, 'r', encoding='utf8') as json_file:
        return json.load(json_file)

def write_json(data: dict, to_file: str) -> dict:
    print('write_json(data:to_file:) not yet implemented')

def parse_yaml(file: str) -> dict:
    """
    Parses a given json file and returns the dictionary representing its contents.

    Parameters
    ----------
    file: str
        The absolute path to the json file to be parsed.

    Returns
    -------
    dict
        Returns a dict representing the yaml file if the file exists or None.
    """

    if path.isfile(file):
        with open(file, 'r', encoding='utf8') as yaml_file:
            return yaml.load(yaml_file, yaml.Loader)
    return None

def write_yaml(data: dict, to_file: str) -> dict:
    """
    Converts a dictionary to yaml and saves the data to a given file.

    Parameters
    ----------
    data: dict
        The data to write to the yaml file.

    to_file: str
        The absolute path of the yaml file to write to.

    Returns
    -------
    dict
        The data that was written to the file. For sanity checking purposes, this method
        reads the data that was written instead of the data that was passed in.
    """

    with open(to_file, 'w', encoding='utf8') as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False)
        return parse_yaml(to_file)

def extract_zip(file: str, to_dir: str) -> str:
    '''
    Extracts the contents of a zip file to a given directory.

    Parameters
    ----------
    file: str
        The file to extract.

    to_dir: str
        The directory to extract to

    Returns
    -------
    str | None
        Returns the path that the zip file was extracted to or None if the operation
        wasn't successful.
    '''

    file = file.strip()
    if path.isfile(file):
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(to_dir)
            return to_dir
    return None
