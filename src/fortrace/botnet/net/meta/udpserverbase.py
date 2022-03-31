from __future__ import absolute_import
from __future__ import print_function
import abc
import select
from socket import socket

from fortrace.botnet.net.netutility import NetUtility

from fortrace.botnet.net.meta.tcpserverbase import TcpServerBase
import six

__author__ = 'Sascha Kopp'

class UdpServerBase(six.with_metaclass(abc.ABCMeta, TcpServerBase)):
    """ This is a very basic UDP server implementation.
        It provides methods to start and stop a thread for accepting incoming connections.
        Note: This is an abstract class and you need to override the server_acceptor_handle method.
    """

    def __init__(self):
        TcpServerBase.__init__(self)

    def server_acceptor_listener(self):
        """ This thread listens for incoming connections and passes them to the server_acceptor_handler method.


        """
        self.server_listener_socket = NetUtility.create_ipv4_udp_socket(self.server_port, self.server_bind_address)
        while self.server_working:
            try:
                readable, writable, exceptional = select.select([self.server_listener_socket], [], [])
                for c in readable:
                    s, ad = c.accept()
                    self.server_acceptor_handler(s, ad)
            except socket.error as e:
                print("Socket Error: ", e.message)
            except RuntimeError as e:
                print("Runtime Error: ", e.message)
            # except:
            #    pass

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
