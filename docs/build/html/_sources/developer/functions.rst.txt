.. _func:

===================
Functions of ForTrace
===================

Currently a selected group of modules is supported by the ForTrace framework.
An overview can be seen in the following table:

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

+-------------------+--------------------------------------------------------------+
|Module             |Available functions / user actions                            |
+===================+==============================================================+
|**Guest/Agent/VMM**|Create and clone virtual machine                              |
+-------------------+--------------------------------------------------------------+
|                   |Establish connection to VM                                    |
+-------------------+--------------------------------------------------------------+
|                   |Start, shutdown, restart VM                                   |
+-------------------+--------------------------------------------------------------+
|                   |Execute other modules                                         |
+-------------------+--------------------------------------------------------------+
|                   |Execute arbitrary commands via CLI/Linux Bash (e.g. SSH)      |
+-------------------+--------------------------------------------------------------+
|                   |Set OS time and date                                          |
+-------------------+--------------------------------------------------------------+
|                   |Send keystrokes                                               |
+-------------------+--------------------------------------------------------------+
|                   |Create network traffic dump (automated)                       |
+-------------------+--------------------------------------------------------------+
|                   |Create memory dump                                            |
+-------------------+--------------------------------------------------------------+
|**File System**    |Copy, move, delete files and folders                          |
+-------------------+--------------------------------------------------------------+
|                   |Change directory                                              |
+-------------------+--------------------------------------------------------------+
|                   |Empty recycle bin                                             |
+-------------------+--------------------------------------------------------------+
|                   |Secure delete files and folders (SDelete)                     |
+-------------------+--------------------------------------------------------------+
|**File Transfer**  |Transfer files between guest and SMB share                    |
+-------------------+--------------------------------------------------------------+
|                   |Transfer files between guest and (S)FTP share                 |
+-------------------+--------------------------------------------------------------+
|                   |Transfer files between guest and NFS share                    |
+-------------------+--------------------------------------------------------------+
|**User management**|Add, delete, change local accounts                            |
+-------------------+--------------------------------------------------------------+
|                   |Logon, logoff desired user                                    |
+-------------------+--------------------------------------------------------------+
|**PowerShell**     |Install, uninstall a program                                  |
+-------------------+--------------------------------------------------------------+
|                   |Launch, terminate a program                                   |
+-------------------+--------------------------------------------------------------+
|                   |Enable, disable UAC                                           |
+-------------------+--------------------------------------------------------------+
|                   |Open Windows explorer                                         |
+-------------------+--------------------------------------------------------------+
|                   |Search for keyword                                            |
+-------------------+--------------------------------------------------------------+
|                   |Attach, detach USB devices                                    |
+-------------------+--------------------------------------------------------------+
|                   |Connect, mount, unmount a network drive                       |
+-------------------+--------------------------------------------------------------+
|                   |Basic file and folder manipulation                            |
+-------------------+--------------------------------------------------------------+
|**Printer**        |Setup software network printer                                |
+-------------------+--------------------------------------------------------------+
|                   |Print files                                                   |
+-------------------+--------------------------------------------------------------+
|**Anti Forensics** |Disable, delete Event Log history                             |
+-------------------+--------------------------------------------------------------+
|                   |Disable Hibernation file                                      |
+-------------------+--------------------------------------------------------------+
|                   |Disable Page file                                             |
+-------------------+--------------------------------------------------------------+
|                   |Disable, empty Recycle bin                                    |
+-------------------+--------------------------------------------------------------+
|                   |Disable, delete Prefetch files                                |
+-------------------+--------------------------------------------------------------+
|                   |Disable, delete Recent files                                  |
+-------------------+--------------------------------------------------------------+
|                   |Disable, delete Thumbcache                                    |
+-------------------+--------------------------------------------------------------+
|                   |Disable, delete MRUs/User Assist                              |
+-------------------+--------------------------------------------------------------+
|                   |Disable, delete File History or Volume Shadow Copy            |
+-------------------+--------------------------------------------------------------+
|                   |Clear jump lists                                              |
+-------------------+--------------------------------------------------------------+
|                   |Set, manipulate, delete arbitrary Registry keys               |
+-------------------+--------------------------------------------------------------+
|**Malware**        |Set up environment (Web server, DNS server, C&C server)       |
|**Synthesis**      |                                                              |
+-------------------+--------------------------------------------------------------+
|                   |Deliver Malware (via dropper, email, download)                |
+-------------------+--------------------------------------------------------------+
|                   |Use persistence mechanisms (search order hijacking, service   |
|                   |creation, Registry manipulation)                              |
+-------------------+--------------------------------------------------------------+
|                   |Execute various commands (upload, download, ...)              |
+-------------------+--------------------------------------------------------------+
|**Firefox**        |Open, close browser                                           |
+-------------------+--------------------------------------------------------------+
|                   |Browse to one, multiple, specific or random websites          |
+-------------------+--------------------------------------------------------------+
|                   |Perform downloads and "right click save as" operations        |
+-------------------+--------------------------------------------------------------+
|                   |Click elements via ID, xpath                                  |
+-------------------+--------------------------------------------------------------+
|                   |Perform logins                                                |
+-------------------+--------------------------------------------------------------+
|**Thunderbird**    |Open, close mail application                                  |
+-------------------+--------------------------------------------------------------+
|                   |Add IMAP, POP3 accounts                                       |
+-------------------+--------------------------------------------------------------+
|                   |Send, receive emails (with or without attachments)            |
+-------------------+--------------------------------------------------------------+
|                   |Fill mailbox artificially                                     |
+-------------------+--------------------------------------------------------------+
|**VeraCrypt**      |Create encrypted container                                    |
+-------------------+--------------------------------------------------------------+
|                   |Mount, unmount encrypted container                            |
+-------------------+--------------------------------------------------------------+
|                   |Transfer data to encrypted container                          |
+-------------------+--------------------------------------------------------------+
|**Pidgin**         |Instant messaging via IRC, Jabber, Bonjour, ...               |
+-------------------+--------------------------------------------------------------+


