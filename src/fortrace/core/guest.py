# Copyright (C) 2013-2014 Reinhard Stamp
# Copyright (C) 2017 Sascha Kopp
# This file is part of fortrace - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.

# TODO base64 encoding causes trouble here - questionable if it is even needed. If it is, a way to integrate it has to be found
# TODO /2 as it severly interferes with how commands are sent, received and executed
# TODO Remote Shell Exec, set os time and Copy Directory to guest still troublesome, most functions work as intended


from __future__ import absolute_import
from __future__ import print_function
import subprocess
import os
import re
import threading
import time
import logging
import inspect  # for listing all method of a class
import base64
import sys
import re
import io
import zipfile
from os.path import join, basename

from io import StringIO
import socket

import fortrace.utility.constants as constants
from fortrace.utility.line import lineno
from fortrace.utility.logger_helper import create_logger
import fortrace.utility.clockmod as cm

try:
    #from virtinst.util import randomMAC
    from fortrace.utility.dummy_virtinst_util import randomMAC

    isnewvirtinst = False
except ImportError:
    try:
        from virtinst.deviceinterface import _random_mac as randomMAC  # was moved in newer version
        isnewvirtinst = True
    except ImportError:
        from fortrace.utility.dummy_virtinst_util import randomMAC
        isnewvirtinst = False


class newvirtinstfixup(object):
    def __init__(self, is_qemu):
        self._is_qemu = is_qemu

    def is_qemu(self):
        return self._is_qemu


class ShellExecResult(object):
    def __init__(self, id):
        self.id = id
        self.original_command = ""
        self.exit_code = 0
        self.std_out = ""
        self.std_err = ""
        self.state = "running"

    def wait(self, poll_interval=1.0):
        while self.state != "complete":
            time.sleep(poll_interval)


