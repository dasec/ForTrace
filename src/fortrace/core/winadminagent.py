# Copyright (C) 2017 Sascha Kopp
# This file is part of fortrace - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.
from __future__ import absolute_import
import platform

if platform.system() == "Windows":
    from fortrace.utility.winmessagepipe import WinMessagePipe
    from fortrace.utility.logger_helper import create_logger
    from logging import DEBUG
    import six.moves.cPickle
    import time
    import win32api
    import pywintypes
else:
    raise RuntimeError("This module is ony supported on Windows!")


class WinAdminAgent(object):
    """ A supplementary agent for processing commands that need admin rights within Windows

    """

    def __init__(self):
        self.logger = create_logger("winadminagent", DEBUG)
        self.logger.info("Establishing connecting to command pipe...")
        self.p = WinMessagePipe()
        self.p.open("fortraceadmin")
        self.logger.info("Now connected to command pipe!")

    def process(self):
        """ Start main loop for receiving commands.

        """
        self.logger.debug("Entering main processing loop...")
        while True:
            try:
                msg = self.p.read()  # receive a pickled message
                msg = six.moves.cPickle.loads(msg)  # deserialize message
                try:
                    cmd = msg["cmd"]
                    self.logger.debug("received command of type:" + str(cmd))
                    param = msg["param"]
                    self._handle(cmd, param)
                except six.moves.cPickle.PickleError:
                    self.logger.warning("Bad pickle data received!")
                except KeyError:
                    self.logger.warning("Bad dictionary data received!")
            except OSError:
                break
        self.logger.debug("Left main processing loop!")

    def _handle(self, cmd, param):
        """ Handle a received command.

        :type cmd: str
        :type param: List[T]
        :param cmd: command to handle
        :param param: list of parameters for command
        """
        self.logger.debug("adminpipe command: " + cmd)

        if cmd == "setostime":
            ptime = param[0]
            local_time = param[1]
            try:
                t = time.strptime(ptime, "%Y-%m-%d %H:%M:%S")
                self.logger.info("Trying to set time to: " + ptime)
            except ValueError:
                self.logger.error("Bad datetime format")
                return
            try:
                if local_time:
                    wt = pywintypes.Time(t)
                    rval = win32api.SetLocalTime(wt)  # you may prefer localtime
                else:
                    rval = win32api.SetSystemTime(t[0], t[1], t[6], t[2], t[3], t[4], t[5], 0)
                if rval == 0:
                    self.logger.error("Setting system time failed - function returned 0 - error code is {0}".format(
                        str(win32api.GetLastError())))
            except win32api.error:
                self.logger.error("Setting system time failed due to exception!")

        elif cmd == "runelevated":
            self.logger.debug("runelevated winadminagent")
            run = param[0]
            try:
                import subprocess
                import os
                subprocess.call(['runas', '/user:Administrator', os.system(run)])
            except Exception as e:
                self.logger.error(str(e))
