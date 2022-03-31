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

# Function status
addUser = True
changeUser = True
delUserDel = True
delUserKeep = True
delUserSec = True

# Instanciate VMM and a VM
logger = create_logger('fortraceManager', logging.INFO)
macsInUse = []
guests = []
guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
imagename = "userManagement_testscript"
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
    addUser = False
    print("An error occured: ")
    print(e)
time.sleep(5)

logger.info("Adding user2")
try:
    userManagement_obj.addUser("user2", "password2")
    while userManagement_obj.is_busy is True:
        time.sleep(1)
except Exception as e:
    addUser = False
    print("An error occured: ")
    print(e)
time.sleep(5)
logger.info("Adding user3")
try:
    userManagement_obj.addUser("user3", "password")
    while userManagement_obj.is_busy is True:
        time.sleep(1)
except Exception as e:
    addUser = False
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

# change context to each user account, so it is logged in to one time
logger.info("Changing Context to user2")
try:
    userManagement_obj.changeUser("user2", "password2")
    while userManagement_obj.is_busy is True:
        time.sleep(1)
except Exception as e:
    changeUser = False
    print("An error occured: ")
    print(e)
time.sleep(5)
guest.shutdown("keep")
while guest.isGuestPowered():
    time.sleep(5)
guest.start()
guest.waitTillAgentIsConnected()
time.sleep(5)

logger.info("Changing Context to user3")
try:
    userManagement_obj.changeUser("user3", "password")
    while userManagement_obj.is_busy is True:
        time.sleep(1)
except Exception as e:
    changeUser = False
    print("An error occured: ")
    print(e)
time.sleep(5)
guest.shutdown("keep")
while guest.isGuestPowered():
    time.sleep(5)
guest.start()
guest.waitTillAgentIsConnected()
time.sleep(5)

logger.info("Changing Context to fortrace")
try:
    userManagement_obj.changeUser("fortrace")
    while userManagement_obj.is_busy is True:
        time.sleep(1)
except Exception as e:
    changeUser = False
    print("An error occured: ")
    print(e)
time.sleep(5)
guest.shutdown("keep")
while guest.isGuestPowered():
    time.sleep(5)
guest.start()
guest.waitTillAgentIsConnected()
time.sleep(5)

# Delete user1 and delete files
logger.info("Deleting user1, deleting files")
try:
    userManagement_obj.deleteUser("user1", "delete")
    while userManagement_obj.is_busy is True:
        time.sleep(1)
except Exception as e:
    delUserDel = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Delete user2 and keep files
logger.info("Deleting user1, keeping files")
try:
    userManagement_obj.deleteUser("user2", "keep")
    while userManagement_obj.is_busy is True:
        time.sleep(1)
except Exception as e:
    delUserKeep = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Delete user2 and securely delete files
logger.info("Deleting user1, securely deleting files")
try:
    userManagement_obj.deleteUser("user3", "secure")
    while userManagement_obj.is_busy is True:
        time.sleep(1)
except Exception as e:
    delUserSec = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Shut down system and delete guest
#guest.shutdown("keep")
#while guest.isGuestPowered():
#    time.sleep(5)
#guest.delete()
logger.info("Scenario finished!")
logger.info("Results:")
logger.info("addUser: " + str(addUser))
logger.info("changeUser: " + str(changeUser))
logger.info("deleteUser(delete): " + str(delUserDel))
logger.info("deleteUser(keep): " + str(delUserKeep))
logger.info("deleteUser(secure): " + str(delUserSec))




