#!/bin/bash
# A collection of clean up scripts to be run every week on a Minecraft server. This file does none 
# of the acutal cleaning. Rather, it executes other shell scripts contained within this folder.

./stopServer.sh
./trimEnd.sh