============================================
Preparing the Input Drivers for Linux VMs
============================================

Step 1:
Install the kernel headers and build tools.
You can do this easily via the module-assistant application on ubuntu or debian systems.
::

    $ apt-get install module-assistant
    $ sudo module-assistant #or sudo m-a

Do "Update" and "Prepare".
This will install all necessary packages.

Step 2:

Traverse into the drivers/linux subdirectory.
For each folder do:
::

    $ sudo make
    $ sudo make install

Step 3:

Copy the set1-de.conf file from src/fortrace/utility/conf to /etc/fortrace.

Step 4:

Add the following lines to /etc/modules to enable automodule loading::

    vkbd
    vsermouse

Step 5:

Reboot and check that the following devices exist under /dev:
::

    vsermouse
    vkbd

Step 6:

You may run the DevControlServer now.
