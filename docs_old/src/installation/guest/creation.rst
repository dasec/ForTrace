========================================
Creation of the Virtual Machine Template
========================================

In order to create and control virtual machines during fortraces runtime specific templates have to be generated. The creating are described for Kernel Based Virtual Machine (KVM).


Windows
=======

General:
	* Get a Windows-Installation-Image or DVD (Windows 7 is recommended)
	* See `Windows 7 system requirements <http://windows.microsoft.com/en-us/windows7/products/system-requirements>`_ for minimal Hardware Settings

For Windows the following steps have to be done:

* Create a virtual machine using virtual Machine Manager (VMM)
	* Start VMM (virt-manager)
	* Press button "Create a new Virtual Machine" and use the name "windows_template".
	* As Installation-Image choose an available Windows-Installation-Medium
	* Afterwards configure the Hardware (recommended: 2 GB RAM, 2 CPU-Cores, 25 GB hard disk size)
	* Being asked for a disk-image, create a qcow2 diskimage named windows_template.qcow2
	* Follow the next instructions until the last screen (step 5) will be show up, which provides the option to modify the VM before the installation starts. Select this option. On top of this you are able to modify the default network interface in the advandced section. Provide the informations needed for the local (or internet, the order doesn't matter, but will make some steps easier to follow) common network interface and continue.
	* It is recommended to change the Video-Mode to QXL later on
	* The only thing left, is to add the second network devices for the internet (or local) network. Therefor you have to choose the Button to add hardware. Find the Network-section and choose the appropriate interface.
	* Start the vm and install Windows with *fortrace* as username


 * Using the shell::

    $virt-install --name windows-template \
     --ram 4096 \
     --vcpus sockets=1,cores=4,threads=4 \
     --disk pool=fortrace-pool,bus=sata,size=50,format=qcow2 \
     --cdrom de_windows_7_professional_with_sp1_x64_dvd_u_676919.iso \
     --network network=public \
     --network network=private \
     --graphics spice,listen=0.0.0.0 \
     --noautoconsole \
     -v


Linux
=====

General:
	* Download Ubuntu-Image (14.04 LTS 64-bit recommended)
	* See `SystemRequirements`_ for proposed Hardware-Specifications
	* There exists two ways of creating a vm, which are described in following

* Using virt-manager:
	* Addopt all steps from the windows section, but
		* Use "ubuntu_template" as name
		* As Installation-Image choose a the downloaded ubuntu-image (Ubuntu 14.04 is recommended).
		* Adjust hardware requirement (recommended: 1 GB RAM, 2 CPU-Cores, 10 GB hard disk size)
		* Being asked for a disk-image, create a qcow2 diskimage named ubuntu_template.qcow2
.. _`SystemRequirements`: https://help.ubuntu.com/community/Installation/SystemRequirements

or

* Using the shell::

	$ virt-install --name ubuntu_template \
	--ram 1024 \
	--disk path=/var/lib/libvirt/images/ubuntu_template.qcow2,bus=virtio,size=10,format=qcow2 `#disk image location` \
	--cdrom ~/Downloads/ubuntu-14.04.2-desktop-amd64.iso `#ubuntu-image location`\
	--network bridge=br0 `#choose the correct interface for local`\
	--network bridge=br1 `#choose the correct interface for internet`\
	--graphics vnc,listen=0.0.0.0 \
	--noautoconsole \
	-v


* It is recommended to change the Video-Mode within virt-manager to QXL
* Start the vm and install Ubuntu with *fortrace* as Username

Spice-Configuration (optional)
==============================

At this point you have to select "Spice" as Display-Type, if you want to use Spice later on. Don't worry, this does not change anything relevant up to now.