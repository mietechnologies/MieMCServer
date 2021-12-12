import os, shutil
from zipfile import ZipFile, ZIP_DEFLATED

from .configuration import Maintenance
from .syslog import log

class Backup:
    @classmethod 
    def put(cls, source: str, path: str, file: str):
        log('Backing up the current world...')
        cls.localBackup(source, path, file)
        # TODO: If off-site storage is enabled...

    @classmethod
    def localBackup(cls, source: str, path: str, file: str):
        '''
        Archives all files and folders in the source directory into the file provided, placing the created 
        file at the designated path.
        '''
        path = os.path.expanduser(path)
        zipfile = '{}/{}'.format(path, file)

        # SANITY CHECK: User could have:
        # - Ran backup for the first time
        # - Changed directory in config
        # - Deleted directory
        # So, if the directory doesn't exist, make it
        if not os.path.isdir(path):
            os.mkdir(path)

        # Archive all files in the source directory
        # TODO: I'm not sure if this actually compresses the file or just zips them but we should check into
        # it in the future. For now, it gets the job done.
        with ZipFile(zipfile, 'w', ZIP_DEFLATED) as zip:
            for root, dirs, files in os.walk(source):
                for file in files:
                    zip.write(
                        os.path.join(root, file), 
                        os.path.relpath(os.path.join(root, file), 
                        os.path.join(source, '..')))

        log("Finished creating local backup!")
        # Clean up, if needed
        cls.localClean(path)

    @classmethod
    def localClean(cls, path: str):
        ''' 
        Removes a number of the oldest files in the designated directory according to the user's designation
        under Maintenance.backup.number in config.yml.
        '''
        # List the contents of the directory and compare to settings. If number of files in the directory is
        # greater than what is in the settings, delete oldest files. If lesser than or eqaul, do nothing.
        existingRelative = os.listdir(path)
        if len(existingRelative) > Maintenance.backup_number:
            log('Cleaning up local storage...')
            existing = []
            toDelete = []
            
            # listdir gives the file name (relative path) so we need to construct the correct path to the file
            # so we can appropriately sort, compare, and delete
            for r in existingRelative: 
                existing.append('{}/{}'.format(path, r))
            
            # Sort files oldest to newest
            existing.sort(key=os.path.getctime)

            # Iterate through files popping the oldest to the toDelete array
            while len(existing) > Maintenance.backup_number:
                toDelete.append(existing.pop(0))

            # Delete any files in the toDelete array
            for file in toDelete:
                os.remove(file)

            log('Deleted {} files from local storage!'.format(len(toDelete)))