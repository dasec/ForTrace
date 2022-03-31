import logging
import time

try:
    from fortrace.core.vmm import Vmm
    from fortrace.utility.logger_helper import create_logger
    from fortrace.core.vmm import GuestListener
    from fortrace.core.reporter import Reporter
    import fortrace.utility.scenarioHelper as scenH
except ImportError as ie:
    print("Import error! in fileManagement.py " + str(ie))
    exit(1)

# This test script verifies the functionality and shows the usage of the different antiForensics functions.
# The effect of some functions may interfere with each other (e.g. cleaning the Event Log and then deleting the log
# files seems pretty pointless

##########################################
#            Set IP of Service VM        #
##########################################
smb_share = r"\\192.168.103.143\sambashare"
smb_user = "service"
smb_pass = "fortrace"

# Function status
recycle = True
emptyBin = True
secDel = True
writeFile = True
openFile = True
transFile = True

# Instanciate VMM and a VM
logger = create_logger('fortraceManager', logging.INFO)
macsInUse = []
guests = []
guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
imagename = "fileManagement_testscript"
guest = virtual_machine_monitor1.create_guest(guest_name=imagename, platform="windows")

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()

# Create mailClient object
filemgmt_obj = guest.application("fileManagement", {})

# copy files to Desktop
# Helper function, not associated to the module
logger.info("Copying files")
source = r"C:\Users\fortrace\Desktop\fortrace\docs\figures\architecture.png"
dest1 = r"C:\Users\fortrace\Desktop\file1.png"
dest2 = r"C:\Users\fortrace\Desktop\file2.png"
try:
    guest.guestCopy(source, dest1)
    guest.guestCopy(source, dest2)
except Exception as e:
    raise Exception("File copying failed: " + e)
time.sleep(5)

# Recycle a file
logger.info("Recycling files")
try:
    filemgmt_obj.recycle(dest1)
    while filemgmt_obj.is_busy is True:
        time.sleep(1)
except Exception as e:
    recycle = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Empty Recycle Bin
logger.info("Emptying Recycle bin")
try:
    filemgmt_obj.emptyRecycleBin()
    while filemgmt_obj.is_busy is True:
        time.sleep(1)
except Exception as e:
    emptyBin = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Secure Delete File
logger.info("Secure Deleting File")
try:
    filemgmt_obj.secureDelete(dest2)
    while filemgmt_obj.is_busy is True:
        time.sleep(1)
except Exception as e:
    secDel = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Write Text file
logger.info("writing text file")
path = r"C:\Users\fortrace\Desktop\file.txt"
content = "Lorem ipsum"
try:
    filemgmt_obj.writeTextFile(path, content)
    while filemgmt_obj.is_busy is True:
        time.sleep(1)
except Exception as e:
    writeFile = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Open file, using its default application
logger.info("Opening file")
try:
    filemgmt_obj.openFile(source)
    while filemgmt_obj.is_busy is True:
        time.sleep(1)
except Exception as e:
    openFile = False
    print("An error occured: ")
    print(e)
time.sleep(5)

##########################################
# Verification of fileTransfer_functions #
##########################################

# Create Filetransfer object
fileTransfer_obj = guest.application("fileTransfer", {})

# Copy file from SMB share
source = "{0}\\001.jpg".format(smb_share)
dest3 = r"C:\Users\fortrace\Desktop\smb_picture1.jpg"
logger.info("Copying files from SMB share")
try:
    fileTransfer_obj.openSmb("S:", smb_share, smb_user, smb_pass)
    fileTransfer_obj.smbCopy(source, dest3, smb_share, smb_user, smb_pass)
    while fileTransfer_obj.is_busy is True:
        time.sleep(3)
except Exception as e:
    transFile = False
    print("An error occured: ")
    print(e)
time.sleep(5)
logger.info("Scenario finished!")


# Shut down system and delete guest
guest.shutdown("keep")
while guest.isGuestPowered():
    time.sleep(5)
guest.delete()

# Finish and print results
logger.info("Scenario finished!")
logger.info("Results:")
logger.info("recycle: " + str(recycle))
logger.info("emptyRecycleBin: " + str(emptyBin))
logger.info("secureDelete: " + str(secDel))
logger.info("writeTextFile: " + str(writeFile))
logger.info("openFile: " + str(openFile))
logger.info("smbCopy: " + str(transFile))

