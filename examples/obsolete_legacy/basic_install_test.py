# This is a basic functionality test for the setup
# it will run the vm and browse to a website
# while the script is running you can verify the behaviour by opening the vm
#
# The script was written for evaluation purposes
# creator: Thomas Schaefer
# date: 5.12.18
#
from __future__ import absolute_import
import time
import logging
from fortrace.core.vmm import Vmm
from fortrace.utility.logger_helper import create_logger
from fortrace.core.vmm import GuestListener

# Instanciate VMM and a VM
logger = create_logger('fortraceManager', logging.DEBUG)
macsInUse = []
guests = []
guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
guest = virtual_machine_monitor1.create_guest(guest_name="tbtest", platform="windows")

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()


# do some basic stuff
browser_obj = None
browser_obj = guest.application("webBrowserFirefox", {'webBrowser': "firefox"})
browser_obj.open(url="faz.net")
time.sleep(20)
browser_obj.close()


# We are done, shutdown and keep the VM on disk
guest.shutdown("keep")
