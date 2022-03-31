# Copyright (C) 2013-2014 Reinhard Stampp
# This file is part of fortrace - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.

from __future__ import absolute_import
from __future__ import print_function
from six.moves import range
try:
    import logging
    import os
    import sys
    import platform
    import threading
    import subprocess
    import inspect  # for listing all method of a class
    import socket
    import struct

    # base class VMM side
    from fortrace.application.application import ApplicationVmmSide
    from fortrace.application.application import ApplicationVmmSideCommands

    # base class guest side
    from fortrace.application.application import ApplicationGuestSide
    from fortrace.application.application import ApplicationGuestSideCommands
    from fortrace.utility.line import lineno
    from fortrace.utility.recvall import recvall

    if platform.system() == "Windows":
        import pywinauto
    else:
        import dbus
        from dbus.mainloop.glib import DBusGMainLoop

except ImportError as ie:
    print(("Import error! in InstantMessenger.py " + str(ie)))
    exit(1)


###############################################################################
# Host side implementation
###############################################################################
class InstantMessengerVmmSide(ApplicationVmmSide):
    """
    This class is a remote control on the host-side to control a real <InstantMessenger>
    running on a guest.
    """

    def __init__(self, guest_obj, args):
        """Set default attribute values only.
        @param guest_obj: The guest on which this application is running. (will be inserted from guest::application())
        @param args: containing
                 logger: Logger name for logging.
        """
        try:
            super(InstantMessengerVmmSide, self).__init__(guest_obj, args)
            self.logger.info("function: InstantMessengerVmmSide::__init__")
            self.window_id = None
            self.is_connected = False

        except Exception as e:
            raise Exception(lineno() + " Error: InstantMessengerHostSide::__init__ "
                            + self.guest_obj.guestname + " " + str(e))

    def open(self):
        """Sends a command to open a InstantMessenger on the associated guest.
        """
        try:
            self.logger.info("function: InstantMessengerVmmSide::open")
            self.guest_obj.send("application " + "instantMessenger " + str(self.window_id) + " open ")  # some parameter

        except Exception as e:
            raise Exception("error InstantMessengerVmmSide::open: " + str(e))

    def close(self):
        """Sends a command to close an InstantMessenger window on the associated guest.
        """
        try:
            self.logger.info("function: InstantMessengerVmmSide::close")
            self.guest_obj.send("application " + "instantMessenger " + str(self.window_id) + " close ")
        except Exception as e:
            raise Exception("error InstantMessengerVmmSide:close()" + str(e))

    def set_config(self, jabber_id, password):
        """set_config will create the jabber profile.

        @param jabber_id: jabber id, like vm01@domain.de.
        @param password: password to xmpp account.

        @return: No return value.
        """
        try:
            self.logger.info("function: InstantMessengerVmmSide::set_config")
            # create for every parameter a length value, which will be transmitted
            self.window_id = self.guest_obj.current_window_id
            self.guest_obj.current_window_id += 1
            set_config_command = "application instantMessenger " + str(self.window_id) + " set_config " + \
                                 "%.8x" % len(jabber_id) + jabber_id + \
                                 "%.8x" % len(password) + password

            self.guest_obj.send(set_config_command)

        except Exception as e:
            raise Exception(lineno() + " error InstantMessengerVmmSide:set_config()" + str(e))

    def get_contact_list(self):
        """Get all buddys from the users contact list
        Should return a list of all contacts (buddys)
        :return:
        """
        # TODO: get all contacts
        self.logger.info("function: InstantMessengerVmmSide::get_contact_list")
        if self.is_connected:
            self.guest_obj.send("application " + "instantMessenger " + str(self.window_id) + " get_contact_list ")
        else:
            self.logger.error("function: InstantMessengerVmmSide::get_contact_list: not connected!")

    def send_msg_to(self, jabber_id, message):
        """Send an message via the xmpp.

        @param jabber_id: Full jabber id, like vm01@domain.de
        @param message: Message to send.

        @return: No return value.
        """
        try:
            self.logger.info("function: InstantMessengerVmmSide::send_msg_to")

            send_msg = "application instantMessenger " + str(self.window_id) + " send_msg_to " + \
                       "%.8x" % len(jabber_id) + jabber_id + \
                       "%.8x" % len(message) + message
            self.logger.debug(send_msg)
            self.guest_obj.send(send_msg)
            self.is_busy = True

        except Exception as e:
            raise Exception("function: InstantMessengerVmmSide::send_msg_to:" + str(e))


