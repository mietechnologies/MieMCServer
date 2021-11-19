
from minecraft.version import Versioner

versioner = Versioner()
print('Checking for version updates! Please wait...')
currentVersion = versioner.getCurrentVersion()
latestVersion = versioner.getLatestVersion()

print(currentVersion)
print(latestVersion)

if currentVersion['versionGroup'] != latestVersion['versionGroup']:
    print('Minecraft Server {} is now available!'.format(latestVersion['versionGroup']))
if currentVersion['version'] != latestVersion['version']:
    print('Minecraft Server {} is now available!'.format(latestVersion['version']))
if currentVersion['build'] < latestVersion['build']:
    print('Paper has released update {}!'.format(latestVersion['build']))