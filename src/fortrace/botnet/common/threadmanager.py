""" This module contains a class for managing threads.

"""

from __future__ import absolute_import
import threading

from fortrace.botnet.common.loggerbase import LoggerBase

__author__ = 'Sascha Kopp'


class ThreadManager(object):
    """ A simple class for implementing a minimalistic thread-pool providing simple functions for creating threads
        and for cleanup.

    """

    def __init__(self):
        self._tm_logger = LoggerBase("ThreadManager")
        self._tp = list()

    def create_thread(self, func, args, name=None):
        """ Creates and adds a new running thread to the pool.

        :param func: the worker function to run as a thread
        :param args: additional arguments
        :param name: name for the thread
        """
        t = threading.Thread(name=name, target=func, args=args)
        t.start()
        self._tp.append(t)

    def remove_thread(self, thread):
        """ Remove a thread from pool.

        :param thread: the thread to be removed from pool
        """
        self._tp.remove(thread)

    def cleanup_threads(self):
        """ Remove all inactive/dead threads from pool.


        """
        for x in self._tp:
            if not x.isAlive():
                try:
                    self._tp.remove(x)
                except ValueError:
                    pass

    def join_all_threads(self, timeout=None):
        """ Wait for all threads to end.

        :param timeout: the individual timeout for each thread
        """
        for t in self._tp:
            thread_id = t.ident
            if thread_id is not None:
                self._tm_logger.logger.debug("waiting for thread: %d", thread_id)
            t.join(timeout)
