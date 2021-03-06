# added by Thomas Schaefer in 2019
# testing basic mailbox manipulation functionality

# this is a testscript for running the new-style thunderbird application plugin
# the script assumes that no errors occur during runtime
# note: always check the error state of the mailer application object while waiting
#       and call close on error, you may want to tweak internal timeouts inside the
#       application plugin's module "mailClientThunderbird.py" before deploying for
#       slow VMs
from __future__ import absolute_import
import time
import logging
import xml.etree.ElementTree as ET

from fortrace.core.vmm import Vmm
from fortrace.utility.logger_helper import create_logger
from fortrace.core.vmm import GuestListener


import mailbox
import email.utils
import os

# Instanciate VMM and a VM
logger = create_logger('fortraceManager', logging.DEBUG)
macsInUse = []
guests = []
guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
guest = virtual_machine_monitor1.create_guest(guest_name="tbtest", platform="windows")

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()

# Create a mailer object
mail = guest.application("mailClientThunderbird", {})
# Important set a password used by the mail service, it will be saved inside thunderbird
mail.set_session_password("fortraceMail")
while mail.is_busy:
    time.sleep(1)
# Prepare a new Profile; assume the profile folders don't exist; these options assume a insecure mail server without SSL/TLS using an unencrypted password exchange

#theo.11111@web.de / fortraceMail / Theo Tester
mail.add_pop3_account("pop3.web.de", "smtp.web.de", "theo.11111@web.de", "theo.11111", "Theo Tester", "Example", 2, 3, 2, 3)
while mail.is_busy:
    time.sleep(1)
# Open thunderbird and check for mail
mail.open()
while mail.is_busy:
    time.sleep(1)
# We are done close the application
mail.close()
while mail.is_busy:
    time.sleep(1)
time.sleep(10)

# Send a new mail by invoking thunderbird with special command line options
mail.send_mail(message="testmail", subject="testmail", receiver="theo.test1@web.de")
while mail.is_busy:
    time.sleep(1)
time.sleep(10)

tree = ET.parse('email_hay.xml')
root = tree.getroot()

for item in root:

    type = item[0].text
    from_name = item[1].text
    from_ad = item[2].text
    to_name = item[3].text
    to_ad = item[4].text
    user = item[5].text
    server = item[6].text
    timestamp = item[7].text
    subject = item[8].text
    message = item[9].text

    mail.loadMailboxData(type, from_name, from_ad, to_name, to_ad, user, server, timestamp, subject, message)

    time.sleep(1)

time.sleep(3000)

# We are done, shutdown and keep the VM on disk
#guest.shutdown("keep")
