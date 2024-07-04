.. _serviceinstall:

***************************
Installation of Service VM
***************************

The recommended OS for setting up the service VM is a minimal install of debian 10. Since the service VM will ideally be running constantly,
using only the most necessary of resources is preferred. Since this VM will most likely have no graphical interface, you will need to access it
using SSH.


.. code-block:: console

    $ virt-install
    --name service_vm
    --ram 512
    --disk path=/var/lib/libvirt/images/service_vm.qcow2,bus=virtio,size=10,format=qcow2
    --cdrom <iso-file-of-linux-distribution>
    --network bridge=br0
    --network bridge=br1
    --graphics vnc,listen=0.0.0.0
    --noautoconsole -v

We recommend using the Service-VM provided by us `here <https://hessenbox.tu-darmstadt.de/dl/fiVMPTSEjfKCTjHfLpVYpRLF/.zip>`_.

If you have decided to use the service VM image we provide, you will need to perform a few steps to enable all functionalities.
First, you will need to add your public and private networks manually. This can be done using **virt-manager**.
Next, start the VM and log in as **root** with the password **fortrace**. Run the commands **dhclient** and **dnsmasq**, then
**systemctl stop cups**. Finally, run the **Print Service** installation seen below. If you reboot the service VM you will need to perform
these steps again (with the exception of adding the networks and potentially **dnsmasq**).

Once you have performed these steps, run **ip addr** to display the service VM's ip address. This is important since the generator
needs the address to perform various services. The IP address will look like this: **192.168.103.xxx** with **103** indicating that it
is an IP address of the **public** network. Naturally, this will change if you decide to configure your networks differently.



**Login data for provided service VM:**

+---------------------+--------------+
| **User**            | **Password** |
+---------------------+--------------+
| root (SSH disabled) | hystck       |
+---------------------+--------------+
| service             | hystck       |
+---------------------+--------------+


Print Service
...................

To install the virtual printer, only a few steps are necessary. First, clone the **ippsample** tool repository:

.. code-block:: console

    $ git clone https://github.com/istopwg/ippsample.git

Navigate into the downloaded folder:

.. code-block:: console

    $ cd ippsample

Build the container:

.. code-block:: console

    $ docker build -t ippsample .


You may need an updated version of docker to install the print service. Find a guide on how to install the correct docker version `here <https://docs.docker.com/engine/install/ubuntu/>`_.

Before starting the service, you need to disable encryption. To do so, a few configuration need to be changed.

.. code-block:: console

    $ docker run --name ippserver -d --rm -it -p 631:631 ippsample /bin/hash

    $ docker exec -it ippserver bash -c "mkdir -p config/print && echo Encryption Never > config/system.conf && touch config/print/name.conf"


After completing the steps above you have to simple start the service.

.. code-block:: console

    $ docker exec -it ippserver bash -c "ippserver -v -p 631 -C /config"


SMB Service
...............

To install the SMB server, two steps need to be followed:

1. Install **samba** packet.

.. code-block:: console

    $ apt-get install samba

2. Create a **samba** user.

.. code-block:: console

    comment = samba
    path = /home/samba_share
    read only = no
    browsable = yes

Make sure to adjust any of the above parameters to your preferences.




Mail Server
................

First we will start with the SMTP server which is primarily responsible for forwarding and storing of mails.


.. code-block:: console

    $ sudo apt-get update
    $ sudo apt-get install install postfix

Next, edit the Postfix config files.
Edit /etc/postfix/main.cf:

.. code-block:: console

    $ myhostname = localhost
    $
    $ mydomain = fortrace.local
    $
    $ myorigin = $mydomain
    $
    $ inet_interfaces = all
    $
    $ inet_protocols = all
    $
    $ mydestination = $myhostname, localhost.$mydomain, localhost, $mydomain
    $
    $ mynetworks = 192.168.1.0/24, 127.0.0.0/8
    $
    $ home_mailbox = Maildir/

Restart postfix to apply the changes:

.. code-block:: console

    $ systemctl restart postfix

Now, create a test user called "fortrace":

.. code-block:: console

    $ /usr/sbin/adduser fortrace
    $ passwd <type_a_password_of_your_choice>

Next we will install the IMAP/POP3 server:

.. code-block:: console

    $ sudo apt-get install dovecot

Similarly to the SMTP installation, we will need to edit the dovecot config files.

First /etc/dovecot/dovecot.conf:

.. code-block:: console

    $ protocols = imap pop3 lmtp

Next, edit /etc/dovecot/conf.d/10-mail.conf:

.. code-block:: console

    $ mail_location = maildir:~/Maildir

Finally, add the following lines to the unix_listener auth-userdb bracket in /etc/dovecot/conf.d/10-master.conf:

.. code-block:: console

    $ user = postfix
    $ group = postfix

Restart the service.

.. code-block:: console

    $ systemctl restart postfix



You can also set up a NFS-server.

Host side installation:

.. code-block:: console

    $ sudo apt-get install nfs-kernel-server
    $ sudo systemctl start nfs-server

Then add the following line to /etc/exports/:

.. code-block:: console

    $ <path_to_your_nfs_directory> *(rw,sync,no_root_squash,subtree_check,nohide)

Apply changes and restart service:

