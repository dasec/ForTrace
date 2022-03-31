============
Requirements
============

Before proceeding on configuring fortrace, you'll need to install some required
software and libraries.

Installing Python libraries
===========================

fortrace host components are completely written in Python, therefore make sure to
have an appropriate version installed. For the current release **Python 2.7** is preferred.

Run the ``pre_setup.py`` as admin with the following command to install the system dependencies and python dependencies:
    $ sudo python pre_setup.py

``pre_setup.py`` will install the following dependencies.

``packet_requirements.txt``:

 * python (should be present on the system. Required to use the pre_setup script.): Required to run fortrace framework
 * python-pip: required to manage python packages
 * qemu-kvm: used for various management tasks regarding VMs.
 * libvirt-bin: basic library used to manage virtual environments.
 * virt-manager: used to manage VMs.
 * libcap2-bin: used to modify the user permissions for tcpdump. Otherwise no non-root user could not use tcpdump.
 * tcpdump: used to capture the network traffic

``PIP_requirements.txt``
 * pywinauto: used by email plugins in Windows
 * pywin32: base plugin for Windows
 * setuptools: a pip dependency (old name: pypa-setuptools)
 * selenium: legacy - meant for old browser plugin, not needed by new browser plugin (instead use marionette-driver)
 * marionette_driver: user by new browser plugin, mozrunner and mozprofile should be part of this installation
 * netifaces: network stuff, this module requires the installation of Windows Visual C++. `Download here`_.
 * psutil: used for task management (kill, etc.)
 * netaddr: network stuff
 * enum34: required for the bot network
 * protobuf: required for the bot network

.. _Download here: http://aka.ms/vcpython27

Configure KVM
=============

There are several permission related settings to adjust in order to be able to run fortrace without root permissions.

For all created/cloned VMs you should verify that the owner of the files is "libvirt-qemu" and the usergroup is "kvm".

Furthermore you should adjust the permissions of qemu by editing /etc/qemu.conf.
Change the following parameters.

::

$ User = "libvirt-qemu"
$ Group = "kvm"

Installing Tcpdump
==================

In order to dump the network activity performed by the application during
execution, you'll need a network sniffer properly configured to capture
the traffic and dump it to a file.

By default fortrace adopts `tcpdump`_, the prominent open source solution.

It will be installed by the pre_setup script.

Tcpdump requires root privileges, but since you don't want fortrace to run as root
you'll have to set specific Linux capabilities to the binary::

    $ sudo setcap cap_net_raw,cap_net_admin=eip /usr/sbin/tcpdump

You can verify the results of last command with::

    $ getcap /usr/sbin/tcpdump
    /usr/sbin/tcpdump = cap_net_admin,cap_net_raw+eip


Or otherwise (**not recommended**) do::

    $ sudo chmod +s /usr/sbin/tcpdump

.. _tcpdump: http://www.tcpdump.org

Further the folder where tcpdump places the .pcap files should be owned by the user who is running fortrace.



Installing Spice (optional)
===========================

This step is not required, but will make further steps easier, because Spice enables Copy-and-Paste between Host and Guest::

	$ sudo apt-get install spice-client
	$ sudo apt-get install spice-client-gtk
	$ sudo apt-get install python-spice-client-gtk


Trouble shooting (optional)
===========================

If you have trouble getting everything to work, take a look at already known issues:

1. KVM is throwing messages about the firewall
::

    $ sudo apt install ebtables

2. Network issues
::

    $ sudo apt install dnsmasq

or

::

    $ sudo pip install netaddr

3. KVM messages about performance or missing additions
::

    $ sudo apt install qemu-utils

| 4. KVM is having issues with creating the Diff-Images
| /var/lib/libvirt/images/backing does need writing permission.

::

    $ sudo chmod 755 /var/lib/libvirt/images/backing
