# Copyright (C) 2013-2014 Reinhard Stampp
# This file is part of fortrace - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.

from __future__ import absolute_import
try:
    import logging

    from fortrace.utility.SendKeys import SendKeys
    from fortrace.utility.logger_helper import create_logger
except ImportError as e:
    raise Exception("Error keyboard.py " + str(e))
    exit(1)


class KeyboardManagement(object):
    """Via method execute some keystrokes will be done. """

    def __init__(self, logger=None):
        self.logger = logger
        if self.logger is None:
            self.logger = create_logger('webBrowserManager', logging.INFO)

    def execute(self, command):
        self.logger.info("command: " + command)

        try:
            com = command.split(" ")
            if len(com) < 2:
                return

            if "type" in com[0]:
                """type the appending keys"""
                SendKeys(" ".join(com[1:]), pause=0, with_spaces=True, with_tabs=True, with_newlines=True)

            else:
                raise Exception("command " + com[0] + " not found!")

        except Exception as e:
            raise Exception("inputDevice->keyboard->execute " + str(e))
