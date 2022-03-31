import time
import logging
import random
import subprocess
from fortrace.core.vmm import Vmm
from fortrace.utility.logger_helper import create_logger
from fortrace.core.vmm import GuestListener

# Instanciate VMM and a VM
logger = create_logger('fortraceManager', logging.DEBUG)
macsInUse = []
guests = []
guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
vm_name = "FileManagementTest{0}".format(random.randint(0, 9999))
guest = virtual_machine_monitor1.create_guest(guest_name=vm_name, platform="windows")


url = "http://192.168.103.1:8000"
userManagement_obj = guest.application("userManagement", {})
fileManagement_obj = guest.application("fileManagement", {})
# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()
# Create new Useraccount and enable autostart

# Do not use Passwords longer than 14
time.sleep(5)
Downloaddir = r"C:\Users\fortrace\Downloads\forest.jpg"
target1 = r"C:\Users\fortrace\Downloads\recycleempty.png"
target2 = r"C:\Users\fortrace\Downloads\recycle.png"
target3 = r"C:\Users\fortrace\Downloads\secure.png"
logger.info("copying files")
guest.guestCopy(Downloaddir, target1)
time.sleep(10)
guest.guestCopy(Downloaddir, target2)
time.sleep(10)
guest.guestCopy(Downloaddir, target3)
time.sleep(10)
logger.info("touching files")
guest.guestTouchFile(target1)
time.sleep(10)
guest.guestTouchFile(target2)
time.sleep(10)
guest.guestTouchFile(target3)
time.sleep(10)
logger.info("deleting files")
# recycle and delete, recycle and secure delete the files
fileManagement_obj.recycle(target1)
while fileManagement_obj.is_busy:
    time.sleep(2)
time.sleep(5)
logger.info("emptyBin")
fileManagement_obj.emptyRecycleBin()
while fileManagement_obj.is_busy:
    time.sleep(2)
time.sleep(5)
logger.info("deleting files")
fileManagement_obj.recycle(target2)
while fileManagement_obj.is_busy:
    time.sleep(2)
time.sleep(5)
logger.info("sdelete")
fileManagement_obj.secureDelete(target3)
while fileManagement_obj.is_busy:
    time.sleep(2)
time.sleep(30000)

# Shutdown
guest.shutdown("keep")
while guest.isGuestPowered():
    time.sleep(5)
guest.start("2021-06-02 11:00:00")
guest.waitTillAgentIsConnected()
time.sleep(10)

# Browse some Websites and delete different useraccounts

# Shutdown 3
#guest.shutdown("keep")
#while guest.isGuestPowered():
#    time.sleep(5)
#guest.start("2021-06-02 11:30:00")
#guest.waitTillAgentIsConnected()

# Cycle 4
print("Scenario completed!")
print("Going to sleep...")
#time.sleep(5)
#guest.shutdown("keep")
#while guest.isGuestPowered():
#    time.sleep(5)