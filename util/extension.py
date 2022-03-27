import base64
import re

def cleanString(haystack: str, needles: list[str]) -> str:
    '''Finds and removes the needles from the haystack string if they exist'''
    cleaned = haystack
    for needle in needles:
        cleaned = cleaned.replace(needle, '')
    return cleaned

def string_contains(haystack: str, needle_pattern: str) -> bool:
    '''Searches the given str for any instance of the given regex pattern'''
    return len(re.findall(needle_pattern, haystack)) >= 1

def stringContainsAnyCase(haystack: str, needles: list[str]) -> bool:
    '''Searches a given str for a match from a list of str'''
    lower = haystack.lower()
    for needle in needles:
        if needle.lower() in lower:
            return True
    return False

def decode(value: bytes or str) -> str:
    '''Decodes a given str with utf-8 encoding'''
    return base64.b64decode(value.decode())

def encode(string: str) -> str:
    '''Encodes a given str with utf-8 encoding'''
    return base64.b64encode(string.encode())
