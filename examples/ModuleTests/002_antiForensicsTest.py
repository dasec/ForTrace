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

# This test script verifies the functionality and shows the usage of the different antiForensics functions.
# The effect of some functions may interfere with each other (e.g. cleaning the Event Log and then deleting the log
# files seems pretty pointless

# Function status
disableEventLog = True
disableHibernation = True
disablePageFile = True
disablePrefetch = True
disableRecentFiles = True
disableRecycleBin = True
disableThumbcache = True
disableUserAssist = True
clearEventLogFiles = True
clearEventLogEntries = True
clearJumpLists = True
clearPrefetch = True
clearThumbcache = True
clearUserAssist = True
clearRecentDocs = True
setRegistryKey = True
deleteRegistryKey = True

# Instanciate VMM and a VM
logger = create_logger('fortraceManager', logging.INFO)
macsInUse = []
guests = []
guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
imagename = "antiForensics_testscript"
guest = virtual_machine_monitor1.create_guest(guest_name=imagename, platform="windows")

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()

# Create mailClient object
antifor = guest.application("antiForensics", {})

# Disable the Recycle Bin
logger.info("Disabling the Recycle Bin")
try:
    antifor.disableRecycleBin("1")
    while antifor.is_busy is True:
        time.sleep(1)
except Exception as e:
    disableRecycleBin = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Disble creation of Thumbcache entries
logger.info("Disabling the Thumbcache")
try:
    antifor.disableThumbcache("1")
    while antifor.is_busy is True:
        time.sleep(1)
except Exception as e:
    disableThumbcache = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Disble creation of Prefetch files
logger.info("Disabling Prefetch")
try:
    antifor.disablePrefetch("1")
    while antifor.is_busy is True:
        time.sleep(1)
except Exception as e:
    disablePrefetch = False
    print("An error occured: ")
    print(e)
time.sleep(5)


# clear Event log entries
# Event Log service must be running
logger.info("Clearing Event log entries")
try:
    antifor.clearEventLogEntries("security")
    while antifor.is_busy is True:
        time.sleep(1)
except Exception as e:
    clearEventLogEntries = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Disable the Event Log Service
# CAUTION: Disabling the Service does NOT prevent the creation of events, but is necessary to delete the Log files.
logger.info("Disabling the Event Log service")
try:
    antifor.disableEventLog("1")
    while antifor.is_busy is True:
        time.sleep(1)
except Exception as e:
    disableEventLog = False
    print("An error occured: ")
    print(e)
time.sleep(5)


# Disable the creation of UserAssist entries in the Registry
logger.info("Disabling UserAssist")
try:
    antifor.disableUserAssist("1")
    while antifor.is_busy is True:
        time.sleep(1)
except Exception as e:
    disableUserAssist = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Disable System Hibernation and therefore the creation of the Hibernation file
logger.info("Disabling Hibernation")
try:
    antifor.disableHibernation("1")
    while antifor.is_busy is True:
        time.sleep(1)
except Exception as e:
    disableHibernation = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Disable the page file usage
# This can have a negative effect on the system performance, but clearing the pagefile at shutdown
# did not work in every test run
logger.info("Disabling page file usage")
try:
    antifor.disablePagefile("1")
    while antifor.is_busy is True:
        time.sleep(1)
except Exception as e:
    disablePageFile = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# disable recent files
logger.info("Disabling recent files")
try:
    antifor.disableRecentFiles("1")
    while antifor.is_busy is True:
        time.sleep(1)
except Exception as e:
    disableRecentFiles = False
    print("An error occured: ")
    print(e)
time.sleep(5)

##############
# To ensure all set options are active, the system is rebooted
##############
guest.shutdown("keep")
while guest.isGuestPowered():
    time.sleep(5)
guest.start()
guest.waitTillAgentIsConnected()

# clear User Assist Registry key
logger.info("Deleting User Assist")
try:
    antifor.clearUserAssist()
    while antifor.is_busy is True:
        time.sleep(1)
except Exception as e:
    clearUserAssist = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# clear Recent Docs Registry key
logger.info("Deleting Recent Docs")
try:
    antifor.clearRecentDocs()
    while antifor.is_busy is True:
        time.sleep(1)
except Exception as e:
    clearRecentDocs = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# clear Event Log files
logger.info("Deleting Event Log files")
try:
    antifor.clearEventLogFiles()
    while antifor.is_busy is True:
        time.sleep(1)
except Exception as e:
    clearEventLogFiles = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Clear Prefetch Files
logger.info("Clearing Prefetch files")
try:
    antifor.clearPrefetch()
    while antifor.is_busy is True:
        time.sleep(1)
except Exception as e:
    clearPrefetch = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Clear Thumbcache files
logger.info("Clearing Thumbcache files")
try:
    antifor.clearThumbcache("fortrace")
    while antifor.is_busy is True:
        time.sleep(1)
except Exception as e:
    clearThumbcache = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Clear Jumplist files
logger.info("Clearing Jumplist files")
try:
    antifor.clearJumpLists("fortrace")
    while antifor.is_busy is True:
        time.sleep(1)
except Exception as e:
    clearJumpLists = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Set Registry key
logger.info("Changing user defined Registry key")
regKey_set = r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
regkey_set_value = "DisableThumbnails"
regkey_set_type = "REG_DWORD"
try:
    antifor.setRegistryKey(regKey_set, regkey_set_type, regkey_set_value, "1")
    while antifor.is_busy is True:
        time.sleep(1)
except Exception as e:
    setRegistryKey = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Delete Registry key
regkey_del = r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Power"
regkey_del_val = "HibernateEnabledDefault"
try:
    antifor.deleteRegistryKey(regkey_del, regkey_del_val)
    while antifor.is_busy is True:
        time.sleep(1)
except Exception as e:
    deleteRegistryKey = False
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
logger.info("disableEventLog: " + str(disableEventLog))
logger.info("disableHibernation: " + str(disableHibernation))
logger.info("disablePageFile: " + str(disablePageFile))
logger.info("disablePrefetch: " + str(disablePrefetch))
logger.info("disableRecentFiles: " + str(disableRecentFiles))
logger.info("disableRecycleBin: " + str(disableRecycleBin))
logger.info("disableThumbcache: " + str(disableThumbcache))
logger.info("disableUserAssist: " + str(disableUserAssist))
logger.info("clearEventLogEntries: " + str(clearEventLogEntries))
logger.info("clearEventLogFiles: " + str(clearEventLogFiles))
logger.info("clearJumpLists: " + str(clearJumpLists))
logger.info("clearPrefetch: " + str(clearPrefetch))
logger.info("clearThumbcache: " + str(clearThumbcache))
logger.info("clearUserAssist: " + str(clearUserAssist))
logger.info("clearRecentDocs: " + str(clearRecentDocs))
logger.info("setRegistryKey: " + str(setRegistryKey))
logger.info("deleteRegistryKey: " + str(deleteRegistryKey))
