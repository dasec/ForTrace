""" This module contains a basic implementation for a tcp server.

"""
from __future__ import absolute_import
import abc
import select
import socket
import threading

from fortrace.botnet.common.loggerbase import LoggerBase
from fortrace.botnet.net.netutility import NetUtility
import six

__author__ = 'Sascha Kopp'


class TcpServerBase(six.with_metaclass(abc.ABCMeta, object)):
    """ This is a very basic TCP server implementation.
        It provides methods to start and stop a thread for accepting incoming connections.
        Note: This is an abstract class and you need to override the server_acceptor_handle method.
    """

    def __init__(self):
        self.server_logger = LoggerBase("TcpServerBase")
        self.server_port = 0
        self.server_bind_address = ''
        self.server_listener_socket = None
        self.server_working = True
        self.server_acceptor_thread = None

    def server_start_listener(self, port, bind_address=''):
        """ Starts the listening thread.

        :type bind_address: str
        :type port: int
        :param port: the port to listen on
        :param bind_address: the address to listen on (defaults to any)
        """
        self.server_logger.logger.debug("starting the global listener...")
        self.server_working = True
        self.server_bind_address = bind_address
        self.server_port = port
        self.server_acceptor_thread = threading.Thread(None, self.server_acceptor_listener)
        self.server_acceptor_thread.start()
        self.server_logger.logger.debug("global listener has been started!")

    def server_stop_listener(self):
        """ Stops the listening thread.
            Note: All accepted connections still need to be closed by hand.

        """
        self.server_logger.logger.debug("stopping the global listener...")
        self.server_working = False
        try:
            self.server_listener_socket.shutdown(socket.SHUT_RDWR)
            self.server_listener_socket.close()
        except socket.error:
            pass
        self.server_acceptor_thread.join()
        self.server_logger.logger.debug("global listener has been stopped!")

    def server_acceptor_listener(self):
        """ This thread listens for incoming connections and passes them to the server_acceptor_handler method.


        """
        self.server_listener_socket = NetUtility.create_ipv4_tcp_socket(self.server_port, self.server_bind_address)
        while self.server_working:
            try:
                readable, writable, exceptional = select.select([self.server_listener_socket], [], [], 1)
                for c in readable:
                    s, ad = c.accept()
                    self.server_acceptor_handler(s, ad)
            # except select.error as e:
            #     self.server_logger.logger.debug("Select Error: %s", e)
            #     break
            except socket.error as e:
                self.server_logger.logger.debug("Socket Error on select: %s", e)
                # print "Socket Error: ", e.message
                break
            except RuntimeError as e:
                self.server_logger.logger.debug("Runtime Error on select: %s", e)
                # print "Runtime Error: ", e.message
                break
        self.server_logger.logger.debug("Left the acceptor-listener-loop!")

    @abc.abstractmethod
    def server_acceptor_handler(self, sock, address):
        """ This method is intended to be overridden by an inherited class.
            The handler itself receives the connection details of an newly established connection and it's up to the
            programmer to do something useful with the data like spawning a new thread that handles that connection.

        :type address: tuple of (str, int)
        :type sock: socket._socketobject
        :param sock: the socket object of the newly established connection
        :param address: the address-port-tuple of the client
        :raise NotImplementedError: this method is purely abstract and not implemented
        """
        raise NotImplementedError()
