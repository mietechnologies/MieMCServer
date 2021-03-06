import os
import yaml

from .mielib import custominput as ci
from .extension import cleanString, decode, encode

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
        Messaging.reset()
        Maintenance.reset()

        if os.path.exists(cls.__file_dir):
            os.remove(cls.__file_dir)
        
        Minecraft.update()
        Email.update()
        Messaging.update()
        Maintenance.update()

    @classmethod
    def build(cls):
        if os.path.exists(cls.__file_dir):
            user_response = ci.bool_input("This will override your current " \
                "config.yml, are you sure you want to do that?", default=False)
            if user_response:
                os.remove(cls.__file_dir)
            else:
                return False

        print("I will ask a series of questions to build your config.yml\n" \
            "You are free to edit your config.yml file manually after creation.")

        if ci.bool_input('First, I need to know if you\'re using a ' \
            'Raspberry Pi.', default=False):
            Temperature.build()

        Email.build()
        Messaging.build()
        Server.build()
        Minecraft.build_object()
        Maintenance.build()

        return True

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
    def accept_eula(cls) -> bool:
        '''
        Prompts the user to accept or decline Minecraft's EULA.
        
        Returns:
            A boolean indicating whether or not the user accepted the EULA.
        '''
        print('\n\n****** WARNING ******')
        print('Hosting a Minecraft server requires you to accept Minecraft\'s \
            EULA.')
        print('You can find more information about Minecraft\'s EULA at \
            https://account.mojang.com/documents/minecraft_eula')
        return ci.bool_input('If you like, I can accept the terms of the EULA \
            for you now. Would you like me to do that?', default=True)

    @classmethod
    def version_str(cls):
        if cls.patch is None:
            return "{}.{}:{}".format(cls.major, cls.minor, cls.build)
        else:
            return "{}.{}.{}:{}".format(cls.major, cls.minor, cls.patch, cls.build)

    @classmethod
    def build_object(cls):
        cls.reset()
        ram = ci.int_input("How much RAM would you like to dedicate to your " \
            "Minecraft Server? (your input will be Mbs)", default=1024)
        version = ci.version_input("What version of Minecraft would you like " \
            "to install?")
        if version != "":
            version_split = version.split(".")
            if len(version_split) == 2:
                cls.major = version_split[0]
                cls.minor = version_split[1]
            elif len(version_split) == 3:
                cls.major = version_split[0]
                cls.minor = version_split[1]
                cls.patch = version_split[2]
            cls.version_group = "{}.{}".format(version_split[0], version_split[1])

        cls.update()

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
    password = ""
    try:
        password = decode(__data.get("password"))
    except:
        password = "<your password>"
    server = __data.get("server", "smtp.gmail.com")
    port = __data.get("port", 587)
    recipients = __data.get("recipients", [])

    @classmethod
    def build(cls):
        email_address = ci.email_input("What is the gmail address you would " \
            "like me to use to send you reports?", provider="gmail")
        password = ci.password_input("What is the password to the account you" \
            " just entered?")
        recipients = ci.email_input("What email address(es) would you like " \
            "to recieve the logs and reports?", multiples=True)
        cls.address = email_address
        cls.password = password
        cls.recipients = recipients
        cls.update()

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
    __data = File.data.get("Maintenance", {})
    __backup = __data.get("backup", {})
    __update = __data.get("update", {})
    complete_shutdown = __data.get("complete_shutdown", "0 4 1 * *")
    schedule = __data.get("schedule", "0 4 * * *")
    backup_schedule = __backup.get("schedule", "0 3 * * *")
    backup_path = __backup.get("path", "~/MC_Backups")
    backup_number = __backup.get("number", 1)
    backup_file_server = __backup.get("file_server", {})
    maintenance_running = __data.get('scheduled_running', False)
    update_schedule = __update.get("schedule", "0 3 * * 0")
    update_allow_major_update = __update.get("allow_major_update", False)

    @classmethod
    def build(cls):
        # print("Warning: A system restart is good practice to clear out any " \
        #     "residual problems that might still be in RAM. Also, in order to " \
        #     "run the commands file a server restart is required.")
        # restart_cron = ci.cron_date_input("restart")

        # print("Warning: It is good practice to backup your server so if any" \
        #     "thing were to happen, you would be able to revert back to your " \
        #     "previous backup.")
        # backup_cron = ci.cron_date_input("backup Minecraft")
        # backup_path = input("Where would you like your backups to be stored? ")
        # backup_limit = ci.int_input("How many backups would you like to be " \
        #     "stored before removing old backups?")
        file_server = cls.__build_external_storage()
        print(file_server)

        # print("Warning: It is wise to check for updates on a regular basis so " \
        #     "any bugs the developers might find and fix will be applied to " \
        #     "your server. We can understand your concern for larger updates, " \
        #     "so we will ask your permission on if you want us to do bigger " \
        #     "updates automatically. If not, we will email you and alert you " \
        #     "of any major updates.")
        # update_cron = ci.cron_date_input("check for updates")
        # major_updates = ci.bool_input("Would you like me to update to " \
        #     "major releases?", default=False)
            
        # print("Warning: I have ben preprogrammed with some useful maintenance " \
        #     "scripts to help keep your server up and running smoothly. It is " \
        #     "always good to run these scripts so your players experience as " \
        #     "little server lag as possible.")
        # maintenance_cron = ci.cron_date_input("run maintenance scripts")

        # cls.complete_shutdown = restart_cron
        # cls.schedule = maintenance_cron
        cls.backup_file_server = file_server
        # cls.backup_schedule = backup_cron
        # cls.backup_path = backup_path
        # cls.backup_number = backup_limit
        # cls.update_schedule = update_cron
        # cls.update_allow_major_update = major_updates
        cls.update()

    @classmethod
    def __build_external_storage(cls) -> object:
        '''
        Requests user input regarding their external file server where backups
        will be stored.

        Returns: An object containing all of the needed values for configuration.
        '''
        should_setup = ci.bool_input('For extra data security, I can also ' \
            'store your backups on an external file security. Would you like ' \
            'to set that up now? (Please ensure that this machine has ' \
            'connected to your file server before!)')
        if should_setup:
            host = ci.server_address_input('What is the host address of your ' \
                'file server?')
            print(f'Collecting ssh key for {host}...')
            key = os.popen(f'ssh-keyscan {host} | grep "ssh-rsa"').read()
            key = key.replace(f'{host} ssh-rsa ', '')
            encoded_key = encode(key)
            username = ci.string_input('What is the username for your file ' \
                'server?')
            password = ci.password_input('What is the password used to ' \
                'connect to your file server?')
            path = ci.string_input('Where would you like to store backups on ' \
                'your file server?', r'^~?(?:\/.+){1,}', '~/backups')
            return {
                'domain' : host,
                'key' : encoded_key,
                'username' : username,
                'password' : password,
                'path' : path
            }
        return {}

    @classmethod
    def update(cls):
        cls.__backup['file_server'] = cls.backup_file_server
        cls.__backup["schedule"] = cls.backup_schedule
        cls.__backup["path"] = cls.backup_path
        cls.__backup["number"] = cls.backup_number
        cls.__backup["file_server"] = cls.backup_file_server
        cls.__update["schedule"] = cls.update_schedule
        cls.__update["allow_major_update"] = cls.update_allow_major_update
        cls.__data["complete_shutdown"] = cls.complete_shutdown
        cls.__data["schedule"] = cls.schedule
        cls.__data["backup"] = cls.__backup
        cls.__data["update"] = cls.__update
        cls.__data['scheduled_running'] = cls.maintenance_running
        File.update(cls.SECTION_NAME, cls.__data)

    @classmethod
    def reset(cls):
        cls.complete_shutdown = "0 4 1 * *"
        cls.schedule = "0 4 * * *"
        cls.backup_schedule = "0 3 * * *"
        cls.backup_path = "~/MC_Backups"
        cls.backup_number = 1
        cls.update_schedule = "0 3 * * 0"
        cls.update_allow_major_update = False
        cls.update()

