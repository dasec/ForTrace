#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
import sys
import platform
import time
import logging
import subprocess
import xml.etree.ElementTree as ET
import hashlib
from six.moves import input

#TODO Paths for main and hash need to be changed to correspond with config.json

try:
    from fortrace.core.vmm import Vmm
    from fortrace.utility.logger_helper import create_logger
    from fortrace.core.vmm import GuestListener
    from fortrace.core.reporter import Reporter

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


def create_vm(logger):
    # virtual_machine_monitor1 = Vmm(logger, linux_template='linux_template')
    macsInUse = []
    guests = []
    guestListener = GuestListener(guests, logger)
    virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
    guest = virtual_machine_monitor1.create_guest(guest_name="l-guest01", platform="linux", boottime=None)
    #guest = virtual_machine_monitor1.create_guest(guest_name="w-guest01", platform="windows", boottime=None)
    logger.debug("Try connecting to guest")

    while guest.state != "connected":
        logger.debug(".")
        time.sleep(1)

    logger.debug(guest.guestname + " is connected!")

    return guest


def main():
    """
    Test Script for fortrace.

    :return: no return value
    """
    try:
        imagename = "kipo_scenario"
        author = "Thomas Schaefer"
        hostplatform = "windows"
        hashfile = generate_file_sh256("/var/lib/libvirt/images/" + hostplatform + "-template.qcow2")

        Reporter.add("imagename", imagename)
        Reporter.add("author", author)
        Reporter.add("baseimage", hostplatform + "-template.qcow2")
        Reporter.add("basehash", "sha256: " + hashfile)


        logger = create_logger('fortraceManager', logging.DEBUG)
        logger.info("This is a test script to check the functionallity of the fortrace library" + '\n')

        guest = create_vm(logger)

        # call all test functions you want to run
        tests = {'firefox': test_firefox, 'thunderbird': test_thunderbird, 'veracrypt': test_veracrypt, 'multiuser': test_multiuser}  # all available test functions
        arguments = sys.argv[1:]  # every argument but the first as the first is the filename

        for argument in arguments:
            try:
                tests[argument](guest, logger)
            except Exception as e:
                print(("argument unknown: " + str(e)))

        time.sleep(5)
        logger.debug("All tests completed. Shutting down now.")
        time.sleep(5)
        guest.remove("keep")

        sha256 = "sha256: " + generate_file_sh256("/var/lib/libvirt/images/backing/" + imagename + ".qcow2")
        Reporter.add("hash", sha256)

        # create report
        Reporter.generate()


    ######## CLEANUP ############# ERROR HANDLING
    except KeyboardInterrupt as k:
        logger.debug(k)
        logger.debug("KeyboardInterrupt")
        logger.debug(k)
        logger.debug(virtual_machine_monitor1)
        input("Press Enter to continue...")
        virtual_machine_monitor1.clear()
        logger.debug("cleanup here")
        try:
            virtual_machine_monitor1.clear()
        except NameError:
            logger.debug("well, host1 was not defined!")

        exit(0)

    except Exception as e:
        logger.debug("main gets the error: " + str(e))
        logger.debug("cleanup here")
        input("Press Enter to continue...")
        try:
            virtual_machine_monitor1.clear()
            subprocess.call(["/etc/init.d/libvirt-bin", "restart"])
        except NameError:
            logger.debug("well, host1 was not defined!")
        sys.exit(1)


def test_firefox(guest, logger):
    logger.debug("test_firefox() started.")
    browser_obj = None
    browser_obj = guest.application("webBrowserFirefox", {'webBrowser': "firefox"})
    # open browser
    browser_obj.open(url="dasec.fbi.h-da.de")
    while browser_obj.is_busy:
        time.sleep(2)
    # browse sites
    browser_obj.browse_to("heise.de")
    while browser_obj.is_busy:
        time.sleep(5)
    time.sleep(10)
    # facebook login
    browser_obj.browse_to("facebook.com")
    while browser_obj.is_busy:
        time.sleep(5)
    browser_obj.facebook_login("tom-g1@gmx.de", "FBgoesfortrace", "loginbutton")  # Credentials need to be changed, button id is correct.
    time.sleep(25)
    # download file
    browser_obj.browse_to("python.org/downloads")
    while browser_obj.is_busy:
        time.sleep(15)
    browser_obj.click_xpath_test('/html/body/div/div[3]/div/section/div[1]/ol/li[1]/span[3]/a')
    time.sleep(25)
    browser_obj.click_xpath_test('/html/body/div/div[3]/div/section/article/table/tbody/tr[1]/td[1]/a')
    time.sleep(25)
    browser_obj.press_enter_test()
    time.sleep(25)

    # close browser
    browser_obj.close()
    while browser_obj.is_busy:
        time.sleep(5)
    logger.debug("test_firefox() ended.")

