""" This module conatins the base implementation of the bot-agent.

"""
from __future__ import absolute_import
import socket
import threading
from time import sleep

from google.protobuf import message
from fortrace.botnet.net import messagegenerator
from fortrace.botnet.net.netutility import NetUtility
from fortrace.botnet.net.proto import announcemessage_pb2
from fortrace.botnet.net.proto import messagetypes_pb2
from fortrace.botnet.net.proto import payloadmessage_pb2
from fortrace.botnet.net.proto.genericmessage_pb2 import GenericMessage

from fortrace.botnet.common.loggerbase import LoggerBase
from fortrace.botnet.common.runtimequery import RuntimeQuery
from fortrace.botnet.common.threadmanager import ThreadManager
from fortrace.botnet.net.meta.tcpclientbase import TcpClientBase
from fortrace.botnet.net.meta.tcpserverbase import TcpServerBase
from fortrace.utility import payloadutils

__author__ = 'Sascha Kopp'


class BotAgentBase(TcpServerBase, TcpClientBase, LoggerBase, RuntimeQuery, ThreadManager):
    """ The basic implementation for the bot-agent implementation.

    """

    def __init__(self):
        RuntimeQuery.__init__(self)
        ThreadManager.__init__(self)
        LoggerBase.__init__(self, 'BotAgent')
        TcpServerBase.__init__(self)
        TcpClientBase.__init__(self)
        self.payload_name = 'group'
        self.client_thread = None
        self.socket_pool = list()
        self.bot_handle = None

    def server_acceptor_handler(self, sock, address):
        """ Same functionality as the super-class-method plus thread-management.

        :type address: tuple of (str, int)
        :type sock: socket._socketobject
        :param sock:  the socket of the new connection
        :param address: the address, port tuple of the connection
        """
        self.logger.info("accepted connection from: %s", address)
        # print 'accepted connection from: ', address
        self.socket_pool.append(sock)
        self.create_thread(self.agent_server_processor_thread, (sock,))
        # check if any thread has ceased to exist
        self.cleanup_threads()

    def agent_server_processor_thread(self, sock):
        """ This is the bot side message listener thread.

        :type sock: socket._socketobject
        :param sock: the socket to work with
        """
        is_graceful = False
        while self.active:
            # msg = ''
            try:
                # receive a message
                msg = NetUtility.receive_prefixed_message(sock)
                m = GenericMessage()
                m.ParseFromString(msg)
                self.logger.debug("(bot-side): got message> %s", str(m))
                # print "agent (bot-side): got message>\n", str(m)
                # check if bot wants to go down
                if m.message_type == messagetypes_pb2.ANNOUNCE:
                    if m.HasExtension(announcemessage_pb2.status_info):
                        if m.Extensions[announcemessage_pb2.status_info].state == announcemessage_pb2.GRACEFUL_SHUTDOWN:
                            is_graceful = True
                            self.logger.info("expecting graceful shutdown")
                            # print "expecting a graceful shutdown"
                # pass message to monitor
                self.client_socket.send(NetUtility.length_prefix_message(msg))
            except socket.error as e:
                # except this to happen if socket was close immaturely
                self.logger.warning("Socket Error: %s", e)
                # print "Socket Error: ", str(e)
                # check if we got a shutdown announcement
                if not is_graceful:
                    try:
                        # the bot crashed most likely, tell the monitor
                        self.logger.error("Instance has crashed!")
                        cm = messagegenerator.generate_announce_message(0, announcemessage_pb2.CRASHED,
                                                                        'AgentConnectorBaseDelegate')
                        self.client_socket.send(NetUtility.length_prefix_message(cm.SerializeToString()))
                    except socket.error:
                        pass
                    break
                # close the socket anyway since it is faulty
                self.logger.warning("Closing socket!")
                sock.close()
                self.socket_pool.remove(sock)
                break
            except RuntimeError as e:
                # except this to happen if the bot wants to close the socket
                if e.message == 'unexpected connection close':
                    try:
                        sock.shutdown(socket.SHUT_RDWR)
                    except socket.error:
                        pass
                    finally:
                        sock.close()
                        self.logger.info("socket has been closed by demand")
                        # print 'socket has been closed by demand'
                        self.socket_pool.remove(sock)
                        # check if we got a shutdown announcement
                        if not is_graceful:
                            try:
                                # the bot crash most likely, tell the monitor
                                self.logger.error("Instance has crashed!")
                                cm = messagegenerator.generate_announce_message(0, announcemessage_pb2.CRASHED,
                                                                                'AgentConnectorBaseDelegate')
                                self.client_socket.send(NetUtility.length_prefix_message(cm.SerializeToString()))
                            except socket.error:
                                pass
                        break
                else:
                    self.logger.error("RuntimeError: %s", e)
                    sock.close()
                    self.socket_pool.remove(sock)
                    break
            except message.Error as e:
                self.logger.error("ProtoBuf Error: %s", e)
                # print "ProtoBuf Error: ", e.message

    def agent_client_command_processor_thread(self):
        """ This is the monitor side message listener thread


        """
        while self.active is True:
            try:
                # receive a command
                msg = NetUtility.receive_prefixed_message(self.client_socket)
                m = GenericMessage()
                m.ParseFromString(msg)
                self.logger.debug("(monitor-side): got message> %s", str(m))
                # print "agent (monitor-side): got message>\n", str(m)
                # pass it on to the bot
                if m.message_type == messagetypes_pb2.PAYLOAD:
                    self.logger.info("received new payload")
                    # print "received a new payload"
                    if m.HasExtension(payloadmessage_pb2.payload_info):
                        if m.Extensions[payloadmessage_pb2.payload_info].source_type == payloadmessage_pb2.EMBEDDED:
                            if m.Extensions[payloadmessage_pb2.payload_info].size == 0:
                                self.logger.warning("got the dummy payload, trying again...")
                                # print "got the dummy payload, trying again..."
                                sleep(1)
                                m = messagegenerator.generate_payload_request(0, self.payload_name)
                                self.client_socket.send(NetUtility.length_prefix_message(m.SerializeToString()))
                            else:
                                if self.bot_handle is not None:  # the current payload should be replaced
                                    self.logger.info("old payload will be replaced")
                                    # print "old payload will be replaced"
                                    self.bot_handle.terminate()
                                    self.bot_handle = None
                                raw_payload = m.Extensions[payloadmessage_pb2.payload_info].content
                                try:
                                    f = open('tmp.zip', 'wb')
                                    f.write(raw_payload)
                                    f.flush()
                                    f.close()
                                    payloadutils.load_and_unpack('tmp.zip')
                                    meta = payloadutils.parse_meta_data()
                                    self.bot_handle = payloadutils.execute_with_metadata(meta)
                                    self.logger.info("started a new payload")
                                    # print "started a new payload"
                                except IOError as e:
                                    self.logger.error("IOError: %s", e)
                                    # print e.message
                                except OSError as e:
                                    self.logger.error("OSError: %s", e)
                        else:
                            pass
                else:
                    msg = NetUtility.length_prefix_message(m.SerializeToString())
                    self.socket_pool[0].send(msg)  # note the first object should always be the bots socket
            except IndexError:
                # expect this to happen if no bot is running
                self.logger.error("IndexError: probably no bot-instance is running")
                # print "IndexError: probably no bot-instance is running"
            except socket.error as e:
                # except this to happen if socket was close immaturely
                self.logger.error("Socket Error: %s", e)
                # print "Socket Error: ", str(e)
                self.client_socket.close()
                break
            except RuntimeError as e:
                # except this to happen if the bot wants to close the socket
                if e.message == 'unexpected connection close':
                    try:
                        self.client_socket.shutdown(socket.SHUT_RDWR)
                    except socket.error:
                        pass
                    finally:
                        self.client_socket.close()
                        self.logger.info("socket has been closed by demand")
                        # print 'socket has been closed by demand'
                        break
                else:
                    self.logger.error("RuntimeError: %s", e)
                    self.client_socket.close()
                    break
            except message.Error as e:
                self.logger.error("ProtoBuf Error: %s", e)
                # print "ProtoBuf Error: ", e.message
        if self.bot_handle is not None:
            self.bot_handle.terminate()
            self.bot_handle = None

    def agent_start(self, monitor_ip='192.168.100.1', monitor_port=10555, bind_ip='127.0.0.1', bind_port=10556,
                    request_payload_on_start=True,
                    payload_name='group'):
        """ Starts the agent.

        :type payload_name: str
        :type request_payload_on_start: bool
        :type bind_port: int
        :type bind_ip: str
        :type monitor_port: int
        :type monitor_ip: str
        :param request_payload_on_start: whether we want to bootstrap a payload on start
        :param payload_name: the name of the payload we want to bootstrap
        :param monitor_ip: ip/host where the monitor is running
        :param monitor_port: the port of the monitor
        :param bind_ip: the address we want the agent to bind to
        :param bind_port: the port we want the agent to bind to
        """
        self.active = True
        self.stopped = False
        self.payload_name = payload_name
        self.logger.info("waiting for connection to monitor...")
        # print "waiting for connection to monitor..."
        self.client_open_connection(monitor_ip, monitor_port)
        self.client_thread = threading.Thread(None, self.agent_client_command_processor_thread)
        self.client_thread.start()
        self.logger.info("established connection to monitor")
        # print "established connection to monitor"
        self.server_start_listener(bind_port, bind_ip)
        self.logger.info("started agent listener")
        # print "started agent listener"
        if request_payload_on_start:
            self.logger.info("beginning bootstrapping process...")
            # print "beginning bootstrapping process..."
            m = messagegenerator.generate_payload_request(0, payload_name)
            self.client_socket.send(NetUtility.length_prefix_message(m.SerializeToString()))

    def agent_stop(self):
        """ Stops the agent.


        """
        self.logger.info("shutting down agent")
        # print "shutting down agent"
        self.active = False
        self.client_close_connection()
        self.client_thread.join()
        self.server_stop_listener()
        for s in self.socket_pool:
            try:
                s.shutdown(socket.SHUT_RDWR)
                s.close()
            except socket.error:
                pass
        self.join_all_threads()
        self.stopped = True
        self.logger.info("agent shutdown complete")
        # print "agent shutdown complete"