class Messaging:
    __data = File.data.get('Messaging', {})
    discord = __data.get('discord', None)

    @classmethod
    def build(cls):
        if ci.bool_input('If you\'d like, I can post important updates (like '\
            'server shut downs and restarts) to a Discord server. Would you like '\
            'to use this service?', False):
            print('Alright, the only information I need to setup discord is a '\
                'webhook URL. You can find out how to get that information at '\
                'https://support.discord.com/hc/en-us/articles/228383668-Intro-to-'\
                'Webhooks.')
            cls.discord = ci.url_input('So, what is that webhook URL?')
            cls.update()

    @classmethod
    def update(cls):
        cls.__data['discord'] = cls.discord
        File.update('Messaging', cls.__data)

    @classmethod
    def reset(cls):
        cls.discord = None

class RCON:
    enabled = False
    password = None
    port = None

    @classmethod
    def build(cls):
        print('RCON is a protocol that allows server administrators to ' \
            'remotely execute Minecraft commands.')
        print('Mie-MCServer uses RCON to run clean up commands to ' \
            'automatically maintain your server.')
        print('Please take a moment to set up RCON by answering the ' \
            'following questions.')
        cls.port = ci.int_input('What internet port would you like to use ' \
            'for RCON?', 25575)
        cls.password = ci.password_input('What password would you like to ' \
            'use for issuing commands via RCON?', pattern=r'^[a-zA-Z0-9_]+$')
        cls.enabled = True
        cls.update()

    @classmethod
    def read(cls):
        dir = os.path.dirname(__file__)
        properties = os.path.join(dir, '../server/server.properties')
        if os.path.isfile(properties):
            lines = open(properties, 'r').readlines()
            for line in lines:
                if 'rcon.port' in line: 
                    cls.port = int(cleanString(line, ['rcon.port=', '\n']))
                elif 'enable-rcon' in line: 
                    cls.enabled = bool(cleanString(line, ['enable-rcon=', '\n']))
                elif 'rcon.password' in line: 
                    cls.password = cleanString(line, ['rcon.password=', '\n'])
        else:
            from .syslog import log
            log('ERR: No server.properties file found!')

    @classmethod
    def update(cls):
        dir = os.path.dirname(__file__)
        properties = os.path.join(dir, '../server/server.properties')
        if os.path.isfile(properties):
            with open(properties, 'r') as fileIn:
                lines = fileIn.readlines()
                fileOut = open(properties, 'w')
                for line in lines:
                    if 'rcon.port' in line:
                        line = 'rcon.port={}\n'.format(cls.port)
                    elif 'enable-rcon' in line:
                        line = 'enable-rcon={}\n'.format(cls.enabled).lower()
                    elif 'rcon.password' in line: 
                        line = 'rcon.password={}\n'.format(cls.password)
                    
                    fileOut.write(line)
        else:
            from .syslog import log
            log('ERR: No server.properties file found!')

