""" Helper-functions for modifying libvirt clocks.

"""

from __future__ import absolute_import
import datetime as dt
import subprocess as sp
import xml.etree.ElementTree as et



def gettimeoffsetinsecondslocal():
    """ Gets the time difference between localtime and utc.

    :rtype int
    :return: Time difference
    """
    ut = dt.datetime.utcnow()
    lt = dt.datetime.now()
    d = lt - ut
    return d.seconds


def ishardwareclockutcsystemdlocal():
    """ Checks if hardware clock is utc.
        Needs systemd.

    :rtype: bool
    :return: Is hardware clock utc
    """
    try:
        s = sp.check_output("LANG=en_US.UTF-8 timedatectl --no-pager | grep TZ", shell=True) # use systemds timedatectl to check
        s = str(s)
    except sp.CalledProcessError:
        raise RuntimeError("Systemd seems not to be installed on this system, functionality not available")
    if "yes" in s:
        return False
    return True


def ishardwareclockutchwclocklocal():
    """ Checks if hardware clock is utc.
        Needs root or suid hwclock.

    :rtype: bool
    :return: Is hardware clock utc
    """
    try:
        s = sp.check_output("LANG=en_US.UTF-8 hwclock --debug | grep \"Hardware clock is on\"", shell=True) # use hwclock to check
    except sp.CalledProcessError:
        raise RuntimeError("Call failed, are you root or is hwclock suid flagged")
    if "local time" in s:
        return False
    return False


def ishardwareclockutclocal():
    """ Checks if hardwareclock is utc.
        Will try systemd timedatectl first.
        If that fails it will try hwclock which needs root rights.
        :rtype: bool
        :return: Is hardware clock utc
    """
    try:
        return ishardwareclockutcsystemdlocal()
    except RuntimeError:
        return ishardwareclockutchwclocklocal()


def setguestboottimeoffsetlocal(guestname, boottime, guestclocktypeisutc=False):
    """ Sets a guest clock to variable with timeshift to simulate new boot time.
        Note: Libvirts clock defaults to utc and might bug to utc so this needs additional adjustments, which might
              make this a bit non precise.

    :type guestname: str
    :type boottime: str
    :param guestname: guests name
    :param boottime: boot time in format "%Y-%m-%d %H:%M:%S"
    :param guestclocktypeisutc: False for windows
    """
    to = 0
    if ishardwareclockutclocal() == False:
        to = gettimeoffsetinsecondslocal()
    tn = dt.datetime.now()
    #bt = dt.datetime.strptime(boottime.decode(), "%Y-%m-%d %H:%M:%S")
    bt = dt.datetime.strptime(boottime, "%Y-%m-%d %H:%M:%S") #.decode()
    td = bt - tn  # difference in seconds to
    tds = int(td.total_seconds() + to)  # this is float round it to int
    try:
        s = sp.check_output("virsh dumpxml " + guestname, shell=True) # todo: remove and test without shell argument, security reason
        with open("/tmp/" + guestname + "-saved.xml", mode='wb') as f:  # make a backup copy for restoring later
           f.write(s)
           f.flush()
    except sp.CalledProcessError:
        raise RuntimeError("Failed to save old domain config")
    x = et.fromstring(s)
    c = x.find("./clock")  # todo: check if element exists, error checking
    c.set('offset', "variable")
    if guestclocktypeisutc:
        c.set('basis', "utc")
    else:
        c.set('basis', "localtime")
    c.set('adjustment', str(tds))
    xt = et.ElementTree(x)
    xt.write("/tmp/mod.xml", encoding="UTF-8")
    try:
        s = sp.check_output("virsh define /tmp/mod.xml", shell=True) # todo: remove and test without shell argument, security reason
    except sp.CalledProcessError:
        raise RuntimeError("Failed to load edited domain config")


