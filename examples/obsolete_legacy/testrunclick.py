#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
import sys
import time
import logging
import subprocess
from six.moves import input

try:
    from fortrace.core.vmm import Vmm
    from fortrace.utility.logger_helper import create_logger
    from fortrace.core.vmm import GuestListener

except ImportError as e:
    print(("Import error in fortracemaster.py! " + str(e)))
    sys.exit(1)


def create_vm(logger):
    # virtual_machine_monitor1 = Vmm(logger, linux_template='linux_template')
    macsInUse = []
    guests = []
    guestListener = GuestListener(guests, logger)
    virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
   # guest = virtual_machine_monitor1.create_guest(guest_name="w-guest01", platform="windows", boottime=None)
    guest = virtual_machine_monitor1.create_guest(guest_name="l-guest01", platform="linux", boottime=None)
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
        logger.info("This is a test script to check the functionallity of the fortrace library" + '\n')

        guest = create_vm(logger)

        browser_obj = None
        browser_obj = guest.application("webBrowserFirefox", {'webBrowser': "firefox"})
        browser_obj.open(url="faz.net")
        time.sleep(30)
        browser_obj.click_xpath_test('/html/body/div[6]/header/div[1]/div[1]/div[2]/nav/div/ul/li[2]/a')
	time.sleep(15)
        browser_obj.close()

        time.sleep(5)
        guest.remove()




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
