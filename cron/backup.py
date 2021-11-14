import os
import sys
import time
import zipfile

sys.path.append('../')

from minecraft.version import Versioner

if __name__ == '__main__':
    # message the server to say that the server will be shutting down temporarily to back up
    os.popen('say MinePi will shut down this server in 5 minutes to back up the server. Please be patient.')
    # sleep for 5 minutes then shut down the server
    time.sleep(300)
    os.popen('stop')
    # gzip server world into new file using version as file name
    versioner = Versioner()
    currentVersion = versioner.currentVersion()
    path = versioner.fetchVersionDirectory(currentVersion)
    
    root = os.path.dirname(__file__)
    print(root)
    backups = os.path.join(root, '../minecraft/server/backups')
    print(backups)
    if not os.path.isdir(backups):
        os.mkdir(backups)
    
    # Compress server in /hackups directory
    zipName = '{}/{}.zip'.format(backups, currentVersion)
    zip = zipfile.ZipFile(zipName, 'w', zipfile.ZIP_DEFLATED)
    for root, dir, files in os.walk(path):
        for file in files:
            if 'server' not in file:
                zip.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))
    zip.close()
    
    # restart server
    os.popen('cd ..')
    os.popen('python start.py')