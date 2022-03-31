""" This is a very basic skeleton for implementing botnet components.
    Some imports that you may find useful have been added.
    You can find additional sample code in the other bot-implementation's modules.

"""

from __future__ import absolute_import
import six.moves.socketserver  # if you want to create a udp or tcp server
import socket  # socket operations and exceptions
import threading  # for running stuff on other threads

from fortrace.botnet.core.botmasterbase import BotMasterBase  # the template component for the botmaster
from fortrace.botnet.core.cncserverbase import CnCServerBase  # the template component for the cnc-server
from fortrace.botnet.core.botbase import BotBase  # the template component for the bot

from fortrace.botnet.common.loggerbase import LoggerStatic  # if you need the static logger (ex. sockserver-handlers)
from fortrace.botnet.net.netutility import NetUtility  # for fast creation of sockets


class SkeletonBotMaster(BotMasterBase):
    def __init__(self, enabled=True):
        BotMasterBase.__init__(self, enabled)

    def place_order_impl(self, unpacked_data):
        pass

    def get_results_impl(self, receiving_host, receiving_port):
        pass

    def start(self, agent_ip='127.0.0.1', agent_port=10556):
        BotMasterBase.start(self, agent_ip, agent_port)
        # evaluate globals here
        # run other sockserver or threads for listening on incoming connections

    def stop(self):
        BotMasterBase.stop(self)
        # stop other sockservers or threads
        # join them


class SkeletonCnC(CnCServerBase):
    def __init__(self, enabled=True):
        CnCServerBase.__init__(self, enabled)

    def push_orders_impl(self, host, port):
        pass

    def host_orders_impl(self, orders):
        pass

    def broadcast_orders_impl(self):
        pass

    def start(self, agent_ip='127.0.0.1', agent_port=10556):
        CnCServerBase.start(self, agent_ip, agent_port)
        # evaluate globals here
        # run other sockserver or threads for listening on incoming connections

    def stop(self):
        CnCServerBase.stop(self)
        # stop other sockservers or threads
        # join them


class SkeletonBot(BotBase):
    def __init__(self, enabled=True):
        BotBase.__init__(self, enabled)

    def pull_orders_impl(self, src_host, src_port):
        pass

    def execute_orders_impl(self):
        pass

    def start(self, agent_ip='127.0.0.1', agent_port=10556):
        BotBase.start(self, agent_ip, agent_port)
        # evaluate globals here
        # run other sockserver or threads for listening on incoming connections

    def stop(self):
        BotBase.stop(self)
        # stop other sockservers or threads
        # join them
