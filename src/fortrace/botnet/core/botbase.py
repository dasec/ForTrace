""" This module contains the class and delegate for the bot template.

"""

from __future__ import absolute_import
import socket
from abc import ABCMeta, abstractmethod

from fortrace.botnet.net import messagegenerator
from fortrace.botnet.net import netutility
from fortrace.botnet.net.proto import messagetypes_pb2

from fortrace.botnet.core.agentconnectorbase import AgentConnectorBase
from fortrace.botnet.core.agentconnectorbase import AgentConnectorBaseDelegate
from fortrace.botnet.net.proto import botmessage_pb2
from fortrace.core.guest import Guest
import six

__author__ = 'Sascha Kopp'


class PeerList(object):
    """ A container to manage peer or server connections

    """

    def __init__(self):
        self.items = list()

    def register_peer(self, host, port):
        """ Registers a new peer.

        :type port: int
        :type host: str
        :rtype : int
        :param host: the host to add
        :param port: the host's port to add
        """
        self.items.append((host, port))
        return self.length

    def get_peer(self, no):
        """ Gets a peer by number.


        :rtype : tuple of (str, int)
        :type no: int
        :param no: the entries id
        """
        return self.items[no]

    @property
    def length(self):
        """ the number of entries



        :rtype : int
        :return: the number of entries
        """
        return len(self.items)


class BotBase(six.with_metaclass(ABCMeta, AgentConnectorBase)):
    """ This is the template for the bot.

    :param enabled: Determines if the bot is default enabled
    """

    def __init__(self, enabled=False):
        AgentConnectorBase.__init__(self, enabled)
        self.delegate_class = 'BotBaseDelegate'
        self.id_mapper[messagetypes_pb2.BOTPULL] = self.pull_orders
        self.id_mapper[messagetypes_pb2.BOTEXECUTE] = self.execute_orders

    #    def bootstrap_peers(self, msg):
    #        pass

    def pull_orders(self, msg):
        """ Tries to get new orders from bots/cnc serves (de-marshalling function)

        :rtype : None | (bool, str)
        :type msg: fortrace.net.proto.genericmessage_pb2.GenericMessage
        :param msg: The message that was received
        """
        if msg.HasExtension(botmessage_pb2.bot_pull):
            if msg.Extensions[botmessage_pb2.bot_pull].HasField("src_port"):
                host = msg.Extensions[botmessage_pb2.bot_pull].src_host
                port = msg.Extensions[botmessage_pb2.bot_pull].src_port
                return self.pull_orders_impl(host, port)
            else:
                return self.pull_orders_impl(None, None)

    @abstractmethod
    def pull_orders_impl(self, src_host, src_port):
        """ Tries to get new orders from bots/cnc serves (implementation function)

        :rtype : None | (bool, str)
        :param src_host: the bot/cnc server containing the orders
        :param src_port: the host's port
        :raise NotImplementedError: called if this abstract method is being called
        """
        raise NotImplementedError()

    def execute_orders(self, msg):
        """ Execute received orders (de-marshalling function)

        :rtype : None | (bool, str)
        :type msg: fortrace.net.proto.genericmessage_pb2.GenericMessage
        :param msg: The message that was received
        """
        return self.execute_orders_impl()

    @abstractmethod
    def execute_orders_impl(self):
        """ Execute received orders (implementation function)

        :rtype : None | (bool, str)
        :raise NotImplementedError:  called if this abstract method is being called
        """
        raise NotImplementedError()


class BotBaseDelegate(AgentConnectorBaseDelegate):
    """ The delegate containing methods for sending the specialized commands for the bot.

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
        return BotBaseDelegate(agent_socket, addr)

    def pull_orders(self, src_host=None, src_port=None):
        """ Tell the bot to pull orders from a cnc server.

        :type src_port: int
        :type src_host: str or fortrace.core.guest.Guest
        :param src_host: optional, the address of the cnc host
        :param src_port: optional, the port of the cnc host
        """
        if isinstance(src_host, Guest):
            src_host = str(src_host.ip_internet)
        m = messagegenerator.generate_bot_pull_orders_message(self.message_id, src_host, src_port)
        msg = netutility.NetUtility.length_prefix_message(m.SerializeToString())
        try:
            self.agent_socket.send(msg)
        except socket.error as e:
            self.logger.error("Socket Error: could not send pull orders message: %s", e)
            # print "could not send pull orders message"
        self.message_id += 1

    def execute_orders(self):
        """ Tell the bot to execute it's orders.


        """
        m = messagegenerator.generate_bot_execute_orders_message(self.message_id)
        msg = netutility.NetUtility.length_prefix_message(m.SerializeToString())
        try:
            self.agent_socket.send(msg)
        except socket.error as e:
            self.logger.error("Socket Error: could not send execute orders message: %s", e)
            # print "could not send execute orders message"
        self.message_id += 1
