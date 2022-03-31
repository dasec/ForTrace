#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This module an example for running a nmap portscan and a ncrack portcrack on an other host.

"""

from __future__ import absolute_import
from __future__ import print_function
import logging
import subprocess
import sys
from six.moves import input

try:
    from fortrace.core.vmm import Vmm
    from fortrace.core.vmm import GuestListener
    from fortrace.utility.logger_helper import create_logger
    from fortrace.attacks.nmap import Nmap
    from fortrace.attacks.ncrack import Ncrack

except ImportError as ie:
    print(("Import error in hello-master.py! " + str(ie)))
    sys.exit(1)


def main():
    """
    Test Script for fortrace with HelloBot.

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

        # instanciate each vm
        initiator = virtual_machine_monitor1.create_guest(guest_name="windows-guest01", platform="windows")
        target = virtual_machine_monitor1.create_guest(guest_name="windows-guest02", platform="windows")

        # wait for dhcp
        initiator.wait_for_dhcp()
        target.wait_for_dhcp()

        # run nmap portscan
        r1 = Nmap.guest_nmap_tcp_syn_scan(initiator, target)
        r1.wait()

        # run ncrack on ssh port
        r2 = Ncrack.crack_guests(initiator, target, service="ssh", user_list=["root", "admin", "user", "vm"], password_list=["root", "password", "vm", "admin", "user"])
        r2.wait()

        # cleanup
        virtual_machine_monitor1.clear()
        print("simulation has ended!")
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
