import os
import sys
import requests
from .version import UpdateType, Versioner
sys.path.append("..")
from configuration import config
from util.download import get
from util.emailer import Mailer
from util.logger import log
from util.date import Date

class Installer:
    DOWNLOAD_URL = "https://papermc.io/api/v2/projects/paper/versions/{}/" \
        "builds/{}/downloads/{}"

    dir = os.path.dirname(__file__)
    server_dir = os.path.join(dir, '../server')
    server_jar = os.path.join(server_dir, 'paper.jar')
    temp_jar = os.path.join(dir, 'paper.jar')
    
    config_file = config.File()

    @classmethod
    def __shouldInstall(cls, override):
        type, version = Versioner.hasUpdate()

        if type is not UpdateType.NONE and override:
            return (True, version)

        if type is UpdateType.BUILD or type is UpdateType.MINOR:
            return (True, version)
        elif type is UpdateType.MAJOR:
            if not Versioner.serverExists():
                return (True, version)
            elif cls.config_file.maintenance.allows_major_udpates():
                return (True, version)
            else:
                cls.__adminUpdateAlert(version)
        else:
            return (False, None)

    @classmethod
    def __adminUpdateAlert(cls, version):
        version_str = Versioner.versionString(version)
        
        subject = "Minecraft Server has an update!"
        body = "Hello there,\n\nIt would seem as if your server has an " \
            "update waiting to be downloaded and installed. Due to your " \
            "settings, I can't do this update automatically.\n\nThe " \
            "new version of Minecraft Server is {}\n\nIf you would like " \
            "to do this manually you can run the command: 'python3 " \
            "main.py -u'\nThen follow the prompt and it will install the " \
            "latest version.\n\nThanks,\nMinePi".format(version_str)
        email = Mailer(subject, body)
        email.send()

    @classmethod
    def install(cls, override_settings = False):
        '''
        A method to download and install the most up to date version the user
        will allow.

        Parameters:
        override_settings (bool): This will override the user's saved setting
        in the configuration on where to limit the update version.
        '''
        should_install, version = cls.__shouldInstall(override_settings)
        if should_install:
            version_str = Versioner.versionString(version)
            log("Downloading {}...".format(version_str))
            download = cls.__download(version)

            log("Installing new server...")
            if os.path.isdir(cls.server_dir) == False:
                os.mkdir(cls.server_dir)
            os.replace(download, cls.server_jar)

            log("Server installed!")
            Versioner.updateInstalledVersion(version)

    @classmethod
    def __download(cls, version):
        version_str = ""
        if version["patch"] is None:
            version_str = ".".join([version["major"], version["minor"]])
        else:
            version_str = ".".join([version["major"], version["minor"],
                version["patch"]])

        filename = "paper-{}-{}.jar".format(version_str, version["build"])
        url = cls.DOWNLOAD_URL.format(version_str, version["build"], filename)
        return get(url, cls.temp_jar)
