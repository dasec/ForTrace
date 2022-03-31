""" This module contains a basic implementation for a tcp client.

"""
from __future__ import absolute_import
import socket

from fortrace.botnet.common.loggerbase import LoggerBase
from fortrace.botnet.net.netutility import NetUtility

__author__ = 'Sascha Kopp'


class TcpClientBase(object):
    """ This class provides basic methods for connecting to a single tcp endpoint and closing that connection as well.
    """
    def __init__(self):
        self.client_logger = LoggerBase("TcpClientBase")
        self.client_socket = socket.socket()
        self.client_socket_is_open = False

    def client_open_connection(self, host, port, timeout=None, operation_timeout=None):
        """ Opens a socket to a TCP-server.
            Will block till connection is established.


        :type port: int
        :type host: str
        :type timeout: float | None
        :type operation_timeout: float | None
        :param host: the host to connect to
        :param port: the port to connect to
        :param timeout: time to wait for till connection is established
        :param operation_timeout: time to wait for all other socket operations
        :raise RuntimeError: is raised if you attempt to open a new connection without closing an old one
        :raise socket.timeout: is raised if an connection could not be established in time
        """
        if self.client_socket_is_open is False:
            while True:
                try:
                    self.client_socket = NetUtility.open_ipv4_tcp_connection(host, port, timeout, operation_timeout)
                    break
                except socket.timeout:  # handle timeouts separate
                    raise socket.timeout("Failed to establish connection in specified time!")
                except socket.error:
                    pass
            self.client_socket_is_open = True
        else:
            raise RuntimeError("socket needs to be closed first")

    def client_close_connection(self):
        """ Call this method to close an existing one.
            Always call it before trying to establish a new connection, even if an connection attempt failed.

        """
        if self.client_socket_is_open is True:
            try:
                self.client_socket.shutdown(socket.SHUT_RDWR)
                self.client_socket.close()
            except socket.error as e:
                self.client_logger.logger.debug("Error closing client connection: %s", e)
                # print "Error closing client connection: ", e.message
            self.client_socket_is_open = False
