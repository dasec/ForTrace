The **ForTrace** framework was published at the Digital Forensics Research Workshop '22 (EU). The article can be freely downloaded from [Digital Investigation](https://www.sciencedirect.com/science/article/pii/S2666281722000130).

The reference to this article is: Thomas Göbel, Stephan Maltan, Jan Türr, Harald Baier, and Florian Mann. "ForTrace - A holistic forensic data set synthesis framework". In: Forensic Science International: Digital Investigation, 40 (2022).

# What is ForTrace
ForTrace is a tool that aims towards the automatic generation of traffic through multiple applications. Supported applications
include Firefox, Thunderbird, Pidgin and a variety of botnet attacks. There are further applications
ForTrace can emulate user input for, but they are of little interest for the generation of network traffic.

## What do different console outputs mean

There are different categories of outputs:
1) notset
1) debug
1) info
1) warning
1) error
1) critical

For info there are different starting symbols describing different actions:
- \[i] means: Information; May mean, that a function is not fully implemented yet.
- \[~] means: Task started and in progress.
- \[+] means: Task successfully ended.
- \[X] means: There have been errors and the program has been terminated.

## Where do I find the documentation?

**Important - The Sphinx documentation is currently being updated to reflect recent changes and additions to the framework and will be updated here as the next version of ForTrace is made public. For immediate information, we recommend the wiki or contacting the authors.**

