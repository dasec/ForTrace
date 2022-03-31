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
    guest = virtual_machine_monitor1.create_guest(guest_name="w-guest01", platform="windows", boottime="2018-01-01 00:00:00")
    # guest = virtual_machine_monitor1.create_guest(guest_name="w-guest01", platform="windows", boottime=None)
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

        guest.setOSTime("2018-01-01 12:00:00")

        browser_obj = None
        browser_obj = guest.application("webBrowserFirefox", {'webBrowser': "firefox"})
        browser_obj.open(url="faz.net")
        time.sleep(30)
        browser_obj.browse_to("heise.de")
        time.sleep(20)
        browser_obj.browse_to("golem.de")
        time.sleep(30)
        browser_obj.browse_to("slashdot.org")
        time.sleep(50)
        browser_obj.browse_to("distrowatch.com")
        time.sleep(30)
        browser_obj.browse_to("archlinux.org")
        time.sleep(20)
        browser_obj.close()

        time.sleep(5)
        guest.setOSTime("2018-01-01 14:00:00")

        browser_obj = guest.application("webBrowserFirefox", {'webBrowser': "firefox"})
        browser_obj.open(url="faz.net")
        time.sleep(30)
        browser_obj.browse_to("heise.de")
        time.sleep(20)
        browser_obj.browse_to("golem.de")
        time.sleep(30)
        browser_obj.browse_to("slashdot.org")
        time.sleep(50)
        browser_obj.browse_to("distrowatch.com")
        time.sleep(30)
        browser_obj.browse_to("archlinux.org")
        time.sleep(20)
        browser_obj.close()

        time.sleep(5)
        se = guest.shellExec("calc")
        time.sleep(10)
        guest.killShellExec(se)

        time.sleep(5)
        # guest.setOSTime("2018-01-02 11:00:00")
        guest.shutdown('keep')
        while guest.isGuestPowered():
            time.sleep(1)
        guest.start("2018-01-02 11:00:00")
        guest.waitTillAgentIsConnected()

        browser_obj = guest.application("webBrowserFirefox", {'webBrowser': "firefox"})
        browser_obj.open(url="faz.net")
        time.sleep(30)
        browser_obj.browse_to("heise.de")
        time.sleep(20)
        browser_obj.browse_to("golem.de")
        time.sleep(30)
        browser_obj.browse_to("archlinux.org")
        time.sleep(20)
        browser_obj.close()

        time.sleep(5)
        # guest.setOSTime("2018-01-03 13:00:00")
        guest.shutdown('keep')
        while guest.isGuestPowered():
            time.sleep(1)
        guest.start("2018-01-03 13:00:00")
        guest.waitTillAgentIsConnected()

        browser_obj = guest.application("webBrowserFirefox", {'webBrowser': "firefox"})
        browser_obj.open(url="faz.net")
        time.sleep(30)
        browser_obj.browse_to("heise.de")
        time.sleep(20)
        browser_obj.browse_to("golem.de")
        time.sleep(30)
        browser_obj.browse_to("slashdot.org")
        time.sleep(50)
        browser_obj.browse_to("distrowatch.com")
        time.sleep(30)
        browser_obj.browse_to("archlinux.org")
        time.sleep(20)
        browser_obj.close()

        time.sleep(5)
        # guest.setOSTime("2018-01-04 12:00:00")
        guest.shutdown('keep')
        while guest.isGuestPowered():
            time.sleep(1)
        guest.start("2018-01-04 12:00:00")
        guest.waitTillAgentIsConnected()

        browser_obj = guest.application("webBrowserFirefox", {'webBrowser': "firefox"})
        browser_obj.open(url="faz.net")
        time.sleep(30)
        browser_obj.browse_to("heise.de")
        time.sleep(20)
        browser_obj.browse_to("golem.de")
        time.sleep(30)
        browser_obj.browse_to("slashdot.org")
        time.sleep(50)
        browser_obj.browse_to("archlinux.org")
        time.sleep(20)
        browser_obj.close()

        time.sleep(5)
        # guest.setOSTime("2018-01-05 13:00:00")
        guest.shutdown('keep')
        while guest.isGuestPowered():
            time.sleep(1)
        guest.start("2018-01-05 13:00:00")
        guest.waitTillAgentIsConnected()

        browser_obj = guest.application("webBrowserFirefox", {'webBrowser': "firefox"})
        browser_obj.open(url="faz.net")
        time.sleep(30)
        browser_obj.browse_to("heise.de")
        time.sleep(20)
        browser_obj.browse_to("golem.de")
        time.sleep(30)
        browser_obj.browse_to("archlinux.org")
        time.sleep(20)
        browser_obj.browse_to("wikipedia.org")
        time.sleep(10)
        browser_obj.close()

        time.sleep(5)
        se = guest.shellExec("calc")
        time.sleep(8)
        guest.killShellExec(se)

        time.sleep(5)
        # guest.setOSTime("2018-01-06 14:00:00")
        guest.shutdown('keep')
        while guest.isGuestPowered():
            time.sleep(1)
        guest.start("2018-01-06 14:00:00")
        guest.waitTillAgentIsConnected()

        browser_obj = guest.application("webBrowserFirefox", {'webBrowser': "firefox"})
        browser_obj.open(url="faz.net")
        time.sleep(30)
        browser_obj.browse_to("heise.de")
        time.sleep(20)
        browser_obj.browse_to("golem.de")
        time.sleep(30)
        browser_obj.browse_to("slashdot.org")
        time.sleep(50)
        browser_obj.browse_to("distrowatch.com")
        time.sleep(30)
        browser_obj.browse_to("archlinux.org")
        time.sleep(20)
        browser_obj.close()

        time.sleep(5)
        # guest.setOSTime("2018-01-07 12:00:00")
        guest.shutdown('keep')
        while guest.isGuestPowered():
            time.sleep(1)
        guest.start("2018-01-07 12:00:00")
        guest.waitTillAgentIsConnected()

        browser_obj = guest.application("webBrowserFirefox", {'webBrowser': "firefox"})
        browser_obj.open(url="faz.net")
        time.sleep(30)
        browser_obj.browse_to("heise.de")
        time.sleep(20)
        browser_obj.browse_to("golem.de")
        time.sleep(30)
        browser_obj.browse_to("slashdot.org")
        time.sleep(50)
        browser_obj.browse_to("distrowatch.com")
        time.sleep(30)
        browser_obj.browse_to("archlinux.org")
        time.sleep(20)
        browser_obj.close()

        time.sleep(5)
        guest.remove("keep")




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
