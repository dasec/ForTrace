""" This module contains the factory for creating bot-delegates.

"""

__author__ = 'Sascha Kopp'


class BotFactory(object):
    """ A factory class for generating bot-delegates.

    """
    factory = dict()

    def __init__(self):
        pass

    @staticmethod
    def generate(key, sock, ip_and_port):
        """ Generate a delegate.


        :type ip_and_port: (str, int)
        :type sock: socket | socket._socketobject
        :rtype : fortrace.core.agentconnectorbase.AgentConnectorBaseDelegate
        :param key: the delegates key-name
        :param sock: the socket that is associated to the delegate
        :param ip_and_port: the ip-address and port tuple
        :return: a delegate of specialized type
        """
        return BotFactory.factory[key](sock, ip_and_port)

    @staticmethod
    def register(factory_function, key):
        """ Registers a factory function with a key-name.
            A factory-function consists of the following parameters:
            A socket followed by an ip-address- and port-tuple

        :type key: str
        :param factory_function: the factory funktion
        :param key: the key-name to map to
        """
        BotFactory.factory[key] = factory_function
