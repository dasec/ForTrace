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
openBrow = True
browse_to = True
browse_to_link_number = True
download_from = True
closeBro = True

# Instanciate VMM and a VM
logger = create_logger('fortraceManager', logging.INFO)
macsInUse = []
guests = []
guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
imagename = "webBrowserFirefox_testscript"
guest = virtual_machine_monitor1.create_guest(guest_name=imagename, platform="windows")

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()

# Create Browser object
browser_obj = guest.application("webBrowserFirefox", {'webBrowser': "firefox"})

# Open Browser
url = "https://coronavirus.jhu.edu/map.html"
logger.info("Opening Browser Window")
try:
    browser_obj.open(url)
    while not browser_obj.is_opened:
        time.sleep(2)
except Exception as e:
    openBrow = False
    print("An error occured: ")
    print(e)
time.sleep(5)


# Browse to another Website
url2 = "https://www.bbc.com/"
logger.info("Browsing to another website")
try:
    browser_obj.browse_to(url2)
    while browser_obj.is_busy is True:
        time.sleep(2)
except Exception as e:
    browse_to = False
    print("An error occured: ")
    print(e)
time.sleep(5)


# Browse to specified link number
link_number = 2
try:
    browser_obj.browse_to_link_number(link_number)
    while browser_obj.is_busy is True:
        time.sleep(2)
except Exception as e:
    browse_to_link_number = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# TODO:
#  browse_to_link_name(self, link_name)
#  send_keys_to_browser_element
#  facebook_login   (experimental?)
#  click_xpath_test (Leiche?)
#  press_enter_test (Leiche?)
#  save_as          (Leiche?)
#  find_firefox_path (Sinn?)
# Doku?

# Download from website
url3 = "https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v8.1.4/npp.8.1.4.portable.x64.zip"
selector = "OK"
logger.info("Downloading file from Website")
try:
    browser_obj.download_from(url3, selector)
    while browser_obj.is_busy is True:
        time.sleep(10)
except Exception as e:
    copyToContainer = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Close browser
logger.info("Closing browser")
try:
    browser_obj.close()
    while browser_obj.is_busy is True:
        time.sleep(2)
except Exception as e:
    closeBro = False
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
logger.info("open: " + str(openBrow))
logger.info("browse_to: " + str(browse_to))
logger.info("browse_to_link_number: " + str(browse_to_link_number))
logger.info("download_from: " + str(download_from))
logger.info("close: " + str(closeBro))


