.. _hostinstall:

**********************
Host Installation
**********************

The installation of the host component of fortrace can be done automatically using **pre_setup.py** and the corresponding
**config.json** located in the install_tools folder. Please check :ref:`config` before you start any of the installation
scripts and make adjustments where necessary. Please also adjust **fortrace-pool.xml** and **backing-pool.xml** if necessary. If you are using a different Ubuntu distribution than recommended in
:ref:`installindex`, you might need to tweak either file or run a completely manual installation of the host component.

.. Regardless of what method you choose, you first need to install python.
.. TODO PRESETUP -> SETUP PY NOT AS USER    -> SUDO USER ANGEBEN IRGENDWIE -> EXECUTE AS SUDO USER
.. TODO GENERATOR INSTALLATION ?
.. TODO: SETFACL -Rdm OWNER=USER TO fortrace IN AUTOMATION ->  qemu.conf dynamic ownership 0, root root, systemctl start stop INSTEAD OF CHMOD; CHMOD as "workaround" in case of issues X
.. TODO BACKING POOL INSTALL SCRIPTS PATHS & NAMES (VIRT INSTALL) X
.. TODO QEMU CONF CHOWN  RIGHT MANAGEMENT SECTION GUEST     X
.. TODO INSTALLBAT ANPASSEN + TESTEN      X
.. TODO WIKI GITLAB ÜBERNEHMEN

Installation Host -- scripted
####################################

The partially automated installation requires just a few steps to set up the host components of fortrace.

First, make sure the name of the user and your chosen paths for the virtual machine data, the location of your cloned fortrace
repository and the path to your tcpdump binary you want to install fortrace on is correctly configured in **config.json**
This is important, since the setup script later adds this user to the libvirtd-group,
which is required to create clones of the virtual guest machines.

A new user can be added with the following command:

.. code-block:: console

    $ sudo adduser fortrace

If you want to install fortrace on a new user, please create that user **before** running any part of the installation process.
Additionally, it is imperative to give the new user root permissions as the installation script has to be called with sudo.

.. code-block:: console

    $ sudo usermod -a -G sudo fortrace


In these two examples replace **fortrace** with a username of your choice. Make sure it matches the username in **config.json**.
You will also need to make several other adjustments, most importantly allowing you new user to access GUI functionalities.
An easy way to do so is editing the **.bashrc** file by adding **export DISPLAY=:0** (**NOTE:** You may need to add a different value -
check before altering your **.bashrc** file.). Then run **xauth**, exit the console session, call **xhost +** and switch to your chosen
new user. This is one of multiple ways of allowing GUI functions for a new user.

**NOTE:** Please adjust the username and ID in **config.json, fortrace-pool.xml** and **backing-pool.xml**.


To run the following commands, you will need to download fortrace now.
fortrace can be found here: `Github link <https://github.com/dasec/fortrace>`_.
Clone or download the repository and navigate into **/install_tools**.

In this folder, you will find a shell script called **linux_installation.sh**. To install the further parts of fortrace's
host component, run the script initially **without** root privileges (you will be asked to enter your password once the script starts) and choose **h** when the console prompts you to make a choice. The
script will then install all necessary packages including the appropriate Python version.


.. code-block:: console

    $ ./linux_installation.sh
    Please choose if this installation is host (h) or guest (g) side installation:
    Selection: h
    ...


This then runs the **pre_setup.py** with the  **host** parameter to start installing all
necessary packages and python modules. You can also start this script by hand if you choose to do so, although it would
require a manual installation of Python beforehand.

.. TODO Part of linux installation script

.. code-block:: console

    $ sudo python pre_setup.py host

After installing all packages and python modules, the script sets up permissions for the
appropriate user to create clones of the virtual guest environments by creating the libvirtd group and adding
the user mentioned in **config.json** to that group as well as to the libvirt group if present. Additionally, rights for the user to run tcpdump are given.
**pre_setup.py** then creates both the virtual machines pool and the network bridges. If you need to adjust any of the
default paths for your pools or the location of tcpdump, you can do so in **config.json** (see: :ref:`config`)
All of these steps will be described further in the next section **Installation Host -- manual**.

