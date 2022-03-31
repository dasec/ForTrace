.. _funcindex:

===================
Functions of fortrace
===================

Currently a selected group of applications is supported by the fortrace framework. An overview can be seen in table X.


+-------------+------------------+---------+-------+
|                                |   Supported on  |
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


Firefox
=======

.. autoclass:: fortrace.application.webBrowserFirefox.WebBrowserFirefoxVmmSide
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
