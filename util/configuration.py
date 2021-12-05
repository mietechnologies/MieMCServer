import os
import yaml
from .cron import CronDate

class File:
    __util_dir = os.path.dirname(__file__)
    __root_dir = os.path.join(__util_dir, "..")
    __file_dir = os.path.join(__root_dir, "config.yml")
    if os.path.exists(__file_dir):
        __file = open(__file_dir, "r")
        data = yaml.load(__file, yaml.Loader)
    else:
        data = {}

    exists = os.path.isfile(__file_dir)

    @classmethod
    def update(cls, section, update):
        with open(cls.__file_dir, "w") as file:
            cls.data[section] = update
            yaml.dump(cls.data, file, default_flow_style=False)

    @classmethod
    def generate(cls):
        Minecraft.reset()
        Email.reset()
        Maintenance.reset()

        if os.path.exists(cls.__file_dir):
            os.remove(cls.__file_dir)
        
        Minecraft.update()
        Email.update()
        Maintenance.update()

    @classmethod
    def build(cls):
        # TODO: Flesh Out
        # print("I will ask a series of questions to build your config.yml")
        # ram = int(input("How much ram would you like your Minecraft Server to " \
        #     "have? (your input will be mb) "))
        # version_str = input("What version would you like to install? [#.##.#] ")
        # should_update = bool(input("Would you like to allow major updates? [y/n] "))
        # email_address = input("What gmail address would you like use to send " \
        #     "your logs and reports from? ")
        # password = input("What is the password to the email provided? ")
        # recipient = input("What email address(es) would you like to recieve " \
        #     "the logs and reports? (If inputting multiple, seperate with a ', ') ")
        # recipients = recipient.split(", ")
        # version_split = version_str.split(".")
        # config = {
        #     "Minecraft" : {
        #         "allocated_ram" : ram,
        #         "allow_major_update" : should_update,
        #         "major" : int(version_split[0]),
        #         "minor": int(version_split[1]),
        #         "patch" : int(version_split[2]),
        #         "version_group" : ".".join([version_split[0], version_split[1]])
        #     },
        #     "Email" : {
        #         "address" : email_address,
        #         "password" : password,
        #         "server" : "smtp.gmail.com",
        #         "port" : 587,
        #         "recipients" : recipients
        #     }
        # }

        os.remove(cls.__file_dir)
        file = open(cls.__file_dir, "w")
        yaml.dump(config, file, default_flow_style=False)

class Minecraft:
    SECTION_NAME = "Minecraft"
    __data = File.data.get("Minecraft", {})
    __version = __data.get("version", {})
    allocated_ram = int(__data.get("allocated_ram", 1024))
    major = __version.get("major", None)
    minor = __version.get("minor", None)
    patch = __version.get("patch", None)
    build = __version.get("build", None)
    install_date = __version.get("install_date", "")
    version_group = __version.get("version_group", None)

    @classmethod
    def version_str(cls):
        if cls.patch is None:
            return "{}.{}:{}".format(cls.major, cls.minor, cls.build)
        else:
            return "{}.{}.{}:{}".format(cls.major, cls.minor, cls.patch, cls.build)

    @classmethod
    def update(cls):
        cls.__version["major"] = cls.major
        cls.__version["minor"] = cls.minor
        cls.__version["patch"] = cls.patch
        cls.__version["build"] = cls.build
        cls.__version["install_date"] = cls.install_date
        cls.__version["version_group"] = cls.version_group
        cls.__data["allocated_ram"] = cls.allocated_ram
        cls.__data["version"] = cls.__version
        File.update(cls.SECTION_NAME, cls.__data)

    @classmethod
    def reset(cls):
        cls.allocated_ram = 1024
        cls.major = None
        cls.minor = None
        cls.patch = None
        cls.build = None
        cls.install_date = ""
        cls.version_group = None


class Email:
    SECTION_NAME = "Email"
    __data = File.data.get("Email", {})
    address = __data.get("address", "<your.email@gmail.com>")
    password = __data.get("password", "<your password>")
    server = __data.get("server", "smtp.gmail.com")
    port = __data.get("port", 587)
    recipients = __data.get("recipients", [])

    @classmethod
    def update(cls):
        cls.__data["address"] = cls.address
        cls.__data["password"] = cls.password
        cls.__data["server"] = cls.server
        cls.__data["port"] = cls.port
        cls.__data["recipients"] = cls.recipients
        File.update(cls.SECTION_NAME, cls.__data)

    @classmethod
    def reset(cls):
        cls.address = "<your.email@gmail.com>"
        cls.password = "<your password>"
        cls.server = "smtp.gmail.com"
        cls.port = 587
        cls.recipients = []


class Maintenance:
    SECTION_NAME = "Maintenance"
    __data = File.data.get("Maintenance")
    __backup = __data.get("backup", {})
    __update = __data.get("update", {})
    complete_shutdown = __data.get("complete_shutdown", "")
    schedule = __data.get("schedule", "")
    backup_schedule = __backup.get("schedule", "")
    backup_path = __backup.get("path", "")
    backup_number = __backup.get("number", 1)
    update_schedule = __update.get("schedule", "")
    update_allow_major_update = __update.get("allow_major_update", False)

    @classmethod
    def update(cls):
        cls.__backup["schedule"] = cls.backup_schedule
        cls.__backup["path"] = cls.backup_path
        cls.__backup["number"] = cls.backup_number
        cls.__update["schedule"] = cls.update_schedule
        cls.__update["allow_major_update"] = cls.update_allow_major_update
        cls.__data["complete_shutdown"] = cls.complete_shutdown
        cls.__data["schedule"] = cls.schedule
        cls.__data["backup"] = cls.__backup
        cls.__data["update"] = cls.__update
        File.update(cls.SECTION_NAME, cls.__data)

    @classmethod
    def reset(cls):
        cls.complete_shutdown = ""
        cls.schedule = ""
        cls.backup_schedule = ""
        cls.backup_path = "~/MC_Backups"
        cls.backup_number = 1
        cls.update_schedule = ""
        cls.update_allow_major_update = False