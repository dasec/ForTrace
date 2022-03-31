#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This module contains the HelloBot global control script.
    For the legacy version see hello-master-legacy.py .
    The script itself will create the vms.
    Setup the groups and their associated control-scripts and run a small simulation.

"""

from __future__ import absolute_import
from __future__ import print_function
import logging
import subprocess
import sys
from time import sleep
from six.moves import range
from six.moves import input

try:
    from fortrace.core.vmm import Vmm
    from fortrace.core.vmm import GuestListener
    from fortrace.utility.logger_helper import create_logger
    from fortrace.botnet.core.botmonitorbase import BotMonitorBase
    from fortrace.botnet.core.simulationmanager import SimulationManager
    from fortrace.botnet.bots.hellobot.hello_bot import HELLO_PORT

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
        logger.info("This is a sample script for testing the HelloBot Sample" + '\n')

        # create GuestListener
        macs_in_use = []
        guests = []
        guest_listener = GuestListener(guests, logger)

        # create all control instances
        virtual_machine_monitor1 = Vmm(macs_in_use, guests, logger)
        bmon = BotMonitorBase()
        sm = SimulationManager(bmon)

        # setup groups
        bmon.group_manager.setup_group('hello_bot', 'hello-bot.py')
        bmon.group_manager.setup_group('hello_cnc', 'hello-cnc.py')
        bmon.group_manager.setup_group('hello_bm', 'hello-bm.py')

        # instantiate each vm
        cnc = virtual_machine_monitor1.create_guest(guest_name="windows-guest01", platform="windows")
        bmast = virtual_machine_monitor1.create_guest(guest_name="windows-guest02", platform="windows")
        bot1 = virtual_machine_monitor1.create_guest(guest_name="windows-guest03", platform="windows")
        bot2 = virtual_machine_monitor1.create_guest(guest_name="windows-guest04", platform="windows")
        bot3 = virtual_machine_monitor1.create_guest(guest_name="windows-guest04", platform="windows")

        # wait for dhcp
        cnc.wait_for_dhcp()
        bmast.wait_for_dhcp()
        bot1.wait_for_dhcp()
        bot2.wait_for_dhcp()
        bot3.wait_for_dhcp()

        # setup some variables, for demonstration purposes
        bmon.globals["cnc"] = str(cnc.ip_internet)
        bmon.globals["bmast"] = str(bmast.ip_internet)

        # allocate vms to groups
        bmon.group_manager.add_bot_to_group('hello_cnc', cnc)
        bmon.group_manager.add_bot_to_group('hello_bm', bmast)
        bmon.group_manager.add_bot_to_group('hello_bot', bot1)
        bmon.group_manager.add_bot_to_group('hello_bot', bot2)
        bmon.group_manager.add_bot_to_group('hello_bot', bot3)

        # begin listening for incomming connections
        bmon.start()

        # wait till the simulation is ready
        sm.wait_for_bots(5)

        # actions
        for i in range(0, 10):
            print("round " + str(i))
            bl = bmon.group_manager.get_bots_by_group_name("hello_bm")
            for b in bl:
                print(b.ip_address + " is placing an order")
                msg = "hello: " + str(i)
                order = {
                    'cnc_target': str(cnc.ip_internet),
                    'cnc_target_port:': HELLO_PORT,
                    'command': 'send',
                    'bot_target': "192.168.110.1",  # this is the hypervisor
                    'msg': msg
                }
                b.place_order(order)
            sleep(5)
            bl = bmon.group_manager.get_bots_by_group_name("hello_bot")
            for b in bl:
                print(b.ip_address + " is pulling orders")
                b.pull_orders(str(cnc.ip_internet), HELLO_PORT)
            sleep(5)
            for b in bl:
                print(b.ip_address + " is executing orders")
                b.execute_orders()
            sleep(5)

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
        bmon.stop()
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
            bmon.stop()
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
