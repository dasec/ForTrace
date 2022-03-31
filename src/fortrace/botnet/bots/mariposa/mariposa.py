""" This module contains components for simulating the Mariposa botnet command and control structures.

"""
from __future__ import absolute_import
from __future__ import print_function
import six.moves.socketserver
import struct
import threading
from time import sleep

from enum import Enum
from fortrace.botnet.core.botmasterbase import BotMasterBase
from fortrace.botnet.core.cncserverbase import CnCServerBase

from fortrace.botnet.bots.mariposa.mariposaprotocol import MariposaProtocol, MariposaMessageType
from fortrace.botnet.common.loggerbase import LoggerBase, LoggerStatic
from fortrace.botnet.core.botbase import BotBase
from fortrace.botnet.net.netutility import NetUtility
import six

__author__ = 'Sascha Kopp'


class ConnectionState(Enum):
    """ Represents different states of bots.

    """
    NO_INIT = 0
    INIT_JOIN_SEND = 1
    INIT_FIN_WAIT_FOR_ACK = 2
    ALIVENESS_PHASE = 3
    ACTION_PHASE = 4


class ThreadedUDPServer(six.moves.socketserver.ThreadingMixIn, six.moves.socketserver.UDPServer):
    """ A non blocking implementation of a socket server.

    """
    pass


class ThreadedUDPRequestHandlerBotMaster(six.moves.socketserver.BaseRequestHandler):
    """ The server handler for the Mariposa bot master.

    """

    def handle(self):
        """ The implementation for the handler.


        """
        LoggerStatic.if_not_then_initialize("BotMasterRequestHandler(bot-channel)")
        data = bytearray(self.request[0])
        LoggerStatic.logger.debug("Got[%s]: %s", str(len(data)), ' '.join('{:02x}'.format(x) for x in data))
        # print "(Bot-channel) Got[" + str(len(data)) + "]:" + ' '.join('{:02x}'.format(x) for x in data)
        sock = self.request[1]
        answer_tuple = (self.client_address[0], MariposaBotMaster.bm_port)
        type_code = data[0]  # store the type-code
        seq = str(data[1:3])  # store the sequence-number, used for decryption
        seq_num = struct.unpack("H", seq)[0]  # convert to integer/short
        if MariposaBotMaster.seq_num < seq_num:  # if seq num is lower update it
            MariposaBotMaster.seq_num = seq_num
        MariposaBotMaster.seq_num += 1
        if type_code == 0x80:  # ack
            # c&c server tells bm that a command was received successfully
            pass
        elif type_code == 0x01:  # cmd/resp, send with sys info
            # a new bot is in the bot net, payload contains the sys info
            LoggerStatic.logger.info("new bot in network")
            # print "new bot in network"
            if len(data) > 3:
                # de-marshalling of payload
                # payload = data[3:]
                # dec_payload = MariposaProtocol.encrypt_decrypt_payload(seq_num, payload, len(payload))
                # cmd_code = dec_payload[0]
                # payload_data = dec_payload[1:]
                pass
            LoggerStatic.logger.info("sending ack")
            # print "sending ack"
            msg = MariposaProtocol.generate_header(MariposaMessageType.ACKNOWLEDGEMENT, MariposaBot.seq_num)
            # send
            sock.sendto(msg, answer_tuple)
            MariposaBotMaster.seq_num += 1
        else:
            pass


