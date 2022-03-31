from __future__ import absolute_import
import time
import logging
import os
import config as cfg

from fortrace.core.vmm import Vmm
from fortrace.utility.logger_helper import create_logger
from fortrace.core.vmm import GuestListener

imagename = cfg.imagename
author = cfg.author
hostplatform = cfg.hostplatform

# Instanciate VMM and a VM
logger = create_logger('fortraceManager', logging.DEBUG)
macsInUse = []
guests = []


guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
guest = virtual_machine_monitor1.create_guest(guest_name=imagename, platform=hostplatform)

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()

# copy files to smb Share
guest.smbCopy(cfg.sourcePath, cfg.targetPath, cfg.username, cfg.password)


# Cleanupha das
#guest.cleanUp("")
#guest.shutdown('keep')

