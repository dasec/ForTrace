# Copyright (C) 2013-2014 Reinhard Stampp
# This file is part of fortrace - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.

from __future__ import absolute_import
import netifaces
import netaddr
import fortrace.utility.constants as constants
from fortrace.utility.exceptions import NetworkError


class NetworkInfo(object):
    """
    NetworkInfo will be used for extracting the IP addresses and MAC from the two interfaces "local" and "internet".

    This can be done, because we assume specific IP address ranges to occur on these devices.
    """

    @staticmethod
    def get_interface_by_addr(addr, mask):
        """Returns interface configured with IP address from specified ranges"""
        for iface in netifaces.interfaces():
            if netifaces.AF_INET in netifaces.ifaddresses(iface):
                ip = netaddr.IPAddress(netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr'])
                nr = netaddr.IPNetwork(addr + "/" + mask)
                if ip in list(nr):
                    return iface
        raise NetworkError()

    @staticmethod
    def get_local_interface():
        """Returns the interface of the local interface"""
        return NetworkInfo.get_interface_by_addr(constants.INET_LOCAL_ADDR, constants.INET_LOCAL_MASK)

    @staticmethod
    def get_internet_interface():
        """Returns the interface of the global (internet) interface"""
        return NetworkInfo.get_interface_by_addr(constants.INET_GLOBAL_ADDR, constants.INET_GLOBAL_MASK)

    @staticmethod
    def get_local_IP():
        """Returns the IP address from the local interface"""
        iface = NetworkInfo.get_local_interface()
        if netifaces.AF_INET in netifaces.ifaddresses(iface):
            return netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']

    @staticmethod
    def get_internet_IP():
        """Returns the IP address from the global (internet) interface"""
        iface = NetworkInfo.get_internet_interface()
        if netifaces.AF_INET in netifaces.ifaddresses(iface):
            return netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']

    @staticmethod
    def get_MAC():
        """Returns the MAC from the local interface"""
        iface = NetworkInfo.get_local_interface()
        return netifaces.ifaddresses(iface)[netifaces.AF_LINK][0]['addr']
