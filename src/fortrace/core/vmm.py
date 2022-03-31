# Copyright (C) 2013-2014 Reinhard Stampp
# Copyright (C) 2017 Sascha Kopp
# This file is part of fortrace - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.

from __future__ import absolute_import
from __future__ import print_function
import socket
import threading
import logging
import libvirt
import sys
import subprocess

import fortrace.utility.constants as constants
from fortrace.core.guest import Guest
from fortrace.utility.line import lineno
from fortrace.utility.logger_helper import create_logger


class Vmm(object):
    """fortrace virtual machine monitor, setup environment to create guests and control them."""

    def __init__(self, macsInUse, guests, logger=None, windows_template="windows-template",
                 linux_template="linux-template",
                 macosx_template="mac-template", hypervisor="kvm", hypervisor_ip="127.0.0.1", hypervisor_user="root",
                 tcpdump="/usr/sbin/tcpdump"):
        """Set default guest values (ip, mac, listen socket, templates ... ) and create a listen socket on all
        interfaces on port 11000 for the agent on the guest.

        @param macsInUse A list of already used MACs, ['52:54:00:...', ...]
        @param windows_template: name of the guest registered by libvirt; operating system Windows.
        @param linux_template:  name of the guest registered by libvirt; operating system Linux.
        @param macosx_template: name of the guest registered by libvirt; operating system Mac OS X.
        @param hypervisor: used hypervisor to manage guest's; currently implemented -> kvm
        @param hypervisor_ip: the host which the hypervisor is running on.
        @param tcpdump: path where tcpdump is installed.
        @param guests: List of all guests
        """
        try:
            self.logger = logger
            if self.logger is None:
                self.logger = create_logger('virtual machine monitor', logging.INFO)

            self.logger.info("method Vmm::__init__ repoDec19")
            self.guest_template = {
                "windows": windows_template,
                "linux": linux_template,
                "macosx": macosx_template
            }
            self.hypervisor = hypervisor
            self.hypervisor_ip = hypervisor_ip
            self.hypervisor_user = hypervisor_user
            self.tcpdump = tcpdump
            self.myGuests = []
            self.macsInUse = macsInUse
            self.allGuests = guests

        except Exception as e:
            self.logger.error("Vmm::__init__ failed:" + str(e))

    def clear(self):
        """Remove networks internet, local and all guests.

        """
        self.logger.debug("Vmm::clear ")
        for guest in self.myGuests:
            if guest.persist:
                guest.remove("keep")
            else:
                guest.remove("force")
        for _ in self.myGuests:
            self.myGuests.pop()

    def guest_dump(self, guestname, filepath, dump):
        if dump.lower() == "mem" or dump.lower() == "memory":
            subprocess.run(["virsh", "dump", guestname, filepath, "--memory-only"])
            self.logger.info("Memory dump created for " + guestname + " at " + filepath)
        else:
            self.logger.info(dump+" dump not implemented yet")
        #TODO extend function, maybe give options -> turn into all around dump function - choice of which dump in parameter?


    def create_guest(self, guest_name, platform="windows", mac1=None, mac2=None, persistent=False, boottime=None):
        """Create guest from template.

        @param guest_name: libvirt name of the guest.
        @param platform: Which platform should be created (windows, linux)
        @param mac1: MAC for local or internet network interface
        @param mac2: MAC for local or internet network interfaces
        @param persistent: Should the guest persist over sessions
        @param boottime: boot time in format "%Y-%m-%d %H:%M:%S" or None to ignore
        """
        self.logger.debug("Vmm::createGuest " + guest_name)

        # create the guest object
        try:
            guest_obj = Guest(guestname=guest_name, template=self.guest_template[platform], hypervisor=self.hypervisor,
                              hypervisor_ip=self.hypervisor_ip, hypervisor_user=self.hypervisor_user,
                              sniffer=self.tcpdump, logger=self.logger, macsInUse=self.macsInUse, mac1=mac1, mac2=mac2,
                              persistent=persistent)
            guest_obj.createAndStart(boottime=boottime)
            self.myGuests.append(guest_obj)
            self.allGuests.append(guest_obj)
        except Exception as e:
            raise Exception("Vmm::createGuest failed:" + str(e))

        # start the guest and wait for their connection as a thread

        self.logger.debug("return guest_obj")

        return guest_obj


