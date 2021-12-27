import os

def username() -> str:
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 6c75c0c (Added doc strings and updated changelog)
    '''
    Fetches the system username by obtaining the expanded root directory
    and iterating through its components until it finds the last non-
    empty string.
    
    Returns:
    str:The system username of the currently executing machine.
    '''
<<<<<<< HEAD
    root_path = os.path.expanduser('~/')
    normalized_path = os.path.normpath(root_path)
    return os.path.basename(normalized_path)
=======
=======
>>>>>>> 6c75c0c (Added doc strings and updated changelog)
    root_path = os.path.expanduser('~/')
    path_components = root_path.split('/')
    for component in reversed(path_components):
        if component != '':
            return component
    raise(NameError('Could not find user name for this system'))
>>>>>>> 55c88be (Added functionality to fetch username from system and updated cron to use this functionality)
