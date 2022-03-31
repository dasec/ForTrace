import logging
import time

try:
    from fortrace.core.vmm import Vmm
    from fortrace.utility.logger_helper import create_logger
    from fortrace.core.vmm import GuestListener
    from fortrace.core.reporter import Reporter
#    import fortrace.utility.scenarioHelper as scenH
except ImportError as ie:
    print("Import error! in fileManagement.py " + str(ie))
    exit(1)

# Instanciate VMM and a VM
logger = create_logger('fortraceManager', logging.INFO)
macsInUse = []
guests = []
guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
imagename = "test"
guest = virtual_machine_monitor1.create_guest(guest_name=imagename, platform="windows")

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()

# Create veraCryptWrapper object
veracrypt_obj = guest.application("veraCryptWrapper", {})

# create new veracrypt container
vc_format_path = "\"C:\\Program Files\\VeraCrypt\\VeraCrypt Format.exe\""
vc_path = "\"C:\\Program Files\\VeraCrypt\\VeraCrypt.exe\""
cont_path = r"C:\Users\fortrace\Desktop\container.vc"
cont_size = "100M"
cont_pass = "password"
mount_point = "Z"
logger.info("Creating veracrypt container")
veracrypt_obj.createContainer(vc_format_path, cont_path, cont_size, cont_pass)
time.sleep(30)

# Mount Container
logger.info("Mountings veracrypt container")
veracrypt_obj.mountContainer(vc_path, cont_path, cont_pass, mount_point)
time.sleep(30)

# Copy file to container
logger.info("Copying data to container")
source = r"C:\Users\fortrace\Desktop\fortrace\docs\figures\architecture.png"
dest = r"{0}:\picture.jpg".format(mount_point)
veracrypt_obj.copyToContainer(source, dest)
time.sleep(30)

# Unmount container
logger.info("Dismounting Container")
veracrypt_obj.dismountContainer(vc_path, mount_point)
time.sleep(30)

logger.info("Scenario finished")

