""" This module contains methods for calling the ncrack program via the guest shellExec method.
    Remember to add ncrack to the path on windows hosts via the installer.

"""

from __future__ import absolute_import
from fortrace.core.guest import Guest
import six


class Ncrack:
    """ This class contains static methods to interface with Ncrack.

    """
    def __init__(self):
        pass

    @staticmethod
    def crack_guests(initiator, guest_or_list, service=None, ssl=False, cl_min=None, cl_max=None, at=None, cd=None,
                     cr=None, to=None, tt=None, tc=None, user_list=None, password_list=None, password_first=False,
                     user_password_pairwise=False):
        """ Attempt to crack other guests.
            If a value is not set, the defaults will be used.

        :type initiator: fortrace.core.guest.Guest
        :type guest_or_list: list[str] | list[fortrace.core.guest.Guest] | fortrace.core.guest.Guest
        :type service: None | str
        :type cl_min: None | str | int
        :type cl_max: None | str | int
        :type at: None | str | int
        :type cd: None | str | int
        :type cr: None | str | int
        :type to: None | str | int
        :type tt: None | str | int
        :type tc: None | str | int
        :type user_list: None | list[str]
        :type password_list: None | list[str]
        :type password_first: bool
        :type user_password_pairwise: bool
        :type ssl: bool
        :param initiator: the guest used to crack the other guest(s)
        :param guest_or_list: a list of hosts or guests
        :param service: the service  to cracks like ssh,ftp,etc. you can also specify a port like this 'ssh:22'
        :param cl_min: minimum number of concurrent connections
        :param cl_max: maximum number of concurrent connections
        :param at: number of attempts to try
        :param cd: delay in seconds between each connection
        :param cr: number of connection retries
        :param to: maximum time in seconds to crack a service
        :param tt: timing template to use, must a value of 0 up to 5
        :param tc: threshold for total concurrent connections
        :param user_list: a list of usernames
        :param password_list: a list of passwords
        :param password_first: try passwords first
        :param user_password_pairwise: try usernames and passwords in pairs
        :param ssl: use ssl for the connection
        :return: a delegate for the cracking result
        :rtype: fortrace.core.guest.ShellExecResult
        """
        if isinstance(guest_or_list, Guest):
            guest_or_list = [guest_or_list]
        return initiator.shellExec(
            Ncrack._service_crack(guest_or_list, service, ssl, cl_min, cl_max, at, cd, cr, to, tt, tc, user_list,
                                  password_list, password_first, user_password_pairwise))

    @staticmethod
    def _service_crack(hosts, service=None, ssl=False, cl_min=None, cl_max=None, at=None, cd=None, cr=None, to=None,
                       tt=None, tc=None, user_list=None, password_list=None, password_first=False,
                       user_password_pairwise=False):
        """ Generates a string for ncrack to crack a host or list of hosts.
            If a value is not set, the defaults will be used.

        :type hosts: list[str] | list[fortrace.core.guest.Guest]
        :type service: None | str
        :type cl_min: None | str | int
        :type cl_max: None | str | int
        :type at: None | str | int
        :type cd: None | str | int
        :type cr: None | str | int
        :type to: None | str | int
        :type tt: None | str | int
        :type tc: None | str | int
        :type user_list: None | list[str]
        :type password_list: None | list[str]
        :type password_first: bool
        :type user_password_pairwise: bool
        :type ssl: bool
        :param hosts: a list of hosts or guests
        :param service: the service  to cracks like ssh,ftp,etc. you can also specify a port like this 'ssh:22'
        :param cl_min: minimum number of concurrent connections
        :param cl_max: maximum number of concurrent connections
        :param at: number of attempts to try
        :param cd: delay in seconds between each connection
        :param cr: number of connection retries
        :param to: maximum time in seconds to crack a service
        :param tt: timing template to use, must a value of 0 up to 5
        :param tc: threshold for total concurrent connections
        :param user_list: a list of usernames
        :param password_list: a list of passwords
        :param password_first: try passwords first
        :param user_password_pairwise: try usernames and passwords in pairs
        :param ssl: use ssl for the connection
        :return: a string that contains the complete commands
        :rtype: str
        """
        if password_list is None:
            password_list = []
        if user_list is None:
            user_list = []
        host_list = list()
        cmd = "ncrack "
        if service is not None:
            svc_list = "-p " + service
        else:
            svc_list = ""
        e_opts = ""
        g_opts = ""
        t_list = ""
        u_list = ""
        p_list = ""
        for x in hosts:
            if isinstance(x, Guest):
                host_list.append(str(x.ip_internet))
            else:
                host_list.append(x)
        for x in host_list:
            t_list += x + " "
        global_opts = dict()
        if cl_min:
            global_opts["cl"] = str(cl_min)
        if cl_max:
            global_opts["CL"] = str(cl_max)
        if at:
            global_opts["at"] = str(at)
        if cd:
            global_opts["cd"] = str(cd)
        if cr:
            global_opts["cr"] = str(cr)
        if to:
            global_opts["to"] = str(to)
        for k, v in six.iteritems(global_opts):
            g_opts += k + "=" + v + ","
        g_opts = g_opts.rstrip(",")
        if ssl:
            g_opts += ",ssl"
        g_opts = g_opts.lstrip(",")
        if len(g_opts) != 0:
            g_opts = "-g " + g_opts
        for x in user_list:
            u_list += x + ","
        u_list = u_list.rstrip(",")
        for x in password_list:
            p_list += x + ","
        p_list = p_list.rstrip(",")
        if tt:
            e_opts += "-T" + str(tt)
        if tc:
            e_opts += " --connection-limit " + str(tc)
        if u_list != "":
            e_opts += " --user " + u_list
        if p_list != "":
            e_opts += " --pass " + p_list
        if password_first:
            e_opts += " --passwords-first"
        elif user_password_pairwise:
            e_opts += " --pairwise"
        cmd = cmd + t_list + e_opts + " " + svc_list + " " + g_opts
        return cmd