###############################################################################
# Commands to parse on host side
###############################################################################
class InstantMessengerVmmSideCommands(ApplicationVmmSideCommands):
    """
    Class with all commands for <InstantMessenger> which will be received from the agent on the guest.

    Static only.
    """

    @staticmethod
    def commands(guest_obj, cmd):
        # cmd[0] = win_id; cmd[1] = state
        guest_obj.logger.info("function: InstantMessengerVmmSideCommands::commands")
        module_name = "instantMessenger"
        guest_obj.logger.debug("InstantMessengerVmmSideCommands::commands: " + cmd)
        cmd = cmd.split(" ")
        try:
            if "opened" in cmd[1]:
                guest_obj.logger.debug("in opened")
                for obj in guest_obj.applicationWindow[module_name]:
                    if cmd[0] == str(obj.window_id):
                        guest_obj.logger.debug("window_id: " + str(obj.window_id) + " found!")
                        guest_obj.logger.info(module_name + " with id: " + str(obj.window_id) + " is_opened = true")
                        obj.is_opened = True
                        guest_obj.logger.debug("obj.is_opened is True now!")

            if "busy" in cmd[1]:
                guest_obj.logger.debug("in busy")
                for obj in guest_obj.applicationWindow[module_name]:
                    if cmd[0] == str(obj.window_id):
                        guest_obj.logger.info(module_name + " with id: " + str(obj.window_id) + " is_busy = true")
                        obj.is_busy = True

            if "ready" in cmd[1]:
                guest_obj.logger.debug("in ready")
                for obj in guest_obj.applicationWindow[module_name]:
                    if cmd[0] == str(obj.window_id):
                        guest_obj.logger.info(module_name + " with id: " + str(obj.window_id) + " is_busy = false")
                        obj.is_busy = False

            if "error" in cmd[1]:
                guest_obj.logger.debug("in error")
                for obj in guest_obj.applicationWindow[module_name]:
                    if cmd[0] == str(obj.window_id):
                        guest_obj.logger.info(module_name + " with id: " + str(obj.window_id) + " has_error = True")
                        obj.has_error = True

        except Exception as e:
            raise Exception(module_name + "_host_side_commands::commands " + str(e))


class InstantMessengerPlatformIndependentGuestSide(object):
    def __init__(self, agent_obj, logger, imParent):
        try:
            self.module_name = "instantMessenger"
            self.agent_object = agent_obj
            self.logger = logger
            self.jabber_id = None
            self.password = None
            self.imParent = imParent

        except Exception as e:
            raise Exception("Error in " + self.__class__.__name__ + ": " + str(e))


