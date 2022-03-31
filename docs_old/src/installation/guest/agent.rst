====================
Installing the Agent
====================

Windows
-------

* Open cmd and change to *fortrace\\*
* Execute::

	> python setup.py install

* Add a shortcut from  fortrace\\examples\\startGuestAgent.bat to the Windows Autostart-folder


Optional: WinAdminAgent
-----------------------

WinAdminAgent is needed for manipulating the System time on Windows VMs for simulating long (in-)activity sessions.

* Open the Windows Task Scheduler
* Add a new Task for running Python with the runwinadminagent.py script
* Make sure you select run on logon and select the 'System' User as parameters
* The Admin Agent will now run in the background whenever a Desktop session begins.


Linux
-----

* Checkout and install fortrace (in the following we will assume *fortrace* containing the fortrace repository)::

	$ pip install --user fortrace/



* Configure Ubuntu to start guestAgent.py on every system startup:


	Create startup script (Removed multiline character > from shell-output for easier copy-and-paste). The sleep-command tries to cover the time the DHCP needs set the IP-addresses
		::

			$ cat > ~/.config/autostart/bash.desktop <<EOL
			[Desktop Entry]
			Type=Application
			Exec=/usr/bin/gnome-terminal -e "bash -c 'sleep 45 && python /home/fortrace/fortrace/examples/guestAgent.py; bash'"
			Hidden=false
			NoDisplay=false
			X-GNOME-Autostart-enabled=true
			Name=StartAgent
			EOL
