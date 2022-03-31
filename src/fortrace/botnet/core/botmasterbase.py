""" This module contains the class and delegate for the bot master template.

"""

from __future__ import absolute_import
import six.moves.cPickle
import socket
from abc import ABCMeta, abstractmethod

from fortrace.botnet.net import netutility
from fortrace.botnet.net.proto import botmastermessage_pb2, messagetypes_pb2

from fortrace.botnet.core.agentconnectorbase import AgentConnectorBase, AgentConnectorBaseDelegate
from fortrace.botnet.net import messagegenerator
from fortrace.core.guest import Guest
import six

__author__ = 'Sascha Kopp'


class BotMasterBase(six.with_metaclass(ABCMeta, AgentConnectorBase)):
    """ This is the template for the bot master.

    :param enabled: Determines if the bot is default enabled
    """

    def __init__(self, enabled=False):
        AgentConnectorBase.__init__(self, enabled)
        self.delegate_class = 'BotMasterBaseDelegate'
        self.id_mapper[messagetypes_pb2.BOTMASTERPLACEORDER] = self.place_order
        self.id_mapper[messagetypes_pb2.BOTMASTERGETRESULT] = self.get_results

    def place_order(self, msg):
        """ Send an order to a server/bot that should be distributed.

        :rtype : None | (bool, str)
        :param msg: The message that was received
        :type msg: fortrace.net.proto.genericmessage_pb2.GenericMessage
        """
        if msg.HasExtension(botmastermessage_pb2.bm_order):
            # receiving_host = msg.Extensions[botmastermessage_pb2.bm_order].receiving_host
            # receiving_port = msg.Extensions[botmastermessage_pb2.bm_order].receiving_port
            # command = msg.Extensions[botmastermessage_pb2.bm_order].command
            # target = msg.Extensions[botmastermessage_pb2.bm_order].target
            # additional = msg.Extensions[botmastermessage_pb2.bm_order].additional
            unpacked_data = six.moves.cPickle.loads(msg.Extensions[botmastermessage_pb2.bm_order].serialized_dict)
            return self.place_order_impl(unpacked_data)
        else:
            return False, "missing field"

    @abstractmethod
    def place_order_impl(self, unpacked_data):
        """ Send an order to a server/bot that should be distributed.
            This is the abstract method that needs to be implemented.

        :rtype : None | (bool, str)
        :type unpacked_data: dict
        :param unpacked_data: dict that contains the order
        :raise NotImplementedError: called if this abstract method is being called
        """
        raise NotImplementedError()

    def get_results(self, msg):
        """ Get the results of an order that is stored on a server.

        :rtype : None | (bool, str)
        :param msg: The message that was received
        :type msg: fortrace.net.proto.genericmessage_pb2.GenericMessage
        """
        if msg.HasExtension(botmastermessage_pb2.bm_result):
            receiving_host = msg.Extensions[botmastermessage_pb2.bm_result].receiving_host
            receiving_port = msg.Extensions[botmastermessage_pb2.bm_result].receiving_port
            return self.get_results_impl(receiving_host, receiving_port)
        else:
            return False, "missing field"

    @abstractmethod
    def get_results_impl(self, receiving_host, receiving_port):
        """ Get the results of an order that is stored on a server.
            This is the abstract method that needs to be implemented.

        :rtype : None | (bool, str)
        :param receiving_host: the server hosting the results
        :param receiving_port: the server port
        :raise NotImplementedError: called if this abstract method is being called
        """
        raise NotImplementedError()

    def print_commands(self):
        """ Print commands for the botmaster that are supported.


        """
        pass


class BotMasterBaseDelegate(six.with_metaclass(ABCMeta, AgentConnectorBaseDelegate)):
    """ The delegate containing methods for sending the specialized commands for the bot master.

    :param agent_socket: the agents socket that was used to connect
    :param addr: the address, port tuple that was used to connect
    """

    def __init__(self, agent_socket, addr):
        AgentConnectorBaseDelegate.__init__(self, agent_socket, addr)

    @staticmethod
    def generate(agent_socket, addr):
        """ Factory method

        :type addr: tuple of (str, int)
        :type agent_socket: socket._socketobject
        :param agent_socket: socket of the associated agent
        :param addr: the ip-address, port tuple
        :return: the new object
        """
        return BotMasterBaseDelegate(agent_socket, addr)

    def place_order(self, order):
        """ Tell the bot master to send an order to the bot/cnc server.

        :type order: dict
        :param order: a dict containing the order with parameters
        """
        # if isinstance(receiving_port, Guest):
        #    receiving_host = str(receiving_host.ip_internet)

        m = messagegenerator.generate_bot_master_place_orders_message(self.message_id, order)
        msg = netutility.NetUtility.length_prefix_message(m.SerializeToString())
        try:
            self.agent_socket.send(msg)
        except socket.error as e:
            self.logger.error("Socket Error: could not send place orders message: %s", e)
            # print "could not send place orders message"
        self.message_id += 1

    def get_results(self, receiving_host, receiving_port):
        """ Tell the bot master to retrieve results from a cnc server.

        :type receiving_port: int
        :type receiving_host: str or fortrace.core.guest.Guest
        :param receiving_host: the server hosting the results
        :param receiving_port: the server port
        """
        if isinstance(receiving_port, Guest):
            receiving_host = str(receiving_host.ip_internet)
        m = messagegenerator.generate_bot_master_get_results_message(self.message_id, receiving_host, receiving_port)
        msg = netutility.NetUtility.length_prefix_message(m.SerializeToString())
        try:
            self.agent_socket.send(msg)
        except socket.error as e:
            self.logger.error("Socket Error: could not send get results message: %s", e)
            # print "could not send get results message"
        self.message_id += 1
