"""
A module to handle the varying tasks related to downloading, installing, and running Forge.

Methods
-------
`get_forge_versions() -> dict`
    Clones the miemcserver-forge github project to parse the json file located there and parses it.

`construct_forge_installer_url(mc_version: str, forge_version: str) -> str`
    Constructs the direct download url for the Forge Installer using the data provided.
"""

from git.repo import Repo
from util import data, path

def get_forge_versions() -> dict:
    """
    Clones the miemcserver-forge github project to parse the json file located there and parses it.

    Returns
    -------
    dict
        A dictionary representing the json file containing Forge installer version info.
    """

    repo_url = 'https://github.com/mietechnologies/miemcserver-forge.git'
    download_dir = path.project_path('tmp/forge', create=False)
    versions_dir = path.project_path('tmp/forge', 'forge-versions.json', False)

    Repo.clone_from(repo_url, download_dir)
    return data.parse_json(versions_dir)

def construct_forge_installer_url(mc_version: str, forge_version: str) -> str:
    """
    Constructs the direct download url for the Forge Installer using the data provided.

    Parameters
    ----------
    mc_version: str
        The targeted version of Minecraft required by the Forge Installer.
    forge_version: str
        The targeted version number of the Forge Installer.

    Warning
    -------
    DO NOT supply this method manually. Use the `get_forge_versions` method to get this info,
    instead.

    Returns
    -------
    str
        The constructed direct download url.
    """

    # Construct and return the url
    # Root url like: https://maven.minecraftforge.net/net/minecraftforge/forge/
    # Download url like: 1.16.5-36.2.34/forge-1.16.5-36.2.34-installer.jar
    root = 'https://maven.minecraftforge.net/net/minecraftforge/forge/'
    download = f'{mc_version}-{forge_version}/forge-{mc_version}-{forge_version}-installer.jar'
    return root + download

def cleanup():
    """
    Cleans up any temporary files created by the process of installing Forge.
    """

    path.remove(path.project_path('tmp'))
    path.remove(path.project_path('server'), file='installer.jar')
    path.remove(path.project_path('server'), file='run.bat')
    path.remove(path.project_path(), file='installer.jar.log')