class ThreadedUDPRequestHandlerCnC(six.moves.socketserver.BaseRequestHandler):
    """ The server handler for the Mariposa cnc.

    """

    def handle(self):
        """ The implementation for the handler.


        """
        LoggerStatic.if_not_then_initialize("CnCRequestHandler(bot-channel)")
        data = bytearray(self.request[0])
        LoggerStatic.logger.debug("Got[%s]: %s", str(len(data)), ' '.join('{:02x}'.format(x) for x in data))
        # print "(Bot-channel) Got[" + str(len(data)) + "]:" + ' '.join('{:02x}'.format(x) for x in data)
        type_code = data[0]
        seq = str(data[1:3])
        seq_num = struct.unpack("H", seq)[0]
        if MariposaCnC.seq_num < seq_num:  # if seq num is lower update it
            MariposaCnC.seq_num = seq_num
        MariposaCnC.seq_num += 1
        if type_code == 0x61:  # join request
            # bot wants to connect
            LoggerStatic.logger.info("new join from bot: %s", self.client_address)
            # print "new join from bot: " + self.client_address[0]
            MariposaCnC.clients[self.client_address[0]] = ConnectionState.INIT_JOIN_SEND
            msg = MariposaProtocol.generate_initial_join_server_ack_ip_address(MariposaCnC.seq_num,
                                                                               self.client_address[0])
            # ack with remote ip
            NetUtility.send_message_ipv4_udp(self.client_address[0], MariposaCnC.bm_port, msg)
        elif type_code == 0x80:  # ack
            # bot or bot master acks a command response message, check by peer list
            if self.client_address[0] in MariposaCnC.clients:
                # bot acknowledging command, forward it to bm
                if MariposaCnC.clients[self.client_address[0]] == ConnectionState.ALIVENESS_PHASE:
                    LoggerStatic.logger.info("bot acknowledges command: %s", self.client_address[0])
                    # print "bot acknowledges command: " + self.client_address[0]
                    NetUtility.send_message_ipv4_udp(MariposaCnC.bm_ip, MariposaCnC.bm_port, data)
                else:
                    LoggerStatic.logger.info("connection half-opened: %s", self.client_address[0])
                    # print "connection half-opened: " + self.client_address[0]
            else:
                # bm acknowledging bot, do nothing
                pass
        elif type_code == 0x01:  # cmd/resp, send with sys info
            if self.client_address[0] in MariposaCnC.clients:
                # bot finalizing connection, forward to bm
                LoggerStatic.logger.info("bot finalized connection or is alive: %s", self.client_address[0])
                # print "bot finalized connection or is alive: " + self.client_address[0]
                if MariposaCnC.clients[self.client_address[0]] != ConnectionState.ALIVENESS_PHASE:
                    LoggerStatic.logger.info("new finalized connection, telling bot-master")
                    # print "new finalized connection, telling bot master"
                    NetUtility.send_message_ipv4_udp(MariposaCnC.bm_ip, MariposaCnC.bm_port, data)
                MariposaCnC.clients[self.client_address[0]] = ConnectionState.ALIVENESS_PHASE
                # tell bot that connection is established
                msg = MariposaProtocol.generate_initial_acknowledgement(MariposaCnC.seq_num)
                NetUtility.send_message_ipv4_udp(self.client_address[0], MariposaCnC.bm_port, msg)
            else:
                # bm sending command, broadcast to all alive peers
                LoggerStatic.logger.info("new order from bot-master")
                # print "new order from bm"
                for p, s in six.iteritems(MariposaCnC.clients):
                    if s == ConnectionState.ALIVENESS_PHASE:
                        NetUtility.send_message_ipv4_udp(p, MariposaCnC.bm_port, data)
        else:
            pass
        MariposaCnC.seq_num += 1


