import time
import logging

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
add_pop3_account = True
mailOpen = True
send_mail = True
mailClose = True

# Instanciate VMM and a VM
logger = create_logger('fortraceManager', logging.INFO)
macsInUse = []
guests = []
guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
imagename = "mailClientThunderbird_Testscript"
guest = virtual_machine_monitor1.create_guest(guest_name=imagename, platform="windows")

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()

# Create mailClient object
mail = guest.application("mailClientThunderbird", {})

# Important set a password used by the mail service, it will be saved inside thunderbird
password = ""
mail.set_session_password(password)
logger.debug("session password is: {0}". format(password))
while mail.is_busy:
    time.sleep(1)

# add mail account
pop3_srv = "pop3.web.de"
smtp_srv = "smtp.web.de"
mail_addr = "theo.test2@web.de"
usr_name = "theo.test2@web.de"
full_name = "Theo Tester"
smtp_description = "Example"
logger.debug("adding pop3 account")
try:
    mail.add_pop3_account(pop3_srv, smtp_srv, mail_addr, usr_name, full_name, smtp_description, 2, 3, 2, 3)
    while mail.is_busy:
        time.sleep(1)
except Exception as e:
    add_pop3_account = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# Open thunderbird and check for mail
logger.info("opening Thunderbird")
try:
    mail.open()
    while mail.is_busy:
        time.sleep(1)
except Exception as e:
    mailOpen = False
    print("An error occured: ")
    print(e)
time.sleep(30)

# send test mail
reciever = "theo.test1@web.de"
subject = "Test-Email"
message = "Hi, here's a message"
logger.info("sending a test email")
try:
    mail.send_mail(reciever, subject, message)
    while mail.is_busy:
        time.sleep(1)
except Exception as e:
    send_mail = False
    print("An error occured: ")
    print(e)
time.sleep(30)

# We are done close the application
logger.debug("closing Thunderbird")
try:
    mail.close()
except Exception as e:
    mailClose = False
    print("An error occured: ")
    print(e)
time.sleep(5)

# End of the Test script
logger.info("done")
# Shut down system and delete guest
guest.shutdown("keep")
while guest.isGuestPowered():
    time.sleep(5)
guest.delete()
logger.info("Scenario finished!")
logger.info("Results:")
logger.info("add_pop3_account: " + str(add_pop3_account))
logger.info("open: " + str(mailOpen))
logger.info("send_mail: " + str(send_mail))
logger.info("close: " + str(mailClose))