import time
import logging
import subprocess

try:
    from fortrace.core.vmm import Vmm
    from fortrace.utility.logger_helper import create_logger
    from fortrace.core.vmm import GuestListener
    from fortrace.core.reporter import Reporter
except ImportError as ie:
    print("Import error! in  " + str(ie))
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
ps_obj = guest.application("powerShell", {})
subprocess.call(["virsh", "attach-device", "test", "--file", "/data/fortrace-pool/usb_device.xml"])
time.sleep(5)
#some buffer to make sure device is attached

#ps_obj.open()
#while ps_obj.is_busy:
#    time.sleep(1)
#a = "ls C:/Users/fortrace/Desktop"
#b = "Remove-Item C:/Users/fortrace/Desktop/test.txt"
#c = "Get-History"
#ps_obj.pscommand(a)
#while ps_obj.is_busy:
#    time.sleep(1)
#ps_obj.pscommand(b)
#while ps_obj.is_busy:
#    time.sleep(1)
#ps_obj.pscommand(a)
#while ps_obj.is_busy:
#    time.sleep(1)
#ps_obj.close()
#while ps_obj.is_busy:
#    time.sleep(1)

#a = "cat (Get-PSReadlineOption).HistorySavePath"

#ps_obj.pscommand(a)
#while ps_obj.is_busy:
#    time.sleep(1)
#ps_obj.disableHistory()
#while ps_obj.is_busy:
#    time.sleep(1)
#ps_obj.delHistory()
#while ps_obj.is_busy:
#    time.sleep(1)
#ps_obj.pscommand(a)
#while ps_obj.is_busy:
#    time.sleep(1)

#ps_obj.disableUAC()
#while ps_obj.is_busy:
#    time.sleep(1)
#guest.shutdown("keep")
#while guest.isGuestPowered():
 #   time.sleep(5)
#guest.start()
#guest.waitTillAgentIsConnected()
ps_obj.autScripts("Bypass")
while ps_obj.is_busy:
    time.sleep(1)
ps_obj.autScripts("ds")
while ps_obj.is_busy:
    time.sleep(1)

#a = "& C:/Users/fortrace/Desktop/test.ps1"
a = "Query-fmExplorerSearch -SearchString 'motor'"
ps_obj.pscommand(a)
while ps_obj.is_busy:
    time.sleep(1)

#ps_obj.installps("C:\\Users\\fortrace\\Desktop\\CrystalDisk.exe")
#while ps_obj.is_busy:
#    time.sleep(1)
#ps_obj.enableUAC()
#while ps_obj.is_busy:
#    time.sleep(1)
#guest.shutdown("keep")
#while guest.isGuestPowered():
#    time.sleep(5)
#guest.start()
#guest.waitTillAgentIsConnected()

