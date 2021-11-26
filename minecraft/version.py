import sys, os, requests
sys.path.append("..")
from util.configuration import Minecraft
from util.syslog import log
from util.date import Date
from enum import Enum

class UpdateType(Enum):
    NONE = 0
    MAJOR = 1
    MINOR = 2
    BUILD = 3

    def __str__(self) -> str:
        if self is UpdateType.NONE:
            return "None"
        elif self is UpdateType.MAJOR:
            return "Major"
        elif self is UpdateType.MINOR:
            return "Minor"
        elif self is UpdateType.BUILD:
            return "Build"


class Versioner:
    VERSION_MANIFEST_URL = "https://papermc.io/api/v2/projects/paper/{}"
    BUILDS_MANIFEST_URL = "https://papermc.io/api/v2/projects/paper/version_group/{}/builds"

    dir = os.path.dirname(__file__)
    server_root = os.path.join(dir, 'server')
    changelog = os.path.join(server_root, 'changelog.txt')
    version_log = os.path.join(server_root, 'versionlog.txt')

    @staticmethod
    def versionString(version):
        '''Converts a version dictionary into a string.'''
        version_str = ""
        if version["patch"] is None:
            version_str = ".".join(version["major"], version["minor"])
            version_str = ":".join(version_str, version["build"])
        else:
            version_str = ".".join(version["major"], version["minor"], version["patch"])
            version_str = ":".join(version_str, version["build"])
        return version_str

    @classmethod
    def __checkForErrors(cls, json):
        '''Check JSON returned from the Paper API for errors'''
        if 'error' in json.keys():
            return {"error" : json["error"]}
        else:
            return None

    @classmethod
    def __extractAbsoluteVersion(cls, json):
        '''Check for the latest version and group when no version group is
        passed to the Paper API'''
        error_check = cls.__checkForErrors(json)
        if error_check is not None:
            return error_check
        else:
            latest_version_group = json["version_groups"][-1]
            latest_version = json["versions"][-1]
            return {
                "version_group" : latest_version_group,
                "version" : latest_version
            }

    @classmethod
    def __extractVersionGroup(cls, json):
        '''Gets the latest version and group from the returned JSON from the
        Paper API'''
        error_check = cls.__checkForErrors(json)
        if error_check is not None:
            return error_check
        else:
            version_group = json["version_group"]
            latest_version = json["versions"][-1]
            return {
                "version_group" : version_group,
                "version" : latest_version
            }

    @classmethod
    def __extractLatestBuild(cls, json):
        '''Check for the latest build from the returned JSON from the Paper
        API'''
        error_check = cls.__checkForErrors(json)
        if error_check is not None:
            return error_check
        else:
            latest_build = json["builds"][-1]
            downloads = latest_build["downloads"]
            application = downloads["application"]

            version = latest_build["version"]
            build = int(latest_build["build"])
            filename = application["name"]
            return {
                "version" : version,
                "build" : build,
                "filename" : filename
            }

    @classmethod
    def getCurrentVersion(cls):
        '''Checks to see if a version has been set in the configuration. If it 
        has it will return the version information, otherwise it will return
        None'''

        if Minecraft.minor is None:
            return None
        else:
            return {
                "major" : Minecraft.major,
                "minor" : Minecraft.minor,
                "patch" : Minecraft.patch,
                "build" : Minecraft.build,
                "version_group" : Minecraft.version_group
            }

    @classmethod
    def __getLatestVersion(cls):
        '''Hits the Paper API to receive what the latest build is. If the user
        has specified whether they want to update minor builds will determine 
        how far this function will look'''

        if Minecraft.version_group is None or Minecraft.allow_major_update:
            version_request = requests.get(cls.VERSION_MANIFEST_URL.format(""))
            data = cls.__extractAbsoluteVersion(version_request.json())
            build_data = cls.__getLatestBuild(data["version_group"])
            return cls.__version(data, build_data)
        else:
            version_request = requests.get(cls.VERSION_MANIFEST_URL
                .format("version_group/" + Minecraft.version_group))
            data = cls.__extractVersionGroup(version_request.json())
            build_data = cls.__getLatestBuild(data["version_group"])
            return cls.__version(data, build_data)

    @classmethod
    def __getLatestBuild(cls, version_group):
        '''Gets the latest build number for a given version group'''
        build_request = requests.get(cls.BUILDS_MANIFEST_URL
            .format(version_group))
        build_data = cls.__extractLatestBuild(build_request.json())
        return build_data

    @classmethod
    def __version(cls, version_dict, build_dict):
        '''Combines a build and version group dictionaries into a single 
        dictionary'''
        version_split = version_dict["version"].split(".")
        major = version_split[0]
        minor = version_split[1]
        patch = None
        if len(version_split) > 2:
            patch = version_split[2]
        return {
            "major" : major,
            "minor" : minor,
            "patch" : patch,
            "build" : build_dict["build"],
            "version_group" : version_dict["version_group"]
        }

    @classmethod
    def hasUpdate(cls):
        '''Determines the type of update there is for the currently installed
        server. If there is an update, this function will return the type and
        the new version. If no update is found, it will return the NONE type
        and a NoneType object.'''
        current_version = cls.getCurrentVersion()
        latest_version = cls.__getLatestVersion()

        log("Checking for an update...")
        # Version Group
        if current_version["version_group"] is None:
            return (UpdateType.MAJOR, latest_version)
        # Major
        major_check = current_version["major"] is not None
        if major_check and int(current_version["major"]) < int(latest_version["major"]):
            return (UpdateType.MAJOR, latest_version)
        # Minor
        minor_check = current_version["minor"] is not None
        if minor_check and int(current_version["minor"]) < int(latest_version["minor"]):
            return (UpdateType.MAJOR, latest_version)
        # Patch
        patch_check = current_version["patch"] is None
        if patch_check or int(current_version["patch"]) < int(latest_version["patch"]):
            return (UpdateType.MINOR, latest_version)
        # Build
        build_check = current_version["build"] is None
        if build_check or int(current_version["build"]) < int(latest_version["build"]):
            return (UpdateType.BUILD, latest_version)

        log("No update found.")
        return (UpdateType.NONE, None)

    @classmethod
    def serverExists(cls):
        '''Checks if there is a server directory. If there is, a server has been
        isntalled. If not, then no server has been installed'''
        if os.path.exists(cls.server_root) == False:
            return False
        else:
            return True

    @classmethod
    def updateInstalledVersion(cls, version):
        """Update all appropriate files of a new server install
        
        Keyword arguments:
            version -- A dictionary containing the keys: major, minor, patch, build, and version_group.
        """
        install_date = Date.timestamp()
        update_dict = version
        update_dict["install_date"] = install_date
        Minecraft.update(update_dict)
        