'''
Handles all functionality related to backing up the user's Minecraft server
(off-site and local).
'''
    
from base64 import decodebytes
import os
import paramiko
import pysftp
import re
import shutil

from zipfile import ZipFile, ZIP_DEFLATED

from .. import command as cmd
from .configuration import Maintenance
from .syslog import log

class Backup:
    @classmethod
    def put(cls, source: str, path: str, file: str):
        '''
        The public-facing method that starts the backup process.
        '''

        cmd.runCommand('say Backing up the current world...')
        log('Backing up the current world...')
        cls.__local_backup(source, path, file)

    ###### Local backups ######
    @classmethod
    def __local_backup(cls, source: str, path: str, file: str):
        '''
        Archives all files and folders in the source directory into the file
        provided, placing the created file at the designated path.
        '''
        path = os.path.expanduser(path)
        zipfile = f'{path}/{file}'

        # SANITY CHECK: User could have:
        # - Ran backup for the first time
        # - Changed directory in config
        # - Deleted directory
        # So, if the directory doesn't exist, make it
        if not os.path.isdir(path):
            os.mkdir(path)

        # Archive all files in the source directory
        # TODO: I'm not sure if this actually compresses the file or just zips 
        # them but we should check into it in the future. For now, it gets the 
        # job done.
        with ZipFile(zipfile, 'w', ZIP_DEFLATED) as zip:
            for root, _, files in os.walk(source):
                for file_to_zip in files:
                    zip.write(
                        os.path.join(root, file_to_zip), 
                        os.path.relpath(os.path.join(root, file_to_zip), 
                        os.path.join(source, '..')))

        log("Finished creating local backup!")
        # Clean up, if needed
        cls.__local_clean(path)

    @classmethod
    def __local_clean(cls, path: str):
        '''
        Removes a number of the oldest files in the designated directory
        according to the user's designation under Maintenance.backup.number in
        config.yml.
        '''
        # List the contents of the directory and compare to settings. If number 
        # of files in the directory is greater than what is in the settings, 
        # delete oldest files. If lesser than or eqaul, do nothing.
        existing_relative = os.listdir(path)
        if len(existing_relative) > Maintenance.backup_number:
            log('Cleaning up local storage...')
            existing = []
            to_delete = []

            # listdir gives the file name (relative path) so we need to 
            # construct the correct path to the file so we can appropriately 
            # sort, compare, and delete
            for relative in existing_relative:
                existing.append(f'{path}/{relative}')

            # Sort files oldest to newest
            existing.sort(key=os.path.getctime)

            # Iterate through files popping the oldest to the to_delete array
            while len(existing) > Maintenance.backup_number:
                to_delete.append(existing.pop(0))

            # Delete any files in the toDelete array
            for file in to_delete:
                os.remove(file)

            log(f'Deleted {len(to_delete)} files from local storage!')

    ###### Offsite backups ######
    @classmethod
    def __offsite_bcakup(cls, path: str, file: str):
        '''
        Handles uploading files to either an external harddrive attached to the
        system or a separate file server.
        '''

        # offsite_path = Maintenance.backup_external_path
        # if re.fullmatch(r'[a-zA-Z]+@.+:.+', offsite_path):
        #     # External path is a file server
        #     # Like: bachapin@mieserver.ddns.net:~/backups
        #     # Like: pi@192.168.1.3:~/backups
        #     print('file server')
        # elif re.fullmatch(r'^(?:\/[\d\s\w]+){1,}', offsite_path):
        #     # External path is an attached hard drive
        #     # Like: /Volumes/storage/dev
        #     print('attached drive')
        # else:
        #     # Invalid external path
        #     print('invalid path')

        if Maintenance.backup_external_drive != {}:
            print('backup to external file server')
            external_path = Maintenance.backup_external_drive.get('path')
            if external_path is None:
                log('ERROR: External drive backups not properly configured!')
                return

        if Maintenance.backup_file_server != {}:
            print('backup to external file server')
            external_domain = Maintenance.backup_file_server.get('domain')
            external_key = Maintenance.backup_file_server.get('key')
            external_password = Maintenance.backup_file_server.get('password')
            external_path = Maintenance.backup_file_server.get('path')
            external_username = Maintenance.backup_file_server.get('username')
            if external_domain is None:
                log('ERROR: File server domain is missing!')
                return
            if external_key is None:
                log('ERROR: File server key is missing!')
                return
            if external_password is None:
                log('ERROR: File server password is missing!')
                return
            if external_path is None:
                log('ERROR: File server path is missing!')
                return
            if external_username is None:
                log('ERROR: File server username is missing!')
                return

            log('Uploading to file server...')
            server_dir = os.path.expanduser(external_path)
            
            keydata = f'{external_key}'.encode('utf-8')
            key = paramiko.RSAKey(data=decodebytes(keydata))
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys.add(external_domain, 'ssh-rsa', key)

            with pysftp.Connection(
                external_domain,
                external_username,
                key,
                external_password) as sftp:
                cls.__create_server_dir_if_needed(sftp, external_path)
                external_file_path = f'{external_path}/{file}'
                file_path = f'{path}/{file}'
                sftp.put(file_path, external_file_path)
                cls.__server_clean(sftp, server_dir)

    @classmethod
    def __server_clean(cls, sftp, path):
        print('')

    @classmethod
    def __create_server_dir_if_needed(cls, sftp, path):
        print('')
