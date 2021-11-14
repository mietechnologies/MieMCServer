#!/bin/bash
PROJECT_DIR=/home/pi/minePi
SERVER_DIR=$PROJECT_DIR/minecraft/server

python $PROJECT_DIR/start.py

cd $SERVER_DIR
java -Xmx2500M -Xms2500M -jar paper.jar nogui