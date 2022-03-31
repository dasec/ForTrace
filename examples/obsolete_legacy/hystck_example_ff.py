#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
import sys
import time
import logging
import subprocess
from six.moves import range
from six.moves import input

try:
    from fortrace.core.vmm import Vmm
    from fortrace.utility.logger_helper import create_logger
    from fortrace.core.vmm import GuestListener

except ImportError as e:
    print(("Import error in fortracemaster.py! " +str(e)))
    sys.exit(1)

def deploy(guest, logger):
    logger.debug("create deployer")
    deployObj = guest.application("deployer", {})
    logger.debug("deploy")
    deployObj.deploy('/media/Daten/test.iso')
    while deployObj.is_busy:  # wait until the object is ready
        logger.debug("deploy process is busy!")
        time.sleep(3)

def gen_browser_traffic(guest, logger):
    f = open("alexa.csv", "r")

    browser_obj = None
    browser_opened = False
    error = False
    error_count = 0
    counter = 0
    """Use one Browser for all browser calls.
    except the browser window is crushed. If so, create a new one"""

    for line in f:
        counter += 1
        if (int(counter) % 10) == 0:
            logger.debug("Link: " + str(counter))
        #if browser is not opened -> open it with a website
        if browser_opened is False:
            logger.debug("browser_opened is False")
            logger.debug("create browser object")
            browser_obj = guest.application("webBrowserFirefox", {'webBrowser': "firefox"})
            logger.debug("browser object created")
            logger.debug("open browser with url: " + line)
            browser_obj.open(url="h-da.de")
            browser_opened = True
            error = False
            while not browser_obj.is_opened:
                if browser_obj.has_error:
                    #error occurs, so the browser was closes by the guest,
                    #create a new one
                    logger.debug("error detected openBrowser wait for browser, break out")
                    browser_opened = False
                    browser_obj.is_busy = False
                    error = True
                    error_count = error_count +1
                    break
                time.sleep(2)
                logger.debug("sleep, because firefox is not opened")
        #else: browser is openend, so call a site
        else:
            logger.debug("browser to url: " + line)
            browser_obj.browse_to(line)
                    #     #after, browser 5 links on this site
        for i in range(0, 1):
            while browser_obj.is_busy:
                if browser_obj.has_error:
                    #error occurs, so the browser was closes by the guest,
                    #create a new one
                    logger.debug("error detected openBrowser, break out")
                    browser_opened = False
                    browser_obj.is_busy = False
                    error = True
                    error_count = error_count +1
                time.sleep(0.01)
            if error:
                break
            logger.debug("click link 1 on this page")
            browser_obj.browse_to_link_number(1)
            #error handling
            while browser_obj.is_busy:
                if browser_obj.has_error:
                    #error occurs, so the browser was closes by the guest,
                    #create a new one
                    logger.debug("error detected openBrowser, break out")
                    browser_opened = False
                    browser_obj.is_busy = False
                    error = True
                    error_count = error_count +1
                time.sleep(0.01)
            if error:
                break

    logger.debug("alexa top sites file is finished, close the browser and end the programm")
    logger.debug("Count crashes :" + str(error_count))
    browser_obj.close()

def gen_IM_traffic(guest, logger):
    logger.debug("create instantMessenger")
    instantmessengerobj = guest.application("instantMessenger", {})
    logger.debug("set_config")
    instantmessengerobj.set_config(jabber_id="vm01@einfachjabber.de", password="L8UW6Aba")
    logger.debug("open instant messenger")
    instantmessengerobj.open()
    time.sleep(20)
    for i in range(10):
        while instantmessengerobj.is_busy is True:  # wait until the object is ready
            logger.debug("pidgin is busy!")
            time.sleep(0.1)
        logger.debug("send_msg_to: " + str(i) + ". time")
        #send instant message
        instantmessengerobj.send_msg_to("vm01@einfachjabber", "Hey Dude, guest01 is talking")
        instantmessengerobj.is_busy = True
        logger.debug("Message sent no.: " + str(i))

        time.sleep(3)

    instantmessengerobj.close()
    logger.debug("closed instantmessenger object")
    time.sleep(10)

def gen_email_traffic(guest, logger):
    mailerobj = guest.application("mailClient", {})

    mailerobj.set_config("Windows guest", "fortrace007@gmail.com", "f!8Uq6b7hKMJX9vz", "fortrace007@gmail.com",
        "imap.googlemail.com", "smtp.googlemail.com")

    #logger.debug("fortracemanager: config is set up, next step: create")
    mailerobj.open()


    while mailerobj.is_busy is True:  # wait until the object is ready
        logger.debug("thunderbird is busy!")
        time.sleep(1)

    mailerobj.send_mail("fortrace007@gmail.com", "Linux guest is alive", "Hello dude!")


    while mailerobj.is_busy is True:  # wait until the object is ready
        logger.debug("thunderbird is busy!")
        time.sleep(1)
    #for i in range(2):
    #    while mailerobj.is_busy is True:  # wait until the object is ready
    #        logger.debug("thunderbird is busy!")
    #        time.sleep(1)
    #    mailerobj.send_mail("reinhard.stampp@rstampp.net", "Windows guest is alive", "Hello Reinhard!")
    #    logger.debug("Email gesendet no.: " + str(i))
    #    time.sleep(3)
    mailerobj.close()
    time.sleep(10)

def create_vm(logger):
    #virtual_machine_monitor1 = Vmm(logger, linux_template='linux_template')
    macsInUse = []
    guests = []
    guestListener = GuestListener(guests, logger)
    virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
    guest = virtual_machine_monitor1.create_guest(guest_name="w-guest01", platform="windows")

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
        logger = create_logger('fortraceManager', logging.DEBUG)
        logger.info("This is a test script to check the functionallity of the fortrace library" +'\n')

        guest = create_vm(logger)

        #deploy(guest, logger)
        #gen_email_traffic(guest, logger)
        gen_browser_traffic(guest, logger)
        #gen_IM_traffic(guest, logger)



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


if __name__ == "__main__":
    try:
        main()
    except:
        sys.exit(1)
