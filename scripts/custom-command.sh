# Purpose: Use this file to execute any custom bash scripting you would like to
# the project to execute. For example, if your server uses a crafting datapack
# that you manage, you can add a command to pull the latest changes here before
# start up.

#!/bin/bash

PROCESS=$1

if [ "$PROCESS" == "start" ]; then
    echo "Running start commands..."
    # Add commands that will run before starting the server here

elif [ "$PROCESS" == "stop" ]; then
    echo "Running stop commands..."
    # Add commands that will run before stopping the server here
    
elif [ "$PROCESS" == "clean" ]; then
    echo "Running clean commands..."
    # Add commands that will run during cleanup here
    
fi