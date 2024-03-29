'''
A module for handling configuring the modded Minecraft server.
'''

import time
from minecraft.modded import forge
from util import files
from util import path
from util import shell
from util.download import get
from util.mielib import custominput as ci

class Modded:
    '''
    A class for handling configuring the modded Minecraft server. Must be initialized
    with a dictionary.

    Methods
    -------
    query() -> bool
        Displays a simple request asking the user if they would like to install a modded
        server using Forge.

    build() -> dict
        Befins building out the configuration for the modded Minecraft server.
    '''

    __FORGE_INSTALLER = path.project_path('server', 'installer.jar')
    __LOG = None

    data = {}
    allocated_ram = 1024
    modpack_id: str = None
    minecraft_version: str = None
    forge_version: str = None
    uses_args_file: bool = False
    jre_version_required: str = None

    def __init__(self, data: dict, logger = None) -> None:
        self.__LOG = logger

        self.data = data
        self.allocated_ram = int(self.data.get('allocated_ram', 1024))
        self.modpack_id = self.data.get('modpack_id', None)
        self.minecraft_version = self.data.get('minecraft_version', None)
        self.forge_version = self.data.get('forge_version', None)
        self.uses_args_file = self.data.get('uses_args_file', False)

    @classmethod
    def query(cls) -> bool:
        """
        Requests whether to install a modded Forge server.

        Returns
        -------
        bool
            User input reflecting if the user wants to install a modded Forge server.
        """

        return ci.bool_input('Would you like to set up a modded server using ' \
            'Forge?', default=False)

    def build(self) -> dict:
        """
        Builds out the configuration for the modded Minecraft server.

        NOTE
        ----
            Should only be used during generation of the config yaml file!
        """

        # Because the Eternals API team is being SO SLOW in getting back to us, we're going
        # to take a slightly different path for install... For now, we're going to ask the user
        # to designate the Minecraft version and supply a zip for the modpack files to install
        # on the server.
        print('The Eternals API team has not allowed me access to their API yet, so I have to ' \
            'take a slightly different approach to installing the modpack on your server.')
        print('*** WARNING *** Because of this, I might not be able to support your modpack. If ' \
            'you run into any errors or issues when attempting to install, please open an issue ' \
            'on https://github.com/mietechnologies/MieMCServer/issues')
        time.sleep(2)

        # Get Minecraft and Forge versions from user
        self.minecraft_version = ci.version_input('First, I need to know what Minecraft version ' \
            'the modpack you want to install uses. You can find this information on the modpacks ' \
            'profile page.')
        self.forge_version = ci.version_input('Next, I need to know what Forge version your ' \
            'modpack uses. You can find this infomration on the modpacks profile page.')

        forge_installer = self.__download_forge()
        mod_files = self.__request_modpack()
        self.__install_forge_and_modpacks(forge_installer, mod_files)

        # Now that we have installed the Forge server files, we need to ask the user to
        # designate an amount of RAM to dedicate to the running the server.
        print('Great! The Forge server has installed successfully. Now I need to know ' \
            'how much RAM do you plan to dedicate to this server. A good suggestion is 4GB ' \
            'plus 1GB for every 2 players you plan on having active on the server at ' \
            'any given time (to a maximum of 16GB). Fyi, we will set your minimum to ' \
            '4GB automatically.')
        self.allocated_ram = ci.int_input('So, how much RAM would you like to dedicate?')

        # Update server files with the correct information
        self.__update_files()

        # Now that we know RAM allocation, we need to run the server to generate the EULA
        # and offer to automatically sign it for the user. Since we're terminating the
        # startup process prematurely, we will also need to kill the process or it will
        # still run...
        self.__initial_setup()

        # Clean up all temporary files
        self.__LOG('Cleaning up temporary files from installing Forge server...')
        forge.cleanup(self.uses_args_file)

        self.__LOG('Installation complete!')

        return self.update()

    def run_command(self) -> str:
        '''
        Iterates through the server's files to find the correct file to use for launching
        the server and returns the command.

        Returns
        -------
        str
            The command to be ran for starting the server.
        '''
        
        server = path.project_path('server')
        command = None

        # for file in path.list_dir(server):
        #     if 'startserver.sh' in file:
        #         return './startserver.sh'

        for file in path.list_dir(server):
            if 'run.sh' in file:
                return './run.sh'

        for file in path.list_dir(server):
            if 'start.sh' in file:
                return './start.sh'

        return command

    def update_modpack(self) -> dict:
        '''
        Installs a new modpack version from an absolute path desifnated by the user.

        Returns
        -------
        dict
            Returns the updated dict representing the Modded class to be saved to the
            config.yml file.
        '''

        new_mc_version = ci.version_input('What version of Minecraft does this update target?')
        new_forge_version = ci.version_input('And what version of Forge?')

        # If this new modpack uses a different version of forge, we need to get a new installer
        # and install.
        forge_installer = None

        if new_mc_version != self.minecraft_version or new_forge_version != self.forge_version:
            self.minecraft_version = new_mc_version
            self.forge_version = new_forge_version
            forge_installer = self.__download_forge()

        mod_files = self.__request_modpack()

        if forge_installer is not None:
            self.__install_forge_and_modpacks(forge_installer, mod_files)

        self.__update_files()
        self.__initial_setup()

        self.__LOG('Cleaning up temporary files from installing Forge server...')
        forge.cleanup(self.uses_args_file)

        return self.update()

    def __download_forge(self) -> str:
        self.__LOG('Downloading Forge Installer...')
        forge_installer_url = forge.construct_forge_installer_url(
            self.minecraft_version,
            self.forge_version
        )
        forge_installer = path.project_path('tmp/forge', 'installer.jar')
        forge_installer = get(forge_installer_url, forge_installer)
        self.__LOG('Download of Forge Installer complete!')
        return forge_installer

    def __initial_setup(self):
        self.__LOG('Running initial setup...')

        # Run the server to generate the EULA,
        server = path.project_path('server')
        shell.run(self.run_command(), server, r'Done \(\d+\.\d+s\)!')

        eula_link = 'https://account.mojang.com/documents/minecraft_eula'
        eula_file = path.project_path('server', 'eula.txt')
        print('Now time for the boring stuff. To use your server, you must agree to Mojang\'s ' \
            'EULA. If you\'d like, I can sign it for you now automatically. You can find more ' \
            f'information about Mojang\'s EULA at {eula_link}.')
        print('Please note that if you do not sign the EULA now, there are features I won\'t ' \
            'be able to set up for you!')
        time.sleep(2)

        if ci.bool_input('Would you like me to sign the EULA for you?', default=True):
            files.update(eula_file, 'eula=false', 'eula=true')
            self.__LOG('Mojang EULA signed')
            self.__first_run()

            # TODO: Set level-seed in server.properties
            # TODO: Whitelist setup
        else:
            self.__LOG('Mojang EULA declined')
            print('Okay, before you can run your server, you will have to agree to the ' \
                f'EULA located at {eula_file}.')

    def __first_run(self):
        # We need to run the server once and stop it early so we can generate the needed files
        # such as the server.properties file.
        self.__LOG('Starting server for the first time to generate setup files...')
        input('Once finished, please input the `stop` command so I can continue setup (press '\
            'any key to continue)')

        server = path.project_path('server')
        shell.run(self.run_command(), server)
        self.__LOG('Initial setup complete!')

    def __install_forge_and_modpacks(self, installer: str, mods: str):
        self.__LOG('Installing moded server and modpack files...')
        # Install the Forge Server
        # java -jar {path/to/installer} --installServer={path/to/server/dir}
        server = path.project_path('server')
        command = f'java -jar {installer} --installServer={server}'
        shell.run(command)

        # Copy the mod files for the modpack to be installed to the server directory.
        path.move(mods, server)
        self.__LOG('Installation complete!')

    def __request_modpack(self) -> str:
        mod_files = None
        message = 'Alright, I need to know where I can find the zip file containing the ' \
            'modpack files you want to install. Please ensure that you downloaded the server ' \
            'pack files.'

        while mod_files is None:
            modpack_location = ci.path_input(message)
            mods = forge.extract_and_confirm_mods(modpack_location)

            if mods is None:
                message = 'Sorry, that is not a valid zip file. Please tell me where I can ' \
                    'find the zip file for your server pack.'
                forge.cleanup(True)
            else:
                mod_files = mods
                break

        self.__LOG('Modpack verified...')
        return mod_files

    def __download_and_install_forge(self, modpack_version: str) -> str:
        self.__LOG('Downloading Forge Installer...')
        forge_versions = forge.get_forge_versions()
        forge_version: dict = forge_versions[modpack_version]
        self.minecraft_version: str = forge_version.get('minecraftVersion', None)
        self.forge_version: str = forge_version.get('forgeVersion', None)
        self.uses_args_file: bool = forge_version.get('usesArgsFile', False)
        self.jre_version_required: str = forge_version.get('jreRequirement', None)

        download_url = forge.construct_forge_installer_url(
            self.minecraft_version,
            self.forge_version
        )
        installer = get(download_url, self.__FORGE_INSTALLER)

        # Now that the installer has been downloaded, we need to execute it to install
        # the needed files for running the forge server. The command to execute this
        # is `java -jar forge-installer.jar --installServer`
        self.__LOG('Installing Forge server...')
        server = path.project_path('server')
        command = f'java -jar {installer} --installServer={server}'
        shell.run(command)
        return server

    def __update_files(self):
        server = path.project_path('server')

        for file in path.list_dir(server):
            # Even though we will have the allocated RAM stored in `config.yml`, we also need
            # to update the `/server/user_jvm_args.txt` file with this info to allow the Forge
            # server to work correctly.
            if 'user_jvm_args.txt' in file:
                files.add([f'-Xms4G -Xmx{self.allocated_ram}G'], file)

            # Update the run script to run with no gui
            if 'run.sh' in file:
                command = 'java @user_jvm_args.txt @libraries/net/minecraftforge/forge/'
                command += f'{self.minecraft_version}-{self.forge_version}/unix_args.txt '
                command += 'nogui "$@"'
                files.write(['#!/bin/sh', command], file)
                shell.run(f'chmod +x {file}', server)

            if 'start.sh' in file:
                shell.run('chmod +x start.sh', server)

    def update(self) -> dict:
        """
        Simply updates the `data` value to be used elsewhere.

        Returns
        -------
        dict
            The `data` object representing this class to be stored in the user's `config.yml`.
        """

        self.data['modpack_id'] = self.modpack_id
        self.data['minecraft_version'] = self.minecraft_version
        self.data['forge_version'] = self.forge_version
        return self.data
