'''
Handles any and all interaction with the server data and/or files.
'''

import shutil
from util.syslog import log
import os
from zipfile import ZipFile

def install_datapack(path: str):
    '''
    This method installs a datapack to the server. It handles:
    - A directory with multiple compressed datapacks
    - A compressed datapack
    - An uncompressed datapack
    '''

    this_dir = os.path.dirname(__file__)
    install_dir = os.path.join(this_dir, '../server/world/datapacks')
    last_path_component = os.path.basename(os.path.normpath(path))

    if os.path.isdir(path):
        contents = os.listdir(path)
        for file in contents:
            if '.mcmeta' in file:
                install_path = f'{install_dir}/{last_path_component}'

                shutil.copytree(path, install_path)
                __remove(path)
                break
            if '.zip' in file:
                print('possible compressed datapack; extract and confirm contents before moving')
                dir_name = file.replace('.zip', '')
                file_path = f'{path}/{file}'
                zip_path = f'{path}/{dir_name}'

                __extract(file_path, zip_path)
                install_datapack(zip_path)
        else:
            log(f'{path} is not a valid datapack!')
            return
    if os.path.isfile(path) and path.endswith('.zip'):
        print('possible compressed datapack; extract and confirm contents before moving')
        unzip_path = path.replace(f'/{last_path_component}', '')
        dir_name = last_path_component.replace('.zip', '')
        dir_path = f'{unzip_path}/{dir_name}'

        __extract(path, dir_path)
        install_datapack(dir_path)

def __remove(file_at_path: str):
    print('remove')

def __extract(zip_file: str, to_path: str):
    with ZipFile(zip_file, 'r') as file:
        file.extractall(to_path)
