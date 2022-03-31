""" This module contains the NetUtility class used to easy establishing and generating different kinds of network
    connections.

"""
from __future__ import absolute_import
import struct
import socket

__author__ = 'Sascha Kopp'


class NetUtility(object):
    """ Contains static methods used for basic network operations
    """

    def __init__(self):
        pass

    @staticmethod
    def length_prefix_message(message):
        """ Add a length prefix to an existing message.
        :type message: str
        :param message: the message to add the prefix to
        :return: the prefixed message
        """
        packed_len = struct.pack('>L', len(message))
        return packed_len + message

    @staticmethod
    def socket_read_n(sock, n):
        """ Read exactly n bytes from the socket.
            Raise RuntimeError if the connection closed before
            n bytes were read.
        :type n: int
        :type sock: socket._socketobject
        :param sock: the socket to read from
        :param n:  the amount of bytes to read
        :return: the extracted bytes read from the socket
        """
        buf = ''
        while n > 0:
            data = sock.recv(n)
            if data == '':
                raise RuntimeError('unexpected connection close')
            buf += data
            n -= len(data)
        return buf

    @staticmethod
    def receive_prefixed_message(sock):
        """ Read exactly one prefixed message from a socket.
        :type sock: socket._socketobject
        :param sock: the socket to read from
        :return: the message without prefix
        """
        # if sock is socket or socket._socketobject:
        if isinstance(sock, socket.SocketType):
            len_buf = NetUtility.socket_read_n(sock, 4)
            msg_len = struct.unpack('>L', len_buf)[0]
            msg_buf = NetUtility.socket_read_n(sock, msg_len)
            return msg_buf
        else:
            raise TypeError('input does not match to a socket instance')

    @staticmethod
    def create_ipv4_tcp_socket(port, bind_address=''):
        """ Creates a new listening ipv4 tcp socket.

        :param bind_address: the host address to bind to
        :type port: int
        :type bind_address: str
        :rtype : socket._socketobject
        :param port: the port to listen on
        :return: the created socket
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((bind_address, port))
        s.listen(1)
        return s

    @staticmethod
    def create_ipv6_tcp_socket(port, bind_address=''):
        """ Creates a new listening ipv6 tcp socket.

        :param bind_address: the host address to bind to
        :type port: int
        :type bind_address: str
        :rtype : socket._socketobject
        :param port: the port to listen on
        :return: the created socket
        """
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        s.bind((bind_address, port))
        s.listen(1)
        return s

    @staticmethod
    def open_ipv4_tcp_connection(host, port, timeout=None, operation_timeout=None):
        """




        :type port: int
        :type host: str
        :type timeout: float | None
        :type operation_timeout: float | None
        :rtype : socket._socketobject
        :param host: the remote host
        :param port: the port of the remote host
        :param timeout: time to wait for an established connection
        :param operation_timeout: timeout for all other socket operations
        :return: the created socket
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)  # temporally change timeout for connecting
        s.connect((host, port))
        s.settimeout(operation_timeout)  # sets timeout for all other operations
        return s

    @staticmethod
    def open_ipv6_tcp_connection(host, port):
        """




        :type port: int
        :type host: str
        :rtype : socket._socketobject
        :param host: the remote host
        :param port: the port of the remote host
        :return: the created socket
        """
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        s.connect((host, port))
        return s

    @staticmethod
    def create_ipv4_udp_socket(port, bind_address=''):
        """ Creates a new listening ipv4 udp socket.



        :param bind_address: the host address to bind to
        :type bind_address: str
        :type port: int
        :rtype : socket._socketobject
        :param port: the port to listen on
        :return: the created socket
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((bind_address, port))
        return s

    @staticmethod
    def create_ipv6_udp_socket(port, bind_address=''):
        """ Creates a new listening ipv6 udp socket.



        :param bind_address: the host address to bind to
        :type bind_address: str
        :type port: int
        :rtype : socket._socketobject
        :param port: the port to listen on
        :return: the created socket
        """
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        s.bind((bind_address, port))
        return s

    @staticmethod
    def send_message_ipv4_udp(host, port, message):
        """ Sends a message over ipv4 udp protocol.



        :type message: str | bytearray
        :type port: int
        :type host: str
        :param host: the remote host
        :param port: the port of the remote host
        :param message: the message to send
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(message, (host, port))
        s.close()

    @staticmethod
    def send_message_ipv6_udp(host, port, message):
        """ Sends a message over ipv6 udp protocol.

        :type message: str or bytearray
        :type port: int
        :type host: str
        :param host: the remote host
        :param port: the port of the remote host
        :param message: the message to send
        """
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        s.sendto(message, (host, port))
        s.close()
