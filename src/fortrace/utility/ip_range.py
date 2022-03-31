""" This module features a simple ip-address-range-list-generator.

"""
from six.moves import map
__author__ = 'Sascha Kopp'


def ip_range(start_ip, end_ip):
    """ Generates a list of ip addresses.

    :type end_ip: str
    :type start_ip: str
    :param start_ip: the start ip-address
    :param end_ip:  the end ip-address
    :return: list of ip-addresses
    """
    start = list(map(int, start_ip.split(".")))
    end = list(map(int, end_ip.split(".")))
    temp = start
    ip_range_list = [start_ip]

    while temp != end:
        start[3] += 1
        for i in (3, 2, 1):
            if temp[i] == 256:
                temp[i] = 0
                temp[i - 1] += 1
        ip_range_list.append(".".join(map(str, temp)))

    return ip_range_list
