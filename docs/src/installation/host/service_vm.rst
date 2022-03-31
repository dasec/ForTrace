==========================
Creation of the Service VM
==========================

The Service-VM is a collection of tools and services that are needed for specific scenarios. All of the services are optional and are not mandatory in general. If you want to use the full functionality of the fortrace_generator you have to install all of the following services.

We decided to use a debian image for the Service-VM, but feel free to choose your favorite linux distribution. In case you choose a linux distribution other than debian be aware that some commands of this instruction won't work on your VM. Nevertheless, the changes for the config files will stay the same for each linux distribution.

Create Service-VM:
::

	virt-install
	--name service_vm
	--ram 512
	--disk path=/var/lib/libvirt/images/service_vm.qcow2,bus=virtio,size=10,format=qcow2
	--cdrom <iso-file-of-linux-distribution>
	--network bridge=br0
	--network bridge=br1
	--graphics vnc,listen=0.0.0.0
	--noautoconsole -v

This command creates a new VM and connects it to the previously configured networks.

After installing the VM, connect to it and follow the instructions to install optional services.

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

Be aware that you have to replace the IP-Range aswell as the interfaces based on your system configuration. The interfaces should be the ones
connected to the bridges br0 and br1.

Setting up the mail server
==========================

The local mailserver is needed for capturing unencrypted mail traffic. Alternatively you can use any provider to send
and receive mails but their traffic is usually encrypted which restricts network analysis.

SMTP-Server
############

We will start by installing the SMTP-Server first, which is primarily responsible for forwarding and storing of mails.

::

$ sudo apt-get update
$ sudo apt-get install install postfix

Configuring Postfix
*******************

Edit /etc/postfix/main.cf:

::

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

This is just the minimal configuration setup.

Note: The home_mailbox parameter is a relative path to the home directory of the current user. It has to be created beforehand.

For further customization see: http://www.postfix.org/postconf.5.html

Edit /etc/postfix/master.cf

Uncommend the following flag

::

$ -o smtpd_reject_unlisted_recipient=no

This enables you to receive mails from unlisted providers and domains.

Restart postfix to apply the changes:
::

$ systemctl restart postfix

Create a new user:
::

$ /usr/sbin/adduser <username>
$ passwd <type_a_password_of_your_choice>

Install the IMAP/POP3-Server
****************************

Dovecot is used as IMAP/POP3-Server. It is needed for registering accounts within Thunderbird or any other mail client.
Although we technically do not need a IMAP/POP3-Server to send emails, it is mandatory for our mail scenarios.

::

$ sudo apt-get install dovecot

Add following line to the /etc/dovecot/dovecot.conf file:
::

$ protocols = imap pop3 lmtp

Add following line to the /etc/dovecot/conf.d/10-mail.conf file:
::

$ mail_location = maildir:~/Maildir

Finally, add following lines to the /etc/dovecot/conf.d/10-master.conf file (within the unix_listener auth-userdb brackets):
::

$ user = postfix
$ group = postfix

Restart dovecot to apply the changes:
::

$ systemctl restart postfix


Setting up a nfs directory
====================================
**Host side**

Installation of the nfs server:
::

$ sudo apt-get install nfs-kernel-server
$ sudo systemctl start nfs-server

Add following line to the /etc/exports/ file:
::

$ <path_to_your_nfs_directory> *(rw,sync,no_root_squash,subtree_check,nohide)

Apply changes and restart the nfs server:
::

$ sudo exportfs -a
$ sudo systemctl restart nfs-server

**Client side (guest vm)**

(**Windows**)

Mounting the nfs directory on a client vm (Windows)
::

$ mount -o nolock <ip_host_vm>:/<mnt_path_host_vm> z:

(Optional) Enable write permission on windows client:

- Open "regedit".
- Browse to "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\ClientForNFS\\CurrentVersion\\Default".
- Create a new "New DWORD (32-bit) Value" inside the "Default" folder named "AnonymousUid" and assign the value 0.
- Create a new "New DWORD (32-bit) Value" inside the "Default" folder named "AnonymousGid" and assign the value 0.
- Reboot the machine.

Auto startup on windows (guest side)

- Press Windows+R, then type "shell:startup"
- Create a .bat file containing following commands:

::

$ @echo off
$ net use z:  \\<ip_host_vm>\<mnt_path_host_vm>

and put the file into the autostart folder.

(**Linux**)

Mounting the nfs directory on a client vm (Linux)
::

$ sudo mount -t nfs4 -o proto=tcp,port=2049 <ip_host_vm>:/<mnt_path_host_vm> <mnt_path_guest_machine>



Setting up the smb server
==========================
A SMB server is needed to access a typical network share inside a windows machine.
It can be used with the fortrace generator.

Installation of the smb server

::

$ sudo apt-get install samba

Edit the smb.conf with

::

    $ sudo nano /etc/samba/smb.conf <<EOL
    [global]
    workgroup = smb
    security = user
    encrypt passwords = true
    valid users = service

    [sambashare]
    comment = samba
    path = /home/samba_share
    read only = no
    browsable = yes
    EOL

change directory owner to smb user
::

$ sudo chown -R <user>.<user> <path/samba>

::

Add smb password for user
::

$ sudo  smbpasswd -a <user>

::

Seting up the print server
=========================

**Installing the IPP Server**

For the simulation of a printer we use the `ippsample` tool.
In the following we will present the initial setup on a clean debian with docker installed.

Clone the IPPSample Repository

::

    $ git clone https://github.com/istopwg/ippsample.git && cd ippsample


Build the container
::

    $ docker build -t ippsample .



**Starting the IPP Server**

The service has encryption enabled by default. In order to disable it, it is necessary to create certain configs as described in the following.
Within the `debian_service` VM:


::

    docker run --name ippserver -d --rm -it -p 631:631 ippsample /bin/bash
    docker exec -it ippserver bash -c "mkdir -p config/print && echo Encryption Never > config/system.conf && touch config/print/name.conf"


Structure:

::


    ippsample   
    └───config
    │   │   system.conf
    │   └───print
    │       │   <name>.conf



* `system.conf` contains the global `ippserver` config. To disable encryption it should contain `Encryption Never`
* `name.conf` contains config related to the printer (currently empty). `name` is the name of the simulated printer

The service can be started now.
Within the `debian_service` VM:

::

    docker exec -it ippserver bash -c "ippserver -v  -p 631 -C /config"


* The printer is now ready to receive print jobs
* Printed documents are saved in the `/tmp/` directory
