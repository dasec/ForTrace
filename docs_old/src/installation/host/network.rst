========================
Creation of the Networks
========================

fortrace relies on two types of networks. The local network will be used for framework configuration traffic, which should not be part of the sniffed traffic. Therefor the monitored traffic will be transfered through a second interface from now on called internet network.

Network Local and Network Internet
==================================

The fortrace-framework has to do some management stuff and therefor uses this network. All server with a hypervisor, which should be used by fortrace have to be reachable through this network. One possibility is to create one bridge on every server with an interface eth0 attached to it. Where eth0 is the interface which is connected to all other servers.

The public network interface will only be used for the "real" traffic and has to have a internet-connection. This could also be done by a second bridge with an attached interface eth1. The interface eth1 is internet-ready.

Possibly you need to remove the default network that virsh installs:

::

$ virsh net-destroy default
$ virsh net-undefine default

Use the following command from the fortrace base directory to create the network interface from the template:

::

$ virsh net-define public.xml
$ virsh net-define private.xml

Start the newly created network with:

::

$ virsh net-start public
$ virsh net-start private

Mark both network as autostart, to ensure they restart after a reboot of the physical host.

::

$ virsh net-autostart public
$ virsh net-autostart private

Check for correctness:

::

$ virsh net-list
$ virsh net-dumpxml NETWORK_NAME

You can use the following command to edit a network via command line. You need to specify an editor on first use.

::

$ virsh net-edit NETWORK_NAME


Alternatively use the following command to update a network definition with an XMl file:

::

$ virsh net-update NETWORK_NAME

DHCP
====

Having a DHCP-Server in place can be handy if you have no existing DHCP-Server or for keeping things separatly.
The DHCP-Server is part of the Service-VM and thus is documented in the according section.





Sample Network Layout
=====================

When you are done with the network configuration your simulation network may look like this:

.. image:: fortrace_network.png

Take a look at the fortrace-controllers ip-address configuration.
All sample scripts expect the controllers ip-address to be static and with the address 192.168.2.2 .

In this sample layout we also decided to setup a separate dhcp-server.
You may put the dhcp-server on the fortrace-controller as well if you don't want to use another machine for this.

Other things we did was to setup two hypervisor-servers with multiple VMs using the bridges br0 for management traffic and br1 for internet or simulation traffic.
We joined the interfaces on each hypervisor with a two hardware-switches (or use vnets on a managed switch) to join the internal networks of each VM.
The internet-switch has an additional connection with the gateway joining the external internet-cloud.
