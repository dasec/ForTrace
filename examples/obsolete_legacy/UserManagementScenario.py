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
vm_name = "WindowsUserTest{0}".format(random.randint(0, 9999))
guest = virtual_machine_monitor1.create_guest(guest_name=vm_name, platform="windows")
userManagement_obj = None
userManagement_obj = guest.application("userManagement", {})
browser_obj = None
browser_obj = guest.application("webBrowserFirefox", {'webBrowser': "firefox"})

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()
# Create new Useraccount and enable autostart

# Do not use Passwords longer than 14
userManagement_obj.addUser('John', 'A5G2v63-nA3!L')
while userManagement_obj.is_busy:
    time.sleep(2)
userManagement_obj.changeUser('John', 'A5G2v63-nA3!L')
while userManagement_obj.is_busy:
    time.sleep(2)
time.sleep(10)

# Reboot System to new user and install fortrace
guest.shutdown('keep')
while guest.isGuestPowered():
    time.sleep(5)
guest.start("2021-06-02 11:00:00")
guest.waitTillAgentIsConnected()

# Create Useraccount "Fred" and browse some Websites with user John
userManagement_obj.addUser('Fred', 'P45Swor7')
time.sleep(10)
browser_obj.open(url="faz.net")
while browser_obj.is_busy:
    time.sleep(2)
browser_obj.browse_to("heise.de")
while browser_obj.is_busy:
    time.sleep(2)
time.sleep(10)
userManagement_obj.addUser('George', 'P45Swor7')
time.sleep(10)
userManagement_obj.addUser('Ron', 'P45Swor7')
time.sleep(10)
browser_obj.open(url="faz.net")
while browser_obj.is_busy:
    time.sleep(2)
userManagement_obj.changeUser('Fred', 'P45Swor7')
while userManagement_obj.is_busy:
    time.sleep(2)
time.sleep(10)

# Shutdown
guest.shutdown("keep")
while guest.isGuestPowered():
    time.sleep(5)
guest.start("2021-06-02 11:00:00")
guest.waitTillAgentIsConnected()
time.sleep(10)

# Browse some Websites and delete different useraccounts
browser_obj.open(url="faz.net")
while browser_obj.is_busy:
    time.sleep(2)
browser_obj.open(url="unibw.de")
while browser_obj.is_busy:
    time.sleep(2)
browser_obj.open(url="google.com")
while browser_obj.is_busy:
    time.sleep(2)
userManagement_obj.deleteUser('John', "delete")
while userManagement_obj.is_busy:
    time.sleep(2)
userManagement_obj.deleteUser('George', "Keep")
while userManagement_obj.is_busy:
    time.sleep(2)
userManagement_obj.deleteUser('Ron', "secure")
while userManagement_obj.is_busy:
    time.sleep(2)
userManagement_obj.deleteUser('Fred', "delete")
while userManagement_obj.is_busy:
    time.sleep(2)
time.sleep(10)
userManagement_obj.changeUser('fortrace', None)
while userManagement_obj.is_busy:
    time.sleep(2)
time.sleep(30000)

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