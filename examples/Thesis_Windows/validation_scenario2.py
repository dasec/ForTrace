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
vm_name = "Thesis-Windows_val2"
author = "Stephan Maltan"
creation_date = date.today().strftime('%Y-%m-%d')

##### SMB Server Data #####
smb_share = r"\\192.168.103.8\sambashare"
smb_user = "service"
smb_pass = "fortrace"

##### Email Data #####

##### Beginning Date of the scenario #####
# set to None to use current date
scenario_start = "2022-06-25 08:32:15"
#############################################
#       Space for additional content        #
#############################################
textfile2_text = "Hi, this is a Test message. How are you?"

#############################################
#              Helper Functions             #
#############################################

def generate_file_sh256(filename, blocksize=2 ** 20):
    """
    Generates the SHA_256 hashsum of the given file
    @param filename: name of the file, the hashsum will calculated for
    @param blocksize: blocksize used during calculation
    """
    m = hashlib.sha256()
    with open(filename, "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest()

def wait(min=10, max=60):
    """
    Waits for a random amount of seconds in the provided interval
    Gives the user time to "think"
    @param min: minimum time to wait
    @param max: maximum time to wait
    """
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
guest = virtual_machine_monitor1.create_guest(guest_name=vm_name, platform="windows")
sc = scenH.Scenario(logger, Reporter(), guest)

sc.Reporter.add("imagename", vm_name)
sc.Reporter.add("author", author)
sc.Reporter.add("baseimage", hostplatform + "-template.qcow2")
#############################################
#                Scenario                   #
#############################################

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()
###############################################
# create User and copy some files to it
# needed to verify the "deletion" of the user afterwards
sc.addUser("TestUser", "123", "needle")
sc.changeUser("TestUser", "123", "needle")
sc.reboot()
# copy some files to the Desktop, that may be easier to find in the analysis
picture1 = "{0}\\team42\\holiday01.jpg".format(smb_share)
picture2 = "{0}\\public_shared\\customer02.jpg".format(smb_share)
picture3 = "{0}\\team42\\mountain.jpg".format(smb_share)
picture1_t = r"C:\Users\TestUser\Desktop\holiday01.jpg"
picture2_t = r"C:\Users\TestUser\Desktop\customer02.jpg"
picture3_t = r"C:\Users\TestUser\Desktop\mountain.jpg"
sc.smbCopy(picture1, picture1_t, smb_share, smb_user, smb_pass, "needle")
wait(5,15)
sc.smbCopy(picture2, picture2_t, smb_share, smb_user, smb_pass, "needle")
wait(5,15)
sc.smbCopy(picture3, picture3_t, smb_share, smb_user, smb_pass, "needle")
wait(5,15)
sc.changeUser("fortrace", "", "needle")
sc.reboot()
###############################################
# disable different functions and clean up the according data structures after reboot
sc.disableRecentFiles("1", "needle")
wait(5,15)
sc.disableRecycleBin("1", "needle")
wait(5,15)
sc.disableUserAssist("1", "needle")
wait(5,15)
sc.disableEventLog("1", "needle")
# disable Thumbcache "manually"
regKey_set = r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
regkey_set_value = "DisableThumbnails"
regkey_set_type = "REG_DWORD"
sc.setRegistryKey(regKey_set, regkey_set_type, regkey_set_value, "1", "needle")
# delete Registry key
regkey_del = r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Power"
regkey_del_val = "HibernateEnabledDefault"
sc.deleteRegistryKey(regkey_del, regkey_del_val, "needle")
sc.reboot()
# reboot, so changes take effect
sc.clearUserAssist("needle")
sc.clearRecentDocs("needle")
sc.clearEventLogFiles("needle")
sc.clearJumpLists("fortrace", "needle")
# create some files for UserAssist, RecentFiles and Recycle Bin and open Firefox
textfile_t = r"C:\Users\fortrace\Desktop\message.txt"
h_picture1 = "{0}\\public_shared\\customer01.jpg".format(smb_share)
h_picture1_t = r"C:\Users\fortrace\Desktop\customer01.jpg"
h_doc1 = "{0}\\team42\\2019_cybercrime_ger.pdf".format(smb_share)
h_doc1_t = r"C:\Users\fortrace\Documents\2019_cybercrime_ger.pdf"
sc.smbCopy(h_picture1, h_picture1_t, smb_share, smb_user, smb_pass, "needle")
sc.smbCopy(h_doc1, h_doc1_t, smb_share, smb_user, smb_pass, "needle")
sc.openFile(h_doc1_t)
sc.openFile(h_picture1_t)
sc.writeTextFile(textfile_t, textfile2_text, "needle")
sc.Reporter.add("chronological", "User {0} started a Firefox Session".format(sc.activeUser))
sc.browserOpen("www.unibw.de")
wait()
sc.browserBrowseTo("www.heise.de")
wait()
sc.browserBrowseTo("www.docs.microsoft.com")
wait()
sc.browserClose()
# delete TestUser
sc.deleteUser("TestUser", "delete", "needle")
sc.recycle(textfile_t, "needle")
wait()
# Scenario finished
sc.shutdown()
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
logger.info("converting qcow2-file to raw")
raw_path = export_dir + vm_name + ".raw"
try:
    subprocess.call(["qemu-img", "convert", qcow2_path, raw_path])
except Exception as e:
    logger.error("could not convert image:" + e)
logger.info("Image was converted to raw")

# calculate hash value of the raw image
logger.info("Calculating hash of the raw image")
sha256 = "raw_sha256: " + generate_file_sh256(raw_path)
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