.. code-block:: console

    $ sudo exportfs -a
    $ sudo systemctl restart nfs-server


Client side installation:

Mount the directory on Windows client:

.. code-block:: console

    C:\ mount -o nolock <ip_host_vm>:/<mnt_path_host_vm> z:


(Optional) Enable write permission on windows client:

- Open "regedit".
- Browse to "HKEY_LOCAL_MACHINESOFTWAREMicrosoftClientForNFSCurrentVersionDefault".
- Create a new "New DWORD (32-bit) Value" inside the "Default" folder named "AnonymousUid" and assign the value 0.
- Create a new "New DWORD (32-bit) Value" inside the "Default" folder named "AnonymousGid" and assign the value 0.
- Reboot the machine.

Auto startup on windows:

- Press Windows+R, then type "shell:startup"
- Create a .bat file containing following commands:

.. code-block:: console

    @echo off
    net use z:  \\<ip_host_vm>\<mnt_path_host_vm>



Mount directory on Linux client:

.. code-block:: console

    $ sudo mount -t nfs4 -o proto=tcp,port=2049 <ip_host_vm>:/<mnt_path_host_vm> <mnt_path_guest_machine>


Installing NFS server
-----------------------

To install an NFS server, a few steps need to be taken.

First, run the following commands:

.. code-block:: console

    $ sudo apt update
    $ sudo apt install nfs-kernel-server
    $ sudo apt install portmap


You can lock the access to the NFS services by adding the following line to /etc/hosts.deny:

.. code-block:: console

    rpcbind mountd nfsd statd lockd rquotad : ALL

Then you can modify /etc/hosts.allow to allow certain IP addresses to access the NFS server.

.. code-block:: console

    rpcbind mountd nfsd statd lockd rquotad : example_IP : allow
    rpcbind mountd nfsd statd rquotad : ALL : deny

You can skip these two steps since the guest VM ip addresses are currently given random within a range.

Next, create the folder NFS will use and modify the ownership attributes:

.. code-block:: console

    $ sudo mkdir /var/nfsroot
    $ sudo chown nobody:nogroup /var/nfsroot

The penultimate step is modifying the /etc/exports file by adding an entry with the service VM's ip address.

.. code-block:: console

    /var/nfsroot     192.168.103.[xxx]/17(rw,root_squash,subtree_check)

Next, update the exported file systems:

.. code-block:: console

    $ sudo exportfs -ra

Lastly, restart the NFS service.

.. code-block:: console

    $ sudo systemctl restart nfs-kernel-server










**Note**: If you want to use the generator's current functions that use a NFS server to maintain file transfer data, we recommend
installing an NFS server on your **host machine** or at least connecting your **host** to the NFS server as a client.



DHCP
====

Here comes a quick introduction for configuring dnsmasq to serve as a DHCP-Server.

Configuration
#############

The following config parameters need to be adjusted:
::

	$ cat /etc/dnsmasq.conf

	...
	interface=eth0
	interface=eth1
	...
	dhcp-range=eth0,192.168.2.10,192.168.2.254,12h
	dhcp-range=eth1,192.168.3.10,192.168.3.254,12h
	...

	$ sudo ifconfig eth0 192.168.2.2
	$ sudo ifconfig eth1 192.168.3.2

	$ sudo service dnsmasq restart

Be aware that you have to replace the IP-Range as well as the interfaces based on your system configuration. The interfaces should be the ones
connected to the bridges br0 and br1.

.. TODO install instruction service VM including DHCP server


####################
Malware Service
####################

We recommend using either Windows Server or Windows 10 as the basis of the Malware Service VM. An easy solution would be to clone
the Windows guest template **after** you have already pulled the ForTrace repository.

Additionally, *Microsoft Visual C++ Redistributables* and a current Python version need to be installed. Python is used to provide
the HTTP malware download scenarios with a webserver.

You will also need to allow and install *OpenSSH* on the Windows Service VM.

#. Go to Setting.
#. Go to Apps.
#. Go to Apps & features.
#. Go to Optional features.
#. Choose *Add a feature*.
#. Locate *OpenSSH server*.
#. Select Install.

In case you are running the Service VM on a Windows 11 machine, installing OpenSSH will look like this:

#. Go to Setting.
#. Go to Apps.
#. Go to Optional features.
#. Click *View features*.
#. Locate *OpenSSH server*.
#. Select Install.

The *MalwareServer* found in the root directory of the repository can now be extracted. Check */MalwareServer/server_config.txt*
to amend paths and amend IP addresses here and in the *MalwareBot* code if needed. All that is left is to execute the Malware Server code on the VM.

There need to be some adjustments on the **Windows guest template** as well. *Microsoft Visual C++ Redistributables* need to be
installed here as well. It is also recommended to deactivate *Windows defender* if you choose to use the sample *MalwareBot*.
Furthermore deactivating UAC is recommended, as it is preventing the creation of services.
There are multiple ways to disable UAC, one of them is PowerShell:

.. code-block:: console

    C:\ New-ItemProperty -Path 'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\policies\\system' -Name 'EnableLUA' -PropertyType 'DWord' -Value 0 -Force

You may also need to install Office 365 or an alternative that can deploy macros to access the dropper component of this module.




