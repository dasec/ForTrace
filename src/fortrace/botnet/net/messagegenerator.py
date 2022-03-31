""" This module contains message generators for producing the protobuf messages used for command exchange.
    Messages still need to be serialized to strings using the SerializeToString method.

"""
from __future__ import absolute_import
import six.moves.cPickle

from fortrace.botnet.net.proto import announcemessage_pb2
from fortrace.botnet.net.proto import answermessage_pb2
from fortrace.botnet.net.proto import botmastermessage_pb2
from fortrace.botnet.net.proto import botmessage_pb2
from fortrace.botnet.net.proto import cncmessage_pb2
from fortrace.botnet.net.proto import genericmessage_pb2
from fortrace.botnet.net.proto import logmessage_pb2
from fortrace.botnet.net.proto import messagetypes_pb2
from fortrace.botnet.net.proto import payloadmessage_pb2

from fortrace.botnet.net.proto import genericdatamessage_pb2

__author__ = 'Sascha Kopp'


def generate_enable_message(message_id):
    """ Produces an enable command message ready to be serialized to a string.

    :type message_id: long
    :rtype : fortrace.net.proto.genericmessage_pb2.GenericMessage
    :param message_id: the id of this message
    :return: the message to be generated
    """
    m = genericmessage_pb2.GenericMessage()
    m.message_type = messagetypes_pb2.ACTIVATE
    m.message_id = message_id
    assert m.IsInitialized()
    return m


def generate_disable_message(message_id):
    """ Produces a disable command message ready to be serialized to a string.

    :type message_id: long
    :rtype : fortrace.net.proto.genericmessage_pb2.GenericMessage
    :param message_id: the id of this message
    :return: the message to be generated
    """
    m = genericmessage_pb2.GenericMessage()
    m.message_type = messagetypes_pb2.DISABLE
    m.message_id = message_id
    assert m.IsInitialized()
    return m


def generate_terminate_message(message_id):
    """  Produces a terminate command message ready to be serialized to a string.

    :type message_id: long
    :rtype : fortrace.net.proto.genericmessage_pb2.GenericMessage
    :param message_id: the id of this message
    :return: the message to be generated
    """
    m = genericmessage_pb2.GenericMessage()
    m.message_type = messagetypes_pb2.TERMINATE
    m.message_id = message_id
    assert m.IsInitialized()
    return m


def generate_announce_message(message_id, announce_type, delegate_type):
    """  Produces an announcement message ready to be serialized to a string.

    :param delegate_type: the associated delegate, used internal for type casts
    :type announce_type: fortrace.net.proto.announcemessage_pb2.AnnounceStatus
    :type message_id: long
    :rtype : fortrace.net.proto.genericmessage_pb2.GenericMessage
    :param message_id: the id of this message
    :param announce_type: what this message is announcing
    :return: the message to be generated
    """
    m = genericmessage_pb2.GenericMessage()
    m.message_type = messagetypes_pb2.ANNOUNCE
    m.message_id = message_id
    m.Extensions[announcemessage_pb2.status_info].state = announce_type
    m.Extensions[announcemessage_pb2.status_info].instance_of = delegate_type
    assert m.IsInitialized()
    return m


def generate_log_message(message_id, severity, source, context):
    """  Produces a log message ready to be serialized to a string.

    :type message_id: long
    :type context: basestring
    :type source: basestring
    :type severity: fortrace.net.proto.logmessage_pb2.Severity
    :rtype : fortrace.net.proto.genericmessage_pb2.GenericMessage
    :param message_id: the id of this message
    :param severity: the severity of what is to be logged
    :param source: what caused the log message to be generated
    :param context: what actually happened
    :return: the message to be generated
    """
    m = genericmessage_pb2.GenericMessage()
    m.message_type = messagetypes_pb2.LOG
    m.message_id = message_id
    m.Extensions[logmessage_pb2.log_info].type = severity
    m.Extensions[logmessage_pb2.log_info].source = source
    m.Extensions[logmessage_pb2.log_info].context = context
    assert m.IsInitialized()
    return m


