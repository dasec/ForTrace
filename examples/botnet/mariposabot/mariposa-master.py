#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This script demonstrates the MariposaBot simulation.

"""

from __future__ import absolute_import
from __future__ import print_function
import logging
import subprocess
import sys
import time
from six.moves import input

try:
    from fortrace.core.vmm import Vmm
    from fortrace.core.vmm import GuestListener
    from fortrace.utility.logger_helper import create_logger
    from fortrace.botnet.bots.mariposa.mariposaprotocol import MariposaProtocol
    from fortrace.botnet.core.botmonitorbase import BotMonitorBase
    from fortrace.botnet.core.simulationmanager import SimulationManager

except ImportError as ie:
    print(("Import error in fortracemaster.py! " + str(ie)))
    sys.exit(1)


def main():
    """
    Test Script for fortrace.

    :return: no return value
    """
    try:
        # create logger
        logger = create_logger('fortraceManager', logging.DEBUG)

        # program code
        logger.info("This is a sample script for using the MariposaBot simulation!" + '\n')

        # create GuestListener
        macs_in_use = []
        guests = []
        guest_listener = GuestListener(guests, logger)

        # create all control instances
        virtual_machine_monitor1 = Vmm(macs_in_use, guests, logger)
        bmon = BotMonitorBase()
        sm = SimulationManager(bmon)

        # setup groups
        bmon.group_manager.setup_group('mariposa_bot', 'mariposa-bot.py')
        bmon.group_manager.setup_group('mariposa_cnc', 'mariposa-cnc.py')
        bmon.group_manager.setup_group('mariposa_bm', 'mariposa-bm.py')

        # instanciate each vm
        cnc = virtual_machine_monitor1.create_guest(guest_name="windows-guest01", platform="windows")
        bmast = virtual_machine_monitor1.create_guest(guest_name="windows-guest02", platform="windows")
        bot1 = virtual_machine_monitor1.create_guest(guest_name="windows-guest03", platform="windows")
        bot2 = virtual_machine_monitor1.create_guest(guest_name="windows-guest04", platform="windows")

        # wait for dhcp
        cnc.wait_for_dhcp()
        bmast.wait_for_dhcp()
        bot1.wait_for_dhcp()
        bot2.wait_for_dhcp()

        # setup variables, etc.
        cnc_host = str(cnc.ip_internet)
        cnc_port = MariposaProtocol.MARIPOSA_PORT1
        bmon.globals["cnc"] = cnc_host  # optional, default: MARIPOSA_HOST1
        bmon.globals["port"] = cnc_port  # optional, default: MARIPOSA_PORT1
        bmon.globals["bm_ip"] = str(bmast.ip_internet)  # needed

        # allocate vms to groups
        bmon.group_manager.add_bot_to_group('mariposa_cnc', cnc)
        bmon.group_manager.add_bot_to_group('mariposa_bm', bmast)
        bmon.group_manager.add_bot_to_group('mariposa_bot', bot1)
        bmon.group_manager.add_bot_to_group('mariposa_bot', bot2)

        # begin listening for incomming connections
        bmon.start()

        # wait till the simulation is ready
        sm.wait_for_bots(4)

        # wait till bots have completed the initialization phase
        time.sleep(2 * 60)
        time.sleep(30)  # wait some more
        bl = bmon.group_manager.get_bots_by_group_name('mariposa_bm')
        for b in bl:
            print("sending order to: " + b.ip_address)
            order = {
                'cnc_target_host': cnc_host,
                'cnc_target_port': cnc_port,
                'command': 'enable_google',
                'args': ''
            }
            b.place_order(order)
        time.sleep(5 * 60)
        bl = bmon.group_manager.get_bots_by_group_name('mariposa_bm')
        for b in bl:
            print("sending order to: " + b.ip_address)
            order = {
                'cnc_target_host': cnc_host,
                'cnc_target_port': cnc_port,
                'command': 'download2',
                'args': ''
            }
            b.place_order(order)

        input("press enter to exit")
        # close all connections
        bmon.stop()
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
