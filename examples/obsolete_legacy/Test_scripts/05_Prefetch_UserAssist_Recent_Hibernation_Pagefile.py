import time
import logging
import hashlib
import subprocess
import random
import os
from datetime import date

try:
    from fortrace.core.vmm import Vmm
    from fortrace.utility.logger_helper import create_logger
    from fortrace.core.vmm import GuestListener
    from fortrace.core.reporter import Reporter
    import fortrace.utility.scenarioHelper as scenH

except ImportError as ie:
    print("Import error! in fileManagement.py " + str(ie))
    exit(1)

#############################################
#               Values to define            #
#############################################
export_dir = "/data/export/"
vm_name = "Scenario{0}".format(random.randint(0, 9999))
author = "Stephan Maltan"
creation_date = date.today().strftime('%Y-%m-%d')


#############################################
#              Helper Functions             #
#############################################
def generate_file_sh256(filename, blocksize=2 ** 20):
    m = hashlib.sha256()
    with open(filename, "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest()


def wait(min=10, max=60):
    sleeptime = random.randint(min, max)
    time.sleep(sleeptime)



#############################################
#               Initialization              #
#############################################
hostplatform = "windows"
macsInUse = []
guests = []

logger = create_logger('fortraceManager', logging.INFO)
guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
guest = virtual_machine_monitor1.create_guest(guest_name=vm_name, platform="windows")
sc = scenH.Scenario(logger, Reporter(), guest)

sc.Reporter.add("imagename", vm_name)
sc.Reporter.add("author", author)
sc.Reporter.add("baseimage", hostplatform + "-template.qcow2")
#############################################
#                Scenario                   #
#############################################
####### Session 1 #######
# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()
# disable Prefetch, Recent and UserAssist
sc.disablePrefetch()
sc.disableRecentFiles()
sc.disableUserAssist()
sc.disableHibernation()
sc.clearPagefileatShutdown()
sc.reboot()
# Clear remaining Traces
sc.clearPrefetch()
sc.clearUserAssist()
sc.clearRecentDocs()
wait(300,450)
# shut down system
sc.shutdown()
# Scenario finished
logger.info("##############################")
logger.info("#   Scenario completed       #")
logger.info("##############################")