class InstantMessengerWindowsGuestSide(InstantMessengerPlatformIndependentGuestSide):
    def __init__(self, agent_obj, logger, imParent):
        super(InstantMessengerWindowsGuestSide, self).__init__(agent_obj, logger, imParent)
        try:
            self.pidgin_app = None
            self.is_connected = False
            self.pidgin_pluging_listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.pidgin_pluging_listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.pidgin_pluging_listen_socket.bind(('', int(11001)))
            self.pidgin_pluging_listen_socket.listen(255)
            self.plugin_socket = False
            self.thread_recv = None

        except Exception as e:
            raise Exception("Error in " + self.__class__.__name__ +
                            ": " + str(e))

    def open(self, args):
        """
        Open a <InstantMessenger> and save the InstantMessenger object with an id in a dictionary.

        @param args: Not used, only inserted for the generic function
        return:
        Send to the host in the known to be good state:
        'application <InstantMessenger> window_id open'.
        'application <InstantMessenger> window_id ready'.
        in the error state:
        'application <InstantMessenger> window_id error'.

        """
        try:
            self.logger.info("function: InstantMessengerGuestSide::open")

            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " busy")
            # open pidgin
            if os.path.exists(r"c:\Program files (x86)\Pidgin\pidgin.exe"):
                self.pidgin_app = pywinauto.application.Application().start(r"c:\Program files (x86)\Pidgin\pidgin.exe")
            elif os.path.exists(r"c:\Program Files\Pidgin\pidgin.exe"):
                self.pidgin_app = pywinauto.application.Application().start(r"c:\Program Files\Pidgin\pidgin.exe")
            else:
                self.logger.error(
                    "Pidgin is not installed into the standard path c:\Program files (x86)\Pidgin\pidgin" + ".exe or c:\Program Files\Pidgin\pidgin.exe")
                raise Exception(
                    "Pidgin is not installed into the standard path c:\Program files (x86)\Pidgin\pidgin." + "exe or c:\Program Files\Pidgin\pidgin.exe")
            #
            # Todo accept connection from pidgin plugin now.
            #
            # accept connections from outside
            self.logger.debug("pidgin started!")
            self.plugin_socket, (ip_address, port) = self.pidgin_pluging_listen_socket.accept()
            if self.plugin_socket:
                self.logger.info("Client " + str(ip_address) + ":" + str(port) + " is connected!")
                self.is_connected = True

            # start recv thread wich will receive commands from the plugin
            self.thread_recv = threading.Thread(target=self.receive_commands)
            self.thread_recv.daemon = True  # Into background
            self.logger.info("receive thread is defined")
            self.thread_recv.start()
            self.logger.info("receive thread started")

            # send some information about the instantMessenger state
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " opened")
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " ready")

        except Exception as e:
            self.logger.info(
                "InstantMessengerGuestSide::open: Close all open windows and clear the InstantMessenger list")
            subprocess.call(["taskkill", "/IM", "pidgin.exe", "/F"])
            # for obj in self.agent_object.applicationWindow[self.module_name]:
            #    self.agent_obj.applicationWindow[self.module_name].remove(obj)
            # set a crushed flag.
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " error")
            self.logger.error(
                "Error in " + self.__class__.__name__ + "::open" + ": instantMessenger is crushed: " + str(e))

    def close(self, args):
        """Close one given window by window_id

        @param args: Not used, only inserted for the generic function
        """
        self.logger.info(self.__class__.__name__ + "::close ")
        if self.plugin_socket:
            self.plugin_socket.close()
        # disconnect
        self.pidgin_app.kill_()
        self.logger.debug("kill open pidgin windows!")

    def set_config(self, args):
        """
        Generate jabber profile.

        @param jabber_id, JabberID *
        @param password, Password *
        """
        self.logger.info("function: InstantMessengerGuestSide::set_config")
        self.logger.debug("args: " + args)
        jabber_id__password = args
        self.logger.debug("jabber_id__password: " + jabber_id__password)
        ##jabber_id##
        start_pointer = 0  # start position
        end_pointer = 8  # end position to read
        print("length jabber_id_length in hex (16)")
        print(jabber_id__password[start_pointer:end_pointer])
        jabber_id_length = int(jabber_id__password[start_pointer:end_pointer], 16)
        self.logger.debug("jabber_id_length: " + str(jabber_id_length))
        start_pointer = end_pointer  # new start is old end
        end_pointer += jabber_id_length  # end set to end plus length

        jabber_id = jabber_id__password[start_pointer:end_pointer]  # begin at 8 until length +8
        self.logger.info("jabber_id " + jabber_id)

        ##password##
        start_pointer = end_pointer  # new start is old end
        end_pointer += 8  # end set to end plus 8

        password_length = int(jabber_id__password[start_pointer:end_pointer], 16)
        self.logger.debug("password_length: " + str(password_length))
        start_pointer = end_pointer  # new start is old end
        end_pointer += password_length  # end set to end plus length

        password = jabber_id__password[start_pointer:end_pointer]
        self.logger.info("password " + password)

        self.jabber_id = jabber_id
        self.password = password

        # set pidgin config
        if os.path.isfile(os.path.join(os.path.expanduser('~'), "AppData\Roaming\.purple\\accounts.xml")):
            self.logger.debug("remove account.xml")
            os.remove(os.path.join(os.path.expanduser('~'), "AppData\Roaming\.purple\\accounts.xml"))

        account_xml = open(os.path.join(os.path.expanduser('~'), "AppData\Roaming\.purple\\accounts.xml"), 'w')

        account_xml.write("<?xml version='1.0' encoding='UTF-8' ?>\n\n")
        account_xml.write("<account version='1.0'>\n")
        account_xml.write("    <account>\n")
        account_xml.write("        <protocol>prpl-jabber</protocol>\n")
        account_xml.write("        <name>" + self.jabber_id + "/</name>\n")
        account_xml.write("        <password>" + self.password + "</password>\n")
        account_xml.write("        <settings ui='gtk-gaim'>\n")
        account_xml.write("            <setting name='auto-login' type='bool'>1</setting>\n")
        account_xml.write("        </settings>\n")
        account_xml.write("        <current_error/>\n")
        account_xml.write("    </account>\n")
        account_xml.write("</account>\n")
        self.logger.debug("account.xml is written")

    def send_msg_to(self, args):
        """
        Send message to given buddy from contact list.

        @param buddy - Buddy (jabber id)
        @param message - Message to send.
        """
        try:
            self.logger.info("function: InstantMessengerGuestSide::send_msg_to")
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " busy")

            # split args into buddy and message
            buddy_message = args
            self.logger.debug("buddy_message: " + buddy_message)
            ##receiver##
            start_pointer = 0  # start position
            end_pointer = 8  # end position to read

            buddy_length = int(buddy_message[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += buddy_length  # end set to end plus length

            buddy = buddy_message[start_pointer:end_pointer]  # begin at 8 until length +8
            self.logger.debug("buddy: " + buddy)

            ##message##
            start_pointer = end_pointer  # new start is old end
            end_pointer += 8  # end set to end plus 8

            message_length = int(buddy_message[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += message_length  # end set to end plus length

            message = buddy_message[start_pointer:end_pointer]
            self.logger.debug("message: " + message)

            # Send message through pidgin via plugin connection
            if self.is_connected:
                self.logger.debug("send_msg_to " + buddy + " " + message + " to pidgin plugin!")
                # send message via plugin
                self.logger.debug("if plugin is connected")
                list_param = [buddy, message]
                self.send_to_plugin("send_msg_to", list_param)

            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " ready")

        except Exception as e:
            self.logger.error("Error by splitting string into message and jid: " + str(e))

    def get_contact_list(self, args):
        """
        Request contact list form pidgin.

        @param args: Not used, only inserted for the generic function
        """
        self.logger.info("function: InstantMessengerGuestSide::send_msg_to")
        self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " busy")

        #
        # TODO: get contact list via plugin
        #
        self.send_to_plugin("get_contact_list", [])

        self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " ready")

    def receive_commands(self):
        """Starts a listen socket for the lifetime of the pidgin object.

        This socket gets all requests from the pidgin plugin.
        Receive messages in form of:
        ---------------------------------------------------------------------------------------------
        | full   | amount | offset c | offset p1 | .. | offset pn | command | param 1 | .. | param n |
        | length | offsets|          |           | .. |           |         |         | .. |         |
        ---------------------------------------------------------------------------------------------
        Currently each length field is encoded as interger32
        full length: Describe the full length of the command
        amount offsets: Here are the amount of all offsets.
        offset x: Every begin of command or param can be accesses using an offset.
        command: the command to execute (get_contact_list, send_msg_to...).
        param x: parameter for the command.

        """
        try:
            self.logger.info("function: InstantMessengerGuestSide::receive_commands")
            while 1:
                self.logger.debug("check recv on plugin_socket!")
                full_length_binary = recvall(self.plugin_socket, 4)
                if full_length_binary is None:
                    self.logger.error("pidgin plugin socket Error!")
                    continue
                self.logger.debug("GOT command from plugin")
                print(":".join("{:02x}".format(ord(c)) for c in full_length_binary))
                full_length = struct.unpack('>I', full_length_binary)[0]
                self.logger.debug("full length: " + str(full_length))
                # counter for rest in socket
                rest_in_socket = int(full_length) - 4

                self.logger.debug("get amount offsets")
                amount_offsets_binary = recvall(self.plugin_socket, 4)
                rest_in_socket -= 4
                amount_offsets = struct.unpack('>I', amount_offsets_binary)[0]
                self.logger.debug("amount offsets: " + str(amount_offsets))
                # create data with keeps complete socket message
                data = full_length_binary + amount_offsets_binary

                offset_binary_list = []
                offset_list = []

                for i in range(amount_offsets):
                    self.logger.debug("InstantMessengerGuestSide::receive_commands: rest_in_socket: "
                                      + str(rest_in_socket))
                    self.logger.debug("InstantMessengerGuestSide::receive_commands: sock recv 4 bytes")
                    offset_binary = recvall(self.plugin_socket, 4)
                    rest_in_socket -= 4
                    self.logger.debug("InstantMessengerGuestSide::receive_commands: reduced rest_in_socket by 4: "
                                      + str(rest_in_socket))
                    offset = struct.unpack('>I', offset_binary)[0]
                    data += offset_binary

                    # add offsets to list
                    offset_binary_list.append(offset_binary)
                    offset_list.append(offset)

                self.logger.debug("InstantMessengerGuestSide::receive_commands: rest in socket: " + str(rest_in_socket))
                # get commands from socket
                command_params = recvall(self.plugin_socket, rest_in_socket)
                # create command with knowledge of all offsets
                data += command_params
                self.logger.debug("InstantMessengerGuestSide::receive_commands: offset extraction finished")
                self.logger.debug("InstantMessengerGuestSide::receive_commands: complete string from socket: " + data)
                command = ""
                param_list = []
                for i in range(amount_offsets):
                    if i == 0:
                        command = data[offset_list[i]:offset_list[i + 1] - 1]  # get command without '\0'

                    elif i == amount_offsets - 1:
                        param_list.append(data[offset_list[i]:len(data) - 1])  # get last param without '\0'

                    else:
                        param_list.append(data[offset_list[i]:offset_list[i + 1] - 1])  # get param without '\0'

                self.logger.debug("InstantMessengerGuestSide::receive_commands: extracted command: " + str(command))
                for param in param_list:
                    self.logger.debug("extraced param: " + str(param))
                self.logger.debug("parsing information from socket is finished.")
                #
                # receive_msg status buddy msg
                # example: receive event vm01@domain.de "Hi this is guest1"
                if command == "receive_msg":
                    self.logger.debug("command receive_msg received:")
                    for i in range(len(param_list)):
                        self.logger.debug("receive_msg with param:" + param_list[i])

                    self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) +
                                           " receive_msg " + param_list[0] + " " + param_list[1])

                elif command == "get_info":
                    self.logger.debug("command get_info received:")
                    for i in range(len(param_list)):
                        self.logger.debug("get_info with param:" + param_list[i])

                    self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) +
                                           " get_info " + param_list[0])

                elif command == "send_msg_to":
                    self.logger.debug("command send_msg_to received:")
                    for i in range(len(param_list)):
                        self.logger.debug("send_msg_to with param:" + param_list[i])

                    self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) +
                                           " send_msg_to " + param_list[0])

                elif command == "get_contact_list":
                    self.logger.debug("command get_contact_list received:")
                    for i in range(len(param_list)):
                        self.logger.debug("get_contact_list with param:" + param_list[i])

                    self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) +
                                           " get_contact_list " + " ".join(param_list))

                else:
                    raise Exception(lineno() + " command " + command + " not found!")

        except Exception as e:
            raise Exception(lineno() + " " + "InstantMessengerGuestSide::receive_commands failed:" + str(e))

    def send_to_plugin(self, command, list_params):
        """Send message to pidgin plugin.

        @command: i.e. send_msg_to....
        @list_params: more parameter in an list

        ---------------------------------------------------------------------------------------------
        | full   | amount | offset c | offset p1 | .. | offset pn | command | param 1 | .. | param n |
        | length | offsets|          |           | .. |           |         |         | .. |         |
        ---------------------------------------------------------------------------------------------
        Currently each length field is encoded as integer32
        full length: Describe the full length of the command
        amount offsets: Here are the amount of all offsets.
        offset x: Every begin of command or param can be accesses using an offset.
        command: the command to execute (get_contact_list, send_msg_to...); terminated with null byte.
        param x: parameter for the command; terminated with null byte.

        """

        try:
            self.logger.info("function: InstantMessengerGuestSide::send_to_plugin")

            ###
            ###  First amount offset, offset fields, command, params
            ###
            ### Amount Offset ###
            offset_amount = len(list_params) + 1  # amount offsets plus offset for command
            self.logger.debug("offset amount: " + str(offset_amount))
            msg_to_send = struct.pack('>I', offset_amount)  # Add amount Offset into string

            old_offset = offset_amount * 4 + 4 + 4  # offset * 4 Byte +  4 Byte (amount offsets) + 4 Byte (full length)
            msg_to_send += struct.pack('>I', old_offset)
            self.logger.debug("Message after adding offset amount and first offset:" + msg_to_send)
            old_offset += len(command) + 1  # len of command + null byte
            for param in list_params:
                msg_to_send += struct.pack('>I', old_offset)  # Add offset
                old_offset += len(param) + 1  # len of param plus null byte
            self.logger.debug("Message after add all offsets" + msg_to_send)
            msg_to_send = msg_to_send + command + '\0'  # Add command string plus null byte
            for param in list_params:
                msg_to_send = msg_to_send + param + '\0'  # Add param string plus null byte

            self.logger.debug("Message after adding params with \0" + msg_to_send)
            # finally add full length
            msg_to_send = struct.pack('>I', len(msg_to_send)) + msg_to_send  # Add full length

            self.logger.debug("final msg to send: " + msg_to_send)
            self.logger.debug("sent: " + str(msg_to_send))
            sent = self.plugin_socket.send(msg_to_send)
            if sent == 0:
                raise RuntimeError("socket connection broken")
        except Exception as e:
            raise Exception("InstantMessengerGuestSide::send_to_plugin failed: " + str(e))


