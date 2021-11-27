import yaml, os

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
    __data = File.data.get("Minecraft", {})
    __version = File.data.get("version", {})
    allocated_ram = int(__data.get("allocated_ram", 0))
    major = __version.get("major", None)
    minor = __version.get("minor", None)
    patch = __version.get("patch", None)
    build = __version.get("build", None)
    install_date = __version.get("install_date", None)
    version_group = __version.get("version_group", None)

    @classmethod
    def version_str(cls):
        return "{}.{}.{}:{}".format(cls.major, cls.minor, cls.patch, cls.build)

    @classmethod
    def update(cls):
        cls.__data["allocated_ram"] = cls.allocated_ram
        cls.__data["major"] = cls.major
        cls.__data["minor"] = cls.minor
        cls.__data["patch"] = cls.patch
        cls.__data["build"] = cls.build
        cls.__data["install_date"] = cls.install_date
        cls.__data["version_group"] = cls.version_group
        File.update(cls.SECTION_NAME, cls.__data)


class Email:
    SECTION_NAME = "Email"
    __data = File.data.get("Email", {})
    address = __data.get("address", None)
    password = __data.get("password", None)
    server = __data.get("server", None)
    port = __data.get("port", None)
    recipients = __data.get("recipients", None)

    @classmethod
    def update(cls):
        cls.__data["address"] = cls.address
        cls.__data["password"] = cls.password
        cls.__data["server"] = cls.server
        cls.__data["port"] = cls.port
        cls.__data["recipients"] = cls.recipients
        File.update(cls.SECTION_NAME, cls.__data)


class Maintenance:
    SECTION_NAME = "Maintenance"
    __data = File.data.get("Maintenance")
    __backup = __data.get("backup", {})
    __update = __data.get("update", {})
    complete_shutdown = __data.get("complete_shutdown", "")
    schedule = __data.get("schedule", "")
    backup_schedule = __backup.get("schedule", None)
    backup_path = __backup.get("path", None)
    update_schedule = __update.get("schedule", None)
    update_allow_major_update = __update.get("allow_major_update", False)

    @classmethod
    def update(cls):
        cls.__backup["schedule"] = cls.backup_schedule
        cls.__backup["path"] = cls.backup_path
        cls.__update["schedule"] = cls.update_schedule
        cls.__update["allow_major_update"] = cls.update_allow_major_update
        cls.__data["complete_shutdown"] = cls.complete_shutdown
        cls.__data["schedule"] = cls.schedule
        cls.__data["backup"] = cls.__backup
        cls.__data["update"] = cls.__update
        File.update(cls.SECTION_NAME, cls.__data)