'''
Handles any and all interaction with the server data and/or files.
'''

import shutil
from zipfile import ZipFile
import os
from util.logger import log
from util.mielib import custominput as ci

__DATAPACKS_TO_INSTALL = []
__DATAPACKS_INSTALLED = []

def install_datapack(path: str):
    '''
    This method installs a datapack to the server given a path to it. It 
    handles:
    - An directory containing an uncompressed datapack
    - A directory containing multiple compressed datapacks
    - A compressed datapack
    '''

    this_dir = os.path.dirname(__file__)
    install_dir = os.path.join(this_dir, '../server/world/datapacks')
    last_path_component = os.path.basename(os.path.normpath(path))

    if os.path.isdir(path):
        # Given path is a directory; directory might be either an uncompressed
        # datapack or contain a collection of compressed datapacks
        contents = os.listdir(path)
        for file in contents:
            if '.mcmeta' in file:
                # Given path is a directory that contains an uncompressed
                # datapack; should copy parent to install_dir
                install_path = f'{install_dir}/{last_path_component}'

                try:
                    shutil.copytree(path, install_path)
                    __remove(path)
                except FileExistsError:
                    log(f'{last_path_component} has already been installed!')
            if '.zip' in file:
                # Given path is a directory that contains one or more compressed
                # datapacks; should extract and confirm contents before moving
                # to install_dir
                log(f'Extracting {file} before installing...')
                dir_name = file.replace('.zip', '')
                file_path = f'{path}/{file}'
                zip_path = f'{path}/{dir_name}'

                __extract(file_path, zip_path)
                install_datapack(zip_path)
                __remove(file_path)
    if os.path.isfile(path) and path.endswith('.zip'):
        # Given path is a zip file; should extract and confirm contents before
        # moving to install_dir
        log(f'Extracting {last_path_component} before installing...')
        unzip_path = path.replace(f'/{last_path_component}', '')
        dir_name = last_path_component.replace('.zip', '')
        dir_path = f'{unzip_path}/{dir_name}'

        __extract(path, dir_path)
        install_datapack(dir_path)
        __remove(path)

def __remove(file_at_path: str):
    # Ask user to confirm deletion of file/directory
    # If user grants permission, remove file/directory
    should_delete = ci.bool_input(f'{file_at_path} is no longer needed. ' \
        'Should I delete it?', True)
    if should_delete:
        try:
            os.remove(file_at_path)
        except PermissionError:
            log(f'WARNING: Unable to remove {file_at_path}. Please remove it ' \
                'manually.')

def __extract(zip_file: str, to_path: str):
    with ZipFile(zip_file, 'r') as file:
        file.extractall(to_path)
