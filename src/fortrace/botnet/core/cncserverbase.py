""" This module contains the class and delegate for the cnc server template.

"""

from __future__ import absolute_import
import socket
from abc import ABCMeta, abstractmethod

from fortrace.botnet.net import messagegenerator
from fortrace.botnet.net import netutility
from fortrace.botnet.net.proto import messagetypes_pb2

from fortrace.botnet.core.agentconnectorbase import AgentConnectorBase, AgentConnectorBaseDelegate
from fortrace.botnet.net.proto import cncmessage_pb2
from fortrace.core.guest import Guest
import six

__author__ = 'Sascha Kopp'


class CnCServerBase(six.with_metaclass(ABCMeta, AgentConnectorBase)):
    """ This is the template for the cnc server.

    :param enabled: Determines if the bot is default enabled
    """

    def __init__(self, enabled=False):
        """ This is the template for the cnc server.

        :param enabled: Determines if the bot is default enabled
        """
        AgentConnectorBase.__init__(self, enabled)
        self.delegate_class = 'CnCServerBaseDelegate'
        self.id_mapper[messagetypes_pb2.CNCBROADCASTORDERS] = self.broadcast_orders
        self.id_mapper[messagetypes_pb2.CNCHOSTORDERS] = self.host_orders
        self.id_mapper[messagetypes_pb2.CNCPUSHORDERS] = self.push_orders

    def push_orders(self, msg):
        """ Pushes orders to a bot (de-marshalling function)

        :rtype : None | (bool, str)
        :param msg: The message that was received
        :type msg: fortrace.net.proto.genericmessage_pb2.GenericMessage
        """
        if msg.HasExtension(cncmessage_pb2.cnc_push):
            host = msg.Extensions[cncmessage_pb2.cnc_push].host
            port = msg.Extensions[cncmessage_pb2.cnc_push].port
            return self.push_orders_impl(host, port)
        else:
            return False, "missing field"

    @abstractmethod
    def push_orders_impl(self, host, port):
        """ Pushes orders to a bot (implementation function)

        :rtype : None | (bool, str)
        :type port: int
        :type host: str
        :param host: the host to receive orders
        :param port: the host's port
        :raise NotImplementedError: called if this abstract method is being called
        """
        raise NotImplementedError()

    def broadcast_orders(self, msg):
        """ Pushes orders to a bots (de-marshalling function)

        :rtype : None | (bool, str)
        :param msg: The message that was received
        :type msg: fortrace.net.proto.genericmessage_pb2.GenericMessage
        """
        return self.broadcast_orders_impl()

    @abstractmethod
    def broadcast_orders_impl(self):
        """ Pushes orders to a bots (implementation function)

        :rtype : None | (bool, str)
        :raise NotImplementedError: called if this abstract method is being called
        """
        raise NotImplementedError()

    def host_orders(self, msg):
        """ Places orders on the cnc server (de-marshalling function)
            Used for testing or if the bot master should be ignored.

        :rtype : None | (bool, str)
        :param msg: The message that was received
        :type msg: fortrace.net.proto.genericmessage_pb2.GenericMessage
        """
        if msg.HasExtension(cncmessage_pb2.cnc_host):
            orders = msg.Extensions[cncmessage_pb2.cnc_host].orders
            return self.host_orders_impl(orders)
        else:
            return False, "missing field"

    @abstractmethod
    def host_orders_impl(self, orders):
        """ Places orders on the cnc server (implementation function)
            Used for testing or if the bot master should be ignored.

        :rtype : None | (bool, str)
        :type orders: str
        :param orders: serialized orders (form defined by implementer)
        :raise NotImplementedError: called if this abstract method is being called
        """
        raise NotImplementedError()


class CnCServerBaseDelegate(six.with_metaclass(ABCMeta, AgentConnectorBaseDelegate)):
    """ The delegate containing methods for sending the specialized commands for the cnc server.

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
        return CnCServerBaseDelegate(agent_socket, addr)

    def push_orders(self, host, port):
        """ Send stored orders to peer.

        :type port: int
        :type host: str or fortrace.core.guest.Guest
        :param host: the host to receive orders
        :param port: the host's port
        """
        if isinstance(host, Guest):
            host = str(host.ip_internet)
        m = messagegenerator.generate_cnc_push_orders_message(self.message_id, host, port)
        msg = netutility.NetUtility.length_prefix_message(m.SerializeToString())
        try:
            self.agent_socket.send(msg)
        except socket.error as e:
            self.logger.error("Socket Error: could not send push orders message: %s", e)
            # print "could not send push orders message"
        self.message_id += 1

    def broadcast_orders(self):
        """ Send orders to all peers.


        """
        m = messagegenerator.generate_cnc_broadcast_orders(self.message_id)
        msg = netutility.NetUtility.length_prefix_message(m.SerializeToString())
        try:
            self.agent_socket.send(msg)
        except socket.error as e:
            self.logger.error("Socket Error: could not send broadcast orders message %s", e)
            # print "could not send broadcast orders message"
        self.message_id += 1

    def host_orders(self, orders):
        """ Host orders.
            Used for internal testing or if no bot master should be used.

        :type orders: str
        :param orders: serialized orders (form defined by implementer)
        """
        m = messagegenerator.generate_cnc_host_orders_message(self.message_id, orders)
        msg = netutility.NetUtility.length_prefix_message(m.SerializeToString())
        try:
            self.agent_socket.send(msg)
        except socket.error as e:
            self.logger.error("Socket Error: could not send host orders message: %s", e)
            # print "could not send host orders message"
        self.message_id += 1
