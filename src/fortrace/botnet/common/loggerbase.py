""" This module contains an extension class for logging.

"""

from __future__ import absolute_import
from logging import getLogger, INFO, DEBUG, StreamHandler, Formatter

__author__ = 'Sascha Kopp'


class LoggerStatic(object):
    """ This is a static logger class, useful for cases where LoggerBase can not be inherited due to multiple calls.
        Example: RequestHandlers for socket servers

    """
    logger = None
    handler = None
    formatter = None

    def __init__(self):
        pass

    @staticmethod
    def if_not_then_initialize(name="LoggerStatic", debug_level=INFO, logger=None):
        """ Will initialize a new logger of static scope if none was set before.
            Else do nothing and ignore.

        :type logger: logging.Logger or None
        :type debug_level: int
        :type name: str
        :param name: name of the logger
        :param debug_level: level of logging
        :param logger: use an existing logger, overriding previous arguments
        """
        if LoggerStatic.logger is None:
            if logger is None:
                # specialy for debug-sessions, override all and raise level to DEBUG
                if __debug__:
                    debug_level = DEBUG
                # instantiate a new logger
                LoggerStatic.logger = getLogger(name)
                LoggerStatic.logger.setLevel(debug_level)
                # create console handler and set level to debug
                LoggerStatic.handler = StreamHandler()
                LoggerStatic.handler.setLevel(debug_level)
                # create formatter
                LoggerStatic.formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                                   datefmt='%m/%d/%Y %I:%M:%S')
                # add formatter to ch
                LoggerStatic.handler.setFormatter(LoggerStatic.formatter)
                # add ch to logger
                LoggerStatic.logger.addHandler(LoggerStatic.handler)
            else:
                # use the provided logger
                LoggerStatic.logger = logger
                LoggerStatic.handler = None
                LoggerStatic.formatter = None


class LoggerBase(object):
    """ A class for logging.

    :type logger: logging.Logger or None
    :type debug_level: int
    :type name: str
    :param name: name of the logger
    :param debug_level: level of logging
    :param logger: use an existing logger, overriding previous arguments
    """

    def __init__(self, name="LoggerBase", debug_level=INFO, logger=None):
        if logger is None:
            # specialy for debug-sessions, override all and raise level to DEBUG
            if __debug__:
                debug_level = DEBUG
            # instantiate a new logger
            self.logger = getLogger(name)
            self.logger.setLevel(debug_level)
            # create console handler and set level to debug
            self.handler = StreamHandler()
            self.handler.setLevel(debug_level)
            # create formatter
            self.formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                       datefmt='%m/%d/%Y %I:%M:%S')
            # add formatter to ch
            self.handler.setFormatter(self.formatter)
            # add ch to logger
            self.logger.addHandler(self.handler)
        else:
            # use the provided logger
            self.logger = logger
            self.handler = None
            self.formatter = None
