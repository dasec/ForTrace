import time
import logging

try:
    from fortrace.core.vmm import Vmm
    from fortrace.utility.logger_helper import create_logger
    from fortrace.core.vmm import GuestListener
    from fortrace.core.reporter import Reporter
except ImportError as ie:
    print("Import error! in fileManagement.py " + str(ie))
    exit(1)
############################################################
# Overview on used guest functions:
# - insertCD(iso_path)



# Instanciate VMM and a VM
logger = create_logger('fortraceManager', logging.INFO)
macsInUse = []
guests = []
guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
guest = virtual_machine_monitor1.create_guest(guest_name="test", platform="windows")

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()

# insert iso image as cd
logger.info("mounting CD")
iso_path = "/data/iso/iso1.iso"
guest.insertCD(iso_path)
time.sleep(3)

# execute a command line operation
#logger.info("executing shell command")
#cmd = "ping 8.8.8.8 -t"
#execute = guest.shellExec(cmd)
#time.sleep(5)

# terminate execution of shell command
#logger.info("terminating shell session")
#guest.killShellExec(execute)
#time.sleep(5)

# toDo: remoteShellExec

# copy files on guest
#logger.info("copying file to guest")
#source = "/data/files/001.jpg"
#destination = r"C:\Users\fortrace\Desktop\001.jpg"
#guest.CopyFileToGuest(source, destination)
#time.sleep(5)

# copy directory to guest
#logger.info("copying directory to guest")
#source = "/data/files/"
#destination = r"C:\Users\fortrace\Desktop\Files"
#guest.CopyDirectoryToGuest(source, destination)
#time.sleep(5)

# create directory on guest
#logger.info("create directory on guest")
#target = r"C:\Users\fortrace\Desktop\Files2"
#guest.guestCreateDirectory(target)
#time.sleep(5)

# touch file on guest
#logger.info("touching file")
#target = r"C:\Users\fortrace\Desktop\File3.jpg"
#guest.guestTouchFile(target)
#time.sleep(5)

# copy file on guest
#logger.info("copying file")
#source = r"C:\Users\fortrace\Desktop\File3.jpg"
#destination = r"C:\Users\fortrace\Desktop\File4.jpg"
#guest.guestCopy(source, destination)
#time.sleep(5)

# moving file on guest
#logger.info("moving file")
#source = r"C:\Users\fortrace\Desktop\File3.jpg"
#destination = r"C:\Users\fortrace\Desktop\File5.jpg"
#guest.guestMove(source, destination)
#time.sleep(5)

# deleting file on guest
#logger.info("deleting file")
#target = r"C:\Users\fortrace\Desktop\File4.jpg"
#guest.guestDelete(target)
#time.sleep(5)

# change working directory of the guest agent
#logger.info("changing working directory")
#target = r"C:\Users\fortrace\Desktop\Files2"
#guest.guestChangeWorkingPath(target)
#time.sleep(5)

# changing OS time
#logger.info("changing guest time")
#target_time = "2021-12-30 11:00:00"
#guest.setOSTime(target_time)
#time.sleep(5)

# toDo: runElevated
# toDo: cleanUp
# toDo: initClean
# toDo: guestTime
# toDo: guestTimezone

logger.info("Test scenario finished!")

