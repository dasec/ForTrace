#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This module contains an example on how to control the virtual device drivers via the DevControlClient.

"""

from __future__ import absolute_import
from __future__ import print_function
import logging
import sys
import time
import subprocess
from six.moves import input

try:
    from fortrace.core.vmm import Vmm
    from fortrace.core.vmm import GuestListener
    from fortrace.utility.logger_helper import create_logger
    from fortrace.inputDevice.devcontroller import DevControlClient

except ImportError as ie:
    print(("Import error in devclient_example.py! " + str(ie)))
    sys.exit(1)


def main():
    """
    Test Script for fortrace with DevControlClient.

    :return: no return value
    """
    try:
        # create logger
        logger = create_logger('fortraceManager', logging.DEBUG)

        # program code
        logger.info("This is a sample script for using the ZeusBot simulation!" + '\n')

        # create GuestListener
        macs_in_use = []
        guests = []
        guest_listener = GuestListener(guests, logger)

        # create all control instances
        virtual_machine_monitor1 = Vmm(macs_in_use, guests, logger)

        bot = virtual_machine_monitor1.create_guest(guest_name="windows-guest01", platform="windows")

        bot.wait_for_dhcp()

        # at this point userspace tools and drivers should have been started
        # generate the client object for the drivers

        bot_drv = DevControlClient()
        bot_drv.connect(bot)

        # this will call winver as a demonstration
        bot_drv.kb_send_special_key("ESC", lctrl=True)
        time.sleep(2)
        bot_drv.kb_send_text("winver\n")  # the function also supports other escape codes to like '\b' for backspace
        time.sleep(2)
        bot_drv.kb_send_special_key("ENTER")
        time.sleep(2)

        # shutdown
        bot_drv.close()
        virtual_machine_monitor1.clear()
        sys.exit(0)

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
