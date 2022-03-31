""" This module contains the basic facilities to connect and work with an agent instance.

"""
from __future__ import absolute_import
import six.moves.cPickle
import datetime
import socket
import sys
import threading
import time

from enum import Enum
from google.protobuf import message
from fortrace.botnet.net import messagegenerator
from fortrace.botnet.net import netutility
from fortrace.botnet.net.meta.tcpclientbase import TcpClientBase
from fortrace.botnet.net.proto import announcemessage_pb2
from fortrace.botnet.net.proto import genericmessage_pb2

from fortrace.botnet.common.loggerbase import LoggerBase
from fortrace.botnet.common.runtimequery import RuntimeQuery
from fortrace.botnet.net.proto import genericdatamessage_pb2

__author__ = 'Sascha Kopp'


class BotStates(Enum):
    """ States for bots.

    """
    invalid = 0
    offline = 1
    disabled = 2
    enabled = 3
    crashed = 4


class CommandState(object):
    """ A container for received answers.

    :type command: bytearray
    :type state: bool
    :type info: str
    :param command: the serialized last command message
    :param state: was the command completed successfully
    :param info: additional info
    """

    def __init__(self, command, state, info):
        self.command = command
        self.state = state
        self.info = info
        self.timestamp = time.time()
        self.readable_timestamp = datetime.datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def update(self, command, state, info):
        """ Update the container writing a new timestamp.

        :type command: bytearray
        :type state: bool
        :type info: str
        :param command: the serialized last command message
        :param state: was the command completed successfully
        :param info: additional info
        """
        self.__init__(command, state, info)


