============================================
Preparing the VMulti Driver for Windows VMs
============================================

Step 1:
Download and install the VC++ 2015 redistributable from.

https://www.microsoft.com/en-us/download/details.aspx?id=48145

Step 2:
Call the prepare_driver.cmd script as admin to enable test-signing mode and reboot.

Step 3:
Install the dirs-Package.cer certificate from one of the subfolders to the trusted certificate publisher store.

Step 4:
You will find a precompiled binary for the VMulti Input Driver under drivers/windows/binaries.
Depending upon your operation systems architecture call the install_driver.cmd script as admin.
You may see a signing warning.
Ignore it and continue with the installation.

Step 5:
Copy the usb-de.conf file from src/fortrace/utility/conf to C:\\.

Step 6:
Run the controlvmulti.exe application to test driver connectivity.
If the application window stays open everything is working fine.
You may run the DevControlServer now.
