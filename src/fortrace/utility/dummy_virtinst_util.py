"""A dummy module to prevent import errors from Guest.

"""

from __future__ import absolute_import
import random


def default_route(nic=None):
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def default_bridge():
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def default_network(conn):
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def default_connection():
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def get_cpu_flags():
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def is_pae_capable(conn=None):
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def is_hvm_capable():
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def is_kqemu_capable():
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def is_kvm_capable():
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def is_blktap_capable():
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def get_default_arch():
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


# this function is directly from xend/server/netif.py and is thus
# available under the LGPL,
# Copyright 2004, 2005 Mike Wray <mike.wray@hp.com>
# Copyright 2005 XenSource Ltd
def randomMAC(type="xen"):
    """Generate a random MAC address.
    00-16-3E allocated to xensource
    52-54-00 used by qemu/kvm
    The OUI list is available at http://standards.ieee.org/regauth/oui/oui.txt.
    The remaining 3 fields are random, with the first bit of the first
    random field set 0.
    >>> randomMAC().startswith("00:16:3E")
    True
    >>> randomMAC("foobar").startswith("00:16:3E")
    True
    >>> randomMAC("xen").startswith("00:16:3E")
    True
    >>> randomMAC("qemu").startswith("52:54:00")
    True
    @return: MAC address string
    """
    ouis = { 'xen': [ 0x00, 0x16, 0x3E ], 'qemu': [ 0x52, 0x54, 0x00 ] }

    try:
        oui = ouis[type]
    except KeyError:
        oui = ouis['xen']

    mac = oui + [
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff)]
    return ':'.join(["%02x" % x for x in mac])


def randomUUID():
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def uuidToString(u):
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def uuidFromString(s):
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


# the following function quotes from python2.5/uuid.py
def get_host_network_devices():
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def get_max_vcpus(conn, type=None):
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def get_phy_cpus(conn):
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def system(cmd):
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def xml_escape(str):
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def compareMAC(p, q):
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def _xorg_keymap():
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def _console_setup_keymap():
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def default_keymap():
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def pygrub_path(conn=None):
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def uri_split(uri):
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def is_uri_remote(uri):
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def get_uri_hostname(uri):
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def get_uri_transport(uri):
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def get_uri_driver(uri):
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def is_storage_capable(conn):
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def get_xml_path(xml, path=None, func=None):
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def lookup_pool_by_path(conn, path):
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")


def check_keytable(kt):
    raise RuntimeError("virtinst.utils not loaded. tried to access dummy method")
