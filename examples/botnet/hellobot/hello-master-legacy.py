#!/usr/bin/env python
""" This is the global control script for the HelloBot implementation.
    It uses the legacy system for controlling a set of bot instances.
    It won't create the vm instances.
    See the hello-master.py file for that.
    This file is included for those who have a set fo heterogeneous vms that don't follow a specific template
    and instantiate the vms themselves.
    This may only be used with a static ip-address-setup.
"""

from __future__ import absolute_import
from __future__ import print_function
from time import sleep

from fortrace.botnet.core.botmonitorbase import BotMonitorBase

from fortrace.botnet.bots.hellobot.hello_bot import HELLO_PORT
from fortrace.botnet.core.simulationmanager import SimulationManager
from six.moves import range
from six.moves import input

__author__ = 'Sascha Kopp'

# setup simulation
bm = BotMonitorBase()
bm.payload_registry.register_payload("hello-bot.py", "group-1")
bm.payload_registry.register_payload("hello-cnc.py", "group-2")
bm.payload_registry.register_payload("hello-bm.py", "group-3")
bm.bot_registry.reserve_for_bot("192.168.100.2", 2)
bm.bot_registry.reserve_for_bot("192.168.100.3", 3)
bm.bot_registry.reserve_for_range("192.168.100.4", "192.168.100.6", 1)
bm.start(10555)
# wait till simulation is setup
sm = SimulationManager(bm)
sm.wait_for_bots(5)
# actions
for i in range(0, 10):
    print("round " + str(i))
    bl = bm.bot_registry.get_bot_list(3)
    for b in bl:
        print(b.ip_address + " is placing an order")
        msg = "hello: " + str(i)
        order = {
            'cnc_target': "192.168.110.2",
            'cnc_target_port:': HELLO_PORT,
            'command': 'send',
            'bot_target': "192.168.110.1",
            'msg': msg
        }
        bm.bot_registry.promote_bot(b.ip_address).place_order(order)
    sleep(5)
    bl = bm.bot_registry.get_bot_list(1)
    for b in bl:
        print(b.ip_address + " is pulling orders")
        bm.bot_registry.promote_bot(b.ip_address).pull_orders("192.168.110.2", HELLO_PORT)
    sleep(5)
    for b in bl:
        print(b.ip_address + " is executing orders")
        bm.bot_registry.promote_bot(b.ip_address).execute_orders()
    sleep(5)
bm.stop()
print("test script ended!")
input("press enter to exit!")
