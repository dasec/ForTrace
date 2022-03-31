from __future__ import absolute_import
import socket

from fortrace.botnet.core.agentconnectorbase import AgentConnectorBaseDelegate
from fortrace.botnet.core.botbase import BotBaseDelegate
from fortrace.botnet.core.botmasterbase import BotMasterBaseDelegate
from fortrace.botnet.core.cncserverbase import CnCServerBaseDelegate

from fortrace.botnet.core.bmoncomponents.botfactory import BotFactory
from fortrace.botnet.common.loggerbase import LoggerBase
from fortrace.utility import ip_range
import six

__author__ = 'Sascha Kopp'


class DelegateContainer(object):
    """ Contains a delegate object and it's group id
    """

    def __init__(self, delegate=None, gid=0):
        """ The constructor.


        :type gid: int
        :type delegate: fortrace.core.agentconnectorbase.AgentConnectorBaseDelegate or None
        """
        self.delegate = delegate
        self.gid = gid


class BotRegistry(LoggerBase):
    """ A class for reserving, registering and getting delegate objects.
        Note that gid=0 means any group
    """

    def __init__(self):
        LoggerBase.__init__(self, "BotRegistry")
        self.items = dict()
        # initialize basic factory key-function-assignment
        BotFactory.register(AgentConnectorBaseDelegate.generate, "AgentConnectorBaseDelegate")
        BotFactory.register(BotBaseDelegate.generate, "BotBaseDelegate")
        BotFactory.register(CnCServerBaseDelegate.generate, "CnCServerBaseDelegate")
        BotFactory.register(BotMasterBaseDelegate.generate, "BotMasterBaseDelegate")

    def get_bot(self, ip_address):
        """ Returns a delegate object for the requested bot.

        :rtype : fortrace.core.agentconnectorbase.AgentConnectorBaseDelegate
        :type ip_address: str
        :param ip_address: the ip-address of the requested bot delegate
        :return: a bot delegate

        """
        return self.items[ip_address].delegate

    def promote_bot(self, ip_address):
        """ Returns a specialized variant of the bot delegate.
            Only works after first announcement was received.


        :type ip_address: str
        :param ip_address: the bot's ip address
        :return: the promoted bot delegate
        """
        b = self.get_bot(ip_address)
        # if b.instance_of == 'BotBaseDelegate':
        #     b2 = BotBaseDelegate.generate(b.agent_socket, (b.ip_address, b.port))
        #     b2.state = b.state
        # elif b.instance_of == 'CnCServerBaseDelegate':
        #     b2 = CnCServerBaseDelegate.generate(b.agent_socket, (b.ip_address, b.port))
        #     b2.state = b.state
        # elif b.instance_of == 'BotMasterBaseDelegate':
        #     b2 = BotMasterBaseDelegate.generate(b.agent_socket, (b.ip_address, b.port))
        #     b2.state = b.state
        # else:
        #     b2 = b
        # return b2
        try:
            promoted_bot = BotFactory.generate(b.instance_of, b.agent_socket, (b.ip_address, b.port))
            promoted_bot.state = b.state
            promoted_bot.sub_state = b.sub_state
            promoted_bot.last_answer = b.last_answer
            return promoted_bot
        except KeyError:
            self.logger.warning("%s is not registered to the factory, basic delegate returned", b.instance_of)
            return b

    def reserve_for_bot(self, ip_address, gid=0):
        """ Reserves a slot for a delegate in the bot registry

        :type gid: int
        :type ip_address: str
        :param ip_address: used as index for the bot delegates
        :param gid: group for the associated bot delegate
        """
        bc = DelegateContainer(AgentConnectorBaseDelegate(socket._closedsocket, (ip_address, 0)), gid)
        self.items[ip_address] = bc

    def reserve_for_range(self, start_ip, end_ip, gid=0):
        """ Reserves a range of ip-addresses to a group.

        :param start_ip: the start-ip-address
        :param end_ip: the end-ip-address
        :param gid: the group to reserve for
        """
        address_range = ip_range.ip_range(start_ip, end_ip)
        for i in address_range:
            self.reserve_for_bot(i, gid)

    def register_bot(self, delegate):
        """ Registers a bot in the bot registry with the delegates ip as key
            Intended to be called by the BotMonitor

        :type delegate: fortrace.core.agentconnectorbase.AgentConnectorBaseDelegate
        :param delegate: a delegate that should be added to the registry
        """
        bc = DelegateContainer(delegate, 0)
        try:
            bc_existing = self.items[delegate.ip_address]
            bc.gid = bc_existing.gid
        except KeyError:
            bc = DelegateContainer(delegate, 0)
        self.items[delegate.ip_address] = bc

    def get_bot_list(self, gid=0):
        """ Returns a list of bot delegates which correspond to the gid parameter

        :type gid: int
        :rtype : list
        :param gid: the group id that the returned bots should have (0 means all bots)
        :return a list of bots
        """
        l = list()
        if gid == 0:
            for b in six.itervalues(self.items):
                l.append(b.delegate)
        else:
            for b in six.itervalues(self.items):
                if b.gid == gid:
                    l.append(b.delegate)
        return l

    def get_unmanaged_bot_list(self):
        """ Returns a list of unmanaged bot delegates.

        :rtype : list
        :return a list of bots
        """
        l = list()
        for b in six.itervalues(self.items):
            if b.gid == 0:
                l.append(b.delegate)
        return l

    def get_promoted_unmanaged_bot_list(self):
        """ Returns a list of unmanaged bot delegates, converted to special role type.

        :rtype : list
        :return a list of bots
        """
        l = list()
        for b in six.itervalues(self.items):
            if b.gid == 0:
                x = self.promote_bot(b.delegate.ip_address)
                l.append(x)
        return l

    def get_promoted_bot_list(self, gid=0):
        """ Returns a list of bot delegates which correspond to the gid parameter, converted to special role type

        :type gid: int
        :rtype : list
        :param gid: the group id that the returned bots should have (0 means all bots)
        :return a list of bots
        """
        l = list()
        if gid == 0:
            for b in six.itervalues(self.items):
                x = self.promote_bot(b.delegate.ip_address)
                l.append(x)
        else:
            for b in six.itervalues(self.items):
                if b.gid == gid:
                    x = self.promote_bot(b.delegate.ip_address)
                    l.append(x)
        return l
