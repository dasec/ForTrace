# This is is script template, aiming to allow easy scenario definitions with full reporter functionallity but
import logging
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
hostplatform = "windows"
creation_date = date.today().strftime('%Y-%m-%d')

##### SMB Server Data #####
smb_share = r"\\192.168.103.66\sambashare"
smb_user = "service"
smb_pass = "fortrace"

##### Email Data #####

##### Beginning Date of the scenario #####
# System time that will be set on first startup
# use None for current date
scenario_start = "2021-08-15 08:32:15"

#############################################
#       Space for additional content        #
#############################################
textfile1_text = "Lorem ipsum dolor sit amet et dolore magna aliqua.\n Ut enim ad minim veniam,  consequat."

#############################################
#               Initialization              #
#############################################
macsInUse = []
guests = []

logger = create_logger('fortraceManager', logging.INFO)
guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
guest = virtual_machine_monitor1.create_guest(guest_name=vm_name, platform=hostplatform, boottime=scenario_start)
sc = scenH.Scenario(logger, Reporter(), guest)

sc.Reporter.add("imagename", vm_name)
sc.Reporter.add("author", author)
#sc.Reporter.add("baseimage", hostplatform + "-template.qcow2")
sc.Reporter.add("operatingSystem", hostplatform)

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()
guest.guestTimezone()
#############################################
#                Scenario                   #
#############################################

####### Session 0 #######
# Start as fortrace user and create new user for scenario (recommended)
sc.addUser("Fred", "jyrL-Lvfah")
sc.changeUser("Fred", "jyrL-Lvfah")
# reboot to new user
sc.reboot("2020-12-24 19:52:12")

####### Session 1 #######
# reduce traces left by template creation (recommended)
sc.deleteUser("fortrace", "needle")
sc.initClean()
scenH.wait()
# Start your scenario here




####### Finishing scenario #######
# Either shut down system, or clean up before shutdown
# Remember, that the system has to be shut down manually on manual cleanup

# shut down system (no cleanup)
# sc.shutdown()

# automatic shutdown (with cleanup, leaves artifacts for active user)
sc.cleanUp()

# manual cleanup (needs manual interaction, but allows to remove also the traces for the active user
# Change to the guest system and follow the instructions of /install_tools/uninstall_fortrace_manual
# Shut system down after running the commands
# sc.cleanUp("manual")

# Scenario finished
logger.info("##############################")
logger.info("#   Scenario completed       #")
logger.info("##############################")

#############################################
#               Finalizing                  #
#############################################

# check if export-Directory exists and create if not
if not os.path.exists(export_dir):
    os.makedirs(export_dir)
# calculate hash value of the qcow2 image
logger.info("Calculating hash of the qcow2 file")
qcow2_path = "/data/fortrace-pool/backing/" + vm_name + ".qcow2"
sha256 = "qcow2_sha256: " + scenH.generate_file_sh256(qcow2_path)
logger.debug("Hash of the qcow2 file calculated")
sc.Reporter.add("hash", sha256)

# convert image to raw, so it can be distributed
logger.info("converting qcow2-file to raw")
raw_path = export_dir + vm_name + ".raw"
try:
    subprocess.call(["qemu-img", "convert", qcow2_path, raw_path])
except Exception as e:
    logger.error("could not convert image:" + e)
logger.info("Image was converted to raw")

# calculate hash value of the raw image
logger.info("Calculating hash of the raw image")
sha256 = "raw_sha256: " + scenH.generate_file_sh256(raw_path)
logger.debug("Hash of the raw file calculated")
sc.Reporter.add("hash", sha256)

# create report
logger.info("Creating report")
sc.Reporter.generate(export_dir)

# create final package for Trainer
logger.info("creating final package, this may take a while...")
try:
    subprocess.call(["tar", "cfvz", "{0}/{1}.tar.gz".format(export_dir, vm_name), export_dir])
except Exception as e:
    logger.error("could not create final package:" + e)
# Scenario finished
logger.info("##############################")
logger.info("#     Script completed       #")
logger.info("##############################")
