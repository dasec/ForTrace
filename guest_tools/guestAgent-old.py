# Copyright (C) 2013-2014 Reinhard Stampp
# This file is part of  - http://.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.


from __future__ import absolute_import
import sys
import time
import logging
import platform

from fortrace.core.agent import Agent
from fortrace.utility.logger_helper import create_logger


fortrace_CONTROLLER_IP = '192.168.102.1'
fortrace_CONTROLLER_PORT = 11000

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

    # wait for commands
    while 1:
        time.sleep(1)
        a.receiveCommands()


if __name__ == "__main__":
    main()
