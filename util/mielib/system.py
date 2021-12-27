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
    path_components = root_path.split('/')
    for component in reversed(path_components):
        if component != '':
            return component
    raise(NameError('Could not find user name for this system'))