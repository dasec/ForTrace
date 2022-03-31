from __future__ import absolute_import
from fortrace.botnet.common.loggerbase import LoggerBase
from fortrace.core.guest import Guest

__author__ = 'Sascha Kopp'


class GroupManager(LoggerBase):
    """ Manages symbolic names.
        Bridge between symbolic names and bot registry as well as the payload registry.
        Replaces access to the bot registry and the payload registry.

    :param bot_registry: an instance of a bot registry
    :param payload_registry: an instance of a payload_registry
    """

    def __init__(self, bot_registry, payload_registry):
        """ The init method.


        :type payload_registry: fortrace.core.bmoncomponents.payloadregistry.PayloadRegistry
        :type bot_registry: fortrace.core.bmoncomponents.botregistry.BotRegistry
        """
        LoggerBase.__init__(self, "GroupManager")
        self.br = bot_registry
        self.pr = payload_registry
        self.items = dict()
        self.current_index = 1

    def setup_group(self, group_name, payload_file_name):
        """ Registers a group associated with a payload.



        :type payload_file_name: str
        :type group_name: str
        :param group_name: a symbolic group name
        :param payload_file_name: the path of a payload
        """
        self.items[group_name] = self.current_index
        internal_group = "group-" + str(self.current_index)
        self.current_index += 1
        self.pr.register_payload(payload_file_name, internal_group)
        self.logger.info("added new group <%s>: %s", internal_group, group_name)
        # print "added new group <" + internal_group + ">: " + group_name

    def __add_bot_to_group_by_guest_object(self, group_name, guest_object):
        """ Adds a bot to a group by using a Guest object



        :type guest_object: fortrace.core.guest.Guest
        :type group_name: str
        :param group_name: a symbolic group name
        :param guest_object: a Guest instance
        """
        self.br.reserve_for_bot(str(guest_object.ip_local), self.get_group_id(group_name))

    def __add_bot_to_group_by_ip(self, group_name, ip_address):
        """ Adds a bot to a group by using an ip address



        :type ip_address: str
        :type group_name: str
        :param group_name: a symbolic group name
        :param ip_address: ip address of the bot
        """
        self.br.reserve_for_bot(ip_address, self.get_group_id(group_name))

    def add_bot_to_group(self, group, guest_or_ip):
        """ Adds a bot to a group by using either a guest object or an ip address

        :type guest_or_ip: fortrace.core.guest.Guest | str
        :type group: str
        :param group: group name
        :param guest_or_ip: a guest object or an ip that should be added to group
        """
        if isinstance(guest_or_ip, Guest):
            self.__add_bot_to_group_by_guest_object(group, guest_or_ip)
        else:
            self.__add_bot_to_group_by_ip(group, guest_or_ip)

    def get_group_id(self, group_name):
        """ Returns the internal group identifier.



        :rtype : int
        :type group_name: str
        :param group_name: a symbolic group name
        :return: the internal group identifier
        """
        return self.items[group_name]

    def get_bots_by_group_name(self, group_name):
        """ Gets a list of bots in group.


        :type group_name: str
        :param group_name: a symbolic group name
        :return: a list of bots
        """
        return self.br.get_promoted_bot_list(self.get_group_id(group_name))

    def get_unmanaged_bots(self):
        """ Gets a list of bots that are in neither group.


        :return: a list of bots
        """
        return self.br.get_promoted_unmanaged_bot_list()

    def get_single_bot(self, guest_or_ip):
        """

        :type guest_or_ip: fortrace.core.guest.Guest | str
        :param guest_or_ip: the guest object to resolve
        :return: the requested bot object
        """
        if isinstance(guest_or_ip, Guest):
            return self.br.promote_bot(str(guest_or_ip.ip_local))
        else:
            return self.br.promote_bot(guest_or_ip)

    def __getitem__(self, item):
        return self.get_group_id(item)
