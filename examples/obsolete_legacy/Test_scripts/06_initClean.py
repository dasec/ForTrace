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
    print("Import error! in fileManagement.py " + str(ie))
    exit(1)

#############################################
#               Values to define            #
#############################################
##### Scenario Metadata #####
export_dir = "/data/export/"
vm_name = "Scenario{0}".format(random.randint(0, 9999))
author = "Stephan Maltan"
creation_date = date.today().strftime('%Y-%m-%d')

##### SMB Server Data #####
smb_share = r"\\192.168.103.66\sambashare"
smb_user = "service"
smb_pass = "fortrace"

##### Email Data #####

##### Beginning Date of the scenario #####
# set to None to use current date
scenario_start = "2020-12-02 08:32:15"
#############################################
#       Space for additional content        #
#############################################
textfile1_text = "Lorem ipsum dolor sit amet, consectetur adipisici elit, sed eiusmod tempor incidunt ut labore et dolore magna aliqua.\n Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquid ex ea commodi consequat.\nQuis aute iure reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.\n Excepteur sint obcaecat cupiditat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum"


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
    if min >= max:
        max = min + 30
    sleeptime = random.randint(min, max)
    time.sleep(sleeptime)

#############################################
#               Initialization              #
#############################################
hostplatform = "windows"
macsInUse = []
guests = []

logger = create_logger('fortraceManager', logging.DEBUG)
guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
guest = virtual_machine_monitor1.create_guest(guest_name=vm_name, platform="windows", boottime=scenario_start)
sc = scenH.Scenario(logger, Reporter(), guest)

sc.Reporter.add("imagename", vm_name)
sc.Reporter.add("author", author)
sc.Reporter.add("baseimage", hostplatform + "-template.qcow2")
#############################################
#                Scenario                   #
#############################################

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()

# Start as fortrace user and create new user for scenario
sc.addUser("Fred", "jyrL-Lvfah")
sc.changeUser("Fred", "jyrL-Lvfah")
sc.reboot()

# run cleanup at the beginning
wait()
sc.initClean()
logger.info("send next command here!")