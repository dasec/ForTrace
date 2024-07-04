.. _installindex:

**********************
Installation of ForTrace
**********************

ForTrace is a framework that consists of two distinct parts as we described in
:ref:`Architecture of ForTrace <architecture_index>`. For that reason
it is mandatory to install ForTrace on both, the host and the guest system. In the next sections we will show how that
installation can be done.

Once you have finished the installation process, visit :ref:`firstrun` if you need help getting started with ForTrace.

It is recommended to install the Service VM before you install the guest components.

Configuration of installation paths and values
#################################################

In case you want to use the automated installation scripts for either the host or the guest machines, it is recommended
to read :ref:`config` and make adjustments if necessary before proceeding with the installation.


Installation Host (physical machine)
####################################

Here we will describe how to install the host part of ForTrace on a physical machine.

For this **Ubuntu 22.04** is the recommended OS. Other Ubuntu distributions will work as well, but the automatic setup
script might need some alterations depending on your distribution. Ubuntu versions 19.10 to 22.04 have been tested and are fully compatible.

In-depth instructions can be found in :ref:`hostinstall`.

Installation Guest (virtual machine)
####################################

Here we will describe how to install the guest part of ForTrace on a virtual machine as well as creating said virtual
machine with everything needed for ForTrace to operate correctly.

An in-depth installation manual for both Windows and Ubuntu can be found here: :ref:`guestinstall`.

Windows
*******
Setup the virtual machine and install Windows like you normally would (or use our prepared script
**win10install.sh** in **install_tools**). After that
follow the simple steps in the list below.

#. Download ForTrace source code inside VM
#. Download additional MSI installers for C++ and Python
#. extract ForTrace source code to a folder on the Desktop of your virtual machine
#. open the folder *install_tools*
#. start auto_install.bat or install.bat

In-depth instructions can be found in :ref:`guestinstall`.


Linux
*****
Setup the virtual machine and install Ubuntu like you normally would (or use our prepared script
**ubuntu19.10.sh** in **install_tools**). After that follow the simple steps in the list below.
The name of the install script should not deter you from using it on other versions of Ubuntu as the process should be the same.
Ubuntu 22.04 has been tested with this script.

#. Download ForTrace source code inside VM
#. extract ForTrace source code to a folder on the Desktop of your virtual machine
#. open the folder *install_tools*
#. start linux_installation.sh

In-depth instructions can be found in :ref:`guestinstall`.


Installation Service VM
#########################


Here we will describe how to install the Service VM containing third party services that enhance ForTrace's capabilities
such as a DHCP server as well as services needed for specific scenarios.

Instructions can be found in :ref:`serviceinstall`.



