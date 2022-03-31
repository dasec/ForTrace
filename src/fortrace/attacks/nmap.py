""" This module contains wrappers to use with Nmap.
    Remember to keep the add to path flag on the Nmap Windows installer.

"""

from __future__ import absolute_import
from fortrace.core.guest import Guest


class Nmap:
    """ This class contains static methods to interface with Nmap.

    """
    def __init__(self):
        pass

    @staticmethod
    def __get_port_range_param(port_start, port_stop):
        # type: (int, int) -> str
        if port_start is not None and port_stop is not None:
            return " -p " + str(port_start) + "-" + str(port_stop)
        else:
            return ""

    @staticmethod
    def __get_random_order_param(random_order):
        # type: (bool) -> str
        if not random_order:
            return " -r"
        else:
            return ""

    @staticmethod
    def __get_no_ping_param(no_ping):
        # type: (bool) -> str
        if no_ping:
            return " -sn"
        else:
            return ""

    @staticmethod
    def __get_version_detection_param(version_detect):
        # type: (bool) -> str
        if version_detect:
            return " -sV"
        else:
            return ""

    @staticmethod
    def __format_host_list(target):
        """ Generate a list of hosts in nmap notation.

        :type target: str | fortrace.core.guest.Guest | list[fortrace.core.guest.Guest] | list[str]
        :param target: host or list of hosts
        :rtype: str
        :return: a comma-separated list of hosts
        """
        if isinstance(target, Guest):
            return str(target.ip_internet)
        elif isinstance(target, list):
            tgt_temp = ""
            for x in target:
                if isinstance(x, Guest):
                    tgt_temp += str(x.ip_internet) + ","
                else:
                    tgt_temp += x + ","
            tgt_temp = tgt_temp.rstrip(",")
            return tgt_temp
        else:
            return target

    @staticmethod
    def guest_nmap_tcp_syn_scan(initiator, target, version_detect=True, port_start=None, port_stop=None,
                                random_order=True,
                                no_ping=False):
        """ Initiates a tcp syn scan (used as default by the Zenmap gui)

        :param initiator: the that initiates the scan
        :param target: host or list of hosts
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type target: str | fortrace.core.guest.Guest | list[fortrace.core.guest.Guest] | list[str]
        :type initiator: fortrace.core.guest.Guest
        :rtype: fortrace.core.guest.ShellExecResult
        """
        target = Nmap.__format_host_list(target)
        return initiator.shellExec(
            Nmap._nmap_tcp_syn_scan(target, version_detect, port_start, port_stop, random_order, no_ping))

    @staticmethod
    def _nmap_tcp_syn_scan(host, version_detect=True, port_start=None, port_stop=None, random_order=True,
                           no_ping=False):
        """ Initiates a tcp syn scan (used as default by the Zenmap gui)

        :param host: host or list of hosts in nmaps notation
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type host: str
        """
        scan_param = " -sS"
        version_detect_param = Nmap.__get_version_detection_param(version_detect)
        port_range_param = Nmap.__get_port_range_param(port_start, port_stop)
        random_order_param = Nmap.__get_random_order_param(random_order)
        no_ping_param = Nmap.__get_no_ping_param(no_ping)
        cmd = "nmap " + host + version_detect_param + scan_param + port_range_param + random_order_param + no_ping_param
        return cmd

    @staticmethod
    def guest_nmap_tcp_connect_scan(initiator, target, version_detect=True, port_start=None, port_stop=None,
                                    random_order=True, no_ping=False):
        """ Initiates a tcp connect scan

        :param initiator: the that initiates the scan
        :param target: host or list of hosts
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type target: str | fortrace.core.guest.Guest | list[fortrace.core.guest.Guest] | list[str]
        :type initiator: fortrace.core.guest.Guest
        :rtype: fortrace.core.guest.ShellExecResult
        """
        target = Nmap.__format_host_list(target)
        return initiator.shellExec(
            Nmap._nmap_tcp_connect_scan(target, version_detect, port_start, port_stop, random_order, no_ping))

    @staticmethod
    def _nmap_tcp_connect_scan(host, version_detect=True, port_start=None, port_stop=None, random_order=True,
                               no_ping=False):
        """ Initiates a tcp connect scan

        :param host: host or list of hosts in nmaps notation
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type host: str
        """
        scan_param = " -sT"
        version_detect_param = Nmap.__get_version_detection_param(version_detect)
        port_range_param = Nmap.__get_port_range_param(port_start, port_stop)
        random_order_param = Nmap.__get_random_order_param(random_order)
        no_ping_param = Nmap.__get_no_ping_param(no_ping)
        cmd = "nmap " + host + version_detect_param + scan_param + port_range_param + random_order_param + no_ping_param
        return cmd

    @staticmethod
    def guest_nmap_tcp_null_scan(initiator, target, version_detect=True, port_start=None, port_stop=None,
                                 random_order=True,
                                 no_ping=False):
        """ Initiates a tcp null scan

        :param initiator: the that initiates the scan
        :param target: host or list of hosts
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type target: str | fortrace.core.guest.Guest | list[fortrace.core.guest.Guest] | list[str]
        :type initiator: fortrace.core.guest.Guest
        :rtype: fortrace.core.guest.ShellExecResult
        """
        target = Nmap.__format_host_list(target)
        return initiator.shellExec(
            Nmap._nmap_tcp_null_scan(target, version_detect, port_start, port_stop, random_order, no_ping))

    @staticmethod
    def _nmap_tcp_null_scan(host, version_detect=True, port_start=None, port_stop=None, random_order=True,
                            no_ping=False):
        """ Initiates a tcp null scan

        :param host: host or list of hosts in nmaps notation
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type host: str
        """
        scan_param = " -sN"
        version_detect_param = Nmap.__get_version_detection_param(version_detect)
        port_range_param = Nmap.__get_port_range_param(port_start, port_stop)
        random_order_param = Nmap.__get_random_order_param(random_order)
        no_ping_param = Nmap.__get_no_ping_param(no_ping)
        cmd = "nmap " + host + version_detect_param + scan_param + port_range_param + random_order_param + no_ping_param
        return cmd

    @staticmethod
    def guest_nmap_tcp_fin_scan(initiator, target, version_detect=True, port_start=None, port_stop=None,
                                random_order=True,
                                no_ping=False):
        """ Initiates a tcp fin scan

        :param initiator: the that initiates the scan
        :param target: host or list of hosts
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type target: str | fortrace.core.guest.Guest | list[fortrace.core.guest.Guest] | list[str]
        :type initiator: fortrace.core.guest.Guest
        :rtype: fortrace.core.guest.ShellExecResult
        """
        target = Nmap.__format_host_list(target)
        return initiator.shellExec(
            Nmap._nmap_tcp_fin_scan(target, version_detect, port_start, port_stop, random_order, no_ping))

    @staticmethod
    def _nmap_tcp_fin_scan(host, version_detect=True, port_start=None, port_stop=None, random_order=True,
                           no_ping=False):
        """ Initiates a tcp fin scan

        :param host: host or list of hosts in nmaps notation
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type host: str
        """
        scan_param = " -sF"
        version_detect_param = Nmap.__get_version_detection_param(version_detect)
        port_range_param = Nmap.__get_port_range_param(port_start, port_stop)
        random_order_param = Nmap.__get_random_order_param(random_order)
        no_ping_param = Nmap.__get_no_ping_param(no_ping)
        cmd = "nmap " + host + version_detect_param + scan_param + port_range_param + random_order_param + no_ping_param
        return cmd

    @staticmethod
    def guest_nmap_tcp_xmas_scan(initiator, target, version_detect=True, port_start=None, port_stop=None,
                                 random_order=True,
                                 no_ping=False):
        """ Initiates a tcp xmas scan

        :param initiator: the that initiates the scan
        :param target: host or list of hosts
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type target: str | fortrace.core.guest.Guest | list[fortrace.core.guest.Guest] | list[str]
        :type initiator: fortrace.core.guest.Guest
        :rtype: fortrace.core.guest.ShellExecResult
        """
        target = Nmap.__format_host_list(target)
        return initiator.shellExec(
            Nmap._nmap_tcp_xmas_scan(target, version_detect, port_start, port_stop, random_order, no_ping))

    @staticmethod
    def _nmap_tcp_xmas_scan(host, version_detect=True, port_start=None, port_stop=None, random_order=True,
                            no_ping=False):
        """ Initiates a tcp xmas scan

        :param host: host or list of hosts in nmaps notation
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type host: str
        """
        scan_param = " -sX"
        version_detect_param = Nmap.__get_version_detection_param(version_detect)
        port_range_param = Nmap.__get_port_range_param(port_start, port_stop)
        random_order_param = Nmap.__get_random_order_param(random_order)
        no_ping_param = Nmap.__get_no_ping_param(no_ping)
        cmd = "nmap " + host + version_detect_param + scan_param + port_range_param + random_order_param + no_ping_param
        return cmd

    @staticmethod
    def guest_nmap_tcp_ack_scan(initiator, target, version_detect=True, port_start=None, port_stop=None,
                                random_order=True,
                                no_ping=False):
        """ Initiates a ack connect scan

        :param initiator: the that initiates the scan
        :param target: host or list of hosts
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type target: str | fortrace.core.guest.Guest | list[fortrace.core.guest.Guest] | list[str]
        :type initiator: fortrace.core.guest.Guest
        :rtype: fortrace.core.guest.ShellExecResult
        """
        target = Nmap.__format_host_list(target)
        return initiator.shellExec(
            Nmap._nmap_tcp_ack_scan(target, version_detect, port_start, port_stop, random_order, no_ping))

    @staticmethod
    def _nmap_tcp_ack_scan(host, version_detect=True, port_start=None, port_stop=None, random_order=True,
                           no_ping=False):
        """ Initiates a tcp ack scan

        :param host: host or list of hosts in nmaps notation
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type host: str
        """
        scan_param = " -sA"
        version_detect_param = Nmap.__get_version_detection_param(version_detect)
        port_range_param = Nmap.__get_port_range_param(port_start, port_stop)
        random_order_param = Nmap.__get_random_order_param(random_order)
        no_ping_param = Nmap.__get_no_ping_param(no_ping)
        cmd = "nmap " + host + version_detect_param + scan_param + port_range_param + random_order_param + no_ping_param
        return cmd

    @staticmethod
    def guest_nmap_tcp_window_scan(initiator, target, version_detect=True, port_start=None, port_stop=None,
                                   random_order=True, no_ping=False):
        """ Initiates a tcp window scan

        :param initiator: the that initiates the scan
        :param target: host or list of hosts
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type target: str | fortrace.core.guest.Guest | list[fortrace.core.guest.Guest] | list[str]
        :type initiator: fortrace.core.guest.Guest
        :rtype: fortrace.core.guest.ShellExecResult
        """
        target = Nmap.__format_host_list(target)
        return initiator.shellExec(
            Nmap._nmap_tcp_window_scan(target, version_detect, port_start, port_stop, random_order, no_ping))

    @staticmethod
    def _nmap_tcp_window_scan(host, version_detect=True, port_start=None, port_stop=None, random_order=True,
                              no_ping=False):
        """ Initiates a tcp window scan

        :param host: host or list of hosts in nmaps notation
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type host: str
        """
        scan_param = " -sW"
        version_detect_param = Nmap.__get_version_detection_param(version_detect)
        port_range_param = Nmap.__get_port_range_param(port_start, port_stop)
        random_order_param = Nmap.__get_random_order_param(random_order)
        no_ping_param = Nmap.__get_no_ping_param(no_ping)
        cmd = "nmap " + host + version_detect_param + scan_param + port_range_param + random_order_param + no_ping_param
        return cmd

    @staticmethod
    def guest_nmap_tcp_maimon_scan(initiator, target, version_detect=True, port_start=None, port_stop=None,
                                   random_order=True, no_ping=False):
        """ Initiates a tcp maimon scan

        :param initiator: the that initiates the scan
        :param target: host or list of hosts
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type target: str | fortrace.core.guest.Guest | list[fortrace.core.guest.Guest] | list[str]
        :type initiator: fortrace.core.guest.Guest
        :rtype: fortrace.core.guest.ShellExecResult
        """
        target = Nmap.__format_host_list(target)
        return initiator.shellExec(
            Nmap._nmap_tcp_maimon_scan(target, version_detect, port_start, port_stop, random_order, no_ping))

    @staticmethod
    def _nmap_tcp_maimon_scan(host, version_detect=True, port_start=None, port_stop=None, random_order=True,
                              no_ping=False):
        """ Initiates a tcp maimon scan

        :param host: host or list of hosts in nmaps notation
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type host: str
        """
        scan_param = " -sM"
        version_detect_param = Nmap.__get_version_detection_param(version_detect)
        port_range_param = Nmap.__get_port_range_param(port_start, port_stop)
        random_order_param = Nmap.__get_random_order_param(random_order)
        no_ping_param = Nmap.__get_no_ping_param(no_ping)
        cmd = "nmap " + host + version_detect_param + scan_param + port_range_param + random_order_param + no_ping_param
        return cmd

    @staticmethod
    def guest_nmap_udp_connect_scan(initiator, target, version_detect=True, port_start=None, port_stop=None,
                                    random_order=True, no_ping=False):
        """ Initiates a udp scan

        :param initiator: the that initiates the scan
        :param target: host or list of hosts
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type target: str | fortrace.core.guest.Guest | list[fortrace.core.guest.Guest] | list[str]
        :type initiator: fortrace.core.guest.Guest
        :rtype: fortrace.core.guest.ShellExecResult
        """
        target = Nmap.__format_host_list(target)
        return initiator.shellExec(
            Nmap._nmap_udp_scan(target, version_detect, port_start, port_stop, random_order, no_ping))

    @staticmethod
    def _nmap_udp_scan(host, version_detect=True, port_start=None, port_stop=None, random_order=True, no_ping=False):
        """ Initiates a udp scan

        :param host: host or list of hosts in nmaps notation
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type host: str
        """
        scan_param = " -sU"
        version_detect_param = Nmap.__get_version_detection_param(version_detect)
        port_range_param = Nmap.__get_port_range_param(port_start, port_stop)
        random_order_param = Nmap.__get_random_order_param(random_order)
        no_ping_param = Nmap.__get_no_ping_param(no_ping)
        cmd = "nmap " + host + version_detect_param + scan_param + port_range_param + random_order_param + no_ping_param
        return cmd

    @staticmethod
    def guest_nmap_sctp_init_scan(initiator, target, version_detect=True, port_start=None, port_stop=None,
                                  random_order=True, no_ping=False):
        """ Initiates a sctp init scan

        :param initiator: the that initiates the scan
        :param target: host or list of hosts
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type target: str | fortrace.core.guest.Guest | list[fortrace.core.guest.Guest] | list[str]
        :type initiator: fortrace.core.guest.Guest
        :rtype: fortrace.core.guest.ShellExecResult
        """
        target = Nmap.__format_host_list(target)
        return initiator.shellExec(
            Nmap._nmap_sctp_init_scan(target, version_detect, port_start, port_stop, random_order, no_ping))

    @staticmethod
    def _nmap_sctp_init_scan(host, version_detect=True, port_start=None, port_stop=None, random_order=True,
                             no_ping=False):
        """ Initiates a sctp init scan

        :param host: host or list of hosts in nmaps notation
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type host: str
        """
        scan_param = " -sY"
        version_detect_param = Nmap.__get_version_detection_param(version_detect)
        port_range_param = Nmap.__get_port_range_param(port_start, port_stop)
        random_order_param = Nmap.__get_random_order_param(random_order)
        no_ping_param = Nmap.__get_no_ping_param(no_ping)
        cmd = "nmap " + host + version_detect_param + scan_param + port_range_param + random_order_param + no_ping_param
        return cmd

    @staticmethod
    def guest_nmap_sctp_echo_scan(initiator, target, version_detect=True, port_start=None, port_stop=None,
                                  random_order=True, no_ping=False):
        """ Initiates a sctp echo scan

        :param initiator: the that initiates the scan
        :param target: host or list of hosts
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type target: str | fortrace.core.guest.Guest | list[fortrace.core.guest.Guest] | list[str]
        :type initiator: fortrace.core.guest.Guest
        :rtype: fortrace.core.guest.ShellExecResult
        """
        target = Nmap.__format_host_list(target)
        return initiator.shellExec(
            Nmap._nmap_sctp_echo_scan(target, version_detect, port_start, port_stop, random_order, no_ping))

    @staticmethod
    def _nmap_sctp_echo_scan(host, version_detect=True, port_start=None, port_stop=None, random_order=True,
                             no_ping=False):
        """ Initiates a sctp echo scan

        :param host: host or list of hosts in nmaps notation
        :param version_detect: Enable port identification and version detection (default: True)
        :param port_start: beginning port of a scan range
        :param port_stop: ending port of a port range
        :param random_order: randomize scan order (default: True)
        :param no_ping: do not ping the target at scan begin (default: False)
        :type no_ping: bool
        :type random_order: bool
        :type port_stop: None | str | int
        :type port_start: None | str | int
        :type version_detect: bool
        :type host: str
        """
        scan_param = " -sZ"
        version_detect_param = Nmap.__get_version_detection_param(version_detect)
        port_range_param = Nmap.__get_port_range_param(port_start, port_stop)
        random_order_param = Nmap.__get_random_order_param(random_order)
        no_ping_param = Nmap.__get_no_ping_param(no_ping)
        cmd = "nmap " + host + version_detect_param + scan_param + port_range_param + random_order_param + no_ping_param
        return cmd
