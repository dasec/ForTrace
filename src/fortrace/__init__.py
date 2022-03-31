"""This package is used to create and control virtual machines (named guest in the further documentation)
with the purpose to generate benign network traffic.

The architecture of fortrace is as follows:

We need a host system with a hypervisor installed. In our case we used Ubuntu 14.04 and
Kernel Based Virtual Machine (KVM) as Virtual Machine Monitor (VMM) in combination with libvirt.

As guest we installed a Windows 7 template. On the guest we have the agent software running which communicates with the
vmm module on the host.

The following modules are in fortrace package.

* core (classes: Vmm, Guest, Agent)
* application (webBrowser, mailClient, instantMessaging)
* inputDevice (keyboard, mouse)
* utility (network, ipaddr, macaddr, window, line, exceptions, constants, recvall, seleniumkeys, SendKeys)

Additionally a folder with examples exist:

* examples (fortrace_tutorial, setupNetworks, destroyNetworks, guestAgent)

"""
