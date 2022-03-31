""" This module contains methods for getting ip addresses.
    Needs netifaces>=0.10.0 .
    Optional component.

"""

from __future__ import absolute_import
import netifaces

__author__ = 'Sascha Kopp'


def get_default_ip_address():
    """ Returns the ip address of the host default exterior access port/adapter.

    :rtype : str
    :return: the default adapters ipv4 address
    """
    gws = netifaces.gateways()  # get all gateways
    default = gws['default']  # get the default gw
    adapter = default[2][1]  # get the adapter identifier
    realadapter = netifaces.ifaddresses(adapter)  # get the adapter
    addr_dict = realadapter[2][0]  # get the first ipv4 address tuple
    return addr_dict['addr']