Ready compiled html version of the documentation can be found in ```docs/build```. The [wiki](https://github.com/dasec/fortrace/wiki) attached to this repository also contains all information needed to install and run ForTrace and will be updated and maintained alongside the Sphinx documentation.

The documentation can be found in ```docs/src/```. As the folder name suggests this only contains the source 
files of the documentation. In order to get it in readable format you need to install sphinx and inside the folder
run the command ```make html```. After this you will find the newest documentation in HTML format in the subfolder
```_build/html```. Just open the index.html with the browser of your choosing.

[1] http://www.sphinx-doc.org/en/master/# for documentation pip install -U Sphinx for installation

## Installation Host

The partially automated installation requires just a few steps to set up the host components of ForTrace.

First, make sure the name of the user and your chosen paths for the virtual machine data, the location of your cloned ForTrace
repository and the path to your tcpdump binary you want to install ForTrace on is correctly configured in **config.json**
This is important, since the setup script later adds this user to the libvirtd-group,
which is required to create clones of the virtual guest machines.

A new user can be added with the following command:

    $ sudo adduser fortrace

If you want to install ForTrace on a new user, please create that user **before** running any part of the installation process.
Additionally, it is imperative to give the new user root permissions as the installation script has to be called with sudo.

   $ sudo usermod -a -G sudo fortrace

In these two examples replace **fortrace** with a username of your choice. Make sure it matches the username in **config.json**.
You will also need to make several other adjustments, most importantly allowing you new user to access GUI functionalities.
An easy way to do so is editing the **.bashrc** file by adding **export DISPLAY=:0** (**NOTE:** You may need to add a different value -
check before altering your **.bashrc** file.). Then run **xauth**, exit the console session, call **xhost +** and switch to your chosen
new user. This is one of multiple ways of allowing GUI functions for a new user.

**NOTE:** Please adjust the username and ID in **config.json, fortrace-pool.xml** and **backing-pool.xml**.


To run the following commands, you will need to download ForTrace now.
ForTrace can be found here: [Github link](https://github.com/dasec/fortrace).
Clone or download the repository and navigate into **/install_tools**.

In this folder, you will find a shell script called **linux_installation.sh**. To install the further parts of ForTrace's
host component, run the script initially **without** root privileges (you will be asked to enter your password once the script starts) and choose **h** when the console prompts you to make a choice. The
script will then install all necessary packages including the appropriate Python version.

    $ ./linux_installation.sh
    Please choose if this installation is host (h) or guest (g) side installation:
    Selection: h
    ...


## Installation Guest

### Windows

The first step in creating your virtual Windows 10 guest is creating the virtual machine. To do this, you will need to
obtain a Windows 10 image. We recommend downloading an ISO-file from an official source.

Next, you need to set up the virtual machine.
While this can be done via the graphical interface of the **virt-manager**, we recommend running the **win10install.sh**
install script found in the **install_tools** folder

       $ sudo ./win10install.sh path/to/isofile

or simply copying the command seen below:

       $ virt-install --name windows-template \
        --ram 4096 \
        --vcpus sockets=1,cores=2,threads=1 \
        --disk pool=fortrace-pool,bus=sata,size=40,format=qcow2 \
        --cdrom /home/fortrace/Win10_1903_V1_German_x64.iso \
        --network network=public \
        --network network=private \
        --graphics spice,listen=0.0.0.0 \
        --noautoconsole \
        -v

      $ sudo chown [user] [path-to-pool]windows-template.qcow2


Either method would require you to adapt the **--cdrom** parameter with the correct path and name of your installation
medium. You might also want to change **--ram**, **disk space (size)** or **--vcpus** depending on your available resources. When starting the
virtual machine, make sure to name your primary user **fortrace**. Additionally, it is important **not** to set a password
when first starting the guest component. Otherwise, ForTrace will be unable to log into the default chosen user. If, for any
reason the auto login does not work with your Windows 10 guest component,
[this link](https://support.microsoft.com/en-us/help/324737/how-to-turn-on-automatic-logon-in-windows) should guide you
through the process of (re-)enabling auto login.

**Note** - Windows 11 guests can be installed using the same method, with a specific installation script **win11install.sh** being provided with the next update in the same folder as the Windows 10 script.

### Windows installation - automated

While most of the installation of the Windows guest can be automated, a few steps have to be done manually.

First and foremost, ForTrace has to be downloaded and moved or copied to your desktop.
It can be found [here](https://github.com/dasec/fortrace).

Next, you simply have to run **install.bat** with admin privileges. It is located in the **install_tools** folder. This will install two .msi files
located in the same folder.


### Ubuntu

The first step in creating your virtual Ubuntu guest is creating the virtual machine. To do this, you will need to
obtain a Ubuntu image. We recommend downloading an ISO-file from an official source.

**Important - The installation script may still be named after Ubuntu version 19.10, but is compatible with the newest Ubuntu version (22.04 LTS). The rest of the installation is largely compatible with Ubuntu but currently in the process of being tested.**

Next, you need to set up the virtual machine.
While this can be done via the graphical interface of the **virt-manager**, we recommend running the **ubuntu19.10install.sh**
install script found in the **install_tools** folder

       $ sudo ./ubuntu19.10install.sh path/to/isofile

or simply copying the command seen below:

       $ virt-install --name linux-template \
        --ram 4096 \
        --vcpus sockets=1,cores=2,threads=1 \
        --disk pool=fortrace-pool,bus=sata,size=40,format=qcow2 \
        --cdrom /home/fortrace/ubuntu-19.10-desktop-amd64.iso \
        --network network=public \
        --network network=private \
        --graphics spice,listen=0.0.0.0 \
        --noautoconsole \
        -v

      $ sudo chown [user] [path-to-pool]linux-template.qcow2



Either method would require you to adapt the **--cdrom** parameter with the correct path and name of your installation
medium. You might also want to change **--ram** or **--vcpus** depending on your available resources. When starting the
virtual machine, make sure to name your primary user **fortrace**. During your initial setup, you will be asked for your
user credentials. On this screen, it is important to choose the option **Log in automatically**. This is required for
ForTrace, so no manual user inputs are needed on the guest side when synthesizing traffic. If your auto login does not
work, this [guide](https://help.ubuntu.com/stable/ubuntu-help/user-autologin.html.en) will help you activate it after
setting up your host machine.


Once you are able to start the virtual machine and the OS has been installed and initialized, you should eject the installation medium.

### Ubuntu installation - automated


The automated installation for a guest running Ubuntu is similar to the installation of the host machine described in the [host chapter](https://github.com/dasec/fortrace/wiki/Host-Installation).

First and foremost, ForTrace has to be downloaded and moved or copied to your desktop.
It can be found [here](https://github.com/dasec/fortrace).

Next, you will want to install all applications used to generate traffic. Both Firefox and Thunderbird are the default
mail and browsing applications used by ForTrace.

After ForTrace has been downloaded and your traffic generating application have been installed, simply navigate into **install_tools** and run **linux_installation.sh** and choose the option
for the guest installation. You will be asked to enter your password as root privileges are required for parts of the installation. Do not execute the entire script
as root (with sudo).

    $ ./linux_installation.sh
    Please choose if this installation is host (h) or guest (g) side installation:
    Selection: g
    ...


This will install Python and then run the **pre_setup.py** with the **vm** parameter to start installing all
necessary python modules.


A more in-depth explanation of the installation can be found [here](https://github.com/dasec/fortrace/wiki).


