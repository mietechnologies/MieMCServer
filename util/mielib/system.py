import os

def username() -> str:
    root_path = os.path.expanduser('~/')
    path_components = root_path.split('/')
    for component in reversed(path_components):
        if component != '':
            return component
    raise(NameError('Could not find user name for this system'))