Core Modules
=============

.. autoclass:: fortrace.core.vmm.Vmm
    :members:

.. autoclass:: fortrace.core.guest.Guest
    :members:

.. autoclass:: fortrace.core.agent.Agent
    :members:

Firefox
=======

.. autoclass:: fortrace.application.webBrowserFirefox.WebBrowserFirefoxVmmSide
    :members:

.. autoclass:: fortrace.application.webBrowserFirefox.WebBrowserFirefoxGuestSide
    :members:

.. autoclass:: fortrace.utility.marionette_helper.MarionetteHelper
    :members:


Thunderbird
===========

.. autoclass:: fortrace.application.mailClientThunderbird.MailClientThunderbirdVmmSide
    :members:

.. autoclass:: fortrace.application.mailClientThunderbird.MailClientThunderbirdGuestSide
    :members:


VeraCrypt (command-line)
========================

.. autoclass:: fortrace.application.veraCryptWrapper.VeraCryptWrapperVmmSide
    :members:

.. autoclass:: fortrace.application.veraCryptWrapper.VeraCryptWrapperGuestSide
    :members:

User Administration
===================

.. autoclass:: fortrace.application.userManagement.UserManagementVmmSide
    :members:

.. autoclass:: fortrace.application.userManagement.UserManagementGuestSide
    :members:

File Management
===============

.. autoclass:: fortrace.application.fileManagement.FileManagementVmmSide
    :members:

.. autoclass:: fortrace.application.fileManagement.FileManagementGuestSide
    :members:


Anti Forensics
===============

.. autoclass:: fortrace.application.antiForensics.AntiForensicsVmmSide
    :members:

.. autoclass:: fortrace.application.antiForensics.AntiForensicsGuestSide
    :members:

PowerShell
==========

.. autoclass:: fortrace.application.powerShell.PowerShellVmmSide
    :members:

.. autoclass:: fortrace.application.powerShell.PowerShellGuestSide
    :members:

.. TODO ref modules, add comments - powerShell, antiForensics,


..
    Set System Time
    ===============

    .. autoclass:: fortrace.utility.clockmod
        :members:


Reporter
========
The Reporter class has been added to the framework for different reasons.

.. automodule:: fortrace.core.reporter
   :members:
