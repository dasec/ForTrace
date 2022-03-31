.. _installindex:

**********************
Installation of fortrace
**********************

fortrace is a framework that consists of two distinct parts as we described in
:ref:`Architecture of fortrace <architecture_index>`. For that reason
it is mandatory to install fortrace on both, the host and the guest system. In the next sections we will show how that
installation can be done.

Once you have finished the installation process, visit :ref:`firstrun` for some help on getting started with fortrace.

It is recommended to install the service VM before you install the guest components.

Configuration of installation paths and values
#################################################

In case you want to use the automated installation scripts for either the host or the guest machines, it is recommended
to read :ref:`config` and make adjustments if necessary before proceeding with the installation.


Installation Host (physical machine)
####################################

Here we will describe how to install the host part of fortrace on a physical machine.

For this **Ubuntu 19.10** is the recommended OS. Other Ubuntu distributions will work as well, but the automatic setup
script might need some alterations depending on your distribution.

In-depth instructions can be found in :ref:`hostinstall`.

Installation Guest (virtual machine)
####################################

Here we will describe how to install the guest part of fortrace on a virtual machine as well as creating said virtual
machine with everything needed for fortrace to operate correctly.

An in-depth installation manual for both Windows and Ubuntu can be found here: :ref:`guestinstall`.

Windows
*******
Setup the virtual machine and install Windows like you normally would (or use our prepared script
**win10install.sh** in **install_tools**). After that
follow the simple steps in the list below.

#. Download fortrace source code inside VM
#. Download additional MSI installers for C++ and Python
#. extract fortrace source code to a folder on the Desktop of your virtual machine
#. open the folder *fortrace/install*
#. start windows_installation.bat

In-depth instructions can be found in :ref:`guestinstall`.


Linux
*****
Setup the virtual machine and install Ubuntu like you normally would (or use our prepared script
**ubuntu19.10.sh** in **install_tools**). After that
follow the simple steps in the list below.

#. Download fortrace source code inside VM
#. extract fortrace source code to a folder on the Desktop of your virtual machine
#. open the folder *fortrace/install*
#. start linux_installation.sh

In-depth instructions can be found in :ref:`guestinstall`.


Installation Service VM
#########################


Here we will describe how to install the Service VM containing third party services that enhance fortrace's capabilities
such as a DHCP server as well as services needed for specific scenarios.

Instructions can be found in :ref:`serviceinstall`.



