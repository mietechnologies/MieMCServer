from minecraft.modded import forge
from util import files
from util import path
from util.download import get
from util.files import update
from util.logger import log
from util.mielib import custominput as ci
from util.shell import run

class Modded:
    """
    """

    __FORGE_INSTALLER = path.project_path('server', 'installer.jar')

    data = {}
    allocated_ram = 1024
    modpack_id: str = None
    minecraft_version: str = None
    forge_version: str = None

    def __init__(self, data: dict) -> None:
        self.data = data
        self.allocated_ram = int(self.data.get('allocated_ram', 1024))
        self.modpack_id = self.data.get('modpack_id', None)
        self.minecraft_version = self.data.get('minecraft_version', None)
        self.forge_version = self.data.get('forge_version', None)

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
        """

        # Use the CurseForge API to fetch a list of modpacks that the user can
        # install, display these to them, and allow them to select one. This
        # will also give us the correct version of Minecraft to later download
        # the correct version of the Forge Installer.

        # Will be found dynamically depending on the CurseForge API. For now, we're supplying
        # a magic value to make it work.
        modpack_version = '1.18.2'

        # This is where this method is going to get complicated. Since Forge
        # doesn't have an API, we're going to host a JSON file on a separate
        # GitHub repo and use it to figure out what version of the Forge
        # Installer to download and install. This will allow us the flexibility
        # of updating this JSON file whenever is necessary so that we can keep
        # versions of the launcher up-to-date.
        #
        # The process will be as follows:
        # 1. Clone the miemcserver-forge project at
        # https://github.com/mietechnologies/miemcserver-forge.git
        # 2. Parse the JSON file and use the Minecraft version we got from the modpack selection
        # earlier to get the Minecraft and Forge Installer versions.
        # 3. Store this info in configuration
        log('Downloading Forge Installer...')
        forge_versions = forge.get_forge_versions()
        forge_version: dict = forge_versions[modpack_version]
        self.minecraft_version: str = forge_version['minecraftVersion']
        self.forge_version: str = forge_version['forgeVersion']

        download_url = forge.construct_forge_installer_url(
            self.minecraft_version,
            self.forge_version
        )
        installer = get(download_url, self.__FORGE_INSTALLER)

        # Now that the installer has been downloaded, we need to execute it to install
        # the needed files for running the forge server. The command to execute this
        # is `java -jar forge-installer.jar --installServer`
        log('Installing Forge server...')
        server = path.project_path('server')
        command = f'java -jar {installer} --installServer={server}'
        run(command)

        # Clean up all temporary files
        log('Cleaning up temporary files from installing Forge server...')
        forge.cleanup()

        # TODO: Copy the mod files for the modpack to be installed to the server directory
        log('Installing modpack files...')

        # Now that we have installed the Forge server files, we need to ask the user to
        # designate an amount of RAM to dedicate to the running the server.
        print('Great! The Forge server has installed successfully. Now I need to know ' \
            'how much RAM you plan to dedicate to this server. A good suggestion is 4GB ' \
            'plus 1GB for every 5 players you plan on having active on the server at ' \
            'any given time (to a maximum of 16GB). Fyi, we will set your minimum to ' \
            '4GB automatically.')
        self.allocated_ram = ci.int_input('So, how much RAM would you like to dedicate?')

        # Even though we will have the allocated RAM stored in `config.yml`, we also need
        # to update the `/server/user_jvm_args.txt` file with this info to allow the Forge
        # server to work correctly.
        args_file = path.project_path('server', 'user_jvm_args.txt')
        files.add([f'-Xms4G -Xmx{self.allocated_ram}G'], args_file)

        old_command = 'java @user_jvm_args.txt @libraries/net/minecraftforge/forge/' \
            '1.18.2-40.1.0/unix_args.txt "$@"'
        new_command = 'java @user_jvm_args.txt @libraries/net/minecraftforge/forge/' \
            '1.18.2-40.1.0/unix_args.txt nogui "$@"'
        run_file = path.project_path('server', 'run.sh')
        files.update(run_file, old_command, new_command)

        # Now that we know RAM allocation, we need to run the server to generate the EULA
        # and offer to automatically sign it for the user.
        log('Running initial setup...')
        command = f'cd {server} && ./run.sh nogui'
        run(command)

        eula_link = 'https://account.mojang.com/documents/minecraft_eula'
        eula_file = path.project_path('server', 'eula.txt')
        print('Now time for the boring stuff. To use your server, you must agree to Mojang\'s ' \
            'EULA. If you\'d like, I can sign it for you now automatically. You can find more ' \
            f'information about Mojang\'s EULA at {eula_link}.')
        if ci.bool_input('Would you like me to sign the EULA for you?', default=True):
            files.update(eula_file, 'eula=false', 'eula=true')
            log('Mojang EULA signed')
        else:
            print('Okay, before you can run your server, you will have to agree to the ' \
                f'EULA located at {eula_file}.')

        log('Installation complete!')
        print('Please start the server using the command `python3 main.py -D`')

        return self.update()

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
