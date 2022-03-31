#!/usr/bin/env python
""" This is the script for running the dev server.
    The script is intended to run on a VM.
    Note that you have to first start the user-space-helper on Windows Vms.

"""
from __future__ import absolute_import
from __future__ import print_function
from fortrace.inputDevice.devcontroller import DevControlServer
import signal
import time


def handler(signum, frame):
    s.stop()
    exit(0)

print("Exit via ctrl-c or signaling SIGTERM")
s = DevControlServer()
signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)
s.start()

while True:
    time.sleep(1)
