""" This module contains interfaces for querying the state of running instances.

"""
from __future__ import absolute_import
import threading

__author__ = 'Sascha Kopp'


class RuntimeQuery(object):
    """ A class for querying simple informations about the running instance.

    """
    def __init__(self):
        self._stopped = True
        self._active = False
        self._pid = threading.current_thread()

    @property
    def pid(self):
        return self._pid

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        if isinstance(value, bool):
            self._active = value
        else:
            raise TypeError("value needs to be of bool-type")

    @property
    def stopped(self):
        return self._stopped

    @stopped.setter
    def stopped(self, value):
        if isinstance(value, bool):
            self._stopped = value
        else:
            raise TypeError("value needs to be of bool-type")
