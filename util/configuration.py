from sys import version
import yaml
import os

class File:
    __util_dir = os.path.dirname(__file__)
    __root_dir = os.path.join(__util_dir, "..")
    __file_dir = os.path.join(__root_dir, "config.yml")
    if os.path.exists(__file_dir):
        __file = open(__file_dir, "r")
        data = yaml.load(__file)
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
        config = {
            "Minecraft" : {
                "allocated_ram" : 2048,
                "allow_major_update" : False
            },
            "Email" : {
                "address" : "<Your Email>@gmail.com",
                "password" : "<Your Password>",
                "server" : "smtp.gmail.com",
                "port" : 587,
                "recipients" : []
            }
        }
        if os.path.exists(cls.__file_dir):
            os.remove(cls.__file_dir)
        file = open(cls.__file_dir, "w")
        yaml.dump(config, file, default_flow_style=False)

    @classmethod
    def build(cls):
        # TODO: Flesh Out
        print("I will ask a series of questions to build your config.yml")
        ram = int(input("How much ram would you like your Minecraft Server to " \
            "have? (your input will be mb) "))
        version_str = input("What version would you like to install? [#.##.#] ")
        should_update = bool(input("Would you like to allow major updates? [y/n] "))
        email_address = input("What gmail address would you like use to send " \
            "your logs and reports from? ")
        password = input("What is the password to the email provided? ")
        recipient = input("What email address(es) would you like to recieve " \
            "the logs and reports? (If inputting multiple, seperate with a ', ') ")
        recipients = recipient.split(", ")
        version_split = version_str.split(".")
        config = {
            "Minecraft" : {
                "allocated_ram" : ram,
                "allow_major_update" : should_update,
                "major" : int(version_split[0]),
                "minor": int(version_split[1]),
                "patch" : int(version_split[2]),
                "version_group" : ".".join([version_split[0], version_split[1]])
            },
            "Email" : {
                "address" : email_address,
                "password" : password,
                "server" : "smtp.gmail.com",
                "port" : 587,
                "recipients" : recipients
            }
        }

        os.remove(cls.__file_dir)
        file = open(cls.__file_dir, "w")
        yaml.dump(config, file, default_flow_style=False)

class Minecraft:
    SECTION_NAME = "Minecraft"
    _data = File.data.get("Minecraft", {})
    allocated_ram = int(_data.get("allocated_ram", 0))
    major = _data.get("major", None)
    minor = _data.get("minor", None)
    patch = _data.get("patch", None)
    build = _data.get("build", None)
    install_date = _data.get("install_date", None)
    version_group = _data.get("version_group", None)
    allow_major_update = _data.get("allow_major_update", False)

    @classmethod
    def version_str(cls):
        return "{}.{}.{}:{}".format(cls.major, cls.minor, cls.patch, cls.build)

    @classmethod
    def update(cls):
        cls._data["allocated_ram"] = cls.allocated_ram
        cls._data["major"] = cls.major
        cls._data["minor"] = cls.minor
        cls._data["patch"] = cls.patch
        cls._data["build"] = cls.build
        cls._data["install_date"] = cls.install_date
        cls._data["version_group"] = cls.version_group
        cls._data["allow_major_update"] = cls.allow_major_update
        File.update(cls.SECTION_NAME, cls._data)

class Email:
    _data = File.data.get("Email", {})
    address = _data.get("address", None)
    password = _data.get("password", None)
    server = _data.get("server", None)
    port = _data.get("port", None)
    recipients = _data.get("recipients", None)
