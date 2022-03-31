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
    import fortrace.utility.scenarioHelper as scenH

except ImportError as ie:
    print("Import error! in fileManagement.py " + str(ie))
    exit(1)

#############################################
#               Values to define            #
#############################################
##### Scenario Metadata #####
export_dir = "/data/export/"
vm_name = "Thesis-Windows_val"
author = "Stephan Maltan"
creation_date = date.today().strftime('%Y-%m-%d')

##### SMB Server Data #####
smb_share = r"\\192.168.103.8\sambashare"
smb_user = "service"
smb_pass = "fortrace"

##### Beginning Date of the scenario #####
# set to None to use current date
scenario_start = "2022-05-19 06:32:15"
#############################################
#       Space for additional content        #
#############################################
textfile1_text = "Lorem ipsum dolor sit amet, consectetur adipisici elit, sed eiusmod tempor incidunt ut labore et dolore magna aliqua.\n Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquid ex ea commodi consequat.\nQuis aute iure reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.\n Excepteur sint obcaecat cupiditat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum"
textfile2_text = "Shopping List:\n-plain flour\n-granulated sugar\n-backing soda\n-butter\n-eggs"

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

# Start as fortrace user and create new user for scenario
####### Session 0 - fortrace #######
sc.addUser("Bill", "jyrL-Lvfah")
sc.changeUser("Bill", "jyrL-Lvfah")
sc.reboot("2022-05-19 10:52:12")

####### Session 1 - Bill #######
# reduce traces to the fortrace user by deleting it first and cleaning the Event Log afterwards
sc.deleteUser("fortrace", "secure", "needle")
sc.clearEventLogEntries("all", "needle")
wait(10, 30)
sc.addUser("Hannah", "V4PIfkkRZ", "needle")
wait(10, 30)
sc.addUser("Percy", "fkkRZIkm", "needle")
wait()
sc.disableHibernation("1", "needle")
wait(10, 20)
sc.disablePagefile("1", "needle")
wait(5, 10)
sc.disableThumbcache("1", "needle")
sc.changeUser("Hannah", "V4PIfkkRZ", "needle")
wait(30, 80)
sc.reboot("2022-05-20 08:23:05")


####### Session 2 - Hannah #######
# copy smb files from share
hannah_picture1 = "{0}\\team42\\holiday01.jpg".format(smb_share)
hannah_picture2 = "{0}\\team42\\CONFIDENTIAL_testing_environment.jpg".format(smb_share)
hannah_document1 = "{0}\\team42\\2019_cybercrime_ger.pdf".format(smb_share)
hannah_picture1_t = r"C:\Users\Hannah\Desktop\holiday01.jpg"
hannah_picture2_t = r"C:\Users\Hannah\Desktop\CONFIDENTIAL_testing_environment.jpg"
hannah_document1_t = r"C:\Users\Hannah\Documents\2019_cybercrime_ger.pdf"
# sc.smbCopy(hannah_document1, hannah_document1_t, smb_share, smb_user, smb_pass, "needle")
sc.smbCopy(hannah_document1, hannah_document1_t, smb_user, smb_pass, "needle")
wait()
# sc.smbCopy(hannah_picture1, hannah_picture1_t, smb_user, smb_pass, "")
wait()
# sc.smbCopy(hannah_picture2, hannah_picture2_t, smb_user, smb_pass, "needle")
# create some exemplary "Background Noise"
wait(10, 20)
sc.writeTextFile(r"C:\Users\Hannah\Desktop\top_secret.txt", textfile2_text)
sc.Reporter.add("chronological", "User {0} created a suspicious but irrelevant textfile C:\\Users\\Hannah\\Desktop\\top_secret.txt".format(sc.activeUser))
wait(5, 15)
sc.openFile(hannah_picture1)
sc.Reporter.add("chronological", "User {0} started a firefox Session".format(sc.activeUser))
sc.browserOpen("www.unibw.de")
wait()
sc.browserBrowseTo("www.h-da.de")
wait()
sc.browserBrowseTo("impfdashboard.de")
wait()
sc.browserClose()
wait()
sc.recycle(r"C:\Users\Hannah\Desktop\top_secret.txt", "needle")
wait()
# secure delete file(s)
sc.secureDelete(hannah_picture2_t, "needle")
sc.secureDelete(hannah_document1_t, "needle")
# reboot
sc.changeUser("Percy", "fkkRZIkm", "needle")
wait()
sc.reboot()#"2021-05-20 10:15:15")

####### Session 3 - Percy #######
# anti-forensics
sc.disablePrefetch("1", "needle")
sc.disableEventLog("1", "needle")
# add malicious user
sc.addUser("George", "enj_Jwaa", "needle")
sc.changeUser("George", "enj_Jwaa", "needle")
# reboot
sc.reboot()

