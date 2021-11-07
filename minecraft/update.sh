# Initiliaze and create a current_ver.txt file and backups directory if it does not exist
if [ ! -f current_ver.txt ]
then
    echo 0 > current_ver.txt
fi

if [ ! -d backups ]
then
    mkdir backups
fi

# Read the current version of the local server
CURRENT_VER=$(cat current_ver.txt)
echo Current Version: $CURRENT_VER

# Download the latest version_manifest.json
wget -q https://launchermeta.mojang.com/mc/game/version_manifest.json

# Get the latest release version number
VER=$(jq -r '.latest.release' version_manifest.json)
echo Latest Version: $VER

if [ $CURRENT_VER != $VER ]
then
    # Create the jq command to extract the <latest_release_version>.json url
    MANIFEST_JQ=$(echo "jq -r '.versions[] | select(.id == \"$VER\") | .url' version_manifest.json")
    echo $VER.json - jq command: $MANIFEST_JQ

    # Query the <latest_release_version>.json
    MANIFEST_URL=$(eval $MANIFEST_JQ)
    echo $VER.json - URL:$MANIFEST_URL
    
    # Download the <latest_release_version>.json
    wget -q $MANIFEST_URL

    # Create the temp script to extract the latest server download URL from the <latest_release_version>.json
    DOWNLOAD_JQ=$(echo "jq -r .downloads.server.url $VER.json")
    echo Latest download jq command - $DOWNLOAD_JQ

    # Query and get the latest release server.jar download URL
    DOWNLOAD_URL=$(eval $DOWNLOAD_JQ)
    echo Latest download URL: $DOWNLOAD_URL
    
    # Make a backup copy of the current server.jar
    echo Backing up the current server.jar to backups/server_$CURRENT_VER.jar
    mv server.jar backups/server_$CURRENT_VER.jar

    # Run the temp script and download the latest server.jar
    # Let the wget run without the quiet mode on to show its progress in the terminal
    echo "### Downloading $VER version server.jar now! ###"
    wget $DOWNLOAD_URL

    # update the current_ver.txt to the latest release version number 
    echo $VER > current_ver.txt

    # Delete the json files
    echo Cleaning up temporary files
    rm version_manifest.json
    rm $VER.json

    echo You have the latest $VER version of server.jar now!
else
    echo Current server version is the latest already.
    rm version_manifest.json
fi