def generate_payload_request(message_id, payload_name):
    """ Produces a payload request ready to be serialized to a string.


    :type message_id: long
    :rtype : fortrace.net.proto.genericmessage_pb2.GenericMessage
    :type payload_name: str
    :param message_id: the id of this message
    :param payload_name: the payload that is requested
    :return: the message to be generated
    """
    m = genericmessage_pb2.GenericMessage()
    m.message_type = messagetypes_pb2.PAYLOAD_REQUEST
    m.message_id = message_id
    m.Extensions[payloadmessage_pb2.payload_req].payload_name = payload_name
    assert m.IsInitialized()
    return m


def generate_payload_message_embedded(message_id, content):
    """ Produces a payload message with embedded payload ready to be serialized to a string.



    :type message_id: long
    :rtype : fortrace.net.proto.genericmessage_pb2.GenericMessage
    :type content: str
    :param message_id: the id of this message
    :param content: binary representation of a payload package
    :return: the message to be generated
    """
    m = genericmessage_pb2.GenericMessage()
    m.message_type = messagetypes_pb2.PAYLOAD
    m.message_id = message_id
    m.Extensions[payloadmessage_pb2.payload_info].source_type = payloadmessage_pb2.EMBEDDED
    m.Extensions[payloadmessage_pb2.payload_info].size = len(content)
    m.Extensions[payloadmessage_pb2.payload_info].content = content
    assert m.IsInitialized()
    return m


def generate_payload_message_uri(message_id, source_type, uri):
    """ Produces a payload message redirecting to an uri payload ready to be serialized to a string.


    :type source_type: fortrace.net.proto.payloadmessage_pb2.SourceType
    :type message_id: long
    :rtype : fortrace.net.proto.genericmessage_pb2.GenericMessage
    :type uri: str
    :param message_id: the id of this message
    :param source_type: the type of service behind the uri
    :param uri: the uri where the payload package is located
    :return: the message to be generated
    """
    m = genericmessage_pb2.GenericMessage()
    m.message_type = messagetypes_pb2.PAYLOAD
    m.message_id = message_id
    m.Extensions[payloadmessage_pb2.payload_info].source_type = source_type
    m.Extensions[payloadmessage_pb2.payload_info].source = uri
    assert m.IsInitialized()
    return m

# utility messages


def generate_globals_request_message(message_id):
    """

    :rtype : fortrace.net.proto.genericmessage_pb2.GenericMessage
    :type message_id: long
    :param message_id: the id of this message
    :return: the message to be generated
    """
    m = genericmessage_pb2.GenericMessage()
    m.message_type = messagetypes_pb2.GLOBALS_REQUEST
    m.message_id = message_id
    assert m.IsInitialized()
    return m


def generate_globals_answer_message(message_id, globals_dict):
    """

    :rtype : fortrace.net.proto.genericmessage_pb2.GenericMessage
    :type globals_dict: dict
    :type message_id: long
    :param message_id: the id of this message
    :param globals_dict: the dict containing the globals
    :return: the message to be generated
    :raise TypeError: is thrown if globals_dict is no dict
    """
    if isinstance(globals_dict, dict):
        m = genericmessage_pb2.GenericMessage()
        m.message_type = messagetypes_pb2.GLOBALS_ANSWER
        m.message_id = message_id
        serialized_dict = six.moves.cPickle.dumps(globals_dict)
        m.Extensions[genericdatamessage_pb2.data].content = serialized_dict
        assert m.IsInitialized()
        return m
    else:
        raise TypeError("globals_dict needs to be of type dict")

# bot messages


def generate_bot_execute_orders_message(message_id):
    """

    :rtype : fortrace.net.proto.genericmessage_pb2.GenericMessage
    :type message_id: long
    :param message_id: the id of this message
    :return: the message to be generated
    """
    m = genericmessage_pb2.GenericMessage()
    m.message_type = messagetypes_pb2.BOTEXECUTE
    m.message_id = message_id
    assert m.IsInitialized()
    return m


def generate_bot_pull_orders_message(message_id, src_host=None, src_port=None):
    """



    :rtype : fortrace.net.proto.genericmessage_pb2.GenericMessage
    :type src_port: int
    :type src_host: str
    :type message_id: long
    :param message_id: the id of this message
    :param src_host: the host containing the order
    :param src_port: the host's port
    :return: the message to be generated
    """
    m = genericmessage_pb2.GenericMessage()
    m.message_type = messagetypes_pb2.BOTPULL
    m.message_id = message_id
    if (src_host is not None) and (src_port is not None):
        m.Extensions[botmessage_pb2.bot_pull].src_host = src_host
        m.Extensions[botmessage_pb2.bot_pull].src_port = src_port
    assert m.IsInitialized()
    return m