####### Session 4 - George #######
# copy confidential documents
george_document1 = "{0}\\team42\\CONFIDENTIAL_Modules.pdf".format(smb_share)
george_picture1 = "{0}\\team42\\CONFIDENTIAL_testing_environment.jpg".format(smb_share)
george_document1_t = r"C:\Users\George\Desktop\CONFIDENTIAL_Modules.pdf"
george_picture1_t = r"C:\Users\George\Desktop\CONFIDENTIAL_testing_environment.jpg"
#sc.smbCopy(george_document1, george_document1_t, smb_share, smb_user, smb_pass, "needle")
#sc.smbCopy(george_picture1, george_picture1_t, smb_share, smb_user, smb_pass, "needle")
sc.smbCopy(george_document1, george_document1_t, smb_user, smb_pass, "needle")
sc.smbCopy(george_picture1, george_picture1_t, smb_user, smb_pass, "needle")
# create VC container
cont_p = r"C:\Users\George\Desktop\rca_logs.hc"
cont_pass = "topSecret012"
sc.createContainer(cont_p, "100M", cont_pass, "needle")
wait(10, 20)
password_p = r"C:\Users\George\Documents\container.txt"
password_t = r"C:\container.txt"
sc.copy(password_p, password_t, "needle")
wait(5,15)
# Copy files to the VC container
sc.mountContainer(cont_p, cont_pass, "X", "needle")
wait(20,30)
sc.copyToContainer(george_document1_t, "X", "needle")
sc.copyToContainer(george_picture1_t, "X", "needle")
wait(5,15)
# Unmount the container
sc.unmountContainer("X", "needle")
wait()
# exfiltrate data via "public" SMB share
smb_tar = "{0}\\public_shared\\rca_logs.hc".format(smb_share)
# sc.smbCopy(cont_p, smb_tar, smb_share, smb_user, smb_pass, "needle")
sc.smbCopy(cont_p, smb_tar, smb_user, smb_pass, "needle")
# clear Thumbcache of user bill (validation purposes only)
sc.clearThumbcache("Bill", "needle")
# reboot system
sc.changeUser("Percy", "fkkRZIkm", "needle")
sc.reboot()#"2021-05-20 17:58:10")

####### Session 5 - Percy #######
wait()
# delete malicious user
sc.deleteUser("George", "secure", "needle")
# re-enable event log and clear Prefetch data
sc.disableEventLog("0", "needle")
sc.clearPrefetch("needle")
# recycle VeraVrypt PW file, can be used as a trace, but source was C:\, so no evidence
sc.recycle(password_t, "needle")
# reboot to Bill
sc.changeUser("Bill", "jyrL-Lvfah")
sc.reboot()#"2021-05-22 07:13:25")

####### Session 6 - Bill #######
wait(60, 180)
bill_picture1 = "{0}\\team42\\holiday01.jpg".format(smb_share)
bill_picture2 = "{0}\\public_shared\\customer02.jpg".format(smb_share)
bill_picture3 = "{0}\\team42\\mountain.jpg".format(smb_share)
bill_doc1 = "{0}\\public_shared\\customer_catalog.pdf".format(smb_share)
bill_picture1_t = r"C:\Users\Bill\Desktop\holiday01.jpg"
bill_picture2_t = r"C:\Users\Bill\Desktop\customer02.jpg"
bill_picture3_t = r"C:\Users\Bill\Desktop\mountain.jpg"
bill_doc1_t = r"C:\Users\Bill\Desktop\customer_catalog.pdf".format(smb_share)
#sc.smbCopy(bill_picture1, bill_picture1_t, smb_share, smb_user, smb_pass, "needle")
#sc.smbCopy(bill_picture2, bill_picture2_t, smb_share, smb_user, smb_pass, "needle")
sc.smbCopy(bill_picture1, bill_picture1_t, smb_user, smb_pass, "needle")
sc.smbCopy(bill_picture2, bill_picture2_t, smb_user, smb_pass, "needle")
wait()
# delete User Hannah
sc.deleteUser("Hannah", "keep", "needle")
wait()
# move files to recycle bin and empty it
sc.recycle(bill_picture1_t, "needle")
sc.recycle(bill_picture2_t, "needle")
wait(5, 30)
#sc.smbCopy(bill_picture3, bill_picture3_t, smb_share, smb_user, smb_pass, "needle")
#sc.smbCopy(bill_doc1, bill_doc1_t, smb_share, smb_user, smb_pass, "needle")
sc.smbCopy(bill_picture3, bill_picture3_t, smb_user, smb_pass, "needle")
sc.smbCopy(bill_doc1, bill_doc1_t, smb_user, smb_pass, "needle")
wait()
sc.emptyRecycleBin("needle")
wait(5, 10)
sc.recycle(bill_picture3_t, "needle")
sc.recycle(bill_doc1_t, "needle")
wait()
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
