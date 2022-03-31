#!/usr/bin/env python
# This file is part of fortrace - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.
# This will run both the guest-agent and bot-agent.


from __future__ import absolute_import
import time
import logging
import platform

from fortrace.core.agent import Agent
from fortrace.utility.logger_helper import create_logger
from fortrace.botnet.core.botagentbase import BotAgentBase

fortrace_CONTROLLER_IP = '192.168.102.1'
fortrace_CONTROLLER_PORT = 11000
fortrace_BOT_CONTROLLER_PORT = 10555


def main():
    # create logger
    logger = create_logger('guestAgent', logging.DEBUG)

    logger.info("create Agent")
    a = Agent(operating_system=platform.system().lower(), logger=logger)
    logger.info("connect to fortrace controller: %s:%i" % (fortrace_CONTROLLER_IP, fortrace_CONTROLLER_PORT))
    a.connect(fortrace_CONTROLLER_IP, fortrace_CONTROLLER_PORT)

    # let all network interfaces come up
    time.sleep(15)

    # inform fortrace controller about network configuration
    a.register()

    # setup and start the bot agent
    ba = BotAgentBase()
    ba.agent_start(fortrace_CONTROLLER_IP, fortrace_BOT_CONTROLLER_PORT)

    # wait for user commands
    while 1:
        time.sleep(1)
        a.receiveCommands()

    ba.agent_stop()


if __name__ == "__main__":
    main()
