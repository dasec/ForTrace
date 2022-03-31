#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This module contains the PlaintextZeus global control script.
    Setup the groups and their associated control-scripts and run a small simulation.

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
    from fortrace.botnet.core.botmonitorbase import BotMonitorBase
    from fortrace.botnet.core.simulationmanager import SimulationManager
    from fortrace.botnet.bots.zeus.zeus_generators import ZeusPacketGenerator
    from fortrace.botnet.bots.zeus.zeus import ZeusCnC

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
        bmon = BotMonitorBase()
        sm = SimulationManager(bmon)

        # setup groups
        bmon.group_manager.setup_group('zeus_bot', 'zeus-bot.py')
        bmon.group_manager.setup_group('zeus_cnc', 'zeus-cnc.py')

        # instanciate each vm
        cnc = virtual_machine_monitor1.create_guest(guest_name="windows-guest01", platform="windows")
        bot1 = virtual_machine_monitor1.create_guest(guest_name="windows-guest02", platform="windows")
        bot2 = virtual_machine_monitor1.create_guest(guest_name="windows-guest03", platform="windows")
        bot3 = virtual_machine_monitor1.create_guest(guest_name="windows-guest04", platform="windows")

        # wait for dhcp
        cnc.wait_for_dhcp()
        bot1.wait_for_dhcp()
        bot2.wait_for_dhcp()
        bot3.wait_for_dhcp()

        # if you want to enable the rc4 cypher, disable for plaintext messages (intended for debugging)
        enable_crypto = True
        encryption_key = "secret key"

        # setup the cnc ip for clients and a botnet name, simulate the bot's embedded config
        bmon.globals["cnc_host"] = str(cnc.ip_internet)  # always needed
        bmon.globals["botnet_name"] = "samplebotnet"  # if not set, 'default' will be used
        # bmon.globals["url_config"] = "/config.bin"
        # bmon.globals["url_compip"] = "/ip.php"
        # bmon.globals["url_server"] = "/gate.php"
        # bmon.globals["url_loader"] = "/bot.exe"
        if enable_crypto:
            bmon.globals["encryption_key"] = encryption_key
        else:
            encryption_key = None

        # allocate vms to groups
        bmon.group_manager.add_bot_to_group('zeus_cnc', cnc)
        bmon.group_manager.add_bot_to_group('zeus_bot', bot1)
        bmon.group_manager.add_bot_to_group('zeus_bot', bot2)
        bmon.group_manager.add_bot_to_group('zeus_bot', bot3)

        # begin listening for incoming connections
        bmon.start()

        # upload zeus server files after verifying that cnc is running

        sm.wait_for_bot(cnc)  # wait till bot is ready
        cnc_bot = bmon.group_manager.get_single_bot(cnc)

        # load plaintext config.bin and send it to cnc bot
        with open('config.bin', 'rb') as f:
            c = f.read()
            ZeusCnC.push_file_to_server(cnc_bot, 'config.bin', c, encryption_key)

        # generate a command to send to all clients
        z = ZeusPacketGenerator()
        z.add_command_info("sethomepage http://example.com")
        cmd = str(z.generate_message(encryption_key))  # if encryption is enabled, cmd will already be encrypted
        ZeusCnC.push_file_to_server(cnc_bot, 'gate.php', cmd)  # no need for an additional cypher round

        # wait till the simulation is ready
        sm.wait_for_bots(4)

        # let the bots create control traffic till key press
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
