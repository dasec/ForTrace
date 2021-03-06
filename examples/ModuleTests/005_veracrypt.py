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
createContainer = True
mountContainer = True
copyToContainer = True
dismountContainer = True

# Instanciate VMM and a VM
logger = create_logger('fortraceManager', logging.INFO)
macsInUse = []
guests = []
guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
imagename = "veracrypt_testscript"
guest = virtual_machine_monitor1.create_guest(guest_name=imagename, platform="windows")

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()

# Create veraCryptWrapper object
veracrypt_obj = guest.application("veraCryptWrapper", {})

# create new veracrypt container
vc_format_path = "\"C:\\Users\\fortrace\\Desktop\\fortrace\\contrib\\veracrypt\\App\\VeraCrypt\\VeraCrypt Format.exe\""
vc_path = "\"C:\\Users\\fortrace\\Desktop\\fortrace\\contrib\\veracrypt\\App\\VeraCrypt\\VeraCrypt.exe\""
cont_path = r"C:\Users\fortrace\Desktop\container.vc"
cont_size = "100M"
cont_pass = "password"
mount_point = "Z"
logger.info("Creating veracrypt container")
try:
    veracrypt_obj.createContainer(vc_format_path, cont_path, cont_size, cont_pass)
    time.sleep(30)
except Exception as e:
    createContainer = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Mount Container
logger.info("Mountings veracrypt container")
try:
    veracrypt_obj.mountContainer(vc_path, cont_path, cont_pass, mount_point)
    time.sleep(30)
except Exception as e:
    mountContainer = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Copy file to container
logger.info("Copying data to container")
source = r"C:\Users\fortrace\Desktop\fortrace\docs\figures\architecture.png"
dest = r"{0}:\picture.jpg".format(mount_point)
try:
    veracrypt_obj.copyToContainer(source, dest)
    time.sleep(30)
except Exception as e:
    copyToContainer = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Unmount container
logger.info("Dismounting Container")
try:
    veracrypt_obj.dismountContainer(vc_path, mount_point)
    time.sleep(30)
except Exception as e:
    dismountContainer = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Shut down system and delete guest
guest.shutdown("keep")
while guest.isGuestPowered():
    time.sleep(5)
guest.delete()

# Finish and print results
logger.info("Scenario finished!")
logger.info("Results:")
logger.info("createContainer: " + str(createContainer))
logger.info("mountContainer: " + str(mountContainer))
logger.info("copyToContainer: " + str(copyToContainer))
logger.info("dismountContainer: " + str(dismountContainer))
