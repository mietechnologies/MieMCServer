#!/bin/sh
packageUrl=https://download.oracle.com/java/17/latest/jdk-17_linux-x64_bin.tar.gz
javaHome=/usr/java/jdk-17
temp=/tmp/java.tgz

wget https://download.oracle.com/java/17/latest/jdk-17_linux-x64_bin.tar.gz -O /tmp/java.tgz
sudo mkdir /usr/java
sudo mkdir /usr/java/jdk-17
# The line below is failing to execute when ran from the shell script, but executes just fine 
# when ran from Terminal... :/
# Skipping and disabling installing JDK for now, but should come back to this eventually.
sudo tar -xzvf /tmp/java.tgz -C /usr/java/jdk-17
# sudo rm -f $temp