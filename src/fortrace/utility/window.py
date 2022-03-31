# Copyright (C) 2013-2014 Reinhard Stampp
# This file is part of fortrace - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.

"""
This module is an api to the windows own window management functions from user32.dll
"""

from __future__ import absolute_import
try:
    import ctypes
    import win32con
    import win32gui
except ImportError as ie:
    raise Exception("Error window.py " + str(ie))

# define all windows specific functions through ctypes and user32.dll
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible


def get_win_id_from_window(title):
    """Returns the Handle of the program window"""
    wins = []
    win32gui.EnumWindows(lambda x, y: y.append(x), wins)

    for win_id in wins:
        win_name = win32gui.GetWindowText(win_id)
        if title in win_name.lower():
            return win_id


def raise_window_by_name(title):
    """The first window which title machtes the name given in the variable title
    will be raised to the front of the gui"""
    wins = []
    win32gui.EnumWindows(lambda x, y: y.append(x), wins)
    for win_id in wins:
        win_name = win32gui.GetWindowText(win_id)
        if title in win_name.lower():
            if win32gui.IsIconic(win_id):
                win32gui.ShowWindow(win_id, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(win_id)
            break


def raise_window_by_win_id(window_id):
    """The first window which windowId matches the given windowId in the variable
    will be raised to the front of the gui"""
    wins = []
    win32gui.EnumWindows(lambda x, y: y.append(x), wins)
    for win_id in wins:
        if win_id == window_id:
            if win32gui.IsIconic(win_id):
                win32gui.ShowWindow(win_id, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(win_id)
            break