class InstantMessengerLinuxGuestSide(InstantMessengerPlatformIndependentGuestSide):
    def __init__(self, agent_obj, logger, imParent):
        super(InstantMessengerLinuxGuestSide, self).__init__(agent_obj, logger, imParent)
        try:
            from fortrace.utility.windowManager import LinuxWindowManager
            self.window_manager = LinuxWindowManager()

        except Exception as e:
            raise Exception("Error in " + self.__class__.__name__ +
                            ": " + str(e))

    def open(self, args):
        """
        Open a <InstantMessenger> and save the InstantMessenger object with an id in a dictionary.

        @param args: Not used, only inserted for the generic function
        return:
        Send to the host in the known to be good state:
        'application <InstantMessenger> window_id open'.
        'application <InstantMessenger> window_id ready'.
        in the error state:
        'application <InstantMessenger> window_id error'.

        """
        try:
            self.logger.info("function: InstantMessengerGuestSide::open")

            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " busy")
            # open pidgin
            self.window_manager.start('pidgin', '*Buddy List*')

            self.logger.debug("pidgin started!")

            # send some information about the instantMessenger state
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " opened")
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " ready")

        except Exception as e:
            self.logger.info(
                "InstantMessengerGuestSide::open: Close all open windows and clear the InstantMessenger list")
            self.window_manager.close("*Buddy List*")
            # for obj in self.agent_object.applicationWindow[self.module_name]:
            #    self.agent_obj.applicationWindow[self.module_name].remove(obj)
            # set a crushed flag.
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " error")
            self.logger.error("Error in " + self.__class__.__name__ +
                              "::open" + ": instantMessenger is crushed: " + str(e))

    def close(self, args):
        """Close one given window by window_id

        @param args: Not used, only inserted for the generic function
        """
        self.logger.info(self.__class__.__name__ + "::close ")

        # disconnect
        os.system("pkill pidgin")
        self.logger.debug("kill open pidgin windows!")

    def set_config(self, args):
        """
        Generate jabber profile.

        @param jabber_id, JabberID *
        @param password, Password *
        """
        self.logger.info("function: InstantMessengerGuestSide::set_config")
        self.logger.debug("args: " + args)
        jabber_id__password = args
        self.logger.debug("jabber_id__password: " + jabber_id__password)
        ##jabber_id##
        start_pointer = 0  # start position
        end_pointer = 8  # end position to read
        print("length jabber_id_length in hex (16)")
        print(jabber_id__password[start_pointer:end_pointer])
        jabber_id_length = int(jabber_id__password[start_pointer:end_pointer], 16)
        self.logger.debug("jabber_id_length: " + str(jabber_id_length))
        start_pointer = end_pointer  # new start is old end
        end_pointer += jabber_id_length  # end set to end plus length

        jabber_id = jabber_id__password[start_pointer:end_pointer]  # begin at 8 until length +8
        self.logger.info("jabber_id " + jabber_id)

        ##password##
        start_pointer = end_pointer  # new start is old end
        end_pointer += 8  # end set to end plus 8

        password_length = int(jabber_id__password[start_pointer:end_pointer], 16)
        self.logger.debug("password_length: " + str(password_length))
        start_pointer = end_pointer  # new start is old end
        end_pointer += password_length  # end set to end plus length

        password = jabber_id__password[start_pointer:end_pointer]
        self.logger.info("password " + password)

        self.jabber_id = jabber_id
        self.password = password

        # set pidgin config
        pidginConfigDir = os.path.join(os.path.expanduser('~'), ".purple")
        pidginAccountConfigPath = os.path.join(pidginConfigDir, "accounts.xml")
        if os.path.isdir(pidginConfigDir):
            self.logger.debug("remove account.xml")
            os.remove(pidginAccountConfigPath)
        else:
            os.mkdir(pidginConfigDir)

        with open(pidginAccountConfigPath, 'w') as account_xml:

            account_xml.write("<?xml version='1.0' encoding='UTF-8' ?>\n\n")
            account_xml.write("<account version='1.0'>\n")
            account_xml.write("    <account>\n")
            account_xml.write("        <protocol>prpl-jabber</protocol>\n")
            account_xml.write("        <name>" + self.jabber_id + "/</name>\n")
            account_xml.write("        <password>" + self.password + "</password>\n")
            account_xml.write("        <settings ui='gtk-gaim'>\n")
            account_xml.write("            <setting name='auto-login' type='bool'>1</setting>\n")
            account_xml.write("        </settings>\n")
            account_xml.write("        <current_error/>\n")
            account_xml.write("    </account>\n")
            account_xml.write("</account>\n")

        self.logger.debug("account.xml is written")

    def send_msg_to(self, args):
        """
        Send message to given buddy from contact list.

        @param buddy - Buddy (jabber id)
        @param message - Message to send.
        """
        try:
            self.logger.info("function: InstantMessengerGuestSide::send_msg_to")
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " busy")

            # split args into buddy and message
            buddy_message = args
            self.logger.debug("buddy_message: " + buddy_message)
            ##receiver##
            start_pointer = 0  # start position
            end_pointer = 8  # end position to read

            buddy_length = int(buddy_message[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += buddy_length  # end set to end plus length

            buddy = buddy_message[start_pointer:end_pointer]  # begin at 8 until length +8
            self.logger.debug("buddy: " + buddy)

            ##message##
            start_pointer = end_pointer  # new start is old end
            end_pointer += 8  # end set to end plus 8

            message_length = int(buddy_message[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += message_length  # end set to end plus length

            message = buddy_message[start_pointer:end_pointer]
            self.logger.debug("message: " + message)

            '''
            See:
            http://stackoverflow.com/questions/1274869/im-trying-to-figure-out-how-to-use-dbus-with-pidgin
            https://developer.pidgin.im/wiki/DbusHowto#CallingPidginmethods
            '''

            MESSAGE_TYPE_IM = 1

            main_loop = DBusGMainLoop()
            session_bus = dbus.SessionBus(mainloop=main_loop)
            obj = session_bus.get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")
            purple = dbus.Interface(obj, "im.pidgin.purple.PurpleInterface")

            all_accounts = purple.PurpleAccountsGetAllActive()
            # - We only have one account -> take the first
            my_account = all_accounts[0]
            conversation = purple.PurpleConversationNew(MESSAGE_TYPE_IM, my_account, buddy)
            im = purple.PurpleConvIm(conversation)
            purple.PurpleConvImSend(im, message)

            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " ready")

        except Exception as e:
            self.logger.error("Error by splitting string into message and jid: " + str(e))

    def get_contact_list(self, args):
        """
        Request contact list form pidgin.

        @param args: Not used, only inserted for the generic function
        """
        raise NotImplemented("Not implemented for Linux")


###############################################################################
# Guest side implementation
###############################################################################
class InstantMessengerGuestSide(ApplicationGuestSide):
    """<InstantMessenger> implementation of the guest side.

    Usually Windows, Linux guest's
    class attributes
    window_id - The ID for the opened object
    """

    def __init__(self, agent_obj, logger):
        super(InstantMessengerGuestSide, self).__init__(agent_obj, logger)
        try:
            self.window_id = None
            self.agent_object = agent_obj
            self.is_connected = False
            if platform.system() == "Windows":
                self.instantMessengerApp = InstantMessengerWindowsGuestSide(agent_obj, logger, self)
            elif platform.system() == "Linux":
                self.instantMessengerApp = InstantMessengerLinuxGuestSide(agent_obj, logger, self)
            else:
                raise NotImplemented("InstantMessenger not implemented for system: " + platform.system())

        except Exception as e:
            raise Exception("Error in " + self.__class__.__name__ + ": " + str(e))

    def open(self, args):
        """
        Open a <InstantMessenger> and save the InstantMessenger object with an id in a dictionary.

        @param args: Not used, only inserted for the generic function
        return:
        Send to the host in the known to be good state:
        'application <InstantMessenger> window_id open'.
        'application <InstantMessenger> window_id ready'.
        in the error state:
        'application <InstantMessenger> window_id error'.

        """

        self.instantMessengerApp.open(args)

    def close(self, args):
        """Close one given window by window_id

        @param args: Not used, only inserted for the generic function
        """
        self.instantMessengerApp.close(args)

    def set_config(self, args):
        """
        Generate jabber profile.

        @param jabber_id, JabberID *
        @param password, Password *
        """
        self.instantMessengerApp.set_config(args)

    def send_msg_to(self, args):
        """
        Send message to given buddy from contact list.

        @param buddy - Buddy (jabber id)
        @param message - Message to send.
        """
        self.instantMessengerApp.send_msg_to(args)

    def get_contact_list(self, args):
        """
        Request contact list form pidgin.

        @param args: Not used, only inserted for the generic function
        """
        self.instantMessengerApp.get_contact_list(args)


###############################################################################
# Commands to parse on guest side
###############################################################################
class InstantMessengerGuestSideCommands(ApplicationGuestSideCommands):
    """
    Class with all commands for one application.

    call the ask method for an object. The call will be done by a thread, so if the timeout is
    reached, the open application will be closed and opened again.
    Static only.

    """

    @staticmethod
    def commands(agent_obj, obj, cmd):  # commands(obj, cmd) obj from list objlist[window_id] win id in cmd[1]?
        try:
            agent_obj.logger.info("static function InstantMessengerGuestSideCommands::commands")
            agent_obj.logger.debug("command to parse: " + cmd)
            com = cmd.split(" ")
            if len(com) > 3:
                args = " ".join(com[3:])

            module = com[0]  # inspect.stack()[-1][1].split(".")[0]
            window_id = com[1]
            method_string = com[2]

            method_found = False
            methods = inspect.getmembers(obj, predicate=inspect.ismethod)

            for method in methods:
                # method[0] will now contain the name of the method
                # method[1] will contain the value

                if method[0] == method_string:
                    # start methods as threads
                    method_found = True
                    agent_obj.logger.debug("method to call: " + method[0] + "(" + args + ")")
                    agent_obj.logger.debug("args")
                    tmp_thread = threading.Thread(target=method[1], args=(args,))
                    agent_obj.logger.debug("thread is defined")
                    tmp_thread.start()
                    agent_obj.logger.debug("thread started")
                    tmp_thread.join(60)  # Wait until the thread is completed
                    if tmp_thread.is_alive():
                        # close InstantMessenger and set obj to crashed
                        agent_obj.logger.error("thread is alive... time outed")
                        agent_obj.logger.info(
                            "InstantMessengerGuestSideCommands::commands: Close all open windows and " + "clear the InstantMessenger list")
                        subprocess.call(["taskkill", "/IM", "pidgin.exe", "/F"])
                        # for obj in agent_obj.applicationWindow[module]:
                        #    agent_obj.applicationWindow[module].remove(obj)
                        # set a crushed flag.
                        obj.is_opened = False
                        obj.is_busy = False
                        obj.has_error = True

                        agent_obj.logger.info("application " + module + " " +
                                              str(window_id) + " error")
                        agent_obj.send("application " + module + " " + str(window_id)
                                       + " error")

            if not method_found:
                raise Exception("Method " + method_string + " is not defined!")
        except Exception as e:
            raise Exception("Error in InstantMessengerGuestSideCommands::commands " + str(e))
