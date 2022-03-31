# Copyright (C) 2013-2014 Reinhard Stampp
# This file is part of fortrace - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.

from __future__ import absolute_import
from __future__ import print_function
try:
    import logging
    import os
    import shutil  # to delete folders with content
    import sys
    import platform
    import threading
    import subprocess
    import time
    import inspect  # for listing all method of a class

    # base class VMM side
    from fortrace.application.application import ApplicationVmmSide
    from fortrace.application.application import ApplicationVmmSideCommands

    # base class guest side
    from fortrace.application.application import ApplicationGuestSide
    from fortrace.application.application import ApplicationGuestSideCommands
    from fortrace.utility.line import lineno
    from fortrace.utility.io import parse_attachment_string

    if platform.system() == "Windows":
        import pywinauto
        from fortrace.utility.SendKeys import SendKeys

except ImportError as ie:
    print(("Import error! in MailClient.py " + str(ie)))
    exit(1)


###############################################################################
# Host side implementation
###############################################################################
class MailClientVmmSide(ApplicationVmmSide):
    """
    This class is a remote control on the host-side to control a real <MailClient>
    running on a guest.
    """

    def __init__(self, guest_obj, args):
        """Set default attribute values only.
        @param guest_obj: The guest on which this application is running. (will be inserted from guest::application())
        @param args: containing
                 logger: Logger name for logging.
        """
        try:
            super(MailClientVmmSide, self).__init__(guest_obj, args)
            self.logger.info("function: MailClientVmmSide::__init__")
            self.window_id = None
            # self.mail_client = "thunderbird"

        except Exception as e:
            raise Exception(lineno() + " Error: MailClientHostSide::__init__ "
                            + self.guest_obj.guestname + " " + str(e))

    def open(self):
        """Sends a command to open a MailClient on the associated guest.
        """
        try:
            self.logger.info("function: MailClientVmmSide::open")
            self.guest_obj.send("application " + "mailClient " + str(self.window_id) + " open ")  # some parameter
        except Exception as e:
            raise Exception("error MailClientVmmSide::open: " + str(e))

    def close(self):
        """Sends a command to close a MailClient on the associated guest.
        """
        try:
            self.logger.info("function: MailClientVmmSide::close")
            self.guest_obj.send("application " + "mailClient " + str(self.window_id) + " close ")
        except Exception as e:
            raise Exception("error MailClientVmmSide:close()" + str(e))

    def set_config(self, full_name, email, password, username, imap_server, smtp_server, server_mode="imap"):
        """set_config will create the Thunderbird profile with the given parameters.

        @param full_name: Name of the User to the email address.
        @param email: email address.
        @param password: password to the email address.
        @param username: username to login.
        @param imap_server: imap server to connect.
        @param smtp_server: smtp server to send emails.
        @param server_mode: imap or pop3

        @return: No return value.
        """
        try:
            self.logger.info("function: MailClientVmmSide::set_config")
            # create for every parameter a length value, which will be transmitted
            self.window_id = self.guest_obj.current_window_id
            self.guest_obj.current_window_id += 1

            set_config_command = "application mailClient " + str(self.window_id) + " set_config " + \
                                 "%.8x" % len(server_mode) + server_mode + \
                                 "%.8x" % len(full_name) + full_name + \
                                 "%.8x" % len(email) + email + \
                                 "%.8x" % len(password) + password + \
                                 "%.8x" % len(username) + username + \
                                 "%.8x" % len(imap_server) + imap_server + \
                                 "%.8x" % len(smtp_server) + smtp_server

            self.guest_obj.send(set_config_command)

        except Exception as e:
            raise Exception(lineno() + " error MailClientVmmSide:setConfig()" + str(e))

    def send_mail(self, receiver, subject, message, attachment_path_list=None):
        """Send an email via the mailClient.

        @param receiver: Receiver for this email.
        @param subject: Subject for this email.
        @param message: Message for this email.
        @param attachment_path_list: (Optional) list of paths for files to attach to the mail.

        @return: No return value.
        """
        attachment_string = parse_attachment_string(attachment_path_list)

        try:
            # incluce length before the values reciever, subject and message
            send_mail_command = "application mailClient " + str(self.window_id) + " send_mail " + \
                                "%.8x" % len(receiver) + receiver + \
                                "%.8x" % len(subject) + subject + \
                                "%.8x" % len(message) + message
            if attachment_string is not None:
                send_mail_command += "%.8x" % len(attachment_string) + attachment_string

            self.is_busy = True
            self.guest_obj.send(send_mail_command)
        except Exception as e:
            raise Exception("error mailer::sendMail: " + str(e))


###############################################################################
# Commands to parse on host side
###############################################################################
class MailClientVmmSideCommands(ApplicationVmmSideCommands):
    """
    Class with all commands for MailClient which will be received from the agent on the guest.

    Static only.
    """

    @staticmethod
    def commands(guest_obj, cmd):
        # cmd[0] = win_id; cmd[1] = state
        guest_obj.logger.info("function: MailClientVmmSideCommands::commands")
        module_name = "mailClient"
        guest_obj.logger.debug("MailClientVmmSideCommands::commands: " + cmd)
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


###############################################################################
# Guest side implementation
###############################################################################
class MailClientPlatformIndependentGuestSide(object):
    """<MailClient> implementation of the guest side.

    Usually Windows, Linux guest's
    class attributes
    window_id - The ID for the opened object
    """

    def __init__(self, agent_obj, logger, imParent):
        try:
            self.module_name = "mailClient"
            self.timeout = None
            self.window_is_crushed = None
            self.agent_object = agent_obj
            # settings for the thunderbird profile
            self.full_name = None
            self.email = None
            self.password = None
            self.username = None
            self.thunderbird_app = None
            self.thunderbird_window = None
            self.logger = logger
            self.agent_object = agent_obj
            self.imParent = imParent
            self.server_mode = "imap"

        except Exception as e:
            raise Exception("Error in " + self.__class__.__name__ +
                            ": " + str(e))


