# Copyright (C) 2013-2014 Reinhard Stampp
# This file is part of fortrace - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.

# import c++ dynamic library
from __future__ import absolute_import
import ctypes

try:
    import win32gui
    import logging

    from fortrace.utility.logger_helper import create_logger
except ImportError as ie:
    raise Exception("Error mouse.py " + str(ie))


def mouse_click(left_right, down_up, x, y):
    """Click on the gui.
    Options:
        eft down
        left up
        right down
        right up
        x, y
    """
    mouse_events = {
        "leftdown": 0x8002,
        "leftup": 0x8004,
        "rightdown": 0x8008,
        "rightup": 0x8010
    }
    ctypes.windll.user32.SetCursorPos(x, y)
    ctypes.windll.user32.mouse_event(mouse_events[left_right.lower() + down_up.lower()], int(x), int(y), 0, 0)


def relative_mouse_click(left_right, down_up, x, y):
    """Click relative to the active window.
    Options:
        eft down
        left up
        right down
        right up
        x, y
    """
    try:
        winId = win32gui.GetForegroundWindow()
        (left, top, right, bottom) = win32gui.GetWindowRect(winId)
        mouse_events = {
            "leftdown": 0x02,
            "leftup": 0x04,
            "rightdown": 0x08,
            "rightup": 0x10
        }

        ctypes.windll.user32.SetCursorPos(x, y)
        ctypes.windll.user32.mouse_event(mouse_events[left_right.lower() + down_up.lower()], int(x) + left,
                                         int(y) + top, 0, 0)
    except Exception as e:
        raise Exception("relativeMouseClick: " + str(e))


class MouseManagement(object):
    """Via the execute method the right function will be called to do some mouse interaction."""

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

            if "click" in com[0]:
                """click on the position the the screen"""

                left_right = com[1]
                down_up = com[2]
                x = com[3]
                y = com[4]
                mouse_click(left_right, down_up, x, y)

            elif "clickRelative" in com[0]:
                """click on the position relative to the active window on the screen"""
                left_right = com[1]
                down_up = com[2]
                x = com[3]
                y = com[4]
                relative_mouse_click(left_right, down_up, x, y)
            else:
                raise Exception("command " + com[0] + " not found!")

        except Exception as e:
            raise Exception("inputDevice->mouse->execute " + str(e))
