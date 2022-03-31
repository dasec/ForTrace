fortrace
=====


Requirements
=====
Ubuntu:
  Packages via sudo apt-get install <package_name>
    python 2.7 
    libvirt-bin
    qemu-kvm

  replace CloneManager.py (Path is /usr/lib/python2.7/dist-packages/virtinst/CloneManager.py) with the install/CloneManager.py
    
  Install a windows vm using kvm (name -> windows-template)
    after installation there are two options
      1. Add the two network devices local and internet to your <vmname>.xml file (see install/windows-template.xml for more details)
      2. replace the /etc/libvirt/qemu/windows-template.xml file with install/windows-template.xml   