The backing folder, which will contain the differential images created during the execution of fortrace tasks, is currently created
as a pool as well. Refer to the next section in case this causes any issues for you. Alternatively, you could alter **src/fortrace/utility/constants.py**
and remove the necessity for this backing folder.
.. Important note: It is possible, that the **backing** folder inside the created pool location is missing, which
means you have to add it manually before running any **fortrace** commands. If your pool is located in **/data**,
simply add a folder **/data/[pool-name]/backing**. You can also remove **backing** part of the path in
**/src/fortrace/utility/constants.py**

.. TODO: code snippet?

Lastly, fortrace needs to be installed. Navigate into the folder and then run:

.. code-block:: console

    $ python setup.py install --user


Installation Host -- manual
####################################

In case there are any issues with the partially automatic installation, you are using a different Ubuntu distribution
or simply want to adapt the installation process to a different OS, this section will guide you through the entire
host-side installation process.

First, make sure the name of the user and your chosen paths for the virtual machine data, the location of your cloned fortrace
repository and the path to your tcpdump binary you want to install fortrace on is correctly configured in **config.json** (:ref.
This is important, since the setup script later adds this user to the libvirtd-group,
which is required to create clones of the virtual guest machines.

A new user can be added with the following command:

.. code-block:: console

    $ sudo adduser fortrace

If you want to install fortrace on a new user, please create that user **before** running any part of the installation process.
Additionally, it is imperative to give the new user root permissions as the installation script has to be called with sudo.

.. code-block:: console

    $ sudo usermod -a -G sudo fortrace


In these two examples replace **fortrace** with a username of your choice. Make sure it matches the username in **config.json**.

You will also need to make several other adjustments, most importantly allowing you new user to access GUI functionalities.
An easy way to do so is editing the **.bashrc** file by adding **export DISPLAY=:0** (**NOTE:** You may need to add a different value -
check before altering your **.bashrc** file.). Then run **xauth**, exit the console session, call **xhost +** and switch to your chosen
new user. This is one of multiple ways of allowing GUI functions for a new user.

**NOTE:** Please adjust the username and ID in **config.json, fortrace-pool.xml** and **backing-pool.xml**.


By default, only python 3 is installed on the recommended Ubuntu distribution, but fortrace is
currently still running on python 2. The following command should install python 2.7.

.. code-block:: console

    $ sudo apt install python


You can check your python version:

.. code-block:: console

    $ python -V


Next, you need to install the required packages.

.. code-block:: console

    $ sudo apt install python-pip
    $ sudo apt install python-libvirt
    $ sudo apt install qemu-kvm
    $ sudo apt install libvirt-bin
    $ sudo apt install libvirt-dev
    $ sudo apt install virt-manager
    $ sudo apt install libcap2-bin
    $ sudo apt install tcpdump

The required packages can also be found in **/install_tools/packet_requirements.txt**.


In a similar manner, all necessary python packages need to be installed.

.. code-block:: console

    $ pip install -U pywinauto
    $ pip install -U pywin32
    $ pip install -U setuptools
    $ pip install -U selenium
    $ pip install -U marionette_driver
    $ pip install -U netifaces
    $ pip install -U psutil
    $ pip install -U netaddr
    $ pip install -U enum34
    $ pip install -U protobuf==2.5.0

These packages can also be located under **/install_tools/PIP_requirements.txt**.

The default network sniffer chosen by fortrace ist tcpdump. Usually, tcpdump requires root privileges to function
properly, but since it should not be a requirement to run fortrace with root privileges, a simple modification to tcpdump
needs to be made.

.. code-block:: console

    $ sudo setcap cap_net_raw,cap_net_admin=eip /usr/sbin/tcpdump

Naturally, you will need to verify if tcpdump ist located in the folder used by this command an potentially adjust the
path. You can check if the change was successful by entering the following command:

.. code-block:: console

    $ getcap /usr/sbin/tcpdump
    /usr/sbin/tcpdump = cap_net_admin,cap_net_raw+eip     "This is the output you should get"

In case this solution does not work for you, you can simply give tcpdump the necessary privileges:

.. code-block:: console

    $ sudo chmod +s /usr/sbin/tcpdump

Another privilege issue concerns libvirtd and the created fortrace user. Only root and members of the **libvirtd** group
are able to fully access and modify the virtual machine images. To remedy this situation, we first usually have to create
the libvirtd group. After creating the group, we can add the fortrace user to it.

.. code-block:: console

    $ sudo groupadd libvirtd
    $ sudo usermod -a -G libvirtd fortrace
    $ sudo usermod -a -G libvirt fortrace

Following the installation of all necessary packages, we need to create the virtual machine pools. This is were our
guest components original and instanced images are stored. To do so navigate into **install_tools** and run the following four commands:

.. code-block:: console

    $ virsh pool-define fortrace-pool.xml
    $ virsh pool-build fortrace-pool
    $ virsh pool-start fortrace-pool
    $ virsh pool-autostart fortrace-pool

The path **/data/** may have to be created manually beforehand. After running the commands above, you might
want to add a directory named **backing** into **/data/fortrace-pool** - this is where the clones of our guest images
are going to be stored. This can be achieved by simply running the same 4 commands
but replacing **fortrace-pool** with **backing** and **fortrace-pool.xml** with **backing-pool.xml**.

.. code-block:: console

    $ virsh pool-define backing-pool.xml
    $ virsh pool-build backing
    $ virsh pool-start fortrace-pool
    $ virsh pool-autostart fortrace-pool

You can check your pools with the following commands:

.. code-block:: console

    $ virsh pool-list --all
    $ virsh pool-info fortrace-pool


To run the following commands, you will need to download fortrace now.
fortrace can be found here: `Github link <https://github.com/dasec/fortrace>`_.
Clone or download the repository and navigate into **/install_tools**. Here, you will find **private.xml** and
**public.xml**. These two files will help you to set up the network connections needed to communicate between the
guest and the host without tainting the actual internet traffic fortrace is creating. The following set of commands
will use the XML templates provided.

.. code-block:: console

    $ virsh net-define public.xml
    $ virsh net-define private.xml

    $ virsh net-start public
    $ virsh net-start private

    $ virsh net-autostart public
    $ virsh net-autostart private


Similarly to the pools, you can check your created networks:

.. code-block:: console

    $ virsh net-list
    $ virsh net-dumpxml [name]
    $ virsh net-info [name]


Lastly, fortrace needs to be installed. Navigate into the folder and then run:

.. code-block:: console

    $ python setup.py install --user




Template Rights Management
###################################

After installing the host side of fortrace, you need alter the **/etc/libvirt/qemu.conf**. First, you need to stop the libvirt service:

.. code-block:: console

    $ systemctl stop libvirtd.service

Then, find the following section in the config file mentioned above and change the parameters **user**, **group** and **dynamic_ownership**
to look like this:

.. code-block:: console

    # Some examples of valid values are:
    #
    #       user = "qemu"   # A user named "qemu"
    #       user = "+0"     # Super user (uid=0)
    #       user = "100"    # A user named "100" or a user with uid=100
    #
    user = "root"

    # The group for QEMU processes run by the system instance. It can be
    # specified in a similar way to user.
    group = "root"

    # Whether libvirt should dynamically change file ownership
    # to match the configured user/group above. Defaults to 1.
    # Set to 0 to disable file ownership changes.
    dynamic_ownership = 0

The last step is reactivating the libvirt service.

.. code-block:: console

    $ systemctl start libvirtd.service



Troubleshooting
###################################

.. code-block:: console

    $ sudo apt install ebtables  "If there are KVM or firewall errors"
    $ sudo apt install dnsmasq  "If there are general Network issues"
    $ sudo apt install qemu-utils "If KVM gives warnings about performance"
    $ sudo chmod 755 [path/to/**backing**} "If KVM has issues with creating differential images"
