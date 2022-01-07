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
    lower = haystack.lower()
    for needle in needles:
        if needle.lower() in lower:
            return True
    return False