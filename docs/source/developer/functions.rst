.. _func:

===================
Functions of fortrace
===================

Currently a selected group of applications is supported by the fortrace framework. An overview can be seen in the following table:

..
    +-------------+------------------+---------+-------+
    |             |                  |   Supported on  |
    +-------------+------------------+---------+-------+
    | Application | Function         | Windows | Linux |
    +-------------+------------------+---------+-------+
    | Firefox     |                  |         |       |
    +-------------+------------------+---------+-------+
    |             | open             |         |       |
    +-------------+------------------+---------+-------+
    |             | close            |         |       |
    +-------------+------------------+---------+-------+
    |             | browse_to        |         |       |
    +-------------+------------------+---------+-------+
    |             | facebook_login   |         |       |
    +-------------+------------------+---------+-------+
    | Thunderbird |                  |         |       |
    +-------------+------------------+---------+-------+
    |             | open             |         |       |
    +-------------+------------------+---------+-------+
    |             | close            |         |       |
    +-------------+------------------+---------+-------+
    |             | add_imap         |         |       |
    +-------------+------------------+---------+-------+
    |             | send_mail        |         |       |
    +-------------+------------------+---------+-------+
    |             | load_mailboxdata |         |       |
    +-------------+------------------+---------+-------+
    | VeraCrypt   |                  |         |       |
    +-------------+------------------+---------+-------+
    |             | open             |         |       |
    +-------------+------------------+---------+-------+
    |             | close            |         |       |
    +-------------+------------------+---------+-------+
    |             | create_container |         |       |
    +-------------+------------------+---------+-------+
    |             | mount_container  |         |       |
    +-------------+------------------+---------+-------+
    |             | copy_to_container|         |       |
    +-------------+------------------+---------+-------+
    |             | unmount_container|         |       |
    +-------------+------------------+---------+-------+
    |             | delete_container |         |       |
    +-------------+------------------+---------+-------+

+------------------------------+-----------------+----------------+------------+
|Function                      |Protocol         | Windows 7/10   | Ubuntu     |
+==============================+=================+================+============+
|Firefox Browse URL            |HTTP/HTTPS       |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+
|Firefox Click Element         |HTTP/HTTPS       |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+
|Firefox Download              |HTTP/HTTPS       |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+
|Thunderbird receive Email     |POP3/IMAP/IMAPS  |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+
|Thunderbird send Email        |SMTP/SMTPS       |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+
|Thunderbird fill mailbox file |-                |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+
|VeraCrypt create container    |-                |Yes             |Not tested  |
+------------------------------+-----------------+----------------+------------+
|VeraCrypt un-/mount container |-                |Yes             |Not tested  |
+------------------------------+-----------------+----------------+------------+
|Execute console commands      |-                |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+
|Change system clock           |-                |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+
|Multiuser capability          |-                |Yes             |No          |
+------------------------------+-----------------+----------------+------------+
|SSH connection/file transfer  |SSH/SFTP         |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+
|SMB file transfer             |SMB              |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+
|IPP print job                 |IPP              |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+


Firefox
=======

.. autoclass:: fortrace.application.webBrowserFirefox.WebBrowserFirefoxVmmSide
    :members:

.. autoclass:: fortrace.utility.marionette_helper.MarionetteHelper
    :members:


Thunderbird
===========

.. autoclass:: fortrace.application.mailClientThunderbird.MailClientThunderbirdVmmSide
    :members:


VeraCrypt (command-line)
========================

.. autoclass:: fortrace.application.veraCryptWrapper.VeraCryptWrapperVmmSide
    :members:

User Administration
===================

.. autoclass:: fortrace.application.userManagement.UserManagementVmmSide
    :members:

Set System Time
===============

.. autoclass:: fortrace.utility.clockmod
    :members:

Elevated Shell Commands
=======================

(Network Share)
===============

(Network Printer Simulation)
============================

Reporter
========
The Reporter class has been added to the framework for different reasons.

.. automodule:: fortrace.core.reporter
   :members:
