import os, sys, requests
from re import sub
from .version import UpdateType, Versioner
sys.path.append("..")
from util.configuration import Email, Minecraft
from util.emailer import Emailer
from util.syslog import log
from util.date import Date

class Installer:
    DOWNLOAD_URL = "https://papermc.io/api/v2/projects/paper/versions/{}/" \
        "builds/{}/downloads/{}"

    dir = os.path.dirname(__file__)
    server_dir = os.path.join(dir, '../server')
    server_jar = os.path.join(server_dir, 'paper.jar')
    temp_jar = os.path.join(dir, 'paper.jar')

    def __shouldInstall(self, override):
        type, version = Versioner.hasUpdate()
        if type is UpdateType.MAJOR and not Minecraft.allow_major_update:
            self.__adminUpdateAlert(version)

        if type is not UpdateType.NONE and override:
            return (True, version)

        if type is UpdateType.BUILD or type is UpdateType.MINOR:
            return (True, version)
        elif type is UpdateType.MAJOR and not Versioner.serverExists():
            return (True, version)
        elif type is UpdateType.MAJOR and Minecraft.allow_major_update:
            return (True, version)
        else:
            return (False, None)

    def __adminUpdateAlert(self, version):
        version_str = Versioner.versionString(version)
        
        subject = "Minecraft Server has an update!"
        body = "Hello there,\n\nIt would seem as if your server has an " \
            "update waiting to be downloaded and installed. Due to your " \
            "settings, I can't do this update automatically.\n\nThe " \
            "new version of Minecraft Server is {}\n\nIf you would like " \
            "to do this manually you can run the command: 'python3 " \
            "main.py -u'\nThen follow the prompt and it will install the " \
            "latest version.\n\nThanks,\nMinePi".format(version_str)
        email = Emailer(subject, body)
        email.send()

    def install(self, override_settings = False):
        should_install, version = self.__shouldInstall(override_settings)
        if should_install:
            version_str = Versioner.versionString(version)
            log("Downloading {}...".format(version_str))
            download = self.__download(version)

            log("Installing new server...")
            if os.path.isdir(self.server_dir) == False:
                os.mkdir(self.server_dir)
            os.replace(download, self.server_jar)


    def __download(self, version):
        version_str = ""
        if version["patch"] is None:
            version_str = ".".join(version["major"], version["minor"])
        else:
            version_str = ".".join(version["major"], version["minor"],
                version["patch"])

        filename = "paper-{}-{}.jar".format(version_str, version["build"])
        url = self.DOWNLOAD_URL.format(version_str, version["build"], filename)
        with requests.get(url, stream=True) as request:
            request.raise_for_status()
            with open(self.temp_jar, 'wb') as file:
                for chunk in request.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                    else:
                        log("Error: Unable to download file!")
                        return None

        log("Download Complete!")
        return self.temp_jar
