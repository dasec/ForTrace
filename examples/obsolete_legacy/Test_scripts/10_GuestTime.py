# This is is script template, aiming to allow easy scenario definitions with full reporter functionallity but
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
    print("Import error! in 10_GuestTime.py " + str(ie))
    exit(1)

#############################################
#               Values to define            #
#############################################
##### Scenario Metadata #####
export_dir = "/data/export/"
vm_name = "Scenario{0}".format(random.randint(0, 9999))
author = "Stephan Maltan"
creation_date = date.today().strftime('%Y-%m-%d')
hostplatform = "windows"

##### SMB Server Data #####
smb_share = r"\\192.168.103.66\sambashare"
smb_user = "service"
smb_pass = "fortrace"

##### Email Data #####

##### Beginning Date of the scenario #####
# System time that will be set on first startup
# use None for current date
scenario_start = "2021-08-07 08:32:15"

#############################################
#       Space for additional content        #
#############################################
textfile1_text = "Lorem ipsum dolor sit amet et dolore magna aliqua.\n Ut enim ad minim veniam,  consequat."

#############################################
#               Initialization              #
#############################################
macsInUse = []
guests = []

logger = create_logger('fortraceManager', logging.DEBUG)

guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
guest = virtual_machine_monitor1.create_guest(guest_name=vm_name, platform=hostplatform, boottime=scenario_start)
sc = scenH.Scenario(logger, Reporter(), guest)

sc.Reporter.add("imagename", vm_name)
sc.Reporter.add("author", author)
sc.Reporter.add("baseimage", hostplatform + "-template.qcow2")

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()
guest.guestTimezone()

#############################################
#                Scenario                   #
#############################################

scenH.wait(5,10)
guest.guestTime()
scenH.wait(5, 10)
print("Guest time is: {0}".format(guest.datetime))
guest.guestTimezone()
scenH.wait(5, 10)
print("Guest timezone is: {0}".format(guest.timezone))
scenH.wait(5,10)
sc.addUser("Josef", "123", "needle")
scenH.wait(5,10)
sc.changeUser("Josef", "123", "needle")
scenH.wait()
sc.reboot("2021-08-19 10:52:12")
scenH.wait()
sc.addUser("Bob", "123", "needle")
scenH.wait()
sc.changeUser("Bob", "123", "needle")
sc.reboot("2021-09-19 10:52:12")
sc.deleteUser("Josef", "keep", "needle")
sc.shutdown()
logger.info("Creating report")
sc.Reporter.generate(export_dir)
