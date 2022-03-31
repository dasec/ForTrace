# This scenario uses the presented template to realize a realistic set of actions, including different benign and
# malicious users


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
    from fortrace.utility.dumpgen import guest_dump
    import fortrace.utility.scenarioHelper as scenH

except ImportError as ie:
    print("Import error! in fileManagement.py " + str(ie))
    exit(1)

#############################################
#               Values to define            #
#############################################
##### Scenario Metadata #####
export_dir = "/data/export/"
vm_name = "ForTraceScen2"
author = "Stephan Maltan"
creation_date = date.today().strftime('%Y-%m-%d')

##### SMB Server Data #####
smb_share = r"\\192.168.103.98\sambashare"
smb_user = "service"
smb_pass = "fortrace"

##### Beginning Date of the scenario #####
# set to None to use current date
scenario_start = "2021-05-19 06:32:15"
#############################################
#       Space for additional content        #
#############################################

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

logger = create_logger('fortraceManager', logging.INFO)
guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
guest = virtual_machine_monitor1.create_guest(guest_name=vm_name, platform="windows")#, boottime=scenario_start.encode())
sc = scenH.Scenario(logger, Reporter(), guest)

sc.Reporter.add("imagename", vm_name)
sc.Reporter.add("author", author)
sc.Reporter.add("baseimage", hostplatform + "-template.qcow2")
#############################################
#                Scenario                   #
#############################################

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()

####### Session 4 - George #######
# copy confidential documents
george_document1 = "{0}\\sambashare\\hda_master.pdf".format(smb_share)
george_document1_t = r"C:\Users\fortrace\Desktop\CONFIDENTIAL_Modules.pdf"
fileTransObj = guest.application("fileTransfer", {})

fileTransObj.openSmb("X", smb_share, smb_user, smb_pass)
wait()
fileTransObj.winCopy(george_document1, george_document1_t)
wait()
#sc.smbCopy(george_document1, george_document1_t, smb_user, smb_pass, "needle")

# create VC container
cont_p = r"C:\Users\fortrace\Desktop\rca_logs.hc"
cont_pass = "topSecret012"
sc.createContainer(cont_p, "100M", cont_pass, "needle")
wait(10, 20)
password_p = r"C:\Users\fortrace\Documents\container.txt"
password_t = r"C:\container.txt"
sc.copy(password_p, password_t, "needle")
wait(5,15)
# Copy files to the VC container
sc.mountContainer(cont_p, cont_pass, "X", "needle")
wait(20,30)
sc.copyToContainer(george_document1_t, "X", "needle")
wait(5,15)
# Unmount the container
sc.unmountContainer("X", "needle")
wait()
# exfiltrate data via "public" SMB share
smb_tar = "{0}\\public_shared\\rca_logs.hc".format(smb_share)
# sc.smbCopy(cont_p, smb_tar, smb_share, smb_user, smb_pass, "needle")
sc.smbCopy(cont_p, smb_tar, smb_user, smb_pass, "needle")
wait()
pw_file ="C:\\Users\\fortrace\\Documents\\container.txt"
sc.openFile(pw_file)
wait(5)
guest_dump("ForTraceScen2", "/data/export/memdump.file", "mem")
wait(10)
#wait(90, 120)
sc.closeSmb(drive)
wait(2)
sc.reboot()
wait()
#sc.secureDelete(pw_file, "needle")
wait(5)
sc.shutdown()
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
sha256 = "qcow2_sha256: " + generate_file_sh256(qcow2_path)
logger.debug("Hash of the qcow2 file calculated")
sc.Reporter.add("hash", sha256)

# convert image to raw, so it can be distributed
#logger.info("converting qcow2-file to raw")
#raw_path = export_dir + vm_name + ".raw"
#try:
#    subprocess.call(["qemu-img", "convert", qcow2_path, raw_path])
#except Exception as e:
#    logger.error("could not convert image:" + e)
#logger.info("Image was converted to raw")

# calculate hash value of the raw image
#logger.info("Calculating hash of the raw image")
#sha256 = "raw_sha256: " + generate_file_sh256(raw_path)
#logger.debug("Hash of the raw file calculated")
#sc.Reporter.add("hash", sha256)

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
