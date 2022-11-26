import os
import sys
from .version import UpdateType, Versioner
sys.path.append("..")
from util.download import get
from util.emailer import Mailer

class Installer:
    DOWNLOAD_URL = "https://papermc.io/api/v2/projects/paper/versions/{}/" \
        "builds/{}/downloads/{}"

    dir = os.path.dirname(__file__)
    server_dir = os.path.join(dir, '../server')
    server_jar = os.path.join(server_dir, 'paper.jar')
    temp_jar = os.path.join(dir, 'paper.jar')

    __configuration = None
    __log = None
    __versioner: Versioner = None

    @classmethod
    def __init__(cls, configuration, logger):
        cls.__configuration = configuration
        cls.__log = logger
        cls.__versioner = Versioner(cls.__configuration, cls.__log)

    @classmethod
    def __should_install(cls, override):
        install_type, version = cls.__versioner.has_update()

        if install_type is not UpdateType.NONE and override:
            return (True, version)

        if install_type is UpdateType.BUILD or install_type is UpdateType.MINOR:
            return (True, version)

        if install_type is UpdateType.MAJOR:
            if not cls.__versioner.server_exists():
                return (True, version)

            if cls.__configuration.maintenance.allows_major_udpates():
                return (True, version)

            cls.__admin_update_alert(version)

        return (False, None)

    @classmethod
    def __admin_update_alert(cls, version):
        version_str = cls.__versioner.version_string(version)

        subject = "Minecraft Server has an update!"
        body = "Hello there,\n\nIt would seem as if your server has an " \
            "update waiting to be downloaded and installed. Due to your " \
            "settings, I can't do this update automatically.\n\nThe " \
            "new version of Minecraft Server is {}\n\nIf you would like " \
            "to do this manually you can run the command: 'python3 " \
            "main.py -u'\nThen follow the prompt and it will install the " \
            "latest version.\n\nThanks,\nMinePi".format(version_str)
        email = Mailer(subject, body, cls.__configuration)
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
        should_install, version = cls.__should_install(override_settings)
        if should_install:
            version_str = cls.__versioner.version_string(version)
            cls.__log(f"Downloading {version_str}...")
            download = cls.__download(version)

            cls.__log("Installing new server...")
            if os.path.isdir(cls.server_dir) is False:
                os.mkdir(cls.server_dir)
            os.replace(download, cls.server_jar)

            cls.__log("Server installed!")
            cls.__versioner.update_installed_version(version)

    @classmethod
    def __download(cls, version):
        version_str = ""
        if version["patch"] is None:
            version_str = ".".join([version["major"], version["minor"]])
        else:
            version_str = ".".join([version["major"], version["minor"],
                version["patch"]])

        filename = f"paper-{version_str}-{version['build']}.jar"
        url = cls.DOWNLOAD_URL.format(version_str, version["build"], filename)
        return get(url, cls.temp_jar)
