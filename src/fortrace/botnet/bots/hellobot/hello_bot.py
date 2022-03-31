""" This module contains an implementation of a custom bot-variant for testing
    HelloBot itself uses the UDP-protocol to communicate with it's peers.
    The commands itself consist of concated strings.
    All actions are controlled by the BotMonitor itself.
    This module can be seen as a skeleton for udp-style pull-bots.
    This means that each bot will act as a client and requests new orders from a C&C-server.

    In this sample the SocketServer classes are used to simplify implementing the bot-protocol.
    For inter-thread-communication static variables are used for command-storage.

"""
from __future__ import absolute_import
from __future__ import print_function
import six.moves.socketserver
import socket
import threading

from fortrace.botnet.core.botmasterbase import BotMasterBase
from fortrace.botnet.core.cncserverbase import CnCServerBase

from fortrace.botnet.core.botbase import BotBase, PeerList
from fortrace.botnet.common.loggerbase import LoggerStatic
from fortrace.botnet.net.netutility import NetUtility

__author__ = 'Sascha Kopp'

REC_PORT = 10888
HELLO_PORT = 10666


class OrdersContainer(object):
    """ Contains an order.

    :type target: str
    :type target_port: int
    :type message: str
    :param target: Host that receives the order
    :param target_port: Port of host
    :param message: The command message
    """

    def __init__(self, target, target_port, message):
        self.target = target
        self.target_port = target_port
        self.message = message


class ThreadedUDPRequestHandlerBot(six.moves.socketserver.BaseRequestHandler):
    """ The server handler for the HelloBot.

    """

    def handle(self):
        """ The implementation for the handler.
            Called if a new message was received.

        """
        LoggerStatic.if_not_then_initialize("BotRequestHandler(bot-channel)")
        data = self.request[0].strip()
        LoggerStatic.logger.debug("Got: %s", str(data))
        # print "(Bot-channel) Got:" + str(data)
        split_list = data.split()  # split the received message into parts
        if split_list[0] == 'order':  # check if an order was received
            del split_list[0]  # remove the command code HelloBot doesn't use it
            # cmd = split_list[0]
            target = split_list[1]  # save the orders target
            del split_list[0]  # remove the target
            del split_list[0]  # remove the port (not needed)
            msg = ''
            for i in split_list:  # rebuild message to send
                msg += i
                msg += ' '
            msg.strip()
            LoggerStatic.logger.info("new order: <%s> %s", target, msg)
            # print "new order: <" + target + ">" + " " + msg
            HelloBot.orders = OrdersContainer(target, REC_PORT, msg)  # save the order
        else:
            pass


class ThreadedUDPRequestHandlerCnC(six.moves.socketserver.BaseRequestHandler):
    """ The server handler for the HelloCnCServer.

    """

    def handle(self):
        """ The implementation for the handler.
            Called if a new message was received.

        """
        LoggerStatic.if_not_then_initialize("CnCRequestHandler(bot-channel)")
        data = self.request[0].strip()
        LoggerStatic.logger.debug("Got: %s", str(data))
        # print "(Bot-channel) Got:" + str(data)
        sock = self.request[1]
        split_list = data.split()
        if split_list[0] == 'place':  # check if this is a new order
            del split_list[0]  # remove the place keyword
            joined_string = 'order '  # replace it with the order keyword
            for i in split_list:  # append the original order
                joined_string += i
                joined_string += ' '
            joined_string.strip()
            HelloCnC.orders = joined_string
        elif split_list[0] == 'pull':  # check if a bot wants new orders
            answer_tuple = (self.client_address[0], HELLO_PORT)
            if HelloCnC.orders != '':  # if there are orders send it to bot requesting it
                LoggerStatic.logger.info("sending orders to: %s", str(answer_tuple))
                # print "sending orders to: " + str(answer_tuple)
                sock.sendto(HelloCnC.orders, answer_tuple)
            else:
                LoggerStatic.logger.info("no orders to send!")
        else:
            pass


class ThreadedUDPServer(six.moves.socketserver.ThreadingMixIn, six.moves.socketserver.UDPServer):
    """ A non blocking implementation of a socket server.

    """
    pass


