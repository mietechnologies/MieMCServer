import os
from zipfile import ZipFile, ZIP_DEFLATED
from configuration import config

class Backup:
    __configuration = None
    __log = None

    @classmethod
    def __init__(cls, configuration: config.File, logger):
        cls.__configuration = configuration
        cls.__log = logger

    @classmethod
    def put(cls, source: str, path: str, file: str):
        '''
        Starts the backup process.

        TODO: Add parameter info
        '''

        cls.__log('Backing up the current world...')
        cls.local_backup(source, path, file)

    @classmethod
    def local_backup(cls, source: str, path: str, file: str):
        '''
        Archives all files and folders in the source directory into the file provided, placing
        the created file at the designated path.

        TODO: Add parameter info
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
        # TODO: I'm not sure if this actually compresses the file or just zips them but we
        # should check into it in the future. For now, it gets the job done.
        with ZipFile(zipfile, 'w', ZIP_DEFLATED) as zip:
            for root, dirs, files in os.walk(source):
                for file in files:
                    zip.write(
                        os.path.join(root, file), 
                        os.path.relpath(os.path.join(root, file), 
                        os.path.join(source, '..')))

        cls.__log("Finished creating local backup!")
        # Clean up, if needed
        cls.local_clean(path)

    @classmethod
    def local_clean(cls, path: str):
        '''
        Removes a number of the oldest files in the designated directory according to the
        user's designation under Maintenance.backup.number in config.yml.

        TODO: Add parameter info
        '''
        # List the contents of the directory and compare to settings. If number of files in
        # the directory is greater than what is in the settings, delete oldest files. If
        # lesser than or eqaul, do nothing.
        existing_relative = os.listdir(path)
        if len(existing_relative) > cls.__configuration.maintenance.backup_limit():
            cls.__log('Cleaning up local storage...')
            existing = []
            to_delete = []

            # listdir gives the file name (relative path) so we need to construct the correct
            # path to the file so we can appropriately sort, compare, and delete
            for relative in existing_relative:
                existing.append(f'{path}/{relative}')

            # Sort files oldest to newest
            existing.sort(key=os.path.getctime)

            # Iterate through files popping the oldest to the toDelete array
            while len(existing) > cls.__configuration.maintenance.backup_limit():
                to_delete.append(existing.pop(0))

            # Delete any files in the toDelete array
            for file in to_delete:
                os.remove(file)

            cls.__log(f'Deleted {len(to_delete)} files from local storage!')