class Guest(object):
    """Class to create and control a guest from a template.

    """
    datetime = None
    timezone = None
    def __init__(self, guestname, template, macsInUse,
                 hypervisor="kvm", hypervisor_ip="127.0.0.1", hypervisor_user="root",
                 sniffer="/usr/sbin/tcpdump", logger=None, mac1=None, mac2=None, persistent=False):
        """Set default attribute values.

        @param guestname: name of the guest which virsh (libvirt) will use.
        @param template: the guest name which have to be used as template.
        @param macsInUse A list of already used MACs, ['52:54:00:...', ...]
        @param hypervisor: virtualization solution; only kvm is implemented.
        @param sniffer: path to tcpdump.
        @param mac1: MAC for local or internet network interface
        @param mac2: MAC for local or internet network interface
        @param persistent: Should the guest persist between sessions
        """

        try:
            self.logger = logger
            if self.logger is None:
                self.logger = create_logger('interactionManager', logging.INFO)

            self.logger.info("method guest::__init__")

            self.guestname = guestname

            # persistence
            self.persist = persistent

            # IPs will be dynamically (DHCP) and set upon registration
            self.ip_internet = None
            self.ip_local = None
            self.iface_local = None
            self.iface_internet = None

            self.template = template

            self.hypervisor_con = None
            self.hypervisor_ip = hypervisor_ip
            self.hypervisor_user = hypervisor_user
            self.hypervisor_userAtHost = hypervisor_user + "@" + hypervisor_ip
            self.sniffer = sniffer

            self.mac1 = mac1
            self.mac2 = mac2
            self.macsInUse = macsInUse

            # set hypervisor
            if hypervisor is "kvm":
                if hypervisor_ip == "127.0.0.1":
                    self.hypervisor_con = "qemu:///system"
                else:
                    self.hypervisor_con = "qemu+ssh://" + self.hypervisor_userAtHost + "/system"
            elif hypervisor is "virtualbox":
                if hypervisor_ip == "127.0.0.1":
                    self.hypervisor_con = "vbox:///session"
                else:
                    self.hypervisor_con = "vbox+ssh://" + self.hypervisor_userAtHost + "/session"
            else:
                raise Exception("unsupported hypervisor")

            # check if vm exists and has assigned mac-address
            if self.persist:
                if hypervisor_ip == "127.0.0.1":
                    try:
                        res = subprocess.check_output(["virsh", "domiflist", self.guestname])
                        m = re.findall("\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", res)
                        if len(m) < 2:
                            raise RuntimeError("Existing persistent profile does not contain at least 2 interfaces")
                        else:
                            self.mac1 = m[0]
                            self.mac2 = m[1]
                    except subprocess.CalledProcessError:
                        self.logger.info("Could not find Persistent profile, will generate a new one")
                else:
                    try:
                        res = subprocess.check_output(
                            ["ssh", self.hypervisor_userAtHost, "virsh", "domiflist", self.guestname])
                        m = re.findall("\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", res)
                        if len(m) < 2:
                            raise RuntimeError("Existing persistent profile does not contain at least 2 interfaces")
                        else:
                            self.mac1 = m[0]
                            self.mac2 = m[1]
                    except subprocess.CalledProcessError:
                        self.logger.info("Could not find Persistent profile, will generate a new one")

            if self.mac1 is None:
                self.mac1 = self.generateMAC(hypervisor)
            if self.mac2 is None:
                self.mac2 = self.generateMAC(hypervisor)

            # for use with ShellExec
            self._shell_exec_count = 0
            self._shell_exec_result = dict()

            # create a empty socket, which will be assigned from the guestHelper listensocket if the guest connects to the host
            self.socket = None
            self.state = "disconneted"

            # create thread, which will be started from the listener of the guestHelper object which this object is
            # connnected.
            self.thread = None
            # the running programms on the started guest as objects
            self.applicationWindow = {}
            self.current_window_id = 1
        except Exception as e:
            raise Exception(lineno() + " " + "guest::__init__  " + str(e))

    def generateMAC(self, hypervisor):
        if hypervisor in ["kvm", "qemu"]:
            if isnewvirtinst:
                f = newvirtinstfixup(True)  # create a dummy struct, telling it's qemu
                mac = randomMAC(f)
            else:
                mac = randomMAC(type="qemu")
            if mac in self.macsInUse:
                return self.generateMAC(hypervisor)
            else:
                self.macsInUse.append(mac)
                return mac
        raise Exception("No MAC generation alogrithm implemented for hypervisor: " + hypervisor)

    def createAndStart(self, boottime=None):
        """Create the guest using libvirt commmands. After it will be started.

        After the creation phase the starting period will be started as an own thread,
        so the program won't block by waiting until the guest is started/connected.

        @param boottime: boot time in format "%Y-%m-%d %H:%M:%S" or None to ignore
        """
        try:
            self.create()
            # Start the guest
            # start as a thread, that the programm don't have to wait for the hole starting phase
            try:
                self.logger.info("guest: " + self.guestname + " will be started")
                # define thread
                self.thread = threading.Thread(target=self.start, kwargs={"boottime": boottime})
                self.thread.setDaemon(True)
                # start thread
                self.thread.start()
            except Exception as e:
                raise Exception(lineno() + " " + "guest:createAndStart: unable to start thread" + str(e))
        except Exception as e:
            raise Exception(lineno() + " " + "guest:createAndStart: " + self.guestname + " failed:" + str(e))

    def create(self):
        """Create a guest by cloning a template. (i.e. windows-template); using virsh (libvirt).

        If another host is used as hypervisor, connect to host via qemu using ssh

        """
        local_image_file_path = None
        try:

            # virtualbox = vbox:///session
            # vbox+ssh://user@example.com/session
            if self.hypervisor_ip == "127.0.0.1":
                ############################################################################################################
                # Own machine hypervisor                                                                                   #
                ############################################################################################################

                domexists = False
                if self.persist:
                    try:
                        subprocess.check_output(["virsh", "dominfo", self.guestname])
                        domexists = True
                        self.logger.debug("Dom exists, keep it")
                    except subprocess.CalledProcessError:
                        domexists = False

                if not self.persist or (self.persist and not domexists):
                    # - Delete old disk-image
                    local_image_file_path = join(constants.FILEPATH_LOCAL_IMAGES, self.guestname + ".qcow2")
                    try:
                        # - Delete old disk-image
                        if os.path.exists(local_image_file_path):
                            self.logger.info("File already exists, delete it")
                            os.remove(local_image_file_path)
                            self.logger.info("File deleted")
                    except OSError as ose:
                        if os.path.exists(local_image_file_path):
                            raise Exception(lineno() + " Could not delete old image file: %s" % str(ose))
                        # else, reraise
                        raise

                if not self.persist or (self.persist and not domexists):
                    # - Create a backing image from the base image
                    backing_image_file = join(constants.FILEPATH_TEMPLATE_IMAGES, self.template + ".qcow2")
                    subprocess.check_output(
                        ["qemu-img", "create", "-f", "qcow2", "-b", backing_image_file, local_image_file_path])
                    print(self.guestname + " successfully created image file")

                    # create xml config for the new guest
                    try:
                        subprocess.check_output(["virt-clone", "--connect",
                                                 self.hypervisor_con,
                                                 "--preserve-data",
                                                 "--original", self.template,
                                                 "--name", self.guestname,
                                                 "--mac", self.mac1,
                                                 "--mac", self.mac2,
                                                 "--file", local_image_file_path], stderr=subprocess.STDOUT)

                        #subprocess.check_output(["define", join(constants.FILEPATH_LOCAL_IMAGES, self.guestname + ".xml")])
                        #subprocess.check_output(["rm", join(constants.FILEPATH_LOCAL_IMAGES, self.guestname + ".xml")])
                    except subprocess.CalledProcessError as grepexc:
                        raise Exception(lineno() + " " + self.guestname + " clone error: -" + grepexc.output)

                    time.sleep(3)  # give it some time to release file locks

                    print("Finished cloning process")

            ############################################################################################################
            # Other machine hypervisor                                                                                 #
            ############################################################################################################
            else:
                domexists = False
                if self.persist:
                    if subprocess.call(["ssh", self.hypervisor_userAtHost, "virsh", "dominfo", self.guestname]):
                        domexists = True
                    else:
                        domexists = False

                if not self.persist or (self.persist and not domexists):
                    # cleanup old disk-images
                    local_image_file_path = join(constants.FILEPATH_LOCAL_IMAGES, self.guestname + ".qcow2")
                    image_file_already_exists = subprocess.call(
                        ["ssh", self.hypervisor_userAtHost, "test", "-e", local_image_file_path]) == 0
                    if image_file_already_exists:
                        self.logger.error("File already exists, delete it")
                        error_on_delete = subprocess.call(
                            ["ssh", self.hypervisor_userAtHost, "rm", "-f", local_image_file_path]) != 0
                        if error_on_delete:
                            self.logger.error("failed to delete guest harddisk file")

                if not self.persist or (self.persist and not domexists):
                    # create a disk from the golden image
                    backing_image_file = join(constants.FILEPATH_TEMPLATE_IMAGES, self.template + ".qcow2")
                    if (subprocess.call(["ssh", self.hypervisor_userAtHost,
                                         "qemu-img", "create", "-f", "qcow2", "-b", backing_image_file,
                                         local_image_file_path]) != 0):
                        raise Exception(lineno() + " " + local_image_file_path +
                                        " qcow2 file already exists or template is not available")
                    else:
                        print(self.guestname + " successfully defined")

                    # create xml config for the new guest on the hypervisor_ip
                    if (subprocess.call(["virt-clone", "--connect",
                                         self.hypervisor_con,
                                         "--preserve-data",
                                         "--original", self.template,
                                         "--name", self.guestname,
                                         "--mac", self.mac1,
                                         "--mac", self.mac2,
                                         "--file", local_image_file_path]) != 0):
                        raise Exception(lineno() + " " + self.guestname + " clone error")

                    time.sleep(3)  # give it some time to release file locks

                    print("Finished cloning process")

        except Exception as e:
            raise Exception(lineno() + " " + "guest:create: " + self.guestname + " failed:" + str(e))

    def start(self, boottime=None):
        """Starts the guest by using the libvirt command 'virsh start <guestname>'.

            @param boottime: boot time in format "%Y-%m-%d %H:%M:%S" or None to ignore
        """
        try:
            if self.hypervisor_ip == "127.0.0.1":
                ############################################################################################################
                # Own machine hypervisor                                                                                   #
                ############################################################################################################

                if boottime is not None:
                    cm.setguestboottimeoffsetlocal(self.guestname, boottime)
                if subprocess.call(["virsh", "start", self.guestname]) != 0:
                    raise Exception(self.guestname + " could not be started")

                time.sleep(2)
                self.startSniffer()

            ############################################################################################################
            # Other machine hypervisor                                                                                 #
            ############################################################################################################
            else:
                if (subprocess.call(["ssh", self.hypervisor_userAtHost,
                                     "virsh", "start", self.guestname]) != 0):
                    raise Exception(self.guestname + " could not be started")

                time.sleep(2)
                self.startSniffer()

        except Exception as e:
            self.logger.error("guest:start ->" + self.guestname + " failed:" + str(e))

    def extractInternetNetworkInterface(self, remote=False):
        """Checks for the network interface to listen on, based on NETWORK_INTERNET_BRIDGE_INTERFACE entry in constants.py
        :param remote:
        :return:
        """
        bridgeInterface = constants.NETWORK_INTERNET_BRIDGE_INTERFACE
        if remote:
            cmd = ['ssh', self.hypervisor_userAtHost, 'virsh', 'domiflist', self.guestname]
        else:
            cmd = ['virsh', 'domiflist', self.guestname]

        guestInterfacesInfo = subprocess.check_output(cmd).decode()
        guestInterfacesInfo = guestInterfacesInfo.split('\n')
        for guestInterfaceInfo in guestInterfacesInfo:
            if bridgeInterface in guestInterfaceInfo:
                internetInterfaceName = guestInterfaceInfo.split()[0]
                return internetInterfaceName

    def startSniffer(self):
        """Starts tcpdump on the network interface "internet", to capture all packets created by interact with the internet.

        """
        try:
            network_dump_hypervisor_path = join(constants.FILEPATH_NETWORK_DUMPS, self.hypervisor_ip)
            network_dump_guest_path = join(network_dump_hypervisor_path, self.guestname)
            network_dump_file_path = join(network_dump_guest_path, str(int(time.time())) + ".pcap")
            print(network_dump_hypervisor_path)
            print(network_dump_guest_path)
            print((os.path.exists(network_dump_hypervisor_path)))
            print((os.path.exists(network_dump_guest_path)))

            ############################################################################################################
            # Own machine hypervisor                                                                                   #
            ############################################################################################################
            if self.hypervisor_ip == "127.0.0.1":
                internetInterface = self.extractInternetNetworkInterface()
                print(("interface: " + internetInterface))

                # setup dump directory structure
                if not os.path.exists(network_dump_hypervisor_path):
                    os.makedirs(network_dump_hypervisor_path)

                if not os.path.exists(network_dump_guest_path):
                    os.makedirs(network_dump_guest_path)

                # start tcpdump
                self.logger.info(internetInterface)
                self.logger.info(type(internetInterface))
                self.logger.info(network_dump_file_path)
                self.logger.info(type(network_dump_file_path))

                subprocess.Popen([self.sniffer, "-i", internetInterface, "-w", network_dump_file_path, "-s0"])
                self.logger.info("sniffer started")

            ############################################################################################################
            # Other machine hypervisor                                                                                 #
            ############################################################################################################
            else:
                internetInterface = self.extractInternetNetworkInterface(remote=True)

                # start tcpdump
                self.logger.info(self.hypervisor_userAtHost)
                self.logger.info(type(self.hypervisor_userAtHost))
                self.logger.info(network_dump_hypervisor_path)
                self.logger.info(type(network_dump_hypervisor_path))
                self.logger.info(network_dump_guest_path)
                self.logger.info(type(network_dump_guest_path))

                # setup dump directory structure
                if subprocess.call(['ssh', self.hypervisor_userAtHost, 'test', '-d', network_dump_hypervisor_path]):
                    subprocess.check_output(['ssh', self.hypervisor_userAtHost, 'mkdir', network_dump_hypervisor_path])

                if subprocess.call(['ssh', self.hypervisor_userAtHost, 'test', '-d', network_dump_guest_path]):
                    subprocess.check_output(['ssh', self.hypervisor_userAtHost, 'mkdir', network_dump_guest_path])

                # start tcpdump
                subprocess.call(
                    "ssh " + self.hypervisor_userAtHost + " " + self.sniffer + " -i " + internetInterface + " -w " + network_dump_file_path + " -s0 " + " &",
                    shell=True)
                self.logger.info("sniffer started")

        except Exception as e:
            self.logger.error(" guest::startSniffer ->" + self.guestname + " failed:" + str(e) + network_dump_hypervisor_path + " " + network_dump_guest_path)
            raise Exception(str(e))
    def shutdown(self, option):
        """Halt the guest; using libvirt.

        @param option: Options to shutting down the guest:
        'clean' - (default, set by remove) will halt the guest by sending a signal to shutdown the guest.
        'force' - will power off the guest (without waiting for shutting down the guest).
        """
        self.logger.debug("unsetting socket")
        self.socket = None  # this socket wont be usable anyway since we are shutting it down
        try:
            if self.hypervisor_ip == "127.0.0.1":
                ############################################################################################################
                # Own machine hypervisor                                                                                   #
                ############################################################################################################
                self.logger.info("guest::shutdown" + "(" + option + ")" + self.guestname)
                if option == "clean":
                    if subprocess.call(["virsh", "shutdown", self.guestname]) != 0:
                        raise Exception(self.guestname + " could not be shutdown")
                    time.sleep(20)
                elif option == "force":
                    if subprocess.call(["virsh", "destroy", self.guestname]) != 0:
                        raise Exception(self.guestname + " could not be destroyed")
                elif option == "keep":  # same as clean
                    if subprocess.call(["virsh", "shutdown", self.guestname]) != 0:
                        raise Exception(self.guestname + " could not be shutdown")
                    time.sleep(20)
                else:
                    raise Exception(
                        "option " + option + " is not defined! Use clean for normal shutdown or force for force off")

                if os.path.isfile(self.guestname + "_.pcap"):
                    if os.path.isfile(self.guestname + ".pcap"):
                        # merge them
                        if subprocess.call(
                                ["mergecap", "-w", "compare", self.guestname + ".pcap", self.guestname + ".pcap",
                                 self.guestname + "_.pcap"]) != 0:
                            raise Exception(self.guestname + " mergecap failed")
                        if subprocess.call(["mv", "compare", self.guestname + ".pcap", self.guestname + ".pcap"]) != 0:
                            raise Exception(self.guestname + " mv <guestname>.pcap <guestname>.pcapcompare failed")
                        # TODO: replace with os.remove() for portability/security reasons
                        if subprocess.call(["rm", self.guestname + "_.pcap"]) != 0:
                            raise Exception(self.guestname + " rm <guestname>.pcap failed")

                    else:
                        if subprocess.call(["mv", self.guestname + "_.pcap", self.guestname + ".pcap"]) != 0:
                            raise Exception(
                                lineno() + " " + self.guestname + " mv <guestname>_.pcap <guestname>.pcap failed")
                        os.popen("mv", self.guestname + "_.pcap", self.guestname + ".pcap").read()

            ############################################################################################################
            # Other machine hypervisor                                                                                 #
            ############################################################################################################
            else:
                self.logger.info("guest::shutdown" + "(" + option + ")" + self.guestname)
                if option == "clean":
                    if (subprocess.call(["ssh", self.hypervisor_userAtHost,
                                         "virsh", "shutdown", self.guestname]) != 0):
                        raise Exception(self.guestname + " could not be shutdown")
                    time.sleep(20)
                elif option == "force":
                    if (subprocess.call(["ssh", self.hypervisor_userAtHost,
                                         "virsh", "destroy", self.guestname]) != 0):
                        raise Exception(self.guestname + " could not be destroyed")
                elif option == "keep":  # same as clean
                    if (subprocess.call(["ssh", self.hypervisor_userAtHost,
                                         "virsh", "shutdown", self.guestname]) != 0):
                        raise Exception(self.guestname + " could not be shutdown")
                    time.sleep(20)
                else:
                    raise Exception(
                        "option " + option + " is not defined! Use clean for normal shutdown or force for force off")

                if os.path.isfile(self.guestname + "_.pcap"):
                    if os.path.isfile(self.guestname + ".pcap"):
                        # merge them
                        if (subprocess.call(["ssh", self.hypervisor_userAtHost, "mergecap", "-w", "compare",
                                             self.guestname + ".pcap", self.guestname + ".pcap",
                                             self.guestname + "_.pcap"]) != 0):
                            raise Exception(self.guestname + " mergecap failed")
                        if (subprocess.call(["ssh", self.hypervisor_userAtHost, "mv", "compare",
                                             self.guestname + ".pcap", self.guestname + ".pcap"]) != 0):
                            raise Exception(self.guestname + " mv <guestname>.pcap <guestname>.pcapcompare failed")
                        if subprocess.call(["ssh", self.hypervisor_userAtHost, "rm", self.guestname + "_.pcap"]) != 0:
                            raise Exception(self.guestname + " rm <guestname>.pcap failed")

                    else:
                        if (subprocess.call(["ssh", self.hypervisor_userAtHost, "mv", self.guestname + "_.pcap",
                                             self.guestname + ".pcap"]) != 0):
                            raise Exception(
                                lineno() + " " + self.guestname + " mv <guestname>_.pcap <guestname>.pcap failed")
                        os.popen("ssh " + self.hypervisor_userAtHost + " mv " + self.guestname + "_.pcap" + " " +
                                 self.guestname + ".pcap").read()

        except Exception as e:
            raise Exception(lineno() + " " + self.hypervisor_ip + " " + "guest::shutdown ->" + self.guestname +
                            " failed:" + str(e))

    def delete(self):
        """Delete this guest incl. harddisk; using libvirt commands.
        """
        try:
            if self.hypervisor_ip == "127.0.0.1":
                ############################################################################################################
                # Own machine hypervisor                                                                                   #
                ############################################################################################################
                # TODO: bad style to use os.popen, use subprocess and splitt commands and arguments
                self.logger.info(os.popen("virsh undefine " + self.guestname).read())
                self.logger.info(
                    os.popen("rm " + constants.FILEPATH_TEMPLATE_IMAGES + self.guestname + ".qcow2").read())
            ############################################################################################################
            # Other machine hypervisor                                                                                 #
            ############################################################################################################
            else:
                # TODO: bad style to use os.popen, use subprocess and splitt commands and arguments
                self.logger.info(os.popen("ssh " + self.hypervisor_userAtHost + "virsh undefine "
                                          + self.guestname).read())
                self.logger.info(os.popen("ssh " + self.hypervisor_userAtHost + "rm " +
                                          constants.FILEPATH_TEMPLATE_IMAGES + self.guestname + ".qcow2").read())

        except Exception as e:
            raise Exception(lineno() + " " + self.hypervisor_ip + " " + "guest:delete ->" + self.guestname +
                            " failed:" + str(e))

    def remove(self, option="clean"):
        """Disconnect, halt, and delete the guest.
        @param option: Options to remove:
        'clean' - (default) will halt the guest by sending a signal to shutdown the guest.
        'force' - will power off the guest (without waiting for shutting down the guest).
        'keep' - just disconnect the sniffer and poweroff
        """
        try:
            self.logger.info("guest::remove(" + option + ")" + self.guestname)

            self.logger.debug("disconnect")
            self.disconnect()
            self.logger.debug("disconnected")
            self.logger.debug("shutdown")
            self.shutdown(option)
            if option != "keep":
                self.logger.debug("delete")
                self.delete()
            else:
                self.logger.debug("keeping all files on disk!")
        except Exception as e:
            raise Exception(lineno() + " " + self.hypervisor_ip + " " + "guest::remove ->" + self.guestname +
                            " failed:" + str(e))

    def disconnect(self):
        """Close the existing socket.

        """
        try:
            self.logger.info("guest::disconnect " + self.guestname)
            self.socket.close()
            self.socket = None
            self.state = "disconneted"
        except Exception as e:
            raise Exception(
                lineno() + " " + self.hypervisor_ip + " " + "guest::disconnect ->" + self.guestname + " failed:" + str(
                    e))

    def send(self, msg):
        """Send all type of requests to the guest. Key value based communication.

        """
        try:
            self.logger.info("guest::send: " + msg)
            if self.state == "connected":

                message_size = "%.8x" % len(msg)
                buffer = message_size + msg
                sent = self.socket.sendall(buffer.encode())
                self.logger.debug("sent: " + buffer)
                if sent == 0:
                    raise RuntimeError("socket connection broken")
                    # data = self.s.recv(1024)
        except Exception as e:
            self.logger.error("send Error" + str(e) + " Socket set to disconnected")
            self.state = "disconnected"

    def doRecvCommand(self, command):
        """This function is called from recvThread. Check for keywords from guest.
        @param command: Command string.
        Commands: all implemented applications: i.e.
        - webBrowser (module)
        - mailClient
        - instantMessenger

        """
        try:
            self.logger.info("guest::doRecvCommand: " + command)
            com = command.split(" ")
            if len(com) < 2:
                return

        except Exception as e:
            raise Exception("guest::doRecvCommand error - command: " + command + " error: " + str(e))
            ###################################################################
            # new one, dynamic loading modules
        try:
            # supported commands to receive are:
            # - application
            # - info
            if "application" in com[0]:
                self.logger.debug("application in com[0]")
                name = "fortrace.application." + com[1]
                self.logger.debug("module name is: " + name)
                mod = __import__(name, fromlist=[''])
                self.logger.debug("module is imported!")
                class_obj = getattr(mod, com[1][0].upper() + com[1][1:] + 'VmmSideCommands')
                self.logger.debug("class_obj from " + com[1] + "VmmSideCommands created!")
                class_obj.commands(self, " ".join(com[2:]))
                self.logger.debug("static method commands from " + com[1] + "VmmSideCommands called!")

                # mod = __import__(name, fromlist=[com[1]+'VmmSideCommands'])
                # mod.commands(self, " ".join(com[2:]))

            elif "shellExecComplete" in com[0]:
                shell_exec_id = int(com[1])
                self.logger.debug("A shellExec command completed: %s",
                                  self._shell_exec_result[shell_exec_id].original_command)
                exit_code = int(com[2])
 #               std_out = base64.b64decode(com[3])
