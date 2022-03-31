import time
import logging

try:
    from fortrace.core.vmm import Vmm
    from fortrace.utility.logger_helper import create_logger
    from fortrace.core.vmm import GuestListener
    from fortrace.core.reporter import Reporter
    import fortrace.utility.scenarioHelper as scenH
except ImportError as ie:
    print("Import error! in fileManagement.py " + str(ie))
    exit(1)
############################################################
# Overview on used guest functions:
# - insertCD(iso_path)

# Function status
mountCD = True
shellExecute = True
killShellExec = True
copyToGuest = True
copyDirToGuest = True
createDir = True
touchFile = True
copyFile = True
moveFile = True
deleteFileDir = True
changeDir = True
changeTime = True


# Instanciate VMM and a VM
logger = create_logger('fortraceManager', logging.INFO)
macsInUse = []
guests = []
guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
imagename = "guestFunctions_testscript"
guest = virtual_machine_monitor1.create_guest(guest_name=imagename, platform="windows")
logger.info("This script only verifies, if functions are executed correctly on the VMM by now. Verifying the effect on the guest has to be implemented later on")

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()

# Todo: mounting iso fails
# insert iso image as cd
logger.info("mounting CD")
iso_path = "/data/iso/iso1.iso"
try:
    guest.insertCD(iso_path)
except Exception as e:
    mountCD = False
    print("An error occured: ")
    print(e)
time.sleep(3)

# ToDo: Known Bug in guest.py
# execute a command line operation
logger.info("executing shell command")
cmd = "ping 8.8.8.8 -t"
try:
    execute = guest.shellExec(cmd)
except Exception as e:
    shellExecute = False
    print("An error occured: ")
    print(e)
    # raise Exception(e)
time.sleep(5)

# terminate execution of shell command
if shellExecute is True:
    try:
        logger.info("terminating shell session")
        guest.killShellExec(execute)
    except Exception as e:
        killShellExec = False
        print("An error occured: ")
        print(e)
else:
    print("No shell was opened, so it cannot be closed by killShellExec!")
    killShellExec = False
time.sleep(5)

# toDo: remoteShellExec

# copy files to guest
logger.info("copying file to guest")
source = "/data/files/001.jpg"
destination = r"C:\Users\fortrace\Desktop"
try:
    guest.CopyFileToGuest(source, destination)
except Exception as e:
    copyToGuest = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# copy directory to guest
logger.info("copying directory to guest")
source = "/data/files/"
destination = r"C:\Users\fortrace\Desktop\Files"
try:
    guest.CopyDirectoryToGuest(source, destination)
except Exception as e:
    copyDirToGuest = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# create directory on guest
logger.info("create directory on guest")
target = r"C:\Users\fortrace\Desktop\Files2"
try:
    guest.guestCreateDirectory(target)
except Exception as e:
    createDir = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# touch file on guest
logger.info("touching file")
target = r"C:\Users\fortrace\Desktop\File3.jpg"
try:
    guest.guestTouchFile(target)
except Exception as e:
    touchFile = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# copy file on guest
logger.info("copying file")
source = r"C:\Users\fortrace\Desktop\001.jpg"
destination = r"C:\Users\fortrace\Desktop\File4.jpg"
try:
    guest.guestCopy(source, destination)
except Exception as e:
    copyFile = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# moving file on guest
logger.info("moving file")
source = r"C:\Users\fortrace\Desktop\File3.jpg"
destination = r"C:\Users\fortrace\Desktop\File5.jpg"
try:
    guest.guestMove(source, destination)
except Exception as e:
    moveFile = False
    print("An error occured: ")
    print(e)
time.sleep(5)


# deleting file on guest
logger.info("deleting file")
target = r"C:\Users\fortrace\Desktop\001.jpg"
try:
    guest.guestDelete(target)
except Exception as e:
    deleteFileDir = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# change working directory of the guest agent
logger.info("changing working directory")
target = r"C:\Users\fortrace\Desktop\File2"
try:
    guest.guestChangeWorkingPath(target)
except Exception as e:
    changeDir = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# changing OS time
logger.info("changing guest time")
target_time = "2021-12-30 11:00:00"
try:
    guest.setOSTime(target_time)
except Exception as e:
    changeTime = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Shut down System and delete data
guest.shutdown("keep")
while guest.isGuestPowered():
    time.sleep(5)
guest.delete()

# toDo: runElevated
# toDo: cleanUp
# toDo: initClean
# toDo: guestTime
# toDo: guestTimezone

logger.info("Test scenario finished!")
logger.info("Results:")
logger.info("Function insertCD:" + str(mountCD))
logger.info("Function shellExec: " + str(shellExecute))
logger.info("Function killShellExec: " + str(killShellExec))
logger.info("Function CopyFileToGuest: " + str(copyToGuest))
logger.info("Function CopyDirectoryToGuest: " + str(copyDirToGuest))
logger.info("Function guestCreateDirectory: " + str(createDir))
logger.info("Function guestTouch: " + str(touchFile))
logger.info("Function guestCopy: " + str(copyFile))
logger.info("Function guestMove: " + str(moveFile))
logger.info("Function guestDelete:" + str(deleteFileDir))
logger.info("Function guestChangeWorkingPath: " + str(changeDir))
logger.info("Function setOSTime: " + str(changeTime))
