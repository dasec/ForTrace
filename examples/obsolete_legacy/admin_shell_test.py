from __future__ import absolute_import
import time
import logging
import subprocess
from fortrace.core.vmm import Vmm
from fortrace.utility.logger_helper import create_logger
from fortrace.core.vmm import GuestListener

# Instanciate VMM and a VM
logger = create_logger('fortraceManager', logging.DEBUG)
macsInUse = []
guests = []
guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
guest = virtual_machine_monitor1.create_guest(guest_name="adminshelltest", platform="windows")


userManagement_obj = None
userManagement_obj = guest.application("userManagement", {})


# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()

#guest.setOSTime("2019-01-01 12:00:00")

userManagement_obj.addUser('John', 'fadf24s')

#guest.runElevated('net user John fadf24as /ADD')

time.sleep(3000)

#guest.shutdown("keep")