class ThreadedUDPRequestHandlerBot(six.moves.socketserver.BaseRequestHandler):
    """ The server handler for the Mariposa bot.

    """

    def handle(self):
        """ The implementation for the handler.


        """
        LoggerStatic.if_not_then_initialize("BotRequestHandler(bot-channel)")
        data = bytearray(self.request[0])
        LoggerStatic.logger.debug("Got[%s]: %s", str(len(data)), ' '.join('{:02x}'.format(x) for x in data))
        # print "(Bot-channel) Got[" + str(len(data)) + "]:" + ' '.join('{:02x}'.format(x) for x in data)
        sock = self.request[1]
        answer_tuple = (self.client_address[0], MariposaBot.bot_port)
        type_code = data[0]
        seq = str(data[1:3])
        seq_num = struct.unpack("H", seq)[0]
        if MariposaBot.seq_num < seq_num:  # if seq num is lower update it
            MariposaBot.seq_num = seq_num
        MariposaBot.seq_num += 1
        if type_code == 0x40:  # join ack
            # c&c acks the join
            MariposaBot.state = ConnectionState.INIT_FIN_WAIT_FOR_ACK
            MariposaBot.connected_to = self.client_address[0]  # use this cnc for further messages
            # send ack, cmd/resp
            msg = MariposaProtocol.generate_header(MariposaMessageType.ACKNOWLEDGEMENT, MariposaBot.seq_num)
            sock.sendto(msg, answer_tuple)
            MariposaBot.seq_num += 1
            LoggerStatic.logger.info("send ack to half-open connection")
            # print "send ack to half-finish connection"
            msg = MariposaProtocol.generate_initial_response_sys_info(MariposaBot.seq_num)
            # send
            sock.sendto(msg, answer_tuple)
            LoggerStatic.logger.info("send response with hw info")
            # print "send response with hw info"
            LoggerStatic.logger.info("waiting for ack")
            # print "waiting for ack"
        elif type_code == 0x80:  # ack
            # init is done
            MariposaBot.state = ConnectionState.ALIVENESS_PHASE
            LoggerStatic.logger.info("entering aliveness phase")
            # print "entering aliveness phase"
        elif type_code == 0x01:  # cmd/resp
            # command received
            LoggerStatic.logger.info("entering action phase")
            # print "entering action phase"
            MariposaBot.state = ConnectionState.ACTION_PHASE
            if len(data) > 3:
                # de-marshalling of payload
                payload = data[3:]
                dec_payload = MariposaProtocol.encrypt_decrypt_payload(seq_num, payload, len(payload))
                # cmd_code = dec_payload[0]
                payload_data = dec_payload[1:]
                # evaluate the command
                # todo: implement evaluation
                LoggerStatic.logger.info("new command: %s", payload_data)
                # print "new command: " + payload_data
                msg = MariposaProtocol.generate_header(MariposaMessageType.ACKNOWLEDGEMENT, MariposaBot.seq_num)
                # send
                sock.sendto(msg, answer_tuple)
            MariposaBot.state = ConnectionState.ALIVENESS_PHASE
            LoggerStatic.logger.info("left action phase")
            # print "left action phase"
        else:
            pass
        MariposaBot.seq_num += 1


class MariposaCnC(CnCServerBase):
    """ This class represents the Mariposa c&c server.
        It will run in full automatic mode.

    :param enabled: should the instance react to incoming messages
    """
    bm_ip = '127.0.0.1'  # will be replaced
    bm_port = MariposaProtocol.MARIPOSA_PORT1
    clients = dict()
    seq_num = 0

    def __init__(self, enabled=False):
        CnCServerBase.__init__(self, enabled)
        self.sock_server = None
        self.sock_server_thread = None

    def host_orders_impl(self, orders):
        """ unused!

        :param orders: unused!
        """
        pass

    def broadcast_orders_impl(self):
        """ unused!


        """
        pass

    def push_orders_impl(self, host, port):
        """ unused!

        :param host: unused!
        :param port: unused!
        """
        pass

    def start(self, agent_ip='127.0.0.1', agent_port=10556):
        """ Starts the CnC-Bot.

        :type agent_port: int
        :type agent_ip: str
        :param agent_ip: the agents ip-address
        :param agent_port: the agents port
        """
        CnCServerBase.start(self, agent_ip, agent_port)
        try:
            MariposaCnC.bm_port = self.globals["port"]
        except KeyError:
            MariposaCnC.bm_port = MariposaProtocol.MARIPOSA_PORT1
        try:
            MariposaCnC.bm_ip = self.globals["bm_ip"]
        except KeyError:
            raise KeyError("Needed value bm_ip not found")
        self.sock_server = ThreadedUDPServer(('', MariposaCnC.bm_port), ThreadedUDPRequestHandlerCnC)
        self.sock_server_thread = threading.Thread(target=self.sock_server.serve_forever)
        self.sock_server_thread.start()

    def stop(self):
        """ Stops the CnC-Bot.


        """
        CnCServerBase.stop(self)
        self.sock_server.shutdown()
        self.sock_server_thread.join()
        self.sock_server = None


