def cleanString(haystack: str, needles: list[str]) -> str:
    '''Finds and removes the needles from the haystack string if they exist'''
    cleaned = haystack
    for needle in needles:
        cleaned = cleaned.replace(needle, '')
    return cleaned