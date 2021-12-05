#!/bin/bash
ALLOTTED_RAM=$1
SERVER_DIR=$2

cd $SERVER_DIR
java -Xmx$ALLOTTED_RAM -Xms$ALLOTTED_RAM -jar paper.jar nogui