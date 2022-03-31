.. _service:

##########################
Service VM
##########################


SSH
----------------------
The VM has no GUI. Therefore SSH is necessary to install and configure the needed services.

IP: `192.168.103.123`


.. TODO AS TABLE

User  Password

------  ------

`root` (disabled via SSH)  `fortrace`

`service`  `fortrace`

Backup
--------------
Clean image (without any installations) was cloned under: /data/images/backup/ using the following command:

.. code-block:: console

    $ virt-clone --original debian_service --name debian_service_backup --file /data/images/backing/debian_service_backup.qcow2




Mail Server
+++++++++++++++++++

The Service VM provides a local installation of an SMTP server via **Postfix** and an IMAP/POP3 server via **Dovecot**. Both
components are configured to communicate in the specifically set up local network (see :ref:`hostinstall`). Furthermore, to maximize
the amount of analyzable data, the communication is entirely unencrypted.


Printing System
+++++++++++++++++++

To simulate a network connected printer, the Service VM provides an **ippserver**. This allows the simulation of print jobs on a network
connected printer using the IPP protocol and the UNIX-specific printing system **CUPS**.
The **ippserver** is installed, configured and run using **Docker**.


SMB Network Drive
++++++++++++++++++++

The Service VM also provides an **SMB** service. **SMB** is a protocol generally used to share access of network drives or other utilities.
Similarly to the the mail communication, the **SMB** communication remains unencrypted by default to maximize the amount of analyzable data.

