import logging
import time

try:
    from .core.vmm import Vmm
    from .utility.logger_helper import create_logger
    from .core.vmm import GuestListener
    from .core.reporter import Reporter
    import .utility.scenarioHelper as scenH
except ImportError as ie:
    print("Import error! in fileManagement.py " + str(ie))
    exit(1)

# Instanciate VMM and a VM
logger = create_logger('fortraceManager', logging.INFO)
macsInUse = []
guests = []
guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
imagename = "DFRWS_DEMO"
guest = virtual_machine_monitor1.create_guest(guest_name=imagename, platform="windows")

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()
# create userManagement object
userManagement_obj = guest.application("userManagement", {})

# Add different users
logger.info("Adding user1")
try:
    userManagement_obj.addUser("user1", "password")
    while userManagement_obj.is_busy is True:
        time.sleep(1)
except Exception as e:
    print("An error occured: ")
    print(e)
time.sleep(5)

# change User context and reboot system
logger.info("Changing Context to user1")
try:
    userManagement_obj.changeUser("user1", "password")
    while userManagement_obj.is_busy is True:
        time.sleep(1)
except Exception as e:
    changeUser = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Reboot System
guest.shutdown("keep")
while guest.isGuestPowered():
    time.sleep(5)
guest.start()
guest.waitTillAgentIsConnected()
time.sleep(5)

# Delete user  and delete files
logger.info("Deleting fortrace default user, deleting files")
try:
    userManagement_obj.deleteUser("", "delete")
    while userManagement_obj.is_busy is True:
        time.sleep(1)
except Exception as e:
    delUserDel = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Shut down system and delete guest
guest.shutdown("keep")
while guest.isGuestPowered():
    time.sleep(5)
guest.delete()





