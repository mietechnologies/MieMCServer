'''
Handles all functionality related to backing up the user's Minecraft server
(off-site and local).
'''

from base64 import decodebytes
import os
from typing import Tuple
from zipfile import ZipFile, ZIP_DEFLATED
import paramiko
from paramiko import SSHException
import pysftp

from .configuration import Maintenance
from .emailer import Emailer
from .extension import decode
from .syslog import log

class Backup:
    @classmethod
    def put(cls, source: str, path: str, file: str):
        '''
        The public-facing method that starts the backup process.
        '''

        cls.__local_backup(source, path, file)
        cls.__offsite_backup(path, file)

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
    def __connect(cls) -> Tuple[pysftp.Connection, str]:
        '''
        Handles connections to a file server using the information stored in the
        user's config.
        '''

        exception = None
        server = Maintenance.backup_file_server
        external_domain = server.get('domain')
        external_key = server.get('key')
        external_password = decode(server.get('password'))
        external_path = server.get('path')
        external_username = server.get('username')
        if external_domain is None:
            exception = 'File server domain is missing!'
        if external_key is None:
            exception = 'File server key is missing!'
        if external_password is None:
            exception = 'File server password is missing!'
        if external_path is None:
            exception = 'File server path is missing!'
        if external_username is None:
            exception = 'File server username is missing!'

        if exception:
            log(f'ERROR: { exception }')
            return (None, None)

        try:
            keydata = decode(external_key)
            key = paramiko.RSAKey(data=decodebytes(keydata))
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys.add(external_domain, 'ssh-rsa', key)
            try:
                connection = pysftp.Connection(
                    host=external_domain,
                    username=external_username,
                    password=external_password,
                    cnopts=cnopts
                )
                return (connection, external_path)
            except SSHException as exc:
                exception = exc
        except SSHException as exc:
            exception = exc

        # If an exception was encountered, send the admins an email
        if exception:
            message = 'Hey, there! I was unable to connect to your file ' \
                f'server: { exception }\n\nThanks,\nMIE-MCServer'
            Emailer('Unable to connect to your file server', message).send()

        return (None, None)

    @classmethod
    def __offsite_backup(cls, path: str, file: str):
        '''
        Handles uploading files to either an external harddrive attached to the
        system or a separate file server.
        '''

        # I had originally considered also allowing the user to back up their
        # data to an additional external hard drive, but that now seems very 
        # redundant. If the user wishes to use an external HD, they can simply
        # use the Maintenance.backup.path config item.
        (sftp, external_path) = cls.__connect()
        if sftp is not None and external_path is not None:
            log('Uploading to offsite storage...')
            # Create the path to the file on the file server
            normalized_path = sftp.normalize(external_path.replace('~', '.'))
            if cls.__create_server_dir_if_needed(sftp, external_path):
                external_file_path = f'{normalized_path}/{file}'

                # Create the path to the local file
                expanded_path = os.path.expanduser(path)
                file_path = f'{expanded_path}/{file}'

                # Upload and clean
                # Because we are creating the path on the server directly before
                # attempting to upload the file, there is no way this can throw an
                # exception!
                sftp.put(file_path, external_file_path)
                cls.__server_clean(sftp, normalized_path)
                sftp.close()

    @classmethod
    def __server_clean(cls, sftp: pysftp.Connection, path: str):
        '''
        Removes extraneous files from the server based upon the user's stored
        config value.
        '''

        existing = [x.filename for x in sorted(sftp.listdir_attr(path), key = lambda f: f.st_mtime)]
        if len(existing) > Maintenance.backup_number:
            log('Cleaning up file server storage...')
            to_delete = []

            while len(existing) > Maintenance.backup_number:
                to_delete.append(existing.pop(0))

            errors = []
            for file in to_delete:
                try:
                    sftp.remove(f'{path}/{file}')
                except IOError as err:
                    errors.append(f'Unable to delete {file}: {err}')

            log(f'Deleted {len(to_delete)} files from file server storage!')

            # Send any encountered errors to the admins in an email
            if len(errors) > 0:
                joined_errors = '\n'.join(errors)
                err_msg = 'Hey, there!\n\nI was unable to delete some old ' \
                    'backups on your file server! More info below:\n' \
                    f'{ joined_errors }\n\nThanks,\nMIE-MCServer'
                Emailer('Unable to clean up server backups', err_msg).send()

    @classmethod
    def __create_server_dir_if_needed(cls, sftp: pysftp.Connection, path: str):
        '''
        Creates a directory at the passed path if it doesn't exist.
        '''

        # Pysftp doesn't handle home path notation correctly (even when using
        # .normalize(path)), so we're replacing any instance of '~/' with the
        # current working directory (which should always be the user's home path
        # (as we never change it)).
        if '~/' in path:
            path = path.replace('~/', f'{sftp.pwd}/')

        if not sftp.exists(path):
            log(f'Backup directory {path} does not exist! Creating...')
            try:
                sftp.makedirs(path)
            except OSError as err:
                message = 'Hey, there!\n\nI was unable to find or create the ' \
                    'directory you want to save your backups to on your file ' \
                    f'server: { err }\n\nThanks,\nMIE-MCServer'
                Emailer('Unable to save backup to server', message).send()
                return False
        return True
