from __future__ import absolute_import
import atexit
import logging
import os
import subprocess
import time
from os.path import join

import fortrace.utility.constants as constants
from fortrace.utility.logger_helper import create_logger


class Sniffer:
    def __init__(self, name, path='/usr/sbin/tcpdump', pcap_path=os.getcwd(), logger=None):
        self.name = name
        self.path = path
        self.process = None
        self.pcap_path = pcap_path
        self.logger = logger
        if logger is None:
            self.logger = create_logger(name, logging.INFO)
        atexit.register(self.stop)

    def start(self):
        try:
            if not os.path.exists(self.pcap_path):
                os.makedirs(self.pcap_path)
            file = join(self.pcap_path, self.name + "_" + str(int(time.time())) + ".pcap")
            cmd = [self.path, "-i", constants.NETWORK_INTERNET_BRIDGE_INTERFACE, "-w", file, "-s0"]
            self.process = subprocess.Popen(cmd)
            self.logger.info("sniffer {} started".format(self.name))
        except Exception as e:
            self.logger.error("sniffer {} failed: ".format(self.name, str(e)))

    def stop(self):
        if self.process:
            # TODO probably sending a sigint is better
            self.process.kill()
            self.logger.info("sniffer {} stopped".format(self.name))
            self.process = None