def test_thunderbird(guest, logger):
    logger.debug("test_thunderbird() started.")
    mail = guest.application("mailClientThunderbird", {})

    # perhaps move this code to mailClientThunderbird.py?
    if platform.system() == "Windows":  # need to open once before in Windows to work properly, but in Linux this produces an error.
        mail.open()
        while mail.is_busy:
            time.sleep(2)
        time.sleep(60)
        mail.close()
        while mail.is_busy:
            time.sleep(2)
        time.sleep(20)

    # Important set a password used by the mail service, it will be saved inside thunderbird
    mail.set_session_password("newPass2019")
    while mail.is_busy:
        time.sleep(1)

    time.sleep(20)
    # Prepare a new Profile; assume the profile folders don't exist; these options assume a insecure mail server without SSL/TLS using an unencrypted password exchange
    # theo.11111@web.de / fortraceMail / Theo Tester
    mail.add_imap_account("imap.web.de", "smtp.web.de", "theo.test1@web.de", "theo.test1", "Theo Tester", "Example", 2,
                          3, 1, 3)
    while mail.is_busy:
        time.sleep(1)
    time.sleep(20)
    # Open thunderbird and check for mail
    mail.open()
    while mail.is_busy:
        time.sleep(1)
    time.sleep(60)
    # We are done close the application
    mail.close()
    while mail.is_busy:
        time.sleep(1)
    time.sleep(10)
    # Send a new mail by invoking thunderbird with special command line options
    mail.send_mail(message="testmail", subject="testmail", receiver="theo.test1@web.de")
    while mail.is_busy:
        time.sleep(1)
    time.sleep(20)

    # test load into mailbox function
    tree = ET.parse('data/email_hay.xml')
    root = tree.getroot()

    for item in root:
        prepareLoadMailbox(mail, item)

    time.sleep(5)

    tree = ET.parse('data/email_needle.xml')
    root = tree.getroot()

    for item in root:
        # write to report
        Reporter.add("mail", "Mail from: " + item[2].text + " to: " + item[4].text + " subject: " + item[
            8].text + " at: " + item[7].text)
        prepareLoadMailbox(mail, item)

    logger.debug("test_thunderbird() ended.")

def test_veracrypt(guest, logger):
    logger.debug("test_veracrypt() started.")
    veracrypt_obj = guest.application("veracrypt", {})

    # set-up necessary parameters for veracrypt
    container_path = "C:\\Users\\Bill\\Desktop\\test.hc"
    container_size = "100M"
    container_pass = "passtest"
    mount_point = "x"
    veracrypt_exe = "\"C:\\Program Files\\VeraCrypt\\VeraCrypt.exe\""   # should be in veraCryptWrapper.py
    veracrypt_format_exe = "\"C:\\Program Files\\VeraCrypt\\VeraCrypt Format.exe\""  # should be in veraCryptWrapper.py
    data_path = "C:\\Users\\Bill\\Desktop\\"
    data_filename = "test.txt"

    # create test.txt
    guest.shellExec('echo "This will be test content of a file dedicated for testing VeraCrypt." > ' + data_path + data_filename)
    time.sleep(3)

    veracrypt_obj.createContainer(veracrypt_format_exe, container_path, container_size, container_pass)
    while veracrypt_obj.is_busy:
        time.sleep(2)
    veracrypt_obj.mountContainer(veracrypt_exe, container_path, container_pass, mount_point)
    while veracrypt_obj.is_busy:
        time.sleep(10)  # there might be timing issues
    veracrypt_obj.copyToContainer(data_path + data_filename, mount_point.upper() + ':/' + data_filename)
    while veracrypt_obj.is_busy:
        time.sleep(2)
    veracrypt_obj.unmountContainer(veracrypt_exe, mount_point)
    while veracrypt_obj.is_busy:
        time.sleep(2)

    Reporter.add("veracrypt", "VeraCrypt Container generated and mounted with following parameters: " +
                                   "Size:" + container_size + "; pass:" + container_pass
                                    + "; path:" + container_path + "; content: " + data_filename)

    logger.debug("test_veracrypt() ended.")

def test_multiuser(guest, logger):
    logger.debug("test_multiuser() started.")
    # code
    user_name = 'John'
    user_pass = 'fadf24s'

    userManagement_obj = guest.application("userManagement", {})
    userManagement_obj.addUser(user_name, user_pass)

    logger.debug("test_multiuser() ended.")

if __name__ == "__main__":
    try:
        main()
    except:
        sys.exit(1)