class GuestListener(object):
    """
    Every new guest-agent will try to contact to its corresponding vmm. This will be done via network. This class will listen
    for all incoming connections on @server_port and try identify the guest behind the network-connection. Therefore the guest should
    have been send a register-message first, which contains its MAC. The MAC is known for every guest, which allows the GuestListener
    to associate the socket connection to a guest.
    """

    def __init__(self, guests, logger=None, server_port="11000"):
        """
        @param guests: List of all guests
        @param server_port: The port all guest-agents have to connect to
        """
        self.logger = logger
        if self.logger is None:
            self.logger = create_logger('virtual machine monitor', logging.INFO)

        self.guests = guests

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', int(server_port)))
        self.server_socket.listen(255)

        # define thread for the listen socket for the connection from all guests
        self.thread = threading.Thread(target=self.listener)
        self.thread.setDaemon(True)
        self.thread.start()

    def listener(self):
        """Starts a listen socket for the lifetime of the vmm object.

        This socket gets all first requests from the guests. Based on the ip, the socket will be hand over to the
        guests recvThread.
        """
        self.logger.debug("Vmm::listener ")
        try:
            while 1:
                # accept connections from outside
                client_socket, (ip_address, port) = self.server_socket.accept()
                # find the connected machine and update the state

                self.onReceive(client_socket)

        except Exception as e:
            raise Exception(lineno() + " " + "Vmm::listener failed:" + str(e))

    def onReceive(self, socket):
        """
        This tread will be opened for the guest life time.
        If a message is received, doRecvCommand will process it.

        """
        try:
            msg = ""
            # try long as there are unfinished received commands
            isRegistered = False
            while not isRegistered:

                chunk = socket.recv(1024).decode()
                if chunk == '':
                    raise RuntimeError("socket connection broken")
                # get length of the message
                #chunk = chunk.decode()
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
                        isRegistered = self.onRecvCommand(msg[8:(messagesize + 8)], socket)
                        msg = ""
                        break
                    # there are multiple commands in message
                    else:
                        command = msg[8:(messagesize + 8)]
                        msg = msg[(messagesize + 8):]

                        if len(msg) < (messagesize + 8):
                            continue

                        messagesize = int(msg[0:8], 16)
                        isRegistered = self.onRecvCommand(command, socket)
        except Exception as e:
            raise Exception(lineno() + " " + "guest::startrecv ->" + " failed:" + str(e))

    def onRecvCommand(self, command, socket):
        """This function is called from recvThread. Check for keywords from guest.
        @param command: Command string.
        @param socket: the used socket
        Commands: all implemented applications: i.e.
        - webBrowser (module)
        - mailClient
        - instantMessenger

        """
        try:
            self.logger.info("guest::doRecvCommand: " + command)
            com = command.split(" ")
            if len(com) < 2:
                return False

        except Exception as e:
            raise Exception("guest::doRecvCommand error - command: " + command + " error: " + str(e))
            ###################################################################
            # new one, dynamic loading modules
        try:
            if "register" in com[0]:
                self.onRegister(com, socket)
                return True
            else:
                self.logger.error(com[0] + " in com[0] -> not supported")
                raise Exception("guest::doRecvCommand error - command: " + command)

        except Exception as e:
            raise Exception("error guest::application: " + str(e))

    def onRegister(self, com, socket):
        # - Extract network information from command-message
        ip_internet = com[1]
        ip_local = com[2]
        mac = com[3]
        iface_internet = com[4]
        iface_local = com[5]

        guest = self.findGuestForMAC(mac)

        # - hand over socket control to guest
        try:
            self.logger.debug("start recv thread for guest:" + guest.guestname)

            guest.socket = socket
            guest.ip_local = ip_local
            guest.ip_internet = ip_internet
            guest.iface_internet = iface_internet
            guest.iface_local = iface_local

            guest.thread = threading.Thread(target=guest.recv_thread)
            guest.thread.setDaemon(True)
            guest.thread.start()

            guest.state = "connected"
        except Exception as e:
            # print "Error: unable to start thread" + str(e)
            raise Exception(str(lineno()) + " " + "Vmm::listener for " + mac + " failed:", str(e))

    def findGuestForMAC(self, mac):
        for guest in self.guests:
            if guest.mac1 == mac or guest.mac2 == mac:
                return guest
        return None