class MariposaBotMaster(BotMasterBase):
    """ This class represents the bot master and will be used to place orders.

    :param enabled: should the instance react to incoming messages
    """
    seq_num = 0
    bm_port = MariposaProtocol.MARIPOSA_PORT1

    def __init__(self, enabled=False):
        BotMasterBase.__init__(self, enabled)
        self.sock_server = None
        self.sock_server_thread = None

    def place_order_impl(self, unpacked_data):
        """ Send command to c&c server.
            Refer to print commands for details.

        :type unpacked_data: dict
        :param unpacked_data: a dict with the command
        """
        target = unpacked_data['cnc_target_host']
        target_port = unpacked_data['cnc_target_port']
        command = unpacked_data['command']
        additional_params = unpacked_data['args']
        current_seq_num = MariposaBotMaster.seq_num
        if command == "enable_google":
            msg = MariposaProtocol.generate_enable_google_message(current_seq_num)
        elif command == "disable_google":
            msg = MariposaProtocol.generate_disable_google_message(current_seq_num)
        elif command == "enable_msn":
            msg = MariposaProtocol.generate_enable_messenger_message(current_seq_num)
        elif command == "disable_msn":
            msg = MariposaProtocol.generate_disable_messenger_message(current_seq_num)
        elif command == "enable_usb":
            msg = MariposaProtocol.generate_enable_usb_spreader_message(current_seq_num)
        elif command == "disable_usb":
            msg = MariposaProtocol.generate_disable_usb_spreader_message(current_seq_num)
        elif command == "silence":
            msg = MariposaProtocol.generate_silence_channel_message(current_seq_num, additional_params)
        elif command == "send_ip_list":
            msg = MariposaProtocol.generate_channel_ip_list_message(current_seq_num)
        elif command == "update":
            msg = MariposaProtocol.generate_update_malware_message(current_seq_num)
        elif command == "download":
            msg = MariposaProtocol.generate_download_and_exec_message(current_seq_num)
        elif command == "download2":
            msg = MariposaProtocol.generate_new_alternative_download_and_exec_message(current_seq_num)
        elif command == "remove":
            msg = MariposaProtocol.generate_remove_bot_message(current_seq_num)
        else:
            return
        NetUtility.send_message_ipv4_udp(target, target_port, msg)
        MariposaBotMaster.seq_num += 1

    def get_results_impl(self, receiving_host, receiving_port):
        """ unused!

        :param receiving_host: unused!
        :param receiving_port: unused!
        """
        pass

    def print_commands(self):
        """ Print all supported command combinations.


        """

        print("<command>\t<target>\t<additional>")
        print("enable_google\t<empty>\t<empty>\tenable google module")
        print("disable_google\t<empty>\t<empty>\tdisable google module")
        print("enable_msn\t<empty>\t<empty>\tenable msn spreader module")
        print("disable_msn\t<empty>\t<empty>\tdisable msn spreader module")
        print("enable_usb\t<empty>\t<empty>\tenable usb spreader module")
        print("disable_usb\t<empty>\t<empty>\tdisable usb spreader module")
        print("silence\t<empty>\tchannel\tsilence a channel")
        print("send_ip_list\t<empty>\t<empty>\tspreads a list of ip addresses")
        print("update\t<empty\t<empty>\tupdate the malware")
        print("download\t<empty>\t<empty>\tdownload and execute")
        print("download2\t<empty>\t<empty>\tnewer download and execute")
        print("remove\t<empty>\t<empty\tremove the bot")

    def start(self, agent_ip='127.0.0.1', agent_port=10556):
        """ Starts the Bot-Master.

        :type agent_port: int
        :type agent_ip: str
        :param agent_ip: the agents ip-address
        :param agent_port: the agents port
        """
        BotMasterBase.start(self, agent_ip, agent_port)
        try:
            MariposaBotMaster.bm_port = self.globals["port"]
        except KeyError:
            MariposaBotMaster.bm_port = MariposaProtocol.MARIPOSA_PORT1
        self.sock_server = ThreadedUDPServer(('', MariposaBotMaster.bm_port), ThreadedUDPRequestHandlerBotMaster)
        self.sock_server_thread = threading.Thread(target=self.sock_server.serve_forever)
        self.sock_server_thread.start()

    def stop(self):
        """ Stops the Bot-Master.


        """
        BotMasterBase.stop(self)
        self.sock_server.shutdown()
        self.sock_server_thread.join()
        self.sock_server = None