class HelloBot(BotBase):
    """ The HelloBot.
        This represents the infected host.

    """
    orders = OrdersContainer('', 0, '')

    def __init__(self):
        BotBase.__init__(self, True)
        self.server_list = PeerList()
        self.sock_server = ThreadedUDPServer(('', HELLO_PORT), ThreadedUDPRequestHandlerBot)
        self.sock_server_thread = None

    def start(self, agent_ip='127.0.0.1', agent_port=10556):
        """ Starts the bot.

        :type agent_port: int
        :type agent_ip: str
        :param agent_ip: the agents ip-address
        :param agent_port: the agents port
        """
        BotBase.start(self, agent_ip, agent_port)  # call the original start method
        # starting here run extended code to cover the sock-server thread for the bot channel
        self.sock_server_thread = threading.Thread(target=self.sock_server.serve_forever)
        self.sock_server_thread.start()

    def stop(self):
        """ Stops the bot.


        """
        BotBase.stop(self)
        self.sock_server.shutdown()
        self.sock_server_thread.join()

    def pull_orders_impl(self, src_host, src_port):
        """ Request new orders.

        :param src_host: C&C-server hosting orders
        :param src_port: servers port
        """
        try:
            if src_host is not None:
                NetUtility.send_message_ipv4_udp(src_host, src_port, 'pull')
            else:
                server, port = self.server_list.get_peer(0)
                NetUtility.send_message_ipv4_udp(server, port, 'pull')
        except KeyError:
            pass
        except socket.error:
            pass

    def execute_orders_impl(self):
        """ Execute the stored orders.


        """
        if HelloBot.orders.target != '':
            o = HelloBot.orders
            NetUtility.send_message_ipv4_udp(o.target, o.target_port, o.message)


class HelloCnC(CnCServerBase):
    """ The HelloBotCnCServer.
        This represents the servers containing orders for the bots to pull.

    """
    orders = ''

    def __init__(self):
        CnCServerBase.__init__(self, True)
        self.sock_server = ThreadedUDPServer(('', HELLO_PORT), ThreadedUDPRequestHandlerCnC)
        self.sock_server_thread = None

    def start(self, agent_ip='127.0.0.1', agent_port=10556):
        """ Starts the CnC-Bot.

        :type agent_port: int
        :type agent_ip: str
        :param agent_ip: the agents ip-address
        :param agent_port: the agents port
        """
        CnCServerBase.start(self, agent_ip, agent_port)
        self.sock_server_thread = threading.Thread(target=self.sock_server.serve_forever)
        self.sock_server_thread.start()

    def stop(self):
        """ Stops the CnC-Bot.


        """
        CnCServerBase.stop(self)
        self.sock_server.shutdown()
        self.sock_server_thread.join()

    def push_orders_impl(self, host, port):
        """ Unused since this is a pull-model bot-implementation.


        :param host: the host which receives the orders
        :param port: the host's port
        """
        pass

    def host_orders_impl(self, orders):
        """ Sets the orders


        :type orders: str
        :param orders: the raw orders
        """
        HelloCnC.orders = orders

    def broadcast_orders_impl(self):
        """ Unused since this is a pull-model bot implementation.


        """
        pass


class HelloBotMaster(BotMasterBase):
    """ The HelloBotMaster.
        This represents the server used by the Bot-Master to place orders to the C&C-servers.

    """

    def __init__(self):
        BotMasterBase.__init__(self, True)

    def place_order_impl(self, unpacked_data):
        """ Stores a command on a server.

        :type unpacked_data: dict
        :param unpacked_data: a dict containing the orders data
        """
        try:
            receiving_host = unpacked_data['cnc_target']
            receiving_port = unpacked_data['cnc_target_port']
            command = unpacked_data['command']
            target = unpacked_data['bot_target']
            msg = unpacked_data['msg']
            cmd_string = 'place ' + command + ' ' + target + ' ' + msg
            NetUtility.send_message_ipv4_udp(receiving_host, receiving_port, cmd_string)
        except socket.error:
            pass

    def get_results_impl(self, receiving_host, receiving_port):
        """ Unused since we don't need results

        :param receiving_host:
        :param receiving_port:
        """
        pass

    def print_commands(self):
        """ Print commands for the botmaster that are supported.

        """
        print("command\ttarget\tadditional\tdescription")
        print("<any>\t<host>\t<message>\tsend message to host")
