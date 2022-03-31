.. _config:

######################################
Configuration of installation options
######################################

This short chapter will guide you through the **config.json** file located in **install_tools** to help you adjust
necessary information for your fortrace installation on both the host and guest machines. Please adjust this information
**before** running any of the installation scripts.


config.json
#############

.. literalinclude:: ../../../install_tools/config.json
    :language: json


* **User**: Here you can adjust the user in case you are not using the default fortrace user name. This is necessary, because certain important privileges (e.g. rights to the libvirtd group) will be assigned to that user.




* **pip-requirements**: No adjustments are needed here. The required python modules will remain the same regardless of your system.



* **packet-requirements**: No adjustments are needed here. The required packages will remain the same regardless of your host machine's specifications.



* **fortrace-path**: This value should be altered if you do not move fortrace to your desktop or have moved it from your desktop to a different location.



* **tcpdump -> path**: There should not be any adjustments needed here - however, it is possible that tcpdump is installed in a different location on your host machine. If that is the case, please adjust the location here so the required changes can be performed by the install script.



* **libvirt-pools -> path**: This can be changed at your discretion. After changing (or keeping the default value), please ensure that the directory exists.



* **libvirt-pools -> name**: This can be changed at your discretion. After changing (or keeping the default value), please ensure that the directory exists.



* **network-interfaces -> public-interface-config-file**: You can adjust this value to incorporate your own config file. It is recommended to use (and, if needed, adjust) the default template.



* **network-interfaces -> private-interface-config-file**: You can adjust this value to incorporate your own config file. It is recommended to use (and, if needed, adjust) the default template.



* **network-interfaces -> public-interface-name**: This value can be changed **if** you alter the corresponding public interface config file. It is recommended to keep the default value.



* **network-interfaces -> private-interface-name**: This value can be changed **if** you alter the corresponding public interface config file. It is recommended to keep the default value.


