from __future__ import absolute_import
import os
import getpass


def get_home_dir():
    p = os.path.expanduser("~")
    return p


def get_username():
    u = getpass.getuser()
    return u


def win32_get_program_files(os64bit=True, pf64bit=True):
    if os64bit:
        if not pf64bit:
            return "C:\\Program Files (x86)"
    return "C:\\Program Files"
