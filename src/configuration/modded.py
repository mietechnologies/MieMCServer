from minecraft.modded import forge
from util import path
from util.download import get
from util.mielib import custominput as ci

class Modded:
    """
    """

    __FORGE_INSTALLER = path.project_path('tmp/forge_installer/', 'installer.jar')

    data = {}
    modpack_id: str = None
    minecraft_version: str = None
    forge_version: str = None

    def __init__(self, data: dict) -> None:
        self.data = data
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
        forge_versions = forge.get_forge_versions()
        forge_version: dict = forge_versions[modpack_version]
        self.minecraft_version: str = forge_version['minecraftVersion']
        self.forge_version: str = forge_version['forgeVersion']

        download_url = forge.construct_forge_installer_url(
            self.minecraft_version,
            self.forge_version
        )
        installer = get(download_url, self.__FORGE_INSTALLER)

        # Clean up all temporary files
        forge.cleanup()

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
