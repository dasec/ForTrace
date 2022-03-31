===========================
Cloning the Virtual Machine
===========================

fortrace will create clones by itself. Nevertheless this page will describe how cloning can be done manually. To be clear, this step is not neccessary!

Windows
=======

Use virt-manager:
	* Rightclick on the windows-vm and select **clone**.
	* Follow the instructions

Linux
=====

* Create a clone by using virt-manager like for a windows vm

or

* Do it from shell

	1. Create a disk-image using the original disk-image as `backing-file <http://wiki.qemu.org/Documentation/CreateSnapshot>`_
	::
		$ qemu-img create -f qcow2 -b /media/KVM-Images/ubuntu_template.qcow2 /media/KVM-Images/l-guest01.qcow2

	2. Clone the original ubuntu-template
	::
		$ virt-clone --connect qemu:///system \
		--preserve-data `#Do not clone disk image`\
		--original ubuntu_template \
		--name l-guest01 \
		--file /media/KVM-Images/l-guest01.qcow2

