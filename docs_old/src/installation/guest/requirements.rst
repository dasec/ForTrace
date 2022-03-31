============
Requirements
============

In order to make fortrace working properly, you will have to install some required
software and libraries.

Windows
=======

Spice-Guest (optional)
----------------------

Download and install `Spice-Guest`_ for Copy-and-Paste between Host and Guest.

.. _`Spice-Guest`: http://www.spice-space.org/download.html


fortrace Agent
------------

Next step will download the fortrace-framework and install required python-moduls.


Install Python
^^^^^^^^^^^^^^

Python is a strict requirement for the fortraces agent on the guest component in
order to run properly.

You can download the proper installer from the `official website`_.
Also in this case Python 2.7 is preferred. In order to use pywinauto install a 32-bit version of python (see: `pywinauto-issue`_ ).

Add Python to your %PATH% environment variable to be able to execute python easily from cmd. This can be achieved by executing *win_add2path.py* from %PYTHON_INSTALL_DIR%\\Tools\\Scripts\\ or follow the instructions from `finding-the-python-executable`_

.. _finding-the-python-executable: https://docs.python.org/2/using/windows.html#finding-the-python-executable

.. _pywinauto-issue: https://code.google.com/p/pywinauto/issues/detail?id=12

.. _official website: https://www.python.org/downloads/


pywinauto
^^^^^^^^^

Pywinauto is used to start and control applications. Additionally, it can be used
by implementing new applications.
Download and install `pywinauto`_ via::

    > cd pywinauto-<version>
    > python.exe setup.py install

.. _`pywinauto`: https://code.google.com/p/pywinauto/downloads/list


Pywin32
^^^^^^^

Pywin32 is used for Windows control.
Download and install `pywin32`_ via execution of pywin32-<version>.exe

.. _`pywin32`: http://sourceforge.net/projects/pywin32/


pypa-setuptools
^^^^^^^^^^^^^^^

The Setuptools are required by Selenium.
Download `pypa-setuptools`_ and install with::

    > ./ez_setup.py


.. _`pypa-setuptools`: https://bitbucket.org/pypa/setuptools

Selenium
^^^^^^^^

Selenium is required for the web browser control.
Download `Selenium`_ and install with::

    > cd selenium-<version>
    > python.exe setup.py install

.. _`Selenium`: https://pypi.python.org/pypi/selenium

netifaces
^^^^^^^^^

Install module netifaces::

	> pip install netifaces

enum34
^^^^^^

Install module enum34::

	> pip install enum34

protobuf-2.5.0
^^^^^^^^^^^^^^

Install module protobuf-2.5.0::

	> pip install protobuf==2.5.0

psutil
^^^^^^

Install module psutil::

    > pip install psutil



Web Browser
-----------

Download and install `Firefox`_.

.. _`Firefox`: https://www.mozilla.org/en-US/firefox/new/


For the new-style plugin install 'marionette_driver'::

    > pip install -U marionette_driver


Mail Client
-----------

Download and install `Thunderbird`_.

.. _`Thunderbird`: https://www.mozilla.org/thunderbird/

For the new-style plugin install 'mozprofile' and 'mozrunner'::

    > pip install -U mozprofile
    > pip install -U mozrunner


Instant Messenger
-----------------

Download and install `Pidgin`_.

.. _`Pidgin`: https://www.pidgin.im/download/

Addionally copy the compiled pidgin_puppet.dll. To do this open cmd:
::

	> mkdir %APPDATA%\.purple\plugins
	> cp fortrace\templates\pidgin_puppet.dll %APPDATA%\.purple\plugins\.

After start Pidgin and activate the plugin via Tools->Plugins in Pidgin.


Linux
=====

We are assuming Ubuntu as Linux-Distribution, other Distribution should be working as well, but you have to change the commands accordingly.
Ubuntu ships with some applications like Python and Thunderbird, thus this tutorial will not describe installing this applications.
fortrace is only tested for Python 2.7, check your python version and keep this in mind if anything does not behave correctly.

Spice-Guest (optional)
----------------------

Download and install Spice-Guest for Copy-and-Paste between Host and Guest::

	$ sudo apt-get install spice-vdagent

Shutdown and power your vm on again (do not restart!), to get the features enabled.


General
-------

Install pip to install python modules::

	$ sudo apt-get install subversion python-pip


Instant Messenger
-----------------

Install Pidgin as IM-Client

	$ sudo apt-get install pidgin


Install Python-Moduls
---------------------

Install netifaces for extracting IP and MAC-informations and selenium for remote controlling firefox:

	$ sudo apt-get install python-dev # netifaces depends on python-dev see `stackoverflow`_
	$ pip install --user netifaces
	$ pip install --user selenium

.. _`stackoverflow` : http://stackoverflow.com/questions/11094718/error-command-gcc-failed-with-exit-status-1-while-installing-eventlet

If you want to use the new-style plugins install the python modules refered under the Windows section under 'Web Browser' and 'Mail Client'.

Install LDTP
------------

LDTP is used for controlling and managing window-actions

	$ wget http://download.freedesktop.org/ldtp/3.x/3.5.x/ldtp-3.5.0.tar.gz
	$ pip install --user ldtp-3.5.0.tar.gz
	$ sudo apt-get install python-gnome2 python-twisted-web2 python-pyatspi

LDTP uses the accessibility feature as interface, therefore we must enable it in gnome

	$ gsettings set org.gnome.desktop.interface toolkit-accessibility true
