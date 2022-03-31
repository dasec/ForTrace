""" This module contains the base implementation of the bot-monitor and it's associated containers.

"""
from __future__ import absolute_import
import socket

from google.protobuf import message
from fortrace.botnet.core import agentconnectorbase
from fortrace.botnet.net import messagegenerator
from fortrace.botnet.net.netutility import NetUtility
from fortrace.botnet.net.proto import announcemessage_pb2
from fortrace.botnet.net.proto import answermessage_pb2
from fortrace.botnet.net.proto import genericmessage_pb2
from fortrace.botnet.net.proto import messagetypes_pb2
from fortrace.botnet.net.proto import payloadmessage_pb2

from fortrace.botnet.core.bmoncomponents.botregistry import BotRegistry
from fortrace.botnet.core.bmoncomponents.groupmanager import GroupManager
from fortrace.botnet.core.bmoncomponents.payloadregistry import Payload, PayloadRegistry
from fortrace.botnet.common.loggerbase import LoggerBase
from fortrace.botnet.common.runtimequery import RuntimeQuery
from fortrace.botnet.common.threadmanager import ThreadManager
from fortrace.botnet.net.meta.tcpserverbase import TcpServerBase
import six

__author__ = 'Sascha Kopp'


class BotMonitorBase(TcpServerBase, LoggerBase, RuntimeQuery, ThreadManager):
    """ The basic version of the bot-monitor implementation.

    """

    def __init__(self):
        RuntimeQuery.__init__(self)
        ThreadManager.__init__(self)
        LoggerBase.__init__(self, "BotMonitor")
        TcpServerBase.__init__(self)
        self.globals = dict()  # will be requested by bots, set values to it before setting up bots
        self.globals['globals_available'] = True  # this value shows if the globals were received
        self.bot_registry = BotRegistry()
        self.payload_registry = PayloadRegistry()
        self.group_manager = GroupManager(self.bot_registry, self.payload_registry)

    def processor_thread(self, delegate):
        """ This thread will listen to incoming announcements from the delegates associated agent.


        :type delegate: fortrace.core.agentconnectorbase.AgentConnectorBaseDelegate
        :param delegate: the delegate to work with
        :raise RuntimeError:
        """
        while self.active:
            try:
                # receive a message
                msg = NetUtility.receive_prefixed_message(delegate.agent_socket)
                m = genericmessage_pb2.GenericMessage()
                m.ParseFromString(msg)
                self.logger.debug("[%s] got message> %s", delegate.ip_address, str(m))
                # print "[", delegate.ip_address, "] got message>\n", str(m)
                # check what type of message was received
                # todo implement a function mapper
                # check if it's a announcement and set the delegates state
                if m.message_type == messagetypes_pb2.ANNOUNCE:
                    if m.HasExtension(announcemessage_pb2.status_info):
                        if m.Extensions[announcemessage_pb2.status_info].state == announcemessage_pb2.ONLINE_ENABLED:
                            delegate.state = agentconnectorbase.BotStates.enabled
                            delegate.instance_of = m.Extensions[announcemessage_pb2.status_info].instance_of
                            self.logger.info("%s changed state to enabled", delegate.ip_address)
                            # print delegate.ip_address, ' changed state to enabled'
                        elif m.Extensions[announcemessage_pb2.status_info].state == announcemessage_pb2.ONLINE_DISABLED:
                            delegate.state = agentconnectorbase.BotStates.disabled
                            delegate.instance_of = m.Extensions[announcemessage_pb2.status_info].instance_of
                            self.logger.info("%s changed state to disabled", delegate.ip_address)
                            # print delegate.ip_address, ' changed state to disabled'
                        elif announcemessage_pb2.GRACEFUL_SHUTDOWN == \
                                m.Extensions[announcemessage_pb2.status_info].state:
                            delegate.state = agentconnectorbase.BotStates.offline
                            delegate.instance_of = m.Extensions[announcemessage_pb2.status_info].instance_of
                            self.logger.info("%s changed state to offline", delegate.ip_address)
                            # print delegate.ip_address, ' changed state to offline'
                        elif m.Extensions[announcemessage_pb2.status_info].state == announcemessage_pb2.CRASHED:
                            delegate.state = agentconnectorbase.BotStates.crashed
                            delegate.instance_of = m.Extensions[announcemessage_pb2.status_info].instance_of
                            self.logger.info("%s changed state to crashed", delegate.ip_address)
                            # print delegate.ip_address, ' changed state to crashed'
                        else:
                            raise RuntimeError('unhandled announce message type')
                    else:
                        raise RuntimeError('missing extension field')
                # check if it's a payload request and try to send the requested payload to agent
                elif m.message_type == messagetypes_pb2.PAYLOAD_REQUEST:
                    if m.HasExtension(payloadmessage_pb2.payload_req):
                        gid = self.bot_registry.items[delegate.ip_address].gid
                        p = self.payload_registry.request_payload(
                            m.Extensions[payloadmessage_pb2.payload_req].payload_name, gid)
                        if p is None:
                            self.logger.warning("%s requested unregistered payload", delegate.ip_address)
                            # print "requested unregistered payload"
                            m = messagegenerator.generate_payload_message_embedded(0, str())
                            delegate.agent_socket.send(NetUtility.length_prefix_message(m.SerializeToString()))
                        elif isinstance(p, Payload):
                            if p.is_embedded:
                                m = messagegenerator.generate_payload_message_embedded(0, p.embedded_data)
                                delegate.agent_socket.send(NetUtility.length_prefix_message(m.SerializeToString()))
                            else:
                                pass
                        else:
                            pass
                # check if it's an answer and update the last received message info
                elif m.message_type == messagetypes_pb2.ANSWER:
                    if m.HasExtension(answermessage_pb2.answer_info):
                        cmd = m.Extensions[answermessage_pb2.answer_info].request
                        state = m.Extensions[answermessage_pb2.answer_info].ok
                        info = m.Extensions[answermessage_pb2.answer_info].answer
                        delegate.last_answer.update(cmd, state, info)
                # bot requested the globals
                elif m.message_type == messagetypes_pb2.GLOBALS_REQUEST:
                    m = messagegenerator.generate_globals_answer_message(0, self.globals)
                    delegate.agent_socket.send(NetUtility.length_prefix_message(m.SerializeToString()))
                else:
                    self.logger.warning("%s: Unhandled message type", delegate.ip_address)
                    # print "Unhandled message type"
            except socket.error as e:
                # excepts most likely if the socket connection is broken
                self.logger.error("Socket Error: ", e)
                # print "Socket Error: ", str(e)
                delegate.agent_socket.close()
                break
            except RuntimeError as e:
                # excepts most likely if an agent wants to close it's connection gracefully
                self.logger.warning("%s: %s", delegate.ip_address, e)
                # print e.message
                if e.message == 'unexpected connection close':
                    try:
                        delegate.agent_socket.shutdown(socket.SHUT_RDWR)
                    except socket.error:
                        pass
                    finally:
                        delegate.agent_socket.close()
                        self.logger.info("%s: socket has been closed by demand", delegate.ip_address)
                        # print 'socket has been closed by demand'
                        delegate.state = agentconnectorbase.BotStates.offline
                        self.logger.info("%s changed state to offline", delegate.ip_address)
                        # print delegate.ip_address, ' changed state to offline'
                        break
                else:
                    self.logger.error("RuntimeError: %s", e)
                    delegate.agent_socket.close()
                    break
            # except Exception as e:
            #    # a different kind of error was raised
            #    print "Error: ", e.message
            except message.Error as e:
                self.logger.error("ProtoBuf Error: %s", e)
                # print "Protobuf Error: ", e.message

    def server_acceptor_handler(self, sock, address):
        """ This method handles all new incoming connection and registers them and their corresponding worker threads.
            It will also cleanup dead threads, that are no longer used.

        :type address: tuple of (str, int)
        :type sock: socket._socketobject
        :param sock: the socket we want to work with
        :param address: the address port tuple we got the connection from
        """
        self.logger.info("accepted connection from: %s", address)
        # print "accepted connection from: ", address
        d = agentconnectorbase.AgentConnectorBaseDelegate(sock, address)
        # register the bot in the bot registry
        self.bot_registry.register_bot(d)
        # create and start a listener for the new delegate
        self.create_thread(self.processor_thread, (d,))
        # check if any thread has ceased to exist
        self.cleanup_threads()

    def server_stop_listener(self):
        """ Shuts the monitor down and closes all connections.
            Overridden to handle all individual connections.
            This will wait for all threads to finish execution.

        """
        self.active = False
        TcpServerBase.server_stop_listener(self)
        self.logger.info("shutting down client sockets...")
        for i in six.iteritems(self.bot_registry.items):
            try:
                i[1].delegate.agent_socket.shutdown(socket.SHUT_RDWR)
                i[1].delegate.agent_socket.close()
            except socket.error as e:
                self.logger.warning("Socket Error: %s", e)
                # print e
            except AttributeError:
                # this is a reserved entry that was never used
                pass
        self.logger.info("client sockets have been shutdown!")
        self.join_all_threads()
        self.stopped = True

    def start(self, port=10555, bind_address=''):
        """ Starts the monitor.

        :type bind_address: str
        :type port: int
        :param port:
        :param bind_address:
        """
        self.active = True
        self.stopped = False
        self.logger.info("starting monitor")
        # print "starting monitor"
        self.server_start_listener(port, bind_address)
        self.logger.info("monitor startup complete")
        # print "monitor startup complete"

    def stop(self):
        """ Stops the monitor.


        """
        self.logger.info("shutting down monitor")
        # print "shutting down monitor"
        self.server_stop_listener()
        self.logger.info("monitor shutdown complete")
        # print "monitor shutdown complete"

    def kill(self):
        """ Kills all remote bots by sending a termination order and halting all listener threads.
            Stronger variant of stop.

        """
        self.logger.warning("attempting to kill all remote bots!!!")
        self.active = False
        TcpServerBase.server_stop_listener(self)
        for i in six.iteritems(self.bot_registry.items):
            try:
                i[1].delegate.terminate_bot()
                i[1].delegate.agent_socket.shutdown(socket.SHUT_RDWR)
                i[1].delegate.agent_socket.close()
            except socket.error as e:
                self.logger.warning("Socket Error: %s", e)
                # print e
            except AttributeError:
                # this is a reserved entry that was never used
                pass
        self.logger.warning("finished sending kill orders!!!")
        self.stopped = True
