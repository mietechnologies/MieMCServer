#!/bin/sh
packageUrl=https://download.oracle.com/java/17/latest/jdk-17_linux-x64_bin.tar.gz
javaHome=/usr/java/jdk-17
temp=/tmp/java.tgz

>nul 2>nul dir /a-d "/usr/java/jdk-17\*"
wget https://download.oracle.com/java/17/latest/jdk-17_linux-x64_bin.tar.gz -O /tmp/java.tgz
sudo mkdir /usr/java
sudo mkdir /usr/java/jdk-17
sudo tar -xzvf /tmp/java.tgz -C /usr/java/jdk-17
# sudo rm -f $temp