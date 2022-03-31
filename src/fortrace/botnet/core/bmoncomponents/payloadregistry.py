from __future__ import absolute_import
import os

from fortrace.botnet.common.loggerbase import LoggerBase
from fortrace.utility import payloadutils

__author__ = 'Sascha Kopp'


class Payload(object):
    """ A container for payloads.

    """

    def __init__(self, is_embedded, embedded_data='', uri='', protocol=''):
        """ The constructor.

        :type protocol: str
        :type uri: str
        :type embedded_data: str
        :type is_embedded: bool
        :param is_embedded: is the payload of embedded type
        :param embedded_data: the binary representation of the payload
        :param uri: the location of the payload
        :param protocol: the service run at the uri
        """
        self.is_embedded = is_embedded
        self.embedded_data = embedded_data
        self.uri = uri
        self.protocol = protocol


class PayloadRegistry(LoggerBase):
    """ A class for storing payloads.

    """

    def __init__(self):
        LoggerBase.__init__(self, "PayloadRegistry")
        self.items = dict()

    def __register_payload_raw(self, content, payload_name):
        """ Registers a raw/binary payload (from memory).

        :param content: the raw payload to be registered
        :param payload_name: the name of the payload to be registered
        """
        p = Payload(True, content)
        self.items[payload_name] = p
        # default also defaults to group-0
        if payload_name == 'default':
            self.items['group-0'] = p

    def register_payload(self, filename, payload_name):
        """ Registers a raw/binary payload (from file).

        :type payload_name: str
        :type filename: str
        :param filename: the filename of the payload to be registered
        :param payload_name: the name of the payload to be registered
        """
        try:
            ext = os.path.splitext(filename)[1]
            if ext == ".py":
                self.logger.debug("%s seems to be a python file", filename)
                c = payloadutils.generate_payload_from_single_file(filename)
            else:
                self.logger.debug("%s seems to be a zip archive", filename)
                f = open(filename, 'rb')
                c = f.read()
                f.close()
            self.__register_payload_raw(c, payload_name)
        except IOError as e:
            self.logger.error("[IOError] Payload could not be registered: %s", e)
            # print "Payload could not be registered"
        # except WindowsError as e:
        #    self.logger.error("[WindowsError] Payload could not be registered: %s", e)
        except OSError as e:
            self.logger.error("[OSError] Payload could not be registered: %s", e)

    def register_payload_uri(self, payload_name, uri, protocol):
        """ Registers a payload served behind an uri.

        :type payload_name: str
        :type protocol: str
        :type uri: str
        :param payload_name: the name of the payload to be registered
        :param uri: location of the payload
        :param protocol: protocol of the uris service
        """
        p = Payload(False, '', uri, protocol)
        self.items[payload_name] = p

    def request_payload(self, payload_name, gid=0):
        """ Returns the payload served under name


        :type gid: int
        :param gid: the group id used if payload_name is group
        :type payload_name: str
        :rtype : str
        :param payload_name: the payload to request
        """
        try:
            if payload_name == 'group':
                return self.items[payload_name + '-' + str(gid)]
            else:
                return self.items[payload_name]
        except KeyError:
            return None

    def clear_payloads(self):
        """ Removes all entries from the registry


        """
        self.items.clear()
