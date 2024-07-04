.. _service:

##########################
Service VM
##########################

The Service-VM is a collection of tools and services that are needed for specific scenarios.
All of the services are optional and are not mandatory in general.

We decided to use a debian image for the Service-VM, but feel free to choose your favorite linux distribution.
In case you choose a linux distribution other than debian be aware that some commands of this instruction won't work on your VM.
Nevertheless, the changes for the config files will stay the same for each linux distribution.
We recommend using the Service-VM provided by us `here <https://hessenbox.tu-darmstadt.de/dl/fiVMPTSEjfKCTjHfLpVYpRLF/.zip>`_.

If you want to use the full functionality of the ForTrace generator you have to install all of the following services.
Once you have performed these steps, run **ip addr** to display the Service-VM's ip address.
This is important since the generator needs the address to perform various services.
The IP address will look like this: **192.168.103.xxx** with 103 indicating that it is an IP address of the public network.
Naturally, this will change if you decide to configure your networks differently.

SSH
----------------------
The VM has no GUI. Therefore SSH is necessary to install and configure the needed services.

IP: `192.168.103.123`

It is possible that your service VM may have a different IP address. It is recommended to check the ip address before using ForTrace.

Following are the login credentials for the provided VM:

+---------------------+--------------+
| **User**            | **Password** |
+---------------------+--------------+
| root (SSH disabled) | hystck       |
+---------------------+--------------+
| service             | hystck       |
+---------------------+--------------+

.. Backup
--------------
Clean image can be cloned under: /data/images/backup/ using the following command:

.. code-block:: console

    $ virt-clone --original debian_service --name debian_service_backup --file /data/images/backing/debian_service_backup.qcow2




Mail Server
+++++++++++++++++++

The Service VM provides a local installation of an SMTP server via **Postfix** and an IMAP/POP3 server via **Dovecot**. Both
components are configured to communicate in the specifically set up local network (see :ref:`hostinstall`). Furthermore, to maximize
the amount of analyzable data, the communication is entirely unencrypted.


Printing System
+++++++++++++++++++

To simulate a network connected printer, the Service VM provides an **ippserver**. This allows the simulation of print jobs on a network
connected printer using the IPP protocol and the UNIX-specific printing system **CUPS**.
The **ippserver** is installed, configured and run using **Docker**.


SMB Network Drive
++++++++++++++++++++

The Service VM also provides an **SMB** service. **SMB** is a protocol generally used to share access of network drives or other utilities.
Similarly to the the mail communication, the **SMB** communication remains unencrypted by default to maximize the amount of analyzable data.


####################
Malware Service
####################

The Malware module is currently split in two parts. One is the executable Malware component that will create traces on the guest machine.
The other is a DNS and web server which are used to communicate with and control the malware. The following figure will give an overview
of the module's workflow and the integration of the Malware Service VM.

.. figure:: ../../figures/Malware_module_workflow.PNG
    :alt: Malware module workflow.

    Malware module workflow.

Both components of the Malware module are delivered in the *root* directory of this repository. The server component can be configured easily
using *MalwareServer/server_config.txt*. Before starting the Server it is advised to check the config file to amend paths and other attributes to fit your machine.
It is advised to use a Windows virtual machine for this Service VM.