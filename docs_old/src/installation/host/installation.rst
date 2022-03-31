=================
Installing fortrace
=================

Proceed with download and installation. Read :doc:`../../introduction/what` to
learn where you can obtain a copy.

Create a user
=============

You either can run fortrace from your own user or create a new one dedicated just
to your test setup.
Make sure that the user that runs fortrace is the same user that you will
use to create and run the virtual machines, otherwise fortrace won't be able to
identify and launch them.

Create a new user::

    $ sudo adduser fortrace --disabled-login --no-create-home

If you're using KVM or any other libvirt based module, make sure the new user
belongs to the "libvirtd" group (or the group your Linux distribution uses to
run libvirt)::

    $ sudo usermod -a -G libvirtd fortrace

.. If you're using VirtualBox, make sure the new user belongs to the "vboxusers"
   group (or the group you used to run VirtualBox)::

..    $ sudo usermod -G vboxusers fortrace


Configure fortrace
================

Per default the Virtual Machine Manager will store the disk-images in a default pool (where a pool is a container to specifing the location in the filesystem for the images). The default pool will store all images to "/var/lib/libvirt/images". By creating a new pool you can change the location, but you have to adjust the path in fortrace, which we will describe now.


To create a new pool::

	$ virsh pool-create-as pool_name_goes_here --type dir --target "/mnt/your_location_goes_here"

Afterwards you have to tell fortrace about the changes by modifying:

$fortrace/src/fortrace/utility/constants.py



Install fortrace
==============

Extract or checkout your copy of fortrace to a path of your choice and run::


    $ pip install . --user

