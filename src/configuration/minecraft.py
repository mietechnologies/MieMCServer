from util.mielib import custominput as ci

class Minecraft:
    data = {}
    version = {}
    allocated_ram = 1024
    major: int = None
    minor = None
    patch = None
    build = None
    install_date = ''
    version_group = ''

    def __init__(self, data: dict):
        self.data = data
        self.version = self.data.get('version', {})
        self.allocated_ram = int(self.data.get('allocated_ram', 1024))
        self.major = self.version.get("major", None)
        self.minor = self.version.get("minor", None)
        self.patch = self.version.get("patch", None)
        self.build = self.version.get("build", None)
        self.install_date = self.version.get("install_date", "")
        self.version_group = self.version.get("version_group", None)

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

    def version_str(self):
        if self.patch is None:
            return f'{self.major}.{self.minor}:{self.build}'
        return f'{self.major}.{self.minor}.{self.patch}:{self.build}'

    def build_object(self) -> dict:
        self.reset()
        self.allocated_ram = ci.int_input("How much RAM would you like to dedicate " \
            "to your Minecraft Server? (your input will be Mbs)", default=1024)
        version = ci.version_input("What version of Minecraft would you like " \
            "to install?")
        if version != "":
            version_split = version.split(".")
            if len(version_split) == 2:
                self.major = version_split[0]
                self.minor = version_split[1]
            elif len(version_split) == 3:
                self.major = version_split[0]
                self.minor = version_split[1]
                self.patch = version_split[2]
            self.version_group = f'{version_split[0]}.{version_split[1]}'

        return self.update()

    def update(self) -> dict:
        self.version["major"] = self.major
        self.version["minor"] = self.minor
        self.version["patch"] = self.patch
        self.version["build"] = self.build
        self.version["install_date"] = self.install_date
        self.version["version_group"] = self.version_group
        self.data["allocated_ram"] = self.allocated_ram
        self.data["version"] = self.version
        return self.data

    def reset(self):
        self.allocated_ram = 1024
        self.major = None
        self.minor = None
        self.patch = None
        self.build = None
        self.install_date = ""
        self.version_group = None

