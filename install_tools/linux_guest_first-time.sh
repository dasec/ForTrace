#!/bin/bash

echo "Only run this script when using the python 2 version of fortrace. This will backup the sources.list and change it as well as install packages no longer available via packet managers."
echo "Please choose if you want to run this script by typing (y) for yes or (n) for no."

read -p  'Sel: ' sel

if [ $sel == 'y' ]
then
    sh -c "sudo cp /etc/apt/sources.list /etc/apt/sources.list.backup"
    sh -c "sudo sed -i -re 's/([a-z]{2}\.)?archive.ubuntu.com|security.ubuntu.com/old-releases.ubuntu.com/g' /etc/apt/sources.list"
    sh -c "sudo apt-get update"
    sh -c "sudo apt install python-pyatspi"
    sh -c "pip install --user ldtp-3.5.0.tar.gz"
    sh -c "gsettings set org.gnome.desktop.interface toolkit-accessibility true"
    sh -c "sudo dpkg -i python-twisted-web2_8.1.0-3build1_all.deb"
    echo "If python-twisted-web2 is not installing, check the dependencies first and install manually"

else
    exit 1
fi

exit 0
