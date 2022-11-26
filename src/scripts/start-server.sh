#!/bin/bash
ALLOTTED_RAM=$1
SERVER_DIR=$2
LOG_FILE=$3

cd $SERVER_DIR
java -Xmx512M -Xms$ALLOTTED_RAM -jar paper.jar nogui > $LOG_FILE