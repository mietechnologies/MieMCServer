import os
import sys
import requests

sys.path.append("..")
from enum import Enum

from util.date import Date

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

    __configuration = None
    __log = None

    dir = os.path.dirname(__file__)
    server_root = os.path.join(dir, 'server')
    changelog = os.path.join(server_root, 'changelog.txt')
    version_log = os.path.join(server_root, 'versionlog.txt')

    @classmethod
    def __init__(cls, configuration, logger):
        cls.__configuration = configuration
        cls.__log = logger

    @staticmethod
    def version_string(version):
        '''Converts a version dictionary into a string.'''
        version_str = ""
        if version["patch"] is None:
            version_str = ".".join([version["major"], version["minor"]])
            version_str = ":".join([version_str, str(version["build"])])
        else:
            version_str = ".".join([version["major"], version["minor"], version["patch"]])
            version_str = ":".join([version_str, str(version["build"])])
        return version_str

    @classmethod
    def __check_for_errors(cls, json):
        '''Check JSON returned from the Paper API for errors'''
        if 'error' in json.keys():
            return {"error" : json["error"]}
        return None

    @classmethod
    def __extract_absolute_version(cls, json):
        '''Check for the latest version and group when no version group is
        passed to the Paper API'''
        error_check = cls.__check_for_errors(json)
        if error_check is not None:
            return error_check
        latest_version_group = json["version_groups"][-1]
        latest_version = json["versions"][-1]
        return {
            "version_group" : latest_version_group,
            "version" : latest_version
        }

    @classmethod
    def __extract_version_group(cls, json):
        '''Gets the latest version and group from the returned JSON from the
        Paper API'''
        error_check = cls.__check_for_errors(json)
        if error_check is not None:
            return error_check
        version_group = json["version_group"]
        latest_version = json["versions"][-1]
        return {
            "version_group" : version_group,
            "version" : latest_version
        }

    @classmethod
    def __extract_latest_build(cls, json):
        '''Check for the latest build from the returned JSON from the Paper
        API'''
        error_check = cls.__check_for_errors(json)
        if error_check is not None:
            return error_check
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
    def get_current_version(cls):
        '''Checks to see if a version has been set in the configuration. If it 
        has it will return the version information, otherwise it will return
        None'''
        if cls.__configuration.minecraft.minor is None:
            return None
        return {
            "major" : cls.__configuration.minecraft.major,
            "minor" : cls.__configuration.minecraft.minor,
            "patch" : cls.__configuration.minecraft.patch,
            "build" : cls.__configuration.minecraft.build,
            "version_group" : cls.__configuration.minecraft.version_group
        }

    @classmethod
    def __get_latest_version(cls):
        '''Hits the Paper API to receive what the latest build is. If the user
        has specified whether they want to update minor builds will determine
        how far this function will look'''

        version_group = cls.__configuration.minecraft.version_group
        allows_major_updates = cls.__configuration.maintenance.allows_major_udpates()

        url_format = ''
        if version_group is None or allows_major_updates:
            url_format = ''
        else:
            url_format = f'version_group/{cls.__configuration.minecraft.version_group}'

        try:
            version_request = requests.get(cls.VERSION_MANIFEST_URL.format(url_format))
            if version_group is None or allows_major_updates:
                data = cls.__extract_absolute_version(version_request.json())
                build_data = cls.__get_latest_build(data["version_group"])
                return cls.__version(data, build_data)
            data = cls.__extract_version_group(version_request.json())
            build_data = cls.__get_latest_build(data["version_group"])
            return cls.__version(data, build_data)
        except:
            return None

    @classmethod
    def __get_latest_build(cls, version_group):
        '''Gets the latest build number for a given version group'''
        build_request = requests.get(cls.BUILDS_MANIFEST_URL
            .format(version_group))
        build_data = cls.__extract_latest_build(build_request.json())
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
    def has_update(cls):
        '''Determines the type of update there is for the currently installed
        server. If there is an update, this function will return the type and
        the new version. If no update is found, it will return the NONE type
        and a NoneType object.'''
        current_version = cls.get_current_version()
        latest_version = cls.__get_latest_version()

        if latest_version is None:
            return (UpdateType.NONE, None)

        cls.__log("Checking for an update...")
        if current_version is None:
            return (UpdateType.MAJOR, latest_version)
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

        cls.__log("No update found.")
        return (UpdateType.NONE, None)

    @classmethod
    def server_exists(cls):
        '''Checks if there is a server directory. If there is, a server has been
        isntalled. If not, then no server has been installed'''
        return os.path.exists(cls.server_root)

    @classmethod
    def update_installed_version(cls, version: dict) -> dict:
        """Update all appropriate files of a new server install

        Parameters:
            version -- A dictionary containing the keys: major, minor, patch, build, and 
            version_group.
        """

        minecraft_congig = cls.__configuration.minecraft
        minecraft_congig.install_date = Date.timestamp()
        minecraft_congig.major = int(version.get("major", minecraft_congig.major))
        minecraft_congig.minor = int(version.get("minor", minecraft_congig.minor))
        minecraft_congig.patch = int(version.get("patch", minecraft_congig.patch))
        minecraft_congig.build = int(version.get("build", minecraft_congig.build))
        minecraft_congig.version_group = version.get(
            "version_group",
            minecraft_congig.version_group
        )
        return minecraft_congig.update()
        