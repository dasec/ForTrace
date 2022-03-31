# Copyright (C) 2013-2014 Reinhard Stampp
# This file is part of fortrace - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.

"""
This file contain the

"""

from __future__ import absolute_import
try:
    import logging

    from fortrace.inputDevice.keyboard import KeyboardManagement
    from fortrace.inputDevice.mouse import MouseManagement
    from fortrace.utility.logger_helper import create_logger
except ImportError as ie:
    raise Exception("application " + str(ie))
    exit(1)


class InputDeviceManagement(object):
    """InputDeviceManagement class in which the execute command will go one level down,
    finally to the last execute function. Every execute function will remove one keyword.

    """

    def __init__(self, agent_object, logger=None):
        self.keyboardManager = KeyboardManagement()
        self.mouseManager = MouseManagement()
        self.agent_object = agent_object

        self.logger = logger
        if self.logger is None:
            self.logger = create_logger('interactionManager', logging.INFO)

    def execute(self, command):
        """Continue the command execution

        supported sub commands:
            mouse
            keyboard
        """
        try:
            self.logger.info("command: " + command)
            com = command.split(" ")
            if len(com) < 2:
                return

            if "mouse" in com[0]:
                """call the execute function from webBrowser"""
                self.mouseManager.execute(" ".join(com[1:]))

            elif "keyboard" in com[0]:
                """call the execute function from mailClient"""
                self.keyboardManager.execute(" ".join(com[1:]))

            else:
                raise Exception("inputDevice " + com[0] + " not found!")

        except Exception as e:
            raise Exception("inputDeviceManagement->execute " + str(e))
