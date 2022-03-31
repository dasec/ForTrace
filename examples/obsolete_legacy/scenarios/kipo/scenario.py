#!/usr/bin/env python
# -*- coding: utf-8 -*-

# added by Thomas Schaefer in 2019
# basic layout of a scenario implementation to generate an IT forensically interesting image.

from __future__ import absolute_import
from __future__ import print_function
try:
    import sys
    import time
    import logging
    import xml.etree.ElementTree as ET

    from fortrace.core.vmm import Vmm
    from fortrace.utility.logger_helper import create_logger
    from fortrace.core.vmm import GuestListener

    from fortrace.core.reporter import Reporter

    import hashlib

except ImportError as e:
    print(("Import error in fortracemaster.py! " + str(e)))
    sys.exit(1)

def generate_file_sh256(filename, blocksize=2**20):
    print("creating hash. This might take some time.")
    m = hashlib.sha256()
    with open(filename, "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest()

class Scenario:

    Reporter = None

    def __init__(self, reporter):
        print("initializing Scenario.")
        self.Reporter = reporter
        # test


    def prepareLoadMailbox(self, mail, node):
        type = node[0].text
        from_name = node[1].text
        from_ad = node[2].text
        to_name = node[3].text
        to_ad = node[4].text
        user = node[5].text
        server = node[6].text
        timestamp = node[7].text
        subject = node[8].text
        message = node[9].text

        mail.loadMailboxData(type, from_name, from_ad, to_name, to_ad, user, server, timestamp, subject, message)

        time.sleep(1)

    def veracrypt(self):
        veracrypt_obj = guest.application("veraCryptWrapper", {})
        container_path = "C:\\Users\\Bill\\Desktop\\test.hc"
        container_size = "10M"
        container_pass = "passtest"
        mount_point = "x"
        veracrypt_exe = "\"C:\\Program Files\\VeraCrypt\\VeraCrypt.exe\""
        veracrypt_format_exe = "\"C:\\Program Files\\VeraCrypt\\VeraCrypt Format.exe\""
        data_path = "C:\\Users\\Bill\\Downloads\\"
        data_filename = "test.jpeg"

        # write to report
        self.Reporter.add("veracrypt", "VeraCrypt Container generated and mounted with following parameters: Size:" + container_size + "; pass:" + container_pass + "; path:" + container_path + "; content: " + data_filename)

        veracrypt_obj.createContainer(veracrypt_format_exe, container_path, container_size, container_pass)
        time.sleep(2)
        veracrypt_obj.mountContainer(veracrypt_exe, container_path, container_pass, mount_point)
        time.sleep(10)  # there might be timing issues
        veracrypt_obj.copyToContainer(data_path + data_filename, mount_point.upper() + ':/' + data_filename)
        time.sleep(2)
        veracrypt_obj.dismountContainer(veracrypt_exe, mount_point)

    def mail(self):
        mail = guest.application("mailClientThunderbird", {})
        # Important set a password used by the mail service, it will be saved inside thunderbird
        mail.set_session_password("newPass19")
        while mail.is_busy:
            time.sleep(1)
        mail.add_pop3_account("pop3.web.de", "smtp.web.de", "theo.test1@web.de", "theo.test1@web.de", "Theo Tester", "Example", 2,
                          3, 2, 3)
        while mail.is_busy:
            time.sleep(1)
        # Open thunderbird and check for mail
        mail.open()
        while mail.is_busy:
            time.sleep(1)
        # We are done close the application
        mail.close()

        time.sleep(15)

        tree = ET.parse('data/email_hay.xml')
        root = tree.getroot()

        for item in root:
            self.prepareLoadMailbox(mail, item)

        time.sleep(5)

        tree = ET.parse('data/email_needle.xml')
        root = tree.getroot()

        for item in root:
            # write to report
            self.Reporter.add("mail", "Mail from: " + item[2].text + " to: " + item[4].text + " subject: " + item[8].text + " at: " + item[7].text)
            self.prepareLoadMailbox(mail, item)

    def browser(self):
        url = "http://192.168.2.104/test/index.html"
        browser_obj = None
        browser_obj = guest.application("webBrowserFirefox", {'webBrowser': "firefox"})
        browser_obj.open(url="about:blank")
        # Will download the incrimination picture to default download folder
        browser_obj.download_from(url, 'Download')
        # Report downloaded files
        self.Reporter.add("download", "Downloaded file from: " + url)
        time.sleep(10)


        #browse good links
        tree = ET.parse('data/browse_hay.xml')
        root = tree.getroot()

        for item in root:
            browser_obj.browse_to(item[0].text)

        #browse bad links
        tree = ET.parse('data/browse_needle.xml')
        root = tree.getroot()

        for item in root:
            self.Reporter.add("browsings", "Browsed url: " + item[0].text)
            browser_obj.browse_to(item[0].text)

        browser_obj.close()

sc = Scenario(Reporter())

imagename = "kipo_scenario"
author = "Thomas Schaefer"
hostplatform = "windows"
hashfile = generate_file_sh256("/var/lib/libvirt/images/" + hostplatform + "-template.qcow2")

sc.Reporter.add("imagename", imagename)
sc.Reporter.add("author", author)
sc.Reporter.add("baseimage", hostplatform + "-template.qcow2")
sc.Reporter.add("basehash", "sha256: " + hashfile)

# Instanciate VMM and a VM
logger = create_logger('fortraceManager', logging.DEBUG)
macsInUse = []
guests = []
guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
guest = virtual_machine_monitor1.create_guest(guest_name=imagename, platform="windows")

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()

# Scenario Implementation
sc.browser()
sc.veracrypt()
sc.mail()

# Cleanup
guest.cleanUp("")
guest.shutdown('keep')

#md5 = "md5: " + hashlib.md5(file_as_bytes(open("/var/lib/libvirt/images/backing/" + imagename + ".qcow2", 'rb'))).hexdigest()
sha256 = "sha256: " + generate_file_sh256("/var/lib/libvirt/images/backing/" + imagename + ".qcow2")
sc.Reporter.add("hash", sha256)

# create report
sc.Reporter.generate()
