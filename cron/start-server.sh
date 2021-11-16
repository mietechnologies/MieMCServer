#!/bin/bash
PROJECT_DIR=/home/pi/minePi
SERVER_DIR=$PROJECT_DIR/minecraft/server
ALLOTTED_RAM=$1

# python $PROJECT_DIR/start.py

# screen bash
cd $SERVER_DIR
java -Xmx$ALLOTTED_RAM -Xms$ALLOTTED_RAM -jar paper.jar nogui