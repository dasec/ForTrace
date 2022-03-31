#!/bin/bash

# Make sure only root can run our script
#if [[ $EUID -ne 0 ]]; then
   #echo "This script must be run as root" 1>&2
  # exit 1
#fi

echo "Please choose if this installation is host (h) or guest (g) side installation:"
read -p 'Selection: ' sel

if [ $sel == 'h' ]
then
    param='host'
elif [ $sel == 'g' ]
then
    param='vm'
else
    echo "[X] Unknown parameter. Exiting."
    exit 1
fi

echo "[~] Thank you. Installation will proceed for $param."

# install python
sh -c "sudo apt-get install python -y -qqq"

echo "  [+] python installed."

# call pre_setup.py
sh -c "sudo python pre_setup.py $param"

sh -c "python setup.py install --user"

echo "  [+] pre_setup finished successfully."

if [ $sel == 'h' ]
then
    echo "Please check if your chosen user has been added to groups libvirt and libvirtd. If this is not the case, restart the shell or reboot your system."
    echo "You will be asked to enter your user password again in an attempt to reload your shell. "
fi

echo "[+] Installation complete."

if [ $sel == 'h' ]
then
    su - $USER
fi

exit 0