class AgentConnectorBase(TcpClientBase, LoggerBase, RuntimeQuery):
    """ Contains basic methods to create a bot instance that can connect to it's agent.
        This class is intended to be used for extending an actual implementation of a bot application.

    """

    def __init__(self, default_enabled=True):
        """ The __init__ method for constructing this class.

        :type default_enabled: bool
        :param default_enabled: Controls if the enabled-flag is set on creation.
        """
        RuntimeQuery.__init__(self)
        LoggerBase.__init__(self, "AgentConnectorBase")
        TcpClientBase.__init__(self)
        self.enabled = default_enabled
        self.lock = threading.Lock()
        self.thread = threading.Thread()
        self.message_id = 0
        self.globals = dict()
        self.globals['globals_available'] = False  # check this value to determine if the globals were received
        self.delegate_class = 'AgentConnectorBaseDelegate'
        self.id_mapper = dict({
            genericmessage_pb2.DUMMY: self.test_command,
            genericmessage_pb2.ACTIVATE: self.enable_bot,
            genericmessage_pb2.DISABLE: self.disable_bot,
            genericmessage_pb2.TERMINATE: self.terminate_bot,
            genericmessage_pb2.GLOBALS_ANSWER: self._set_globals
        })

    def start_command_listener(self):
        """ Starts up the command listener thread.
            Rather than calling this method directly, use the start method.

        """
        self.active = True
        self.stopped = False
        self.thread = threading.Thread(None, self.listen_thread)
        self.thread.start()

    def stop_command_listener(self):
        """ Sets the working status to False and wait for listener thread to exit on it's own.
            Rather than calling this method directly, use the stop method.

        """
        self.active = False
        self.thread.join()
        self.stopped = True

    def listen_thread(self):
        """ This thread will listen to incoming commands by an agent instance and complete the request.
            Upon start it will tell the agent instance that it's ready by sending a state announcement.


        """
        if self.enabled:
            hello_msg = messagegenerator.generate_announce_message(self.message_id, announcemessage_pb2.ONLINE_ENABLED,
                                                                   self.delegate_class)
        else:
            hello_msg = messagegenerator.generate_announce_message(self.message_id, announcemessage_pb2.ONLINE_DISABLED,
                                                                   self.delegate_class)
        self.message_id += 1
        # tell agent that bot is ready
        self.client_socket.send(netutility.NetUtility.length_prefix_message(hello_msg.SerializeToString()))
        # request the globals
        globals_request_msg = messagegenerator.generate_globals_request_message(self.message_id)
        self.client_socket.send(netutility.NetUtility.length_prefix_message(globals_request_msg.SerializeToString()))
        self.message_id += 1
        # start processing messages
        while self.active:
            try:
                # receive and de-marshall the message
                msg = netutility.NetUtility.receive_prefixed_message(self.client_socket)
                m = genericmessage_pb2.GenericMessage()
                m.ParseFromString(msg)
                self.logger.debug("got message: %s", str(m))
                # print "agent connector: got message>\n", str(m)
                f = self.id_mapper[m.message_type]  # get the mapped function
                ret_val = f(m)  # call and pass the message to it's mapped handler
                if ret_val is None:  # if ret_val is not set, default to success
                    ret_val = (True, "success")
                # generate an answer
                ret_msg = messagegenerator.generate_answer_message(self.message_id, ret_val[0], msg, ret_val[1])
                try:
                    # send the answer back
                    self.client_socket.send(netutility.NetUtility.length_prefix_message(ret_msg.SerializeToString()))
                except socket.error as e:
                    self.logger.error("Failure sending answer message: %s", e)
            except KeyError as e:
                # expect this if a unmapped message type was received
                self.logger.error("KeyError: %s", e)
                # print e
            except socket.error as e:
                # expect this if a serious problem has occurred with the socket
                self.logger.error("Socket Error: %s", e)
                # print "Socket Error: ", str(e)
                self.client_socket.close()
                break
            except RuntimeError as e:
                # expect this if the reading end or the socket itself has been closed
                self.logger.warning("Runtime Error: %s", e)
                # print e.message
                if e.message == 'unexpected connection close':
                    try:
                        self.client_socket.shutdown(socket.SHUT_RDWR)
                    except socket.error:
                        pass
                    finally:
                        self.client_socket.close()
                        self.logger.info("socket has been closed on demand")
                        # print 'socket has been closed by demand'
                        break
                else:
                    self.logger.error("RuntimeError: %s", e)
                    self.client_socket.close()
                    break
            except message.Error as e:
                # a unhandled error happened
                self.logger.error("ProtoBuf Error: %s", e)
                # print "ProtoBuf Error: ", e.message

    def _set_globals(self, msg):
        """ Sets the globals variable

        :rtype : None | (bool, str)
        :param msg: The message that was received
        :type msg: fortrace.net.proto.genericmessage_pb2.GenericMessage
        """
        if msg.HasExtension(genericdatamessage_pb2.data):
            new_globals = six.moves.cPickle.loads(msg.Extensions[genericdatamessage_pb2.data].content)
            if isinstance(new_globals, dict):
                self.globals = new_globals
                self.logger.info("Globals are now available")
            else:
                self.logger.error("bad data received, not a dict")
                return False, "bad data received, not a dict"
        else:
            return False, "missing field"

    def _wait_for_globals(self, poll_interval=1):
        """ Wait till globals are available

        :param poll_interval: time in seconds to recheck
        """
        while not self.globals["globals_available"]:
            if not self.active:  # abort if stop order was received
                break
            time.sleep(poll_interval)

    def test_command(self, msg):
        """ This is a dummy command for testing basic functionality

        :rtype : (bool, str)
        :type msg: fortrace.net.proto.genericmessage_pb2.GenericMessage
        :param msg: The message that was received (not used by this method)
        """
        self.logger.info("Dummy command received")
        return True, "success"

    def enable_bot(self, msg):
        """ This will set the enabled-flag to True.

        :rtype : (bool, str)
        :type msg: fortrace.net.proto.genericmessage_pb2.GenericMessage
        :param msg: The message that was received (not used by this method)
        """
        self.enabled = True
        self.logger.info("agent connector is enabled")
        # print 'agent connector is enabled'
        m = messagegenerator.generate_announce_message(self.message_id, announcemessage_pb2.ONLINE_ENABLED,
                                                       self.delegate_class)
        msg = netutility.NetUtility.length_prefix_message(m.SerializeToString())
        self.client_socket.send(msg)
        self.message_id += 1
        return True, "success"

    def disable_bot(self, msg):
        """ This will set the enabled-flag to False.

        :rtype : (bool, str)
        :type msg: fortrace.net.proto.genericmessage_pb2.GenericMessage
        :param msg: The message that was received (not used by this method)
        """
        self.enabled = False
        self.logger.info("agent connector is disabled")
        # print 'agent connector is disabled'
        m = messagegenerator.generate_announce_message(self.message_id, announcemessage_pb2.ONLINE_DISABLED,
                                                       self.delegate_class)
        msg = netutility.NetUtility.length_prefix_message(m.SerializeToString())
        self.client_socket.send(msg)
        self.message_id += 1
        return True, "success"

    def terminate_bot(self, msg):
        """ This will terminate the process and send a notification that this was intended to the agent.

        :rtype : None
        :type msg: fortrace.net.proto.genericmessage_pb2.GenericMessage
        :param msg: The message that was received (not used by this method)
        """
        self.logger.info("going to terminate process")
        # print 'going to terminate process'
        # Tell the agent that this was planned.
        shutdown_msg = messagegenerator.generate_announce_message(self.message_id,
                                                                  announcemessage_pb2.GRACEFUL_SHUTDOWN,
                                                                  self.delegate_class)
        try:
            self.client_socket.send(netutility.NetUtility.length_prefix_message(shutdown_msg.SerializeToString()))
        except socket.error:
            pass
        sys.exit(0)

    # def register_handler(self, message_type, func):
    #     """ Registers a function that should be called upon receiving a specific message type.
    #         Basically it registers a message handler.
    #
    #     :type func: func of f(fortrace.net.proto.genericmessage_pb2.GenericMessage)
    #     :type message_type: fortrace.net.proto.messagetypes_pb2.MessageType
    #     :param message_type: Corresponds to a type specified in fortrace.net.proto.messagetypes.proto
    #     :param func: The message handler function type func(self, msg)
    #     """
    #     pass

    def start(self, agent_ip='127.0.0.1', agent_port=10556):
        """ Starts the AgentConnector.

        :type agent_port: int
        :type agent_ip: str
        :param agent_ip: ip/host to connect to runs the agent for this host
        :param agent_port: port of the agent
        """
        self.logger.info("starting agent connector")
        # print 'starting agent connector'
        self.logger.info("waiting for connection to agent...")
        # print 'waiting for connection to agent...'
        self.client_open_connection(agent_ip, agent_port)
        self.start_command_listener()
        # print 'agent connector started'
        self.logger.info("waiting for globals...")
        self._wait_for_globals()
        self.logger.info("agent connector startup complete")

    def stop(self):
        """ Stops the AgentConnector.


        """
        self.logger.info("shutting down the agent connector")
        # print 'shutting down the agent connector'
        shutdown_msg = messagegenerator.generate_announce_message(self.message_id,
                                                                  announcemessage_pb2.GRACEFUL_SHUTDOWN,
                                                                  self.delegate_class)
        try:
            self.client_socket.send(netutility.NetUtility.length_prefix_message(shutdown_msg.SerializeToString()))
        except socket.error:
            pass
        self.client_close_connection()
        self.stop_command_listener()
        self.logger.info("agent connector stopped")
        # print 'agent connector stopped'


