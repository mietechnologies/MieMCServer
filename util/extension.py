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