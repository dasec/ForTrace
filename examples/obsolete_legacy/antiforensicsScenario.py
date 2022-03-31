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
vm_name = "WindowsAntiForensicsTest{0}".format(random.randint(0, 9999))
guest = virtual_machine_monitor1.create_guest(guest_name=vm_name, platform="windows")

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()
# Create new anti-forensics object and enable autostart
antiForensics_obj = None
antiForensics_obj = guest.application("antiForensics", {})
# Use all available Functions of the antiForensics object
antiForensics_obj.disableRecycleBin()
while antiForensics_obj.is_busy:
    time.sleep(2)
antiForensics_obj.disablePrefetch()
while antiForensics_obj.is_busy:
    time.sleep(2)
antiForensics_obj.disableThumbcache()
while antiForensics_obj.is_busy:
    time.sleep(2)
antiForensics_obj.disableRecentFiles()
while antiForensics_obj.is_busy:
    time.sleep(2)
antiForensics_obj.disableEventLog()
while antiForensics_obj.is_busy:
    time.sleep(2)
antiForensics_obj.disableRecentFiles()
while antiForensics_obj.is_busy:
    time.sleep(2)
antiForensics_obj.disableUserAssist()
while antiForensics_obj.is_busy:
    time.sleep(2)
antiForensics_obj.disableHibernation()
while antiForensics_obj.is_busy:
    time.sleep(2)
antiForensics_obj.disablePagefile()
while antiForensics_obj.is_busy:
    time.sleep(2)
antiForensics_obj.setRegistryKey("HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "REG_DWORD", "SwapfileControl", "0")
while antiForensics_obj.is_busy:
    time.sleep(2)
# Shut down system
guest.shutdown("keep")
while guest.isGuestPowered():
    time.sleep(5)
guest.start("2021-06-02 11:00:00")
guest.waitTillAgentIsConnected()
#clear Eventlog and Prefetch directory
antiForensics_obj.clearEventLogFiles()
while antiForensics_obj.is_busy:<
    time.sleep(2)
antiForensics_obj.clearPrefetch()
while antiForensics_obj.is_busy:
    time.sleep(2)
antiForensics_obj.clearUserAssist()
while antiForensics_obj.is_busy:
    time.sleep(2)
antiForensics_obj.clearThumbcache("fortrace")
while antiForensics_obj.is_busy:
    time.sleep(2)
print("Scenario completed!")
time.sleep(3600)
print("Going to sleep...")
time.sleep(5)
guest.shutdown("keep")
while guest.isGuestPowered():
    time.sleep(5)