class MariposaBot(BotBase, LoggerBase):
    """ This class represents the Mariposa malware that communicates with the c&c servers.
        It will run in full automatic mode.

    :param enabled: should the instance react to incoming messages
    """
    seq_num = 0
    cnc = MariposaProtocol.MARIPOSA_HOST1
    bot_port = MariposaProtocol.MARIPOSA_PORT1
    state = ConnectionState.NO_INIT
    connected_to = ''

    def __init__(self, enabled=False):
        LoggerBase.__init__(self, "MariposaBot")
        BotBase.__init__(self, enabled)
        self.sock_server = None
        self.sock_server_thread = None
        self.bot_thread = None

    def pull_orders_impl(self, src_host, src_port):
        """ unused!

        :param src_host: unused!
        :param src_port: unused!
        """
        pass

    def execute_orders_impl(self):
        """ unused!


        """
        pass

    def bot_worker_loop(self):
        """ The bot worker thread


        """
        # send initial connection message
        mariposa_cnc = MariposaBot.cnc
        mariposa_port = MariposaBot.bot_port
        sleep(2 * 60)
        msg = MariposaProtocol.generate_initial_connect_message(MariposaBot.seq_num)
        NetUtility.send_message_ipv4_udp(mariposa_cnc, MariposaProtocol.MARIPOSA_PORT1, msg)
        MariposaBot.seq_num += 1
        self.logger.info("send connection request")
        # print "send connection request"
        while self.active:
            if self.state == ConnectionState.ALIVENESS_PHASE:
                # send signal
                msg = MariposaProtocol.generate_aliveness_announcement(MariposaBot.seq_num)
                NetUtility.send_message_ipv4_udp(MariposaBot.connected_to, mariposa_port, msg)
                MariposaBot.seq_num += 1
                self.logger.info("send aliveness signal")
                # print "send aliveness signal"
            sleep(4 * 60)

    def start(self, agent_ip='127.0.0.1', agent_port=10556):
        """ Starts the bot.

        :type agent_port: int
        :type agent_ip: str
        :param agent_ip: the agents ip-address
        :param agent_port: the agents port
        """
        BotBase.start(self, agent_ip, agent_port)
        try:
            MariposaBot.cnc = self.globals["cnc"]
        except KeyError:
            MariposaBot.cnc = MariposaProtocol.MARIPOSA_HOST1
        try:
            MariposaBot.bot_port = self.globals["port"]
        except KeyError:
            MariposaBot.bot_port = MariposaProtocol.MARIPOSA_PORT1
        self.sock_server = ThreadedUDPServer(('', MariposaBot.bot_port), ThreadedUDPRequestHandlerBot)
        self.sock_server_thread = threading.Thread(target=self.sock_server.serve_forever)
        self.sock_server_thread.start()
        self.bot_thread = threading.Thread(target=self.bot_worker_loop)
        self.bot_thread.start()

    def stop(self):
        """ Stops the bot.


        """
        BotBase.stop(self)
        self.sock_server.shutdown()
        self.sock_server_thread.join()
        self.bot_thread.join()
        self.sock_server = None