#                std_err = base64.b64decode(com[4])
                std_out = com[3]
                std_err = com[4]
                self._shell_exec_result[shell_exec_id].exit_code = exit_code
                self._shell_exec_result[shell_exec_id].std_out = std_out
                self._shell_exec_result[shell_exec_id].std_err = std_err
                self._shell_exec_result[shell_exec_id].state = "complete"

            elif "info" in com[0]:
                self.logger.debug("info in com[0]")
                print("not implemented now!")

            elif "time" in com[0]:
                # Set recieved guest timestamp
                self.logger.debug("timestamp in com[0]")
                self.datetime = "{0} {1}".format(com[1],com[2])
                self.logger.info("guest time is {0}".format(self.datetime))

            elif "tzone" in com[0]:
                self.logger.debug("timezone in com[0]")
                self.timezone = base64.b64decode(com[1])
                self.logger.debug("timezone is {0}".format(self.timezone))
            else:
                self.logger.error(com[0] + " in com[0] -> not supported")
                raise Exception("guest::doRecvCommand error - command: " + command)

        except Exception as e:
            raise Exception("error guest::application: " + str(e))

    def application(self, module, args):
        """Return application object i.e. webBrowser or mailClient... etc.

        Note: the convention from webBrowser to WebBrowser will be made by this function.
        This method loads dynamic the requested application type and return a object of it.
        :return: application object
        """
        try:
            # load dynamic the requested application

            args['logger'] = self.logger
            name = "fortrace.application." + module
            self.logger.debug("module name is: " + name)
            # module[0].upper() + module[1:] + 'VmmSide'
            mod = __import__(name, fromlist=[''])
            class_obj = getattr(mod, module[0].upper() + module[1:] + 'VmmSide')
            obj = class_obj(self, args)
            print("object created")
            if module in list(self.applicationWindow.keys()):
                self.applicationWindow[module].append(obj)
            else:
                self.applicationWindow[module] = []
                self.applicationWindow[module].append(obj)

            return obj
        except Exception as e:
            raise Exception("error guest::application: " + str(e))

    def recv_thread(self):
        """
        This tread will be opened for the guest life time.
        If a message is received, doRecvCommand will process it.

        """
        try:
            msg = ""
            # try long as there are unfinished received commands
            while 1:
                #self.logger.debug("socket: " + str(self.socket))
                if self.socket is None:  # if socket is down do nothing at all
                    time.sleep(1)
                    continue
                chunk = self.socket.recv(1024).decode()
                if chunk == '':
                    #raise RuntimeError("socket connection broken")
                    break
                # get length of the message
                msg = msg + chunk
                # if msg do not contain the message length
                if len(msg) < 8:
                    print("half command")
                    continue

                messagesize = int(msg[0:8], 16)

                if len(msg) < (messagesize + 8):
                    print("half command with messagesize")
                    continue

                # get the commands out of the message
                while len(msg) >= (messagesize + 8):
                    # if the command fit into message, return the command list commands
                    if len(msg) == messagesize + 8:
                        self.doRecvCommand(msg[8:(messagesize + 8)])
                        msg = ""
                        break
                    # there are multiple commands in message
                    else:
                        command = msg[8:(messagesize + 8)]
                        msg = msg[(messagesize + 8):]

                        if len(msg) < (messagesize + 8):
                            continue

                        messagesize = int(msg[0:8], 16)
                        self.doRecvCommand(command)
        except socket.error as e:
            if e.errno == 104:  # connection reset, probably guest shutdown, ignore to prevent crash
                self.state = 'disconnected'
            else:
                raise Exception(lineno() + " " + self.hypervisor_ip + " " + "guest::startrecv ->" + self.guestname +
                                " failed:" + str(e) + " code: " + str(e.errno))
        except Exception as e:
            raise Exception(lineno() + " " + self.hypervisor_ip + " " + "guest::startrecv ->" + self.guestname +
                            " failed:" + str(e))

    def insertCD(self, iso_path):
        """
        Attaches a CD-ROM into the CD drive using an iso-image file.
        """
        defaultCDROMDevice = "sdb"

        try:
            ############################################################################################################
            # Own machine hypervisor                                                                                   #
            ############################################################################################################
            if self.hypervisor_ip == "127.0.0.1":
                if subprocess.call(
                        ['virsh', 'change-media', self.guestname, defaultCDROMDevice, '--update', iso_path]) != 0:
                    raise Exception(
                        lineno() + " Could not insert CD image from iso file " + iso_path + " into cdrom device " + defaultCDROMDevice)

            ############################################################################################################
            # Other machine hypervisor                                                                                 #
            ############################################################################################################
            else:
                if subprocess.call(
                        ["ssh", self.hypervisor_userAtHost, 'virsh', 'change-media', self.guestname, defaultCDROMDevice,
                         '--update', iso_path]) != 0:
                    raise Exception(
                        lineno() + " Could not insert CD image from iso file " + iso_path + " into cdrom device " + defaultCDROMDevice)

            print("Successfully inserted CD")

        except Exception as e:
            raise Exception(lineno() + " " + "guest:insertCD: " + self.guestname + " failed:" + str(e))

    def shellExec(self, cmd, path_prefix="#unset", std_in=None):
        """ Calls a blocking command on the VM.
            Warning don't use this with interactive programs that expect user interactions like gui-applications
            as this will block the receive loop.
            Msg will look like this ["shellExec"][id][path_prefix][std_in].
            Blocks are separated by spaces and parameters after id are base64 encoded.

        :type path_prefix: str
        :type cmd: str
        :type std_in: None | str
        :param cmd: a command including parameters to execute
        :param path_prefix: this will be prepended to the command, will only be used on Windows VMs
        :param std_in: used for interactive user input
        :rtype: ShellExecResult
        :return A ShellExecResult-object to query for exit-code, stdout, etc.
        """
        self._shell_exec_count += 1
        self._shell_exec_result[self._shell_exec_count] = ShellExecResult(
            self._shell_exec_count)  # generate a new delegate for result
        self._shell_exec_result[self._shell_exec_count].original_command = cmd
        cmd = cmd.encode()
        path_prefix = path_prefix.encode()
        msg = "shellExec " + str(self._shell_exec_count)
        msg = msg.encode()
        space = " ".encode()
        msg += space + base64.b64encode(cmd)  # use base64 encoding to prevent fragmentation
        msg += space + base64.b64encode(path_prefix)
        if std_in is not None:
            msg += space
            msg += base64.b64encode(std_in)
        msg = msg.decode()
        self.send(msg)
        return self._shell_exec_result[self._shell_exec_count]

    def killShellExec(self, shellexecresult):
        """ Send SIGINT to the associated ShellExecResult process.

        :type shellexecresult ShellExecResult
        :param shellexecresult: A ShellExecResult object
        """
        msg = "killShellExec " + str(shellexecresult.id)
        self.send(msg)

    def remoteShellExec(self, executable, target_dir="#unset", std_in=None):
        """ Run an executable from the local file system on the guest.

        :param executable: path to an executable
        :param target_dir: where to place the executable, leave empty for agents working directory
        :param std_in: used for interactive user input
        :rtype: ShellExecResult | None
        :return A ShellExecResult-object to query for exit-code, stdout, etc. or None if file could not be accessed
        """
        try:
            with open(executable, 'rb') as f:
                file = f.read()
                #file = base64.b64encode(file)  # make file sane for transport
        except IOError:
            self.logger.error("File not accessible: " + executable)
            return
        self._shell_exec_count += 1
        self._shell_exec_result[self._shell_exec_count] = ShellExecResult(
            self._shell_exec_count)  # generate a new delegate for result
        self._shell_exec_result[self._shell_exec_count].original_command = executable
        msg = "remoteShellExec " + str(self._shell_exec_count)
        #msg += " " + base64.b64encode(basename(executable))  # may contain white-spaces
        msg += " " + executable
        msg += " "
        msg += file
        msg += " "
        #msg += base64.b64encode(target_dir)  # same here
        msg += target_dir
        if std_in is not None:
            msg += " "
            #msg += base64.b64encode(std_in)
            msg += std_in
        self.send(msg)
        return self._shell_exec_result[self._shell_exec_count]

    def CopyFileToGuest(self, filename, target_dir):
        """ Copies a file to the guests filesystem.
            Path needs to exist!

        :param filename:
        :param target_dir:
        """
        target_dir = target_dir.encode()
        try:
            with open(filename, 'rb') as f:
                file = f.read()
                #file = base64.b64encode(file)  # make file sane for transport
        except IOError:
            self.logger.error("File not accessible: " + filename)
            return
        msg = "file filecopy "
        msg = msg.encode()
        msg += base64.b64encode(target_dir)
        #msg += target_dir
        space = " ".encode()
        msg += space
        #file = file.decode()
        msg += file
        msg = msg.decode()
        print(msg)
        self.send(msg)

    @staticmethod
    def _zipdir(root_dir, zf):
        """ Zips the content of a directory including subfolders
            originally from: shutil.py
        :type root_dir: str
        :type zf: zipfile.ZipFile
        :param root_dir: path to zip
        :param zf: handle for a ZipFile
        :return:
        """
        save_cwd = os.getcwd()
        os.chdir(root_dir)
        base_dir = os.curdir
        path = os.path.normpath(base_dir)
        print(type(path))
        print(type(zf))
        print(type(root_dir))
        if path != os.curdir:
            zf.write(path, path)
        for dirpath, dirnames, filenames in os.walk(base_dir):
            for name in sorted(dirnames):
                path = os.path.normpath(os.path.join(dirpath, name))
                zf.write(path, path)
            for name in filenames:
                path = os.path.normpath(os.path.join(dirpath, name))
                if os.path.isfile(path):
                    zf.write(path, path)
        os.chdir(save_cwd)

    def CopyDirectoryToGuest(self, directory, target_dir):
        """ Copies a directories contents recursively to a target directory.
            This creates the directory if it did not exist before.

        :param directory: The directory to clone
        :param target_dir: The target directory
        """
        zbuf = io.BytesIO()
        z = zipfile.ZipFile(zbuf, 'w')
        Guest._zipdir(directory, z)
        z.close()
        target_dir = target_dir.encode()
        msg = "file dircopy"
        msg = msg.encode()
        space = " ".encode()
        msg += space + base64.b64encode(target_dir) + space + base64.b64encode(zbuf.getvalue())
        msg = msg.decode()
        self.send(msg)
        zbuf.close()

    def guestCreateDirectory(self, target_dir):
        """ Create a directory on the guest.

        :param target_dir: The directory to create
        """
        target_dir = target_dir.encode()
        msg = "file dircreate"
        space = " ".encode()
        msg = msg.encode()
        msg += space + base64.b64encode(target_dir)
        #msg += target_dir
        msg = msg.decode()
        self.send(msg)

    def guestTouchFile(self, target_file):
        """ Same as the posix touch command.

        :param target_file: The file to touch
        """
        target_file = target_file.encode()
        msg = "file touch"
        msg = msg.encode()
        space = " ".encode()
        msg += space + base64.b64encode(target_file)
        #msg += target_file
        msg = msg.decode()
        self.send(msg)

    def guestCopy(self, guest_source_path, guest_target_path):
        """ Copies file on guest.

        :param guest_source_path: source path on guest
        :param guest_target_path: target path on guest
        """
        guest_source_path = guest_source_path.encode()
        guest_target_path = guest_target_path.encode()
        msg = "file guestcopy"
        msg = msg.encode()
        space = " ".encode()
        msg += space + base64.b64encode(guest_source_path) + space + base64.b64encode(guest_target_path)
        #msg += guest_source_path + " " + guest_target_path
        msg = msg.decode()
        self.send(msg)

   # def smbCopy(self, guest_source_path, smb_target_path, user, passw):
     #   """ Copies file from guest to smb share.
       #         :param guest_source_path: source path on guest
         #       :param smb_target_path: target path on smb
           #     :param user: smb user
             #   :param passw: pass
        #"""
        #msg = "file smbcopy "
        #msg += base64.b64encode(guest_source_path) + " " + base64.b64encode(smb_target_path) + " " + base64.b64encode(user) + " " + base64.b64encode(passw)
        #self.send(msg)

    def guestMove(self, guest_source_path, guest_target_path):
        """ Moves file on guest.

        :param guest_source_path: source path on guest
        :param guest_target_path: target path on guest
        """
        guest_source_path = guest_source_path.encode()
        guest_target_path = guest_target_path.encode()
        msg = "file guestmove"
        msg = msg.encode()
        space = " ".encode()
        msg += space + base64.b64encode(guest_source_path) + space + base64.b64encode(guest_target_path)
        #msg += guest_source_path + " " + guest_target_path
        msg = msg.decode()
        self.send(msg)

    def guestDelete(self, guest_target_path):
        """ Deletes file or directory on guest.

        :param guest_target_path:
        """
        guest_target_path = guest_target_path.encode()
        msg = "file guestdelete"
        msg = msg.encode()
        space = " ".encode()
        msg += space + base64.b64encode(guest_target_path)
        #msg += guest_target_path
        msg = msg.decode()
        self.send(msg)

    def guestTime(self, param=""):
        """
        Queries current guest date and time.
        """
        self.logger.debug("query guest time")
        msg = "guesttime "
        self.send(msg)

    def guestTimezone(self, param=""):
        """
        Queries current guest timezone
        """
        self.logger.debug("query guest timezone")
        msg = "guesttzone "
        self.send(msg)

    def guestChangeWorkingPath(self, path):
        """ Changes the working directory of guest agent.

        :param path: new path
        """
        path = path.encode()
        msg = "file guestchdir"
        msg = msg.encode()
        space = " ".encode()
        msg += space + base64.b64encode(path)
        #msg += path
        msg = msg.decode()
        self.send(msg)

    def setOSTime(self, ptime, local_time=True):
        """ Sets the time on the guests OS
            Notice for Windows guests: Call this function 2 times if new time has a different daylight saving offset
            You may need admin rights to do this.

        :type local_time: bool
        :type ptime: str
        :param ptime: A time in format "%Y-%m-%d %H:%M:%S"
        :param local_time: Is this local time
        """

        ptime = ptime.encode()
        msg = "setOSTime"
        msg = msg.encode()
        space = " ".encode()
        msg += space + base64.b64encode(ptime) + space
        #msg = "setOSTime " + ptime + " "
        if local_time:
            msg += "True".encode()
        else:
            msg += "False".encode()
        msg = msg.decode()
        self.send(msg)

    def runElevated(self, command):
        '''
        This function calls the runElevated method on the guest system to run a shell/bash command with Administrator rights
        :param command: shell/bash command that needs admin rights
        :return:
        '''
        self.logger.debug("guest runElevated")
        command = command.encode()
        msg = "runElevated"
        msg = msg.encode()
        space = " ".encode()
        msg += space + base64.b64encode(command)
        #msg = "runElevated " + command
        msg = msg.decode()
        self.send(msg)

    def cleanUp(self, mode="auto"):
        """
        Call the clenaup method on the guest system to reduce artefacts.
        This function deletes the fortrace folder for all user but the current one, the fortrace site-packages for all users
        but the current one and Prefetch files pointing at the fortrace framework. For best results use mode "manual" and
        follow the instructions provided in /install_tools/uninstall_fortrace_manual_text to remove the traces for the
        active user.
        @param mode: cleanup mode, use "auto" for automatic shutdown and "manual" for manual shutdown
        """
        self.logger.debug("guest cleanUp")
        mode = mode.encode()
        space = " ".encode()
        msg = "cleanUp"
        msg = msg.encode()
        msg += space + base64.b64encode(mode)
        # msg = "cleanUp " + command
        msg = msg.decode()
        self.send(msg)

    def initClean(self, command=""):
        """
        Call the initClean() method on the guest system to reduce artifacts at the beginning of a scenario or after deleting the default fortrace user.
        This function clears all Event Log entries and the created Prefetch files
        @param command: additional parameter, not in use by now
        """
        self.logger.debug("guest initClean")
        msg = "initClean "
        self.send(msg)

    def wait_for_dhcp(self, poll_interval=1.0):
        """ Wait till dhcp server delivered ip address.

        :type poll_interval: float
        :param poll_interval: Interval to wait for retry
        """
        while True:
            if self.ip_internet is not None:
                if self.ip_local is not None:
                    break
            time.sleep(poll_interval)

    def isGuestPowered(self):
        """ Query Hypervisor if guest is powered on

        :rtype: bool | None
        :return: Return True or False, will return None if call failed
        """
        try:
            if self.hypervisor_ip == "127.0.0.1":
                res = subprocess.check_output("LANG=en_US.UTF-8 virsh dominfo " + self.guestname + " | grep State", shell=True)
            else:
                res = subprocess.check_output("ssh" + self.hypervisor_userAtHost + "LANG=en_US.UTF-8 virsh dominfo " + self.guestname + " | grep State") # todo: test
            if "shut off" in str(res):
                return False
            else:
                return True
        except subprocess.CalledProcessError:
            self.logger.error("Could not get domain info for \"" + self.guestname + "\", does it exist?")
            return None

    def waitTillAgentIsConnected(self):
        while self.state != "connected":
            self.logger.debug(".")
            time.sleep(1)
        self.logger.debug(self.guestname + " is connected!")