class Server:
    '''
    Any data we need to store in relation to the server that can't be stored
    in the server.properties file should be stored here. At the time of writing,
    this is just the ip/url used to connect to the server, but could turn into
    other things in the future.
    '''
    __data = File.data.get('Server', {})
    url = __data.get('url', None)

    @classmethod
    def build(cls):
        '''
        Constructs the `Server` section of the user's `config.yml` file based
        upon the user's input.
        '''
        print('Hosting a Minecraft server requires a url to connect to. This ' \
            'url can be an IP address or a url to a private server-space ' \
            'hosted on this device.')
        print('If you are hosting a local server, it\'s fine to use an IP ' \
            'address for your server, but I recommend using a url if you are ' \
            'hosting a public server.')
        print('If you need to create a public-facing url to allow users to ' \
            'connect to your server, I recommend using a service called no-ip' \
            'to generate a dynamic url that always points to your IP, ' \
            'regardless of how it might change.')
        print('You can find more information on no-ip at https://www.noip.com.')
        cls.url = ci.server_address_input('What url would you like to use to' \
            'host your Minecraft server?')
        cls.update()

    @classmethod
    def update(cls):
        '''Updates the `Server` section of the user's `config.yml` file.'''
        cls.__data['url'] = cls.url
        File.update('Server', cls.__data)

class Temperature:
    __data = File.data.get("Temperature", {})
    elapsed = __data.get('elapsed', 0)
    maximum = __data.get('maximum', None)
    minutes = __data.get('minutes', None)

    @classmethod
    def build(cls):
        print('Because I\'m running on a Raspberry Pi, core temperature can be worrysome so I monitor my core temperature for you.')
        cls.maximum = ci.int_input('So, how hot should I let myself get?', default=70)
        cls.minutes = ci.int_input('And how many minutes should pass before I shut everything down?', default=3)
        cls.update()

    @classmethod
    def exists(cls):
        return cls.__data != {}

    @classmethod
    def is_overheating(cls, current_temp: float) -> bool:
        return current_temp >= cls.maximum

    @classmethod
    def update(cls):
        cls.__data['elapsed'] = cls.elapsed
        cls.__data['maximum'] = cls.maximum
        cls.__data['minutes'] = cls.minutes
        File.update('Temperature', cls.__data)
