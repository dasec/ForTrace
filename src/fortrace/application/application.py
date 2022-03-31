# Copyright (C) 2013-2014 Reinhard Stampp
# This file is part of fortrace - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.

from __future__ import absolute_import
from __future__ import print_function
import logging
from abc import ABCMeta, abstractmethod

from fortrace.utility.logger_helper import create_logger
import six


###############################################################################
# Host side implementation
###############################################################################
class ApplicationVmmSide(six.with_metaclass(ABCMeta, object)):
    """
    Abstract class for all applications.

    Describe the application on the hypervisor (virtual machine monitor side)
    """

    def __init__(self, guest_obj, args):
        """Set default attribute values only.

        @param guest_obj: The guest on which this application is running.
        @param args: Contains dict with arguments:
                     logger: for logging.
        """
        print("in ApplicationVmmSide::init")
        try:
            self.logger = args['logger']
            if self.logger is None:
                self.logger = create_logger('interactionManager', logging.INFO)

            # To identify this application object, the guestobj on which it is
            # running and the window id is needed
            self.guest_obj = guest_obj
            self.window_id = None
            self.is_opened = False
            self.is_busy = False
            self.has_error = False

        except Exception as e:
            raise Exception("Error in " + self.__class__.__name__ +
                            ": " + self.guest_obj.guestname + " " + str(e))

    @abstractmethod
    def open(self):
        """
        Abstact method, which all child classes have to overwrite.
        """
        raise NotImplementedError

    @abstractmethod
    def close(self):
        """
        Abstact method, which all child classes have to overwrite.

        Close an instance of an application.
        """
        raise NotImplementedError


###############################################################################
# Commands to parse on host side
###############################################################################
class ApplicationVmmSideCommands(object):
    """
    Class with all commands for one application.

    Static only.
    """

    @staticmethod
    def commands():
        raise NotImplementedError


###############################################################################
# Guest side implementation
###############################################################################
class ApplicationGuestSide(six.with_metaclass(ABCMeta, object)):
    """
    Abstract class for all applications.

    Describe the application on the Guest Side
    """

    def __init__(self, agent_obj, logger):
        try:

            self.agent_object = agent_obj
            self.window_id = None
            self.window_is_crushed = False
            self.module_name = ""

            self.logger = logger
            if self.logger is None:
                self.logger = create_logger('interactionManager', logging.INFO)

        except Exception as e:
            raise Exception("Error in " + self.__class__.__name__ +
                            ": " + str(e))

    @abstractmethod
    def open(self):
        """
        Abstact method, which all child classes have to overwrite.
        """
        raise NotImplementedError

    """
    Abstact method, which all child classes have to overwrite.
    """

    @abstractmethod
    def close(self):
        """
        Abstact method, which all child classes have to overwrite.
        """
        raise NotImplementedError


###############################################################################
# Commands to parse on guest side
###############################################################################
class ApplicationGuestSideCommands(object):
    """
    Class with all commands for one application.

    Static only.
    """

    @staticmethod
    def commands():
        raise NotImplementedError
