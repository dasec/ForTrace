from __future__ import absolute_import
from time import sleep

from fortrace.botnet.core.agentconnectorbase import BotStates
from fortrace.botnet.common.loggerbase import LoggerBase
from fortrace.core.guest import Guest
from six.moves import range

__author__ = 'Sascha Kopp'


class SimulationManager(LoggerBase):
    """ Utility functions for running the simulation.

    :type bot_monitor: fortrace.core.botmonitorbase.BotMonitorBase
    :param bot_monitor: a bot monitor instance
    """

    def __init__(self, bot_monitor):
        LoggerBase.__init__(self, "SimulationManager")
        self.bot_monitor = bot_monitor

    def wait_for_bot(self, guest_or_ip):
        """

        :type guest_or_ip: str | fortrace.core.guest.Guest
        :param guest_or_ip:
        """
        if isinstance(guest_or_ip, Guest):
            ip = str(guest_or_ip.ip_local)
        else:
            ip = guest_or_ip
        while True:
            try:
                b = self.bot_monitor.bot_registry.get_bot(ip)
                if b.state == BotStates.disabled:
                    return
                if b.state == BotStates.enabled:
                    return
            except KeyError:
                pass
            self.logger.info("Waiting for %s...", ip)
            sleep(1)

    def wait_for_bots(self, number_of_bots):
        """ Block till the the specified number of bots is online.


        :type number_of_bots: int
        :param number_of_bots: the number of bots to wait for
        """
        while True:
            ready_bots = 0
            bl = self.bot_monitor.bot_registry.get_bot_list()
            for b in bl:
                if b.state == BotStates.disabled:
                    ready_bots += 1
                    continue
                if b.state == BotStates.enabled:
                    ready_bots += 1
                    continue
            if ready_bots >= number_of_bots:
                self.logger.info("Simulation is ready!")
                # print "Simulation is ready!"
                break
            else:
                self.logger.info("Waiting... (%d bots left)", (number_of_bots - ready_bots))
                # print "Waiting... ({} bots left)".format((number_of_bots - ready_bots))
                sleep(1)
                continue

    @staticmethod
    def generate_multiple_guests(vmm, amount, start_range=0, template="windows"):
        """ Generate a list of multiple guests.
            They still have to be mapped to a group.

        :rtype : list[fortrace.core.guest.Guest]
        :type start_range: int
        :type amount: int
        :type vmm: fortrace.core.vmm.Vmm
        :param start_range: for naming consistence in multiple calls, 0 means naming will start at <template>-guest1
        :param amount: amount of guests to create
        :param vmm: the virtual machine monitor
        :param template: the template to use
        :return: a list of guests
        """
        l = list()
        for x in range(start_range, (start_range + amount)):
            n = template + "-guest" + str(x + 1)
            g = vmm.create_guest(n, template)
            l.append(g)
        return l