class MailClientWindowsGuestSide(MailClientPlatformIndependentGuestSide):
    """<MailClient> implementation of the guest side.

    Usually Windows, Linux guest's
    class attributes
    window_id - The ID for the opened object
    """

    def __init__(self, agent_obj, logger, imParent):
        super(MailClientWindowsGuestSide, self).__init__(agent_obj, logger, imParent)

    def open(self, args):
        """
        Open a <MailClient> and save the MailClient object with an id in a dictionary.
        Set page load timeout to 30 seconds.

        return:
        Send to the host in the known to be good state:
            'application <MailClient> window_id open'.
            'application <MailClient> window_id ready'.
        in the error state:
            'application <MailClient> window_id error'.
        additionally the 'window_is_crushed' attribute is set; so the next
        call will open a new window.

        """
        try:
            self.logger.info("function: MailClientGuestSide::open")

            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " busy")

            # check if profile exists
            if os.path.join(os.path.expanduser('~'), "AppData\Roaming\Thunderbird\profiles.ini"):
                self.logger.debug("Profile exists")
            else:
                raise Exception("MailClientGuestSide::open: no Thunderbird profile are deposited")

            # check for thunderbird exe and start it.
            if os.path.exists(r"c:\Program files (x86)\Mozilla Thunderbird\Thunderbird.exe"):
                self.thunderbird_app = pywinauto.application.Application().start(
                    r"c:\Program files (x86)\Mozilla " + r"Thunderbird\Thunderbird.exe")
            elif os.path.exists(r"c:\Program Files\Mozilla Thunderbird\Thunderbird.exe"):
                self.thunderbird_app = pywinauto.application.Application().start(
                    r"c:\Program Files\Mozilla " + r"Thunderbird\Thunderbird.exe")
            else:
                self.logger.error(
                    "Thundebird is not installed into the standard path c:\Program files (x86)\Mozilla " + "Thunderbird\Thunderbird.exe or c:\Program Files\Mozilla " + "Thunderbird\Thunderbird.exe")
                raise Exception(
                    "Thundebird is not installed into the standard path c:\Program files (x86)\Mozilla " + "Thunderbird\Thunderbird.exe or c:\Program Files\Mozilla Thunderbird\Thunderbird.exe")
            # wait for thunderbird is opened
            time.sleep(4)
            self.logger.debug("Window should now be opened")

        except Exception as e:
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " error")
            self.logger.error("MailClientGuestSide::open: " + str(e))
            return

        try:  # check for thunderbird window
            # mozilla is one of those applications that use existing windows
            # if they exist (at least on my machine!)
            # so if we cannot find any window for that process
            #  - find the actual process
            #  - connect to it
            if self.thunderbird_app.windows_():
                self.thunderbird_window = self.thunderbird_app.window_(title_re=".*Mozilla Thunderbird")

            else:
                self.thunderbird_app = pywinauto.application.Application().connect_(title_re=".*Mozilla Thunderbird")
                self.thunderbird_window = self.thunderbird_app.window_(title_re=".*Mozilla Thunderbird")

        except Exception as e:
            self.logger.error("MailClientGuestSide::open No window named '.*Mozilla Thunderbird'")
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " error")
            return

            # some information about the mailClient state
        time.sleep(9)
        try:
            # app = application.Application()
            # password_window =
            password_window = self.thunderbird_app.window_(title_re=".*Server")
            self.logger.debug("password window = ")
            self.logger.debug(password_window)
            self.logger.debug("password window appeared")
            time.sleep(1)
            self.logger.debug("self.password: " + str(self.password))
            send_key_string = self.password + "{TAB}" + "{SPACE}" + "{ENTER}"
            password_window.TypeKeys(send_key_string)
            self.logger.debug("the password should now be inserted")
            time.sleep(2)
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " opened")
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " ready")
            self.window_is_crushed = False
        except Exception as e:
            self.logger.error("MailClientGuestSide::open: " + str(e))
            self.logger.error("no password window appeard")
            # send some information about the instantMessenger state

        except Exception as e:
            self.logger.info("MailClientGuestSide::open: Close all open windows and clear the MailClientGuestSide list")
            subprocess.call(["taskkill", "/IM", "thunderbird.exe", "/F"])
            # for obj in self.agent_object.applicationWindow[self.module_name]:
            #    self.agent_obj.applicationWindow[self.module_name].remove(obj)
            # set a crushed flag.
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " error")
            self.logger.error("Error in " + self.__class__.__name__ + "::open" + ": mailClient is crushed: " + str(e))

    def close(self, args):
        """Close one given window by window_id"""
        self.logger.info(self.__class__.__name__ +
                         "::close ")
        # close all windows
        self.thunderbird_app.kill_()
        self.logger.debug("kill open thunderbird windows!")

    def set_config(self, args):
        try:
            self.logger.info("function: MailClientGuestSide::set_config ")
            self.logger.debug("args: " + args)

            ###########################
            rest_of_cmd = args
            # The parameter full_name, email, password, username, imap_server, smtp_server are extended at length

            # First 8 character describes length of full_name

            ##full_name##
            start_pointer = 0  # start position
            end_pointer = 8  # end position to read
            self.logger.debug("setConfig:: next step is to read the length of full_name")
            self.logger.debug("complete incoming string command: " + rest_of_cmd)
            self.logger.debug("string value to convert " + rest_of_cmd[start_pointer:end_pointer])
            full_name_length = int(rest_of_cmd[start_pointer:end_pointer], 16)
            self.logger.debug("setConfig: netxtstep ist calculate the pointers")
            start_pointer = end_pointer  # new start is old end
            end_pointer += full_name_length  # end set to end plus length
            self.logger.debug("setConfig next: get full_name")
            full_name = rest_of_cmd[start_pointer:end_pointer]  # begin at 8 until length +8
            self.logger.info("full_name " + full_name)

            ##server mode##
            start_pointer = end_pointer  # new start is old end
            end_pointer += 8  # end set to end plus 8
            self.logger.debug("string value to convert " + rest_of_cmd[start_pointer:end_pointer])
            server_mode_length = int(rest_of_cmd[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += server_mode_length  # end set to end plus length

            server_mode = rest_of_cmd[start_pointer:end_pointer]
            self.logger.debug("server_mode " + server_mode)

            ##email##
            start_pointer = end_pointer  # new start is old end
            end_pointer += 8  # end set to end plus 8
            self.logger.debug("string value to convert " + rest_of_cmd[start_pointer:end_pointer])
            email_length = int(rest_of_cmd[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += email_length  # end set to end plus length

            email = rest_of_cmd[start_pointer:end_pointer]
            self.logger.debug("email " + email)

            ##password##
            start_pointer = end_pointer  # new start is old end
            end_pointer += 8  # end set to end plus 8

            self.logger.debug("string value to convert " + rest_of_cmd[start_pointer:end_pointer])
            password_length = int(rest_of_cmd[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += password_length  # end set to end plus length

            password = rest_of_cmd[start_pointer:end_pointer]
            self.logger.debug("password " + password)

            ##username##
            start_pointer = end_pointer  # new start is old end
            end_pointer += 8  # end set to end plus 8

            self.logger.debug("string value to convert " + rest_of_cmd[start_pointer:end_pointer])
            username_length = int(rest_of_cmd[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += username_length  # end set to end plus length

            username = rest_of_cmd[start_pointer:end_pointer]
            self.logger.debug("username " + username)

            ##imap_server##
            start_pointer = end_pointer  # new start is old end
            end_pointer += 8  # end set to end plus 8

            self.logger.debug("string value to convert " + rest_of_cmd[start_pointer:end_pointer])
            imap_server_lenght = int(rest_of_cmd[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += imap_server_lenght  # end set to end plus length

            imap_server = rest_of_cmd[start_pointer:end_pointer]
            self.logger.debug("imap_server " + imap_server)

            ##smtp_server##
            start_pointer = end_pointer  # new start is old end
            end_pointer += 8  # end set to end plus 8

            self.logger.debug("string value to convert " + rest_of_cmd[start_pointer:end_pointer])
            smtp_server_lenght = int(rest_of_cmd[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += smtp_server_lenght  # end set to end plus length

            smtp_server = rest_of_cmd[start_pointer:end_pointer]
            self.logger.debug("smtp_server " + smtp_server)

            ######################

            # imap_server="imap.googlemail.com"
            # smtp_server="smtp.googlemail.com"
            imapport = "3"
            smtpport = "3"

            self.full_name = full_name
            self.email = email
            self.password = password
            self.logger.debug("print out password " + str(password))

            self.username = username
            # self.window_id = winId

            if os.path.isdir(os.path.join(os.path.expanduser('~'), "AppData\Roaming\Thunderbird\Profiles")):
                shutil.rmtree(os.path.join(os.path.expanduser('~'), "AppData\Roaming\Thunderbird\Profiles"))
                os.remove(os.path.join(os.path.expanduser('~'), "AppData\Roaming\Thunderbird\profiles.ini"))
            # create folder profiles
            os.makedirs(os.path.join(os.path.expanduser('~'), "AppData\Roaming\Thunderbird\Profiles"))
            # create profiles.ini

            profiles_file = open(os.path.join(os.path.expanduser('~'), "AppData\Roaming\Thunderbird\profiles.ini"), 'w')
            random_filename = "2rwu5nti"  # 8 chars
            profiles_file.write('[General]\n')
            profiles_file.write("StartWithLastProfile=1\n")
            profiles_file.write("[Profile0]\n")
            profiles_file.write("Name=default\n")
            profiles_file.write("IsRelative=1\n")
            profiles_file.write("Path=Profiles/" + random_filename + ".default\n")

            profiles_file.close()
            # create randomfile.default folder
            os.makedirs(os.path.join(os.path.expanduser('~'),
                                     "AppData\Roaming\Thunderbird\Profiles\\" + random_filename + ".default"))

            pref_file = open(os.path.join(os.path.expanduser('~'),
                                          "AppData\Roaming\Thunderbird\Profiles\\" + random_filename + ".default" + "\prefs.js"),
                             'w')

            pref_file.write('# Mozilla User Preferences\n\n')
            pref_file.write('/* Do not edit this file.\n')
            pref_file.write(' *\n')
            pref_file.write(' * If you make changes to this file while the application is running,\n')
            pref_file.write(' * the changes will be overwritten when the application exits.\n')
            pref_file.write(' *\n')
            pref_file.write(' * To make a manual change to preferences, you can visit the URL about:config\n')
            pref_file.write(' */\n')

            # calendar, guid seems to be random, TODO: randomize guid
            pref_file.write('user_pref("calendar.integration.notify", false);\n')
            pref_file.write('user_pref("calendar.list.sortOrder", "71636afc-63cc-41b3-aea6-06f9fff5bb29");\n')
            pref_file.write('user_pref("calendar.registry.71636afc-63cc-41b3-aea6-06f9fff5bb29.calendar-main-default", true);\n')
            pref_file.write('user_pref("calendar.registry.71636afc-63cc-41b3-aea6-06f9fff5bb29.calendar-main-in-composite", true);\n')
            pref_file.write('user_pref("calendar.registry.71636afc-63cc-41b3-aea6-06f9fff5bb29.name", "Home");\n')
            pref_file.write('user_pref("calendar.registry.71636afc-63cc-41b3-aea6-06f9fff5bb29.type", "storage");\n')
            pref_file.write('user_pref("calendar.registry.71636afc-63cc-41b3-aea6-06f9fff5bb29.uri", "moz-storage-calendar://");\n')
            pref_file.write('user_pref("calendar.timezone.local", "Europe/Berlin");\n')
            pref_file.write('user_pref("calendar.ui.version", 3);\n')

            pref_file.write('user_pref("mail.account.account1.identities", "id1");\n')
            pref_file.write('user_pref("mail.account.account1.server", "server1");\n')
            pref_file.write('user_pref("mail.accountmanager.accounts", "account1");\n')
            pref_file.write('user_pref("mail.accountmanager.defaultaccount", "account1");\n')
            pref_file.write('user_pref("mail.append_preconfig_smtpservers.version", 2);\n')
            pref_file.write('user_pref("mail.identity.id1.full_name", "' + self.full_name + '");\n')
            pref_file.write('user_pref("mail.identity.id1.reply_on_top", 1);\n')
            pref_file.write('user_pref("mail.identity.id1.smtpServer", "smtp1");\n')
            pref_file.write('user_pref("mail.identity.id1.useremail", "' + self.email + '");\n')
            pref_file.write('user_pref("mail.identity.id1.valid", true);\n')
            pref_file.write(
                'user_pref("mail.root.imap", "%HOMEPATH%\\\\AppData\\\\Roaming\\\\Thunderbird\\\\' + 'Profiles\\\\2rwu5nti.default\\\\ImapMail");\n')
            pref_file.write('user_pref("mail.root.imap-rel", "[ProfD]ImapMail");\n')
            pref_file.write(
                'user_pref("mail.root.none", "%HOMEPATH%\\\\AppData\\\\Roaming\\\\Thunderbird\\\\' + 'Profiles\\\\2rwu5nti.default\\\\Mail");\n')
            pref_file.write('user_pref("mail.root.none-rel", "[ProfD]Mail");\n')
            pref_file.write('user_pref("mail.server.server1.check_new_mail", true);\n')
            pref_file.write(
                'user_pref("mail.server.server1.directory", "%HOMEPATH%\\\\AppData\\\\Roaming\\\\' + 'Thunderbird\\\\Profiles\\\\2rwu5nti.default\\\\ImapMail\\\\' + imap_server + '");\n')
            pref_file.write('user_pref("mail.server.server1.directory-rel", "[ProfD]ImapMail/' + imap_server + '");\n')
            pref_file.write('user_pref("mail.server.server1.hostname", "' + imap_server + '");\n')
            pref_file.write('user_pref("mail.server.server1.login_at_startup", true);\n')
            pref_file.write('user_pref("mail.server.server1.name", "' + self.email + '");\n')
            if server_mode == "imap":
                pref_file.write('user_pref("mail.server.server1.port", 993);\n')
            if server_mode == "pop3":
                pref_file.write('user_pref("mail.server.server1.port", 110);\n')
            pref_file.write('user_pref("mail.server.server1.socketType", 3);\n')
            if server_mode == "imap":
                pref_file.write('user_pref("mail.server.server1.type", "imap");\n')
            if server_mode == "pop3":
                pref_file.write('user_pref("mail.server.server1.type", "pop3");\n')
            pref_file.write('user_pref("mail.server.server1.userName", "' + self.email + '");\n')
            pref_file.write('user_pref("mail.smtpserver.smtp1.authMethod", 3);\n')
            pref_file.write('user_pref("mail.smtpserver.smtp1.description", "Google Mail");\n')
            pref_file.write('user_pref("mail.smtpserver.smtp1.hostname", "' + smtp_server + '");\n')
            pref_file.write('user_pref("mail.smtpserver.smtp1.port", 465);\n')
            pref_file.write('user_pref("mail.smtpserver.smtp1.try_ssl", 3);\n')
            pref_file.write('user_pref("mail.smtpserver.smtp1.username", "' + self.email + '");\n')
            pref_file.write('user_pref("mail.smtpservers", "smtp1");\n')
            pref_file.write('user_pref("mail.winsearch.firstRunDone", true);\n')
            pref_file.close()
            # save password in mailclient
            time.sleep(1)  # time to write the file
            self.logger.info("Writing config file is finished!")
        except Exception as e:
            self.logger.error("MailClientGuestSide::set_config: " + str(e))

    def send_mail(self, args):
        """
        Send email to receiver.

        @param receiver - Email address.
        @param subject - Subject of the email.
        @param message - Message of the email.
        @param attachment_path_list: (Optional) list of paths for files to attach to the mail.

        """
        try:
            self.logger.info("function: MailClientGuestSide::send_mail")

            ################
            receiver_subject_message = args

            ##receiver##
            start_pointer = 0  # start position
            end_pointer = 8  # end position to read

            recv_length = int(receiver_subject_message[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += recv_length  # end set to end plus length

            receiver = receiver_subject_message[start_pointer:end_pointer]  # begin at 8 until length +8
            self.logger.debug("receiver " + receiver)

            ##subject##
            start_pointer = end_pointer  # new start is old end
            end_pointer += 8  # end set to end plus 8

            subject_length = int(receiver_subject_message[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += subject_length  # end set to end plus length

            subject = receiver_subject_message[start_pointer:end_pointer]
            self.logger.debug("subject " + subject)

            ##message##
            start_pointer = end_pointer  # new start is old end
            end_pointer += 8  # end set to end plus 8

            message_length = int(receiver_subject_message[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += message_length  # end set to end plus length

            message = receiver_subject_message[start_pointer:end_pointer]
            self.logger.debug("message " + message)

            attachment_string = None
            # check if attachment_string is added
            if end_pointer < len(receiver_subject_message):
                start_pointer = end_pointer  # new start is old end
                end_pointer += 8  # end set to end plus 8

                attachment_path_length = int(receiver_subject_message[start_pointer:end_pointer], 16)

                start_pointer = end_pointer  # new start is old end
                end_pointer += attachment_path_length  # end set to end plus length

                attachment_string = receiver_subject_message[start_pointer:end_pointer]
                self.logger.debug("attachment_string " + attachment_string)

            ################
            # to = receiver # search if to, cc, bcc is in reciever and split
            self.logger.debug("open email window")
            if attachment_string is None:
                self.thunderbird_app = pywinauto.application.Application().start(
                    'c:\Program files (x86)\Mozilla Thunderbird\Thunderbird.exe -compose "to=%s,subject=%s,body=%s"'% (
                        receiver, subject, message))
            else:
                self.thunderbird_app = pywinauto.application.Application().start(
                    'c:\Program files (x86)\Mozilla Thunderbird\Thunderbird.exe ' +
                    '-compose "to=%s,subject=%s,body=%s,attachment=%s"' % (receiver, subject, message, attachment_string))

            self.logger.debug("email window is here")
            time.sleep(10)
            if self.thunderbird_app.windows_():
                self.logger.debug("if case")
                self.thunderbird_window = self.thunderbird_app.window_(title_re=".*%s" % subject)
            else:
                self.logger.debug("else case")
                app = pywinauto.application.Application().connect_(title_re=".*%s" % subject)
                self.thunderbird_window = app.window_(title_re=".*%s" % subject)

            self.thunderbird_window.TypeKeys("^{ENTER}")
        except Exception as e:
            self.logger.error(lineno() + str(e))

        self.logger.debug("send up the message")

        try:
            time.sleep(3)
            self.logger.debug("Press enter to send the message")
            SendKeys("{ENTER}")
            pass

        except Exception as e:
            self.logger.error(lineno() + "mailClient::sendMail: " + str(e))

        self.logger.info("wait 10 second for the smtp pasword window to appear")
        time.sleep(2)
        # Enter password into window
        try:  # check for thunderbird window
            # mozilla is one of those applications that use existing windows
            # if they exist (at least on my machine!)
            # so if we cannot find any window for that process
            #  - find the actual process
            #  - connect to it
            if self.thunderbird_app.windows_():
                self.thunderbird_window = self.thunderbird_app.window_(title_re=".*Mozilla Thunderbird")

            else:
                self.thunderbird_app = pywinauto.application.Application().connect_(title_re=".*Mozilla Thunderbird")
                self.thunderbird_window = self.thunderbird_app.window_(title_re=".*Mozilla Thunderbird")

        except Exception as e:
            self.logger.error("mailClient::open No window named '.*Mozilla Thunderbird'")
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " error")
            return

        # if window appears
        try:
            password_window = self.thunderbird_app.window_(title_re=".*Server")
            self.logger.info("password window appeared")
            self.logger.info("password window = ")
            self.logger.info(password_window)
            time.sleep(1)
            print("self password")
            print(self.password)
            sendkeystring = self.password + "{TAB}" + "{SPACE}" + "{ENTER}"
            password_window.TypeKeys(sendkeystring)
            self.logger.info("the password should now be inserted")
            time.sleep(2)
        # else
        except Exception as e:
            self.logger.info("MailClientGuestSide::send_mail: " + str(e))
            self.logger.info("no password window appeard")

        # after all is finished
        self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " ready")


class MailClientLinuxGuestSide(MailClientPlatformIndependentGuestSide):
    """<MailClient> implementation of the guest side.

    Usually Windows, Linux guest's
    class attributes
    window_id - The ID for the opened object
    """

    def __init__(self, agent_obj, logger, imParent):
        super(MailClientLinuxGuestSide, self).__init__(agent_obj, logger, imParent)
        try:
            from fortrace.utility.windowManager import LinuxWindowManager
            self.window_manager = LinuxWindowManager()

        except Exception as e:
            raise Exception("Error in " + self.__class__.__name__ +
                            ": " + str(e))

    def open(self, args):
        """
        Open a <MailClient> and save the MailClient object with an id in a dictionary.
        Set page load timeout to 30 seconds.

        return:
        Send to the host in the known to be good state:
            'application <MailClient> window_id open'.
            'application <MailClient> window_id ready'.
        in the error state:
            'application <MailClient> window_id error'.
        additionally the 'window_is_crushed' attribute is set; so the next
        call will open a new window.

        """

        try:
            self.logger.info("function: MailClientGuestSide::open")

            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " busy")

            # check if profile exists
            tbProfilePath = os.path.join(os.path.expanduser('~'), ".thunderbird/profiles.ini")
            if os.path.exists(tbProfilePath):
                self.logger.debug("Profile exists")
            else:
                raise Exception("MailClientGuestSide::open: no Thunderbird profile are deposited")

            # check for thunderbird exe and start it.
            self.window_manager.start('thunderbird', '*Thunderbird')

            self.logger.debug("Window should now be opened")

        except Exception as e:
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " error")
            self.logger.error("MailClientGuestSide::open: " + str(e))
            return

        try:
            self.window_manager.waitforwindow('Mail Server Password Required')
            isFocused = self.window_manager.focus('Mail Server Password Required')
            self.logger.debug("Bringing password window to front")
            self.logger.debug("password window appeared: %s" % isFocused)

            self.logger.debug("self.password: " + str(self.password))

            self.window_manager.text('*Mail*', 'txt0', self.password)
            self.window_manager.check('*Mail*', 'chkUsePasswordManagertorememberthispassword')
            self.window_manager.click('*Mail*', 'btnOK')

            self.logger.debug("the password should now be inserted")

            time.sleep(2)
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " opened")
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " ready")
            self.window_is_crushed = False
        except Exception as e:
            self.logger.error("MailClientGuestSide::open: " + str(e))
            self.logger.error("no password window appeard")
            # send some information about the instantMessenger state

        # - TODO: 2 catch-blocks for the same exception?
        except Exception as e:
            self.logger.info("MailClientGuestSide::open: Close all open windows and clear the MailClientGuestSide list")
            self.window_manager.close('*Thunderbird*')
            # for obj in self.agent_object.applicationWindow[self.module_name]:
            #    self.agent_obj.applicationWindow[self.module_name].remove(obj)
            # set a crushed flag.
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " error")
            self.logger.error("Error in " + self.__class__.__name__ + "::open" + ": mailClient is crushed: " + str(e))

    def close(self, args):
        """Close one given window by window_id"""
        self.logger.info(self.__class__.__name__ + "::close ")
        # close all windows
        self.window_manager.close('*Thunderbird*')
        self.logger.debug("kill open thunderbird windows!")

    def set_config(self, args):
        try:
            self.logger.info("function: MailClientGuestSide::set_config ")
            self.logger.debug("args: " + args)

            ###########################
            rest_of_cmd = args
            # The parameter full_name, email, password, username, imap_server, smtp_server are extended at length

            # First 8 character describes length of full_name

            ##full_name##
            start_pointer = 0  # start position
            end_pointer = 8  # end position to read
            self.logger.debug("setConfig:: next step is to read the length of full_name")
            self.logger.debug("complete incoming string command: " + rest_of_cmd)
            self.logger.debug("string value to convert " + rest_of_cmd[start_pointer:end_pointer])
            full_name_length = int(rest_of_cmd[start_pointer:end_pointer], 16)
            self.logger.debug("setConfig: netxtstep ist calculate the pointers")
            start_pointer = end_pointer  # new start is old end
            end_pointer += full_name_length  # end set to end plus length
            self.logger.debug("setConfig next: get full_name")
            full_name = rest_of_cmd[start_pointer:end_pointer]  # begin at 8 until length +8
            self.logger.info("full_name " + full_name)

            ##server mode##
            start_pointer = end_pointer  # new start is old end
            end_pointer += 8  # end set to end plus 8
            self.logger.debug("string value to convert " + rest_of_cmd[start_pointer:end_pointer])
            server_mode_length = int(rest_of_cmd[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += server_mode_length  # end set to end plus length

            server_mode = rest_of_cmd[start_pointer:end_pointer]
            self.logger.debug("server_mode " + server_mode)

            ##email##
            start_pointer = end_pointer  # new start is old end
            end_pointer += 8  # end set to end plus 8
            self.logger.debug("string value to convert " + rest_of_cmd[start_pointer:end_pointer])
            email_length = int(rest_of_cmd[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += email_length  # end set to end plus length

            email = rest_of_cmd[start_pointer:end_pointer]
            self.logger.debug("email " + email)

            ##password##
            start_pointer = end_pointer  # new start is old end
            end_pointer += 8  # end set to end plus 8

            self.logger.debug("string value to convert " + rest_of_cmd[start_pointer:end_pointer])
            password_length = int(rest_of_cmd[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += password_length  # end set to end plus length

            password = rest_of_cmd[start_pointer:end_pointer]
            self.logger.debug("password " + password)

            ##username##
            start_pointer = end_pointer  # new start is old end
            end_pointer += 8  # end set to end plus 8

            self.logger.debug("string value to convert " + rest_of_cmd[start_pointer:end_pointer])
            username_length = int(rest_of_cmd[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += username_length  # end set to end plus length

            username = rest_of_cmd[start_pointer:end_pointer]
            self.logger.debug("username " + username)

            ##imap_server##
            start_pointer = end_pointer  # new start is old end
            end_pointer += 8  # end set to end plus 8

            self.logger.debug("string value to convert " + rest_of_cmd[start_pointer:end_pointer])
            imap_server_lenght = int(rest_of_cmd[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += imap_server_lenght  # end set to end plus length

            imap_server = rest_of_cmd[start_pointer:end_pointer]
            self.logger.debug("imap_server " + imap_server)

            ##smtp_server##
            start_pointer = end_pointer  # new start is old end
            end_pointer += 8  # end set to end plus 8

            self.logger.debug("string value to convert " + rest_of_cmd[start_pointer:end_pointer])
            smtp_server_lenght = int(rest_of_cmd[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += smtp_server_lenght  # end set to end plus length

            smtp_server = rest_of_cmd[start_pointer:end_pointer]
            self.logger.debug("smtp_server " + smtp_server)

            ######################

            # imap_server="imap.googlemail.com"
            # smtp_server="smtp.googlemail.com"
            imapport = "3"
            smtpport = "3"

            self.full_name = full_name
            self.email = email
            self.password = password
            self.logger.debug("print out password " + str(password))

            self.username = username
            # self.window_id = winId

            # - Reset Thunderbirds folder
            random_filename = '2rwu5nti'  # 8 chars
            profileName = random_filename + '.default'

            tbFolder = os.path.join(os.path.expanduser('~'), '.thunderbird')
            tbProfileIni = os.path.join(tbFolder, 'profiles.ini')
            tbProfileFolder = os.path.join(tbFolder, profileName)
            tbPrefJs = os.path.join(tbProfileFolder, 'prefs.js')
            tbImapMailFolder = os.path.join(tbProfileFolder, 'ImapMail')
            tbMailFolder = os.path.join(tbProfileFolder, 'Mail')
            tbImapMailServerFolder = os.path.join(tbImapMailFolder, imap_server)

            if os.path.isdir(tbFolder):
                shutil.rmtree(tbFolder)
            os.makedirs(tbFolder)

            # - Create profiles.ini
            with open(tbProfileIni, 'w') as profiles_file:
                profiles_file.write('[General]\n')
                profiles_file.write('StartWithLastProfile=1\n')
                profiles_file.write('[Profile0]\n')
                profiles_file.write('Name=default\n')
                profiles_file.write('IsRelative=1\n')
                profiles_file.write('Path=' + profileName + '\n')

            # - Create profile folder
            os.makedirs(tbProfileFolder)

            with open(tbPrefJs, 'w') as pref_file:

                pref_file.write('# Mozilla User Preferences\n\n')
                pref_file.write('/* Do not edit this file.\n')
                pref_file.write(' *\n')
                pref_file.write(' * If you make changes to this file while the application is running,\n')
                pref_file.write(' * the changes will be overwritten when the application exits.\n')
                pref_file.write(' *\n')
                pref_file.write(' * To make a manual change to preferences, you can visit the URL about:config\n')
                pref_file.write(' */\n')

                # calendar, guid seems to be random, TODO: randomize guid
                pref_file.write('user_pref("calendar.integration.notify", false);\n')
                pref_file.write('user_pref("calendar.list.sortOrder", "71636afc-63cc-41b3-aea6-06f9fff5bb29");\n')
                pref_file.write(
                    'user_pref("calendar.registry.71636afc-63cc-41b3-aea6-06f9fff5bb29.calendar-main-default", true);\n')
                pref_file.write(
                    'user_pref("calendar.registry.71636afc-63cc-41b3-aea6-06f9fff5bb29.calendar-main-in-composite", true);\n')
                pref_file.write('user_pref("calendar.registry.71636afc-63cc-41b3-aea6-06f9fff5bb29.name", "Home");\n')
                pref_file.write(
                    'user_pref("calendar.registry.71636afc-63cc-41b3-aea6-06f9fff5bb29.type", "storage");\n')
                pref_file.write(
                    'user_pref("calendar.registry.71636afc-63cc-41b3-aea6-06f9fff5bb29.uri", "moz-storage-calendar://");\n')
                pref_file.write('user_pref("calendar.timezone.local", "Europe/Berlin");\n')
                pref_file.write('user_pref("calendar.ui.version", 3);\n')

                pref_file.write('user_pref("mail.account.account1.identities", "id1");\n')
                pref_file.write('user_pref("mail.account.account1.server", "server1");\n')
                pref_file.write('user_pref("mail.accountmanager.accounts", "account1");\n')
                pref_file.write('user_pref("mail.accountmanager.defaultaccount", "account1");\n')
                pref_file.write('user_pref("mail.append_preconfig_smtpservers.version", 2);\n')
                pref_file.write('user_pref("mail.identity.id1.full_name", "' + self.full_name + '");\n')
                pref_file.write('user_pref("mail.identity.id1.reply_on_top", 1);\n')
                pref_file.write('user_pref("mail.identity.id1.smtpServer", "smtp1");\n')
                pref_file.write('user_pref("mail.identity.id1.useremail", "' + self.email + '");\n')
                pref_file.write('user_pref("mail.identity.id1.valid", true);\n')

                pref_file.write('user_pref("mail.root.imap", "' + tbImapMailFolder + '");\n')
                pref_file.write('user_pref("mail.root.imap-rel", "[ProfD]ImapMail");\n')
                pref_file.write('user_pref("mail.root.none", "' + tbMailFolder + '");\n')
                pref_file.write('user_pref("mail.root.none-rel", "[ProfD]Mail");\n')
                pref_file.write('user_pref("mail.server.server1.check_new_mail", true);\n')
                pref_file.write('user_pref("mail.server.server1.directory", "' + tbImapMailServerFolder + '");\n')
                pref_file.write(
                    'user_pref("mail.server.server1.directory-rel", "[ProfD]ImapMail/' + imap_server + '");\n')
                pref_file.write('user_pref("mail.server.server1.hostname", "' + imap_server + '");\n')
                pref_file.write('user_pref("mail.server.server1.login_at_startup", true);\n')
                pref_file.write('user_pref("mail.server.server1.name", "' + self.email + '");\n')
                if server_mode == "imap":
                    pref_file.write('user_pref("mail.server.server1.port", 993);\n')
                if server_mode == "pop3":
                    pref_file.write('user_pref("mail.server.server1.port", 110);\n')
                pref_file.write('user_pref("mail.server.server1.socketType", 3);\n')
                if server_mode == "imap":
                    pref_file.write('user_pref("mail.server.server1.type", "imap");\n')
                if server_mode == "pop3":
                    pref_file.write('user_pref("mail.server.server1.type", "pop3");\n')
                pref_file.write('user_pref("mail.server.server1.userName", "' + self.email + '");\n')
                pref_file.write('user_pref("mail.smtpserver.smtp1.authMethod", 3);\n')
                pref_file.write('user_pref("mail.smtpserver.smtp1.description", "Google Mail");\n')
                pref_file.write('user_pref("mail.smtpserver.smtp1.hostname", "' + smtp_server + '");\n')
                pref_file.write('user_pref("mail.smtpserver.smtp1.port", 465);\n')
                pref_file.write('user_pref("mail.smtpserver.smtp1.try_ssl", 3);\n')
                pref_file.write('user_pref("mail.smtpserver.smtp1.username", "' + self.email + '");\n')
                pref_file.write('user_pref("mail.smtpservers", "smtp1");\n')
                pref_file.write('user_pref("mail.winsearch.firstRunDone", true);\n')
                pref_file.write('user_pref("mail.shell.checkDefaultClient", false);\n')

            # save password in mailclient
            time.sleep(1)  # time to write the file
            self.logger.info("Writing config file is finished!")
        except Exception as e:
            self.logger.error("MailClientGuestSide::set_config: " + str(e))

    def send_mail(self, args):
        """
        Send email to receiver.

        @param receiver - Email address.
        @param subject - Subject of the email.
        @param message - Message of the email.
        @param attachment_path_list: (Optional) list of paths for files to attach to the mail.

        """
        try:
            self.logger.info("function: MailClientGuestSide::send_mail")

            ################
            receiver_subject_message = args

            ##receiver##
            start_pointer = 0  # start position
            end_pointer = 8  # end position to read

            recv_length = int(receiver_subject_message[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += recv_length  # end set to end plus length

            receiver = receiver_subject_message[start_pointer:end_pointer]  # begin at 8 until length +8
            self.logger.debug("receiver " + receiver)

            ##subject##
            start_pointer = end_pointer  # new start is old end
            end_pointer += 8  # end set to end plus 8

            subject_length = int(receiver_subject_message[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += subject_length  # end set to end plus length

            subject = receiver_subject_message[start_pointer:end_pointer]
            self.logger.debug("subject " + subject)

            ##message##
            start_pointer = end_pointer  # new start is old end
            end_pointer += 8  # end set to end plus 8

            message_length = int(receiver_subject_message[start_pointer:end_pointer], 16)

            start_pointer = end_pointer  # new start is old end
            end_pointer += message_length  # end set to end plus length

            message = receiver_subject_message[start_pointer:end_pointer]
            self.logger.debug("message " + message)

            attachment_string = None
            # check if attachment_string is added
            if end_pointer < len(receiver_subject_message):
                start_pointer = end_pointer  # new start is old end
                end_pointer += 8  # end set to end plus 8

                attachment_path_length = int(receiver_subject_message[start_pointer:end_pointer], 16)

                start_pointer = end_pointer  # new start is old end
                end_pointer += attachment_path_length  # end set to end plus length

                attachment_string = receiver_subject_message[start_pointer:end_pointer]
                self.logger.debug("attachment_string " + attachment_string)

            ################
            # to = receiver # search if to, cc, bcc is in reciever and split
            self.logger.debug("open email window")
            if attachment_string is None:
                self.logger.debug('No attachment specified')
                self.window_manager.start(
                    'thunderbird', args=['-compose', 'to=%s,subject=%s,body=%s"' % (receiver, subject, message)]
                )
            else:
                self.logger.debug('Attachment found')
                self.window_manager.start(
                    'thunderbird', args=['-compose', 'to=%s,subject=%s,body=%s,attachment=file://%s"' %
                                         (receiver, subject, message, attachment_string)]
                )

            self.logger.debug("email window is here")

            composeWindowTitle = "*%s" % subject
            self.window_manager.waitforwindow(composeWindowTitle, 10)

            self.window_manager.sendkeys('<ctrl><enter>')
        except Exception as e:
            self.logger.error(lineno() + str(e))

        self.logger.debug("send up the message")

        try:
            self.window_manager.waitforwindow('Send Message')
            self.logger.debug("Press enter to send the message")
            self.window_manager.sendkeys('<enter>')

        except Exception as e:
            self.logger.error(lineno() + "mailClient::sendMail: " + str(e))

        self.logger.info("wait 10 second for the smtp pasword window to appear")

        # - Wait for password window
        tbPasswordWindowTitle = 'SMTP Server Password Required'
        isWindowOpen = self.window_manager.waitforwindow(tbPasswordWindowTitle)
        if not isWindowOpen:
            self.logger.error("mailClient::open No window named '%s'" % tbPasswordWindowTitle)
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " error")
            return

        # - Insert Password
        try:
            self.logger.info("password window appeared")
            print("self password")
            print(self.password)
            self.window_manager.text('SMTP Server Password Required', 'txt0', self.password)
            self.window_manager.focus('SMTP Server Password Required')
            keys_combo = "<tab>" + "<space>" + "<enter>"
            self.window_manager.sendkeys(keys_combo)
            self.logger.info("the password should now be inserted")

        except Exception as e:
            self.logger.info("MailClientGuestSide::send_mail: " + str(e))
            self.logger.info("no password window appeard")

        # after all is finished
        self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " ready")


class MailClientGuestSide(ApplicationGuestSide):
    """<MailClient> implementation of the guest side.

    Usually Windows, Linux guest's
    class attributes
    window_id - The ID for the opened object
    """

    def __init__(self, agent_obj, logger):
        super(MailClientGuestSide, self).__init__(agent_obj, logger)
        try:
            self.module_name = "mailClient"
            self.timeout = None
            self.window_is_crushed = None
            self.window_id = None
            self.agent_object = agent_obj
            # settings for the thunderbird profile
            self.full_name = None
            self.email = None
            self.password = None
            self.username = None
            self.thunderbird_app = None
            self.thunderbird_window = None

            if platform.system() == "Windows":
                self.mailClientApp = MailClientWindowsGuestSide(agent_obj, logger, self)
            elif platform.system() == "Linux":
                self.mailClientApp = MailClientLinuxGuestSide(agent_obj, logger, self)
            else:
                raise NotImplemented("InstantMessenger not implemented for system: " + platform.system())

        except Exception as e:
            raise Exception("Error in " + self.__class__.__name__ +
                            ": " + str(e))

    def open(self, args):
        """
        Open a <MailClient> and save the MailClient object with an id in a dictionary.
        Set page load timeout to 30 seconds.

        return:
        Send to the host in the known to be good state:
            'application <MailClient> window_id open'.
            'application <MailClient> window_id ready'.
        in the error state:
            'application <MailClient> window_id error'.
        additionally the 'window_is_crushed' attribute is set; so the next
        call will open a new window.

        """
        self.mailClientApp.open(args)

    def close(self, args):
        """Close one given window by window_id"""
        self.mailClientApp.close(args)

    def set_config(self, args):
        self.mailClientApp.set_config(args)

    def send_mail(self, args):
        """
        Send email to receiver.

        @param receiver - Email address.
        @param subject - Subject of the email.
        @param message - Message of the email.
        @param attachment_path_list: (Optional) list of paths for files to attach to the mail.

        """
        self.mailClientApp.send_mail(args)


###############################################################################
# Commands to parse on guest side
###############################################################################
class MailClientGuestSideCommands(ApplicationGuestSideCommands):
    """
    Class with all commands for one application.

    call the ask method for an object. The call will be done by a thread, so if the timeout is
    reached, the open application will be closed and opened again.
    Static only.
    """

    @staticmethod
    def commands(agent_obj, obj, cmd):  # commands(obj, cmd) obj from list objlist[window_id] win id in cmd[1]?
        try:
            agent_obj.logger.info("static function MailClientGuestSideCommands::commands")
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
                        # close MailClient and set obj to crashed
                        agent_obj.logger.error("thread is alive... time outed")
                        agent_obj.logger.info(
                            "MailClientGuestSideCommands::commands: Close all open windows and " + "clear the MailClient list")
                        subprocess.call(["taskkill", "/IM", "thunderbird.exe", "/F"])
                        # for obj in agent_obj.applicationWindow[module]:
                        #    agent_obj.applicationWindow[module].remove(obj)
                        # set a crushed flag.
                        obj.is_opened = False
                        obj.is_busy = False
                        obj.has_error = True

                        agent_obj.logger.info("application " + module + " " +
                                              str(window_id) + " error")
                        agent_obj.send("application " + module + " " + str(window_id) + " error")

            if not method_found:
                raise Exception("Method " + method_string + " is not defined!")
        except Exception as e:
            raise Exception("Error in MailClientGuestSideCommands::commands " + str(e))
