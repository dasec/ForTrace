""" This module contains a method to check if the process is run under elevated rights.
    Original script by Eye of Hell found on Server Fault:
    http://serverfault.com/questions/29659/crossplatform-way-to-check-admin-rights-in-python-script
"""
from __future__ import absolute_import
__author__ = 'Sascha Kopp'

import ctypes
import os


def is_elevated():
    """ Checks if process is run under elevated privileges
    :rtype : bool
    :return: true if elevated rights are available
    """
    try:
        elevated = os.getuid() == 0
    except AttributeError:
        elevated = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return elevated
