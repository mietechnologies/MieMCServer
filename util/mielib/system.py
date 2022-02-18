import os

def username() -> str:
    '''
    Fetches the system username by obtaining the expanded root directory
    and iterating through its components until it finds the last non-
    empty string.
    
    Returns:
    str:The system username of the currently executing machine.
    '''
    root_path = os.path.expanduser('~/')
    normalized_path = os.path.normpath(root_path)
    return os.path.basename(normalized_path)
