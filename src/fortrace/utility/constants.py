"""Constant variables for locating the directorys needed by fortrace.

"""

from __future__ import absolute_import
import os

ROOT = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

#FILEPATH_TEMPLATE_IMAGES = "/var/lib/libvirt/images/"       # where are the template images stored
FILEPATH_TEMPLATE_IMAGES = "/data/fortrace-pool/"       # where are the template images stored
#FILEPATH_LOCAL_IMAGES = "/var/lib/libvirt/images/backing/"          # where will the differential images be placed
FILEPATH_LOCAL_IMAGES = "/data/fortrace-pool/backing/"          # where will the differential images be placed
#FILEPATH_NETWORK_DUMPS = "/tmp/"                # location for pcap-files from tcpdump
FILEPATH_NETWORK_DUMPS = "/data/dumps/"                # location for pcap-files from tcpdump
FILEPATH_NETWORK_CONFIG = "/etc/libvirt/qemu/networks/"
FILEPATH_TMP = "/tmp/"

VERSION = "0.19"
GUEST_PORT = 8000
GUEST_INIT = 0x001
GUEST_RUNNING = 0x002
GUEST_COMPLETED = 0x003
GUEST_FAILED = 0x004

NETWORK_INTERNET_BRIDGE_INTERFACE = 'public'                  # hypervisor bridge interface for internet traffic
INET_GLOBAL_ADDR = "192.168.103.0"
INET_GLOBAL_MASK = "255.255.255.0"
INET_LOCAL_ADDR = "192.168.102.0"
INET_LOCAL_MASK = "255.255.255.0"