class AgentConnectorBaseDelegate(LoggerBase):
    """ Wrapper to send commands to a bot.
        This is the base class that should be extended through inheritance.
        This base class contains only the basic commands to enable, disable or terminate a bot instance
    """

    # def update(self, agent_socket, addr):
    #     """ Updates a delegate entry.
    #         Used for promoting a reserved delegate entry to a valid one
    #
    #     :type addr: tuple of (str, int)
    #     :type agent_socket: socket._socketobject
    #     :param agent_socket: socket of the associated agent
    #     :param addr: the ip-address, port tuple
    #     """
    #     self.agent_socket = agent_socket
    #     self.ip_address = addr[0]
    #     self.port = addr[1]

    def __init__(self, agent_socket, addr):
        """ The constructor.


        :type addr: tuple of (str, int)
        :type agent_socket: socket._socketobject or socket._closedsocket
        :param agent_socket: socket of the associated agent
        :param addr: the ip-address, port tuple
        """
        # self.delegate_type = 0
        LoggerBase.__init__(self, "AgentConnectorBaseDelegate")
        self.last_answer = CommandState(bytearray(), True, "initialized")
        self.agent_socket = agent_socket
        self.ip_address = addr[0]
        self.port = addr[1]
        self.message_id = 0
        self.instance_of = 'AgentConnectorBaseDelegate'
        self.state = BotStates.invalid
        self.sub_state = '<unused>'

    @staticmethod
    def generate(agent_socket, addr):
        """ Factory method

        :type addr: tuple of (str, int)
        :type agent_socket: socket._socketobject
        :param agent_socket: socket of the associated agent
        :param addr: the ip-address, port tuple
        :return: the new object
        """
        return AgentConnectorBaseDelegate(agent_socket, addr)

    def enable_bot(self):
        """ Tell the bot to be active and enable communication with other bots


        """
        m = messagegenerator.generate_enable_message(self.message_id)
        msg = netutility.NetUtility.length_prefix_message(m.SerializeToString())
        try:
            self.agent_socket.send(msg)
        except socket.error:
            self.logger.error("Socket Error: %s", "could not send activation message")
            # print "could not send activation message"
        self.message_id += 1

    def disable_bot(self):
        """ Tell the bot to cease all activities and stop communication with other bots


        """
        m = messagegenerator.generate_disable_message(self.message_id)
        msg = netutility.NetUtility.length_prefix_message(m.SerializeToString())
        try:
            self.agent_socket.send(msg)
        except socket.error:
            self.logger.error("Socket Error: %s", "could not send deactivation message")
            # print "could not send deactivation message"
        self.message_id += 1

    def terminate_bot(self):
        """ Tell the bot to terminate itself and do a clean shutdown


        """
        m = messagegenerator.generate_terminate_message(self.message_id)
        msg = netutility.NetUtility.length_prefix_message(m.SerializeToString())
        try:
            self.agent_socket.send(msg)
        except socket.error:
            self.logger.error("Socket Error: %s", "could not send termination message")
            # print "could not send termination message"
        self.message_id += 1

    def load_payload(self, payload):
        """ Sends a new payload to agent.
            This is handled by the agent and won't be forwarded to the bot.


        :param payload: the payload container
        :type payload: fortrace.core.bmoncomponents.payloadregistry.Payload
        """
        if payload.is_embedded:
            m = messagegenerator.generate_payload_message_embedded(self.message_id, payload.embedded_data)
        else:
            m = messagegenerator.generate_payload_message_uri(self.message_id, payload.protocol, payload.uri)
        msg = netutility.NetUtility.length_prefix_message(m.SerializeToString())
        try:
            self.agent_socket.send(msg)
        except socket.error:
            self.logger.error("Socket Error: %s", "could not send payload")
            # print "could not send payload"
        self.message_id += 1