# cnc messages


def generate_cnc_push_orders_message(message_id, host, port):
    """



    :rtype : fortrace.net.proto.genericmessage_pb2.GenericMessage
    :type port: int
    :type host: str
    :type message_id: long
    :param message_id: the id of this message
    :param host: the host that receives the order
    :param port: the host's port
    :return: the message to be generated
    """
    m = genericmessage_pb2.GenericMessage()
    m.message_type = messagetypes_pb2.CNCPUSHORDERS
    m.message_id = message_id
    m.Extensions[cncmessage_pb2.cnc_push].host = host
    m.Extensions[cncmessage_pb2.cnc_push].port = port
    assert m.IsInitialized()
    return m


def generate_cnc_broadcast_orders(message_id):
    """

    :rtype : fortrace.net.proto.genericmessage_pb2.GenericMessage
    :type message_id: long
    :param message_id: the id of this message
    :return: the message to be generated
    """
    m = genericmessage_pb2.GenericMessage()
    m.message_type = messagetypes_pb2.CNCBROADCASTORDERS
    m.message_id = message_id
    assert m.IsInitialized()
    return m


def generate_cnc_host_orders_message(message_id, orders):
    """


    :rtype : fortrace.net.proto.genericmessage_pb2.GenericMessage
    :type orders: str
    :type message_id: long
    :param message_id: the id of this message
    :param orders: the serialized orders to issue
    :return: the message to be generated
    """
    m = genericmessage_pb2.GenericMessage()
    m.message_type = messagetypes_pb2.CNCHOSTORDERS
    m.message_id = message_id
    m.Extensions[cncmessage_pb2.cnc_host].orders = orders
    assert m.IsInitialized()
    return m


# bot master messages


def generate_bot_master_place_orders_message(message_id, data):
    """

    :rtype : fortrace.net.proto.genericmessage_pb2.GenericMessage
    :type data: dict
    :type message_id: long
    :param message_id: the id of this message
    :param data: a dict that contains a command
    :return: the message to be generated
    """
    serialized = six.moves.cPickle.dumps(data)
    m = genericmessage_pb2.GenericMessage()
    m.message_type = messagetypes_pb2.BOTMASTERPLACEORDER
    m.message_id = message_id
    m.Extensions[botmastermessage_pb2.bm_order].serialized_dict = serialized
    assert m.IsInitialized()
    return m


def generate_bot_master_get_results_message(message_id, receiving_host, receiving_port):
    """

    :rtype : fortrace.net.proto.genericmessage_pb2.GenericMessage
    :type receiving_port: int
    :type receiving_host: str
    :type message_id: long
    :param message_id: the id of this message
    :param receiving_host: the host that receives the order
    :param receiving_port: the host's port
    :return: the message to be generated
    """
    m = genericmessage_pb2.GenericMessage()
    m.message_type = messagetypes_pb2.BOTMASTERGETRESULT
    m.message_id = message_id
    m.Extensions[botmastermessage_pb2.bm_result].receiving_host = receiving_host
    m.Extensions[botmastermessage_pb2.bm_result].receiving_port = receiving_port
    assert m.IsInitialized()
    return m


def generate_answer_message(message_id, is_ok, original_command, return_value):
    """

    :type return_value: str
    :param return_value: additional information about operation
    :type original_command: bytearray
    :param original_command: serialized original message
    :type is_ok: bool
    :param is_ok: was the command executed successfully
    :rtype : fortrace.net.proto.genericmessage_pb2.GenericMessage
    :type message_id: long
    :param message_id: the id of this message
    :return: the message to be generated
    """
    m = genericmessage_pb2.GenericMessage()
    m.message_type = messagetypes_pb2.ANSWER
    m.message_id = message_id
    m.Extensions[answermessage_pb2.answer_info].ok = is_ok
    m.Extensions[answermessage_pb2.answer_info].request = original_command
    m.Extensions[answermessage_pb2.answer_info].answer = return_value
    assert m.IsInitialized()
    return m
