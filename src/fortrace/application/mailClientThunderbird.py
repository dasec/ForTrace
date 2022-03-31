# Copyright (C) 2018 Sascha Kopp
# This file is part of fortrace - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.
# This version of the mail client plugin uses the native mozilla python modules for manipulating the configuration to reduce code bloat
# See fortrace.utility.tbstuff.py for profile manipulation functions

# IMPORTANT!!!
# Bugs and issues:
# For some reason creating the profile may fail, check the error variable for this application after calling the add profile methods.
# Last test worked, just make sure profiles.ini can be accessed.
# Send_mail only works if Thunderbird is closed, pywinauto seems to fail in connecting to the window if Thunderbird is already opened
# Linux side has not been updated and may fail for receiving an sending mail
# For some reason adding an imap account makes Thunderbird fail to provide the correct choices while manually switching authentification methods, it should not matter
# For another unknown reason Thunderbird will ignore the common entries for the local folders and add an additional entry section for it, does not seem to affect anything

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
    from fortrace.utility.io import escape_password_string

    if platform.system() == "Windows":
        import pywinauto
        from fortrace.utility.SendKeys import SendKeys

    import fortrace.utility.picklehelper as ph
    import fortrace.utility.tbstuff as tbs

except ImportError as ie:
    print(("Import error! in MailClientThunderbird.py " + str(ie)))
    exit(1)


###############################################################################
# Host side implementation
###############################################################################
class MailClientThunderbirdVmmSide(ApplicationVmmSide):
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
            super(MailClientThunderbirdVmmSide, self).__init__(guest_obj, args)
            self.logger.info("function: MailClientThunderbirdVmmSide::__init__")
            self.window_id = None
            self.window_id = self.guest_obj.current_window_id
            self.guest_obj.current_window_id += 1
            # self.mail_client = "thunderbird"

        except Exception as e:
            raise Exception(lineno() + " Error: MailClientThunderbirdHostSide::__init__ "
                            + self.guest_obj.guestname + " " + str(e))

    def open(self):
        """Sends a command to open a MailClient on the associated guest.
        """
        try:
            self.logger.info("function: MailClientThunderbirdVmmSide::open")
            self.guest_obj.send(
                "application " + "mailClientThunderbird " + str(self.window_id) + " open ")  # some parameter
        except Exception as e:
            raise Exception("error MailClientVmmSide::open: " + str(e))

    def close(self):
        """Sends a command to close a MailClient on the associated guest.
        """
        try:
            self.logger.info("function: MailClientThunderbirdVmmSide::close")
            self.guest_obj.send("application " + "mailClientThunderbird " + str(self.window_id) + " close ")
        except Exception as e:
            raise Exception("error MailClientThunderbirdVmmSide:close()" + str(e))

    def set_session_password(self, password):
        """ Set password for password dialogs in current session.

            Note: Call this as the first method after opening the mail plugin to prevent profile generation issues.
                  Use an empty password if you have to.
                  The password will be saved inside the thunderbird profile, make sure to delete it if you dont intent to share it.

        :param password:
        """
        try:
            pcl_pw = ph.base64pickle(password)
            pcl_pw = pcl_pw.decode()
            print(type(pcl_pw))
            pw_cmd = "application mailClientThunderbird " + str(self.window_id) + " set_session_password " + pcl_pw
            self.is_busy = True
            self.guest_obj.send(pw_cmd)

        except Exception as e:
            raise Exception("error mailer::set_session_password: " + str(e))

    def run_for(self, timeout):
        """ Run Thunderbird for a limited amount of time to generate folders and files or to receive mail.
            Call this after making changes to the profile config.

            Bug: Don't call this method it will fail since the backend uses incorrect parameters for calling mozrunner.

        :param timeout:
        """
        try:
            pcl_to = ph.base64pickle(timeout)
            pcl_to = pcl_to.decode()
            pw_cmd = "application mailClientThunderbird " + str(self.window_id) + " run_for " + pcl_to
            self.is_busy = True
            self.guest_obj.send(pw_cmd)

        except Exception as e:
            raise Exception("error mailer::run_for: " + str(e))

    def add_pop3_account(self, pop_server, smtp_server, email_address, username, full_name, smtp_description,
                         socket_type=3, auth_method=3, socket_type_smtp=3, auth_method_smtp=3):
        """ Adds a pop3 account to the profile.

        :param pop_server: address of the pop3 mailserver
        :param smtp_server:  address of the smtp server
        :param email_address: the accounts email address
        :param username: username of the mail server, usually the email address
        :param full_name: the account owners full name
        :param smtp_description: desription for the smpt server
        :param socket_type: 0 No SSL, 1 StartTLS, 2 SSL/TLS
        :param auth_method: corresponds to the password exchange method, pop supports other methods than imap
        :param auth_method_smtp: corresponds to the password exchange method for the smtp server
        """
        try:
            ac = {"pop_server": pop_server,
                  "smtp_server": smtp_server,
                  "email_address": email_address,
                  "username": username,
                  "full_name": full_name,
                  "smtp_description": smtp_description,
                  "socket_type": socket_type,
                  "auth_method": auth_method,
                  "socket_type_smtp": socket_type_smtp,
                  "auth_method_smtp": auth_method_smtp}
            pcl_ac = ph.base64pickle(ac)
            pcl_ac = pcl_ac.decode()
            pw_cmd = "application mailClientThunderbird " + str(self.window_id) + " add_pop3_account " + pcl_ac
            self.is_busy = True
            self.guest_obj.send(pw_cmd)

        except Exception as e:
            raise Exception("error mailer::add_pop3_account: " + str(e))

    def add_imap_account(self, imap_server, smtp_server, email_address, username, full_name,
                         socket_type=3, socket_type_smtp=2, auth_method_smtp=3):
        """ Adds a imap account to the profile.

            :param imap_server: address of the pop3 mailserver
            :param smtp_server:  address of the smtp server
            :param email_address: the accounts email address
            :param username: username of the mail server, usually the email address
            :param full_name: the account owners full name
            :param socket_type: 0 No SSL, 1 StartTLS, 2 SSL/TLS
            :param auth_method: corresponds to the password exchange method, has the same methods for smtp
        """
        try:
            ac = {"imap_server": imap_server,
                  "smtp_server": smtp_server,
                  "email_address": email_address,
                  "username": username,
                  "full_name": full_name,
                  "socket_type": socket_type,
                  "socket_type_smtp": socket_type_smtp,
                  "auth_method_smtp": auth_method_smtp}
            pcl_ac = ph.base64pickle(ac)
            pcl_ac = pcl_ac.decode()
            pw_cmd = "application mailClientThunderbird " + str(self.window_id) + " add_imap_account " + pcl_ac
            self.is_busy = True
            self.guest_obj.send(pw_cmd)

        except Exception as e:
            raise Exception("error mailer::add_imap_account: " + str(e))

    def send_mail(self, receiver, subject, message, attachment_path_list=None):
        """Send an email via the mailClient.

           Note: A bug prevents this from working inside an open thunderbird application.
                 Close all thunderbird windows before using this method.

        @param receiver: Receiver for this email.
        @param subject: Subject for this email.
        @param message: Message for this email.
        @param attachment_path_list: (Optional) list of paths for files to attach to the mail.

        @return: No return value.
        """
        try:
            m = {"receiver": receiver,
                 "subject": subject,
                 "message": message}
            # check if attachment_string is added
            if attachment_path_list is not None:
                attachment_string = parse_attachment_string(attachment_path_list)
                if attachment_string is not None:
                    m["attachment_string"] = attachment_string
            pcl_m = ph.base64pickle(m)
            pcl_m = pcl_m.decode()
            send_mail_command = "application mailClientThunderbird " + str(self.window_id) + " send_mail " + pcl_m
            self.is_busy = True
            self.guest_obj.send(send_mail_command)
        except Exception as e:
            raise Exception("error mailer::sendMail: " + str(e))

    def loadMailboxData(self, type, from_name, from_ad, to_name, to_ad, user, server, timestamp, subject,
            message, attachments=None):
        # TODO attachment
        try:
            m = {"type": type,
                 "from_name": from_name,
                 "from_ad": from_ad,
                 "to_name": to_name,
                 "to_ad": to_ad,
                 "user": user,
                 "server": server,
                 "timestamp": timestamp,
                 "subject": subject,
                 "message": message,
                 "attachments": attachments
            }
            pcl_m = ph.base64pickle(m)
            pcl_m = pcl_m.decode()
            load_mailbox_command = "application mailClientThunderbird " + str(self.window_id) + " loadMailboxData " + pcl_m
            self.is_busy = True
            self.guest_obj.send(load_mailbox_command)
        except Exception as e:
            raise Exception("error mailer::loadMailboxData: " + str(e))


###############################################################################
# Commands to parse on host side
###############################################################################
class MailClientThunderbirdVmmSideCommands(ApplicationVmmSideCommands):
    """
    Class with all commands for MailClient which will be received from the agent on the guest.

    Static only.
    """

    @staticmethod
    def commands(guest_obj, cmd):
        # cmd[0] = win_id; cmd[1] = state
        guest_obj.logger.info("function: MailClientThunderbirdVmmSideCommands::commands")
        module_name = "mailClientThunderbird"
        guest_obj.logger.debug("MailClientThunderbirdVmmSideCommands::commands: " + cmd)
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
class MailClientThunderbirdPlatformIndependentGuestSide(object):
    """<MailClient> implementation of the guest side.

    Usually Windows, Linux guest's
    class attributes
    window_id - The ID for the opened object
    """

    def __init__(self, agent_obj, logger, imParent):
        try:
            self.module_name = "mailClientThunderbird"
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

        except Exception as e:
            raise Exception("Error in " + self.__class__.__name__ +
                            ": " + str(e))

    def set_session_password(self, args):
        p = ph.base64unpickle(args)
        self.password = p
        self.logger.debug("Session password set to: " + str(self.password))
        self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " ready")

    def run_for(self, args):
        t = ph.base64unpickle(args)
        tbs.run_thunderbird_for(t)
        self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " ready")

    def add_imap_account(self, args):
        self.logger.debug("Creating Imap account")
        ai = ph.base64unpickle(args)
        if not tbs.has_profile():
            tbs.create_profile_folder_if_non_existent()
            ci = tbs.gen_common()
            tbs.add_account_config_to_profile(ci)
        acno = tbs.find_next_free_profile_id()
        serno = tbs.find_next_free_server_id()
        smtpno = tbs.find_next_free_smtp_id()
        acd = tbs.gen_imap_account(acno, serno, smtpno, ai["imap_server"], ai["smtp_server"], ai["email_address"],
                                   ai["username"], ai["full_name"], ai["socket_type"], ai["socket_type_smtp"],
                                   ai["auth_method_smtp"])
        tbs.add_account_config_to_profile(acd)
        self.logger.debug("Done creating Imap account")
        self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " ready")

    def add_pop3_account(self, args):
        self.logger.debug("Creating Pop3 account")
        ai = ph.base64unpickle(args)
        if not tbs.has_profile():
            tbs.create_profile_folder_if_non_existent()
            ci = tbs.gen_common()
            tbs.add_account_config_to_profile(ci)
        acno = tbs.find_next_free_profile_id()
        serno = tbs.find_next_free_server_id()
        smtpno = tbs.find_next_free_smtp_id()
        acd = tbs.gen_pop_account(acno, serno, smtpno, ai["pop_server"], ai["smtp_server"], ai["email_address"],
                                  ai["username"], ai["full_name"], ai["smtp_description"], ai["socket_type"],
                                  ai["auth_method"], ai["socket_type_smtp"], ai["auth_method_smtp"])
        tbs.add_account_config_to_profile(acd)
        self.logger.debug("Done creating Pop3 account")
        self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " ready")


class MailClientThunderbirdWindowsGuestSide(MailClientThunderbirdPlatformIndependentGuestSide):
    """<MailClient> implementation of the guest side.

    Usually Windows, Linux guest's
    class attributes
    window_id - The ID for the opened object
    """

    def __init__(self, agent_obj, logger, imParent):
        super(MailClientThunderbirdWindowsGuestSide, self).__init__(agent_obj, logger, imParent)

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
            self.logger.info("function: MailClientThunderbirdGuestSide::open")

            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " busy")

            # check if profile exists
            if os.path.join(os.path.expanduser('~'), "AppData\Roaming\Thunderbird\profiles.ini"):
                self.logger.debug("Profile exists")
            else:
                raise Exception("MailClientThunderbirdGuestSide::open: no Thunderbird profile are deposited")

            # check for thunderbird exe and start it.
            if os.path.exists(r"c:\Program files (x86)\Mozilla Thunderbird\Thunderbird.exe"):
                self.thunderbird_app = pywinauto.application.Application().start(
                    r"c:\Program files (x86)\Mozilla " + r"Thunderbird\Thunderbird.exe" + r" -new-instance -P default")
            elif os.path.exists(r"c:\Program Files\Mozilla Thunderbird\Thunderbird.exe"):
                self.thunderbird_app = pywinauto.application.Application().start(
                    r"c:\Program Files\Mozilla " + r"Thunderbird\Thunderbird.exe" + r" -new-instance -P default")
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
            self.logger.error("MailClientThunderbirdGuestSide::open: " + str(e))
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
            self.logger.error("MailClientThunderbirdGuestSide::open No window named '.*Mozilla Thunderbird'")
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " error")
            return

            # some information about the mailClient state
        time.sleep(20)
        try:
            # app = application.Application()
            password_window = None
            #TODO Needs to be refactored
            try:
                password_window = self.thunderbird_app.window_(title_re='Mail Server Password Required')
            except:
                pass
            #for r in [".*Passwort", ".*password", ".*[sS]erver"]: # possible names for the password window, try them all
            #    try:
            #        password_window = self.thunderbird_app.window_(title_re=r)
            #        break
            #    except:
            #        pass
            if password_window is None:
                raise Exception("Tried all combinations for password window, giving up")
            self.logger.debug("password window = ")
            self.logger.debug(password_window)
            self.logger.debug("password window appeared")
            time.sleep(1)
            self.logger.debug("self.password: " + str(self.password))
            escaped_password = escape_password_string(self.password)
            send_key_string = escaped_password + "{TAB}" + "{SPACE}" + "{ENTER}"
            password_window.TypeKeys(send_key_string)
            self.logger.debug("the password should now be inserted")
            time.sleep(2)
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " opened")
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " ready")
            self.window_is_crushed = False
        except Exception as e:
            self.logger.error("MailClientThunderbirdGuestSide::open: " + str(e))
            self.logger.error("no password window appeard")
            # send some information about the instantMessenger state

        except Exception as e:
            self.logger.info(
                "MailClientThunderbirdGuestSide::open: Close all open windows and clear the MailClientThunderbirdGuestSide list")
            subprocess.call(["taskkill", "/IM", "thunderbird.exe", "/F"])
            # for obj in self.agent_object.applicationWindow[self.module_name]:
            #    self.agent_obj.applicationWindow[self.module_name].remove(obj)
            # set a crushed flag.
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " error")
            self.logger.error(
                "Error in " + self.__class__.__name__ + "::open" + ": MailClientThunderbird is crushed: " + str(e))

    def close(self, args):
        """Close one given window by window_id"""
        self.logger.info(self.__class__.__name__ +
                         "::close ")
        # close all windows
        self.thunderbird_app.kill_()
        self.logger.debug("kill open thunderbird windows!")

    def send_mail(self, args):
        """
        Send email to receiver.

        @param receiver - Email address.
        @param subject - Subject of the email.
        @param message - Message of the email.
        @param attachment_path_list: (Optional) list of paths for files to attach to the mail.

        """
        try:
            self.logger.info("function: MailClientThunderbirdGuestSide::send_mail")
            ad = ph.base64unpickle(args)

            ################
            receiver = ad["receiver"]
            self.logger.debug("receiver " + receiver)

            ##subject##
            subject = ad["subject"]
            self.logger.debug("subject " + subject)

            ##message##
            message = ad["message"]
            self.logger.debug("message " + message)

            attachment_string = None
            if 'attachment_string' in ad:
                attachment_string = ad["attachment_string"]
                self.logger.debug("attachment_string " + attachment_string)


            ################
            # to = receiver # search if to, cc, bcc is in reciever and split
            self.logger.debug("open email window")

            thunderbird_x86_path = r"c:\Program files (x86)\Mozilla Thunderbird\Thunderbird.exe"
            thunderbird_path = r"c:\Program Files\Mozilla Thunderbird\Thunderbird.exe"

            if os.path.exists(thunderbird_x86_path):
                if attachment_string is None:
                    self.thunderbird_app = pywinauto.application.Application().start(
                        thunderbird_x86_path + ' -p default -compose "to=%s,subject=\'%s\',body=\'%s\'"' % (
                            receiver, subject, message))
                else:
                    self.thunderbird_app = pywinauto.application.Application().start(
                        thunderbird_x86_path + ' -p default -compose "to=%s,subject=\'%s\',body=\'%s\',attachment=\'%s\'"' % (
                            receiver, subject, message, attachment_string))

            elif os.path.exists(thunderbird_path):
                if attachment_string is None:
                    self.thunderbird_app = pywinauto.application.Application().start(
                        thunderbird_path + ' -p default -compose "to=%s,subject=\'%s\',body=\'%s\'"' % (
                            receiver, subject, message))
                else:
                    self.thunderbird_app = pywinauto.application.Application().start(
                        thunderbird_path + ' -p default -compose "to=%s,subject=\'%s\',body=\'%s\',attachment=\'%s\'"' % (
                            receiver, subject, message, attachment_string))
            else:
                self.logger.error(
                    "Thundebird is not installed into the standard path c:\Program files (x86)\Mozilla " + "Thunderbird\Thunderbird.exe or c:\Program Files\Mozilla " + "Thunderbird\Thunderbird.exe")
                raise Exception(
                    "Thundebird is not installed into the standard path c:\Program files (x86)\Mozilla " + "Thunderbird\Thunderbird.exe or c:\Program Files\Mozilla Thunderbird\Thunderbird.exe")



            self.logger.debug("email window is here")
            time.sleep(10)
            if self.thunderbird_app.windows_():
                self.logger.debug("if case")
                self.thunderbird_window = self.thunderbird_app.window_(title_re=".*%s.*" % subject)
            else:
                self.logger.debug("else case")
                app = pywinauto.application.Application().connect_(title_re=".*%s.*" % subject)
                self.thunderbird_window = app.window_(title_re=".*%s.*" % subject)

            self.thunderbird_window.TypeKeys("^{ENTER}")
        except Exception as e:
            self.logger.error(lineno() + str(e))

        self.logger.debug("send up the message")

        try:
            time.sleep(3)
            self.logger.debug("Press enter to send the message")
            #SendKeys("^{ENTER}")
            # TODO switch to pywinauto, ... -> THIS SEEMS TO HAVE BEEN THE CAUSE FOR CLOSING SMTP PASSWORD WINDOW BEFORE PASSWORD COULD BE ENTERED
            pass

        except Exception as e:
            self.logger.error(lineno() + "MailClientThunderbird::sendMail: " + str(e))

        self.logger.info("wait 10 second for the smtp pasword window to appear")
        time.sleep(10)
        # Enter password into window
        try:  # check for thunderbird window
            # mozilla is one of those applications that use existing windows
            # if they exist (at least on my machine!)
            # so if we cannot find any window for that process
            #  - find the actual process
            #  - connect to it
            # todo: reevaluate these statements, it will throw an error, but will send mail anyway if open was not used before
            if self.thunderbird_app.windows_():
                self.thunderbird_window = self.thunderbird_app.window_(title_re=".*Mozilla Thunderbird")

            else:
                self.thunderbird_app = pywinauto.application.Application().connect_(title_re=".*Mozilla Thunderbird")
                self.thunderbird_window = self.thunderbird_app.window_(title_re=".*Mozilla Thunderbird")

        except Exception as e:
            self.logger.error("MailClientThunderbird::open No window named '.*Mozilla Thunderbird'")
            self.logger.error("MailClientThunderbird::open SMTP password may have been entered previously")

        # if window appears
        try:
            password_window = None
            for r in [".*Password.*", ".*Passwort.*", ".*[sS]erver", "*[eE]nter.*"]: # possible names for the password window, try them all
                try:
                    password_window = self.thunderbird_app.window_(title_re=r)
                    self.logger.info("looking for password window using " + r)

                    break
                except:
                    self.logger.error("Password window not found!")
                    pass
            if password_window is None:
                raise Exception("Tried all combinations for password window, giving up")
            self.logger.info("password window appeared" + r)
            self.logger.info("password window = ")
            self.logger.info(password_window)
            time.sleep(10)
            escaped_password = escape_password_string(self.password)
            sendkeystring = escaped_password + "{TAB}" + "{SPACE}" + "{ENTER}"
            password_window.TypeKeys(sendkeystring)
            # TODO switch to pywinauto, ...
            self.logger.info("the password should now be inserted")
            time.sleep(2)
        # else
        except Exception as e:
            self.logger.info("MailClientThunderbirdGuestSide::send_mail: " + str(e))
            self.logger.info("no password window appeard")

        # after all is finished
        self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " ready")

    def loadMailboxData(self, args):
        '''
        Adding item to a mailbox file of Thunderbird.
        Added by Thomas Schaefer in 2019
        :param type: needle or hay
        :param from_name: display name of the sender
        :param from_ad: email address of the sender
        :param to_name: display name of the receiver
        :param to_ad: email address of recipient
        :param user: username of the currently logged in OS user
        :param server: pop3 or imap address for incoming emails, doesn't matter for outgoing ones
        :param timestamp: time at which the email was received or sent
        :param subject: topic of the mail
        :param message: message body of the mail
        :return:
        '''
        self.logger.info("function: MailClientThunderbirdGuestSide::loadMailboxData")

        #implementation
        from email.mime.base import MIMEBase
        import mailbox
        import email.utils
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email import encoders
        import os
        from os.path import basename

        ad = ph.base64unpickle(args)
        type= ad["type"]
        from_name = ad["from_name"]
        from_ad = ad["from_ad"]
        to_name = ad["to_name"]
        to_ad = ad["to_ad"]
        user = ad["user"]
        server = ad["server"]
        timestamp = ad["timestamp"]
        subject = ad["subject"]
        message = ad["message"]
        attachments = ad["attachments"]

        mboxbasepath = 'C:\\Users\\' + user + '\\AppData\\Roaming\\Thunderbird\\Profiles'
        profile = next(os.walk(mboxbasepath))[1][0]

        from_addr = email.utils.formataddr((from_name, from_ad))
        to_addr = email.utils.formataddr((to_name, to_ad))

        if(type == "in"):
            mboxtrailpath = '\\Mail\\' + server + '\\Inbox'
        elif(type == "out"):
            mboxtrailpath = '\\Mail\\Local Folders\\Sent'
        else:
            self.logger.error("No type match found in function: MailClientThunderbirdGuestSide::loadMailboxData for type: " + type)

        # Check if folder Local Folders is available, if not create!
        mboxfile = mboxbasepath + '\\' + profile + mboxtrailpath
        try:
            f = open(mboxfile, "a+")
            f.close()
        except OSError:
            print(("Creation of the directory %s failed" % mboxfile))
        else:
            print(("Successfully created the directory %s " % mboxfile))

        self.logger.debug("mbox path: " + mboxfile)
        mbox = mailbox.mbox(mboxfile)
        mbox.lock()
        self.logger.debug("testing mail manipulation on " + mboxfile)
        try:
            # TODO Proof if attachment is also 'submittable' here
            msg = MIMEMultipart()
            #msg.set_unixfrom(timestamp)
            msg['From'] = from_addr
            msg['To'] = to_addr
            msg['Subject'] = subject
            if attachments is not None:
                for file in attachments:
                    part = MIMEBase('application', "octet-stream")
                    with open(file, "rb") as f:
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", 'attachement; filename="{}"'.format(basename(file)),)
                    msg.attach(part)
            msg.attach(MIMEText(message, "plain"))
            mbox.add(msg)
            mbox.flush()
        except Exception as e:
            self.logger.debug(e)
        finally:
            mbox.unlock()

        self.logger.info("loaded mailbox data")

class MailClientThunderbirdLinuxGuestSide(MailClientThunderbirdPlatformIndependentGuestSide):
    """<MailClient> implementation of the guest side.

    Usually Windows, Linux guest's
    class attributes
    window_id - The ID for the opened object
    """

    def __init__(self, agent_obj, logger, imParent):
        super(MailClientThunderbirdLinuxGuestSide, self).__init__(agent_obj, logger, imParent)
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
            self.logger.info("function: MailClientThunderbirdGuestSide::open")

            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " busy")

            # check if profile exists
            tbProfilePath = os.path.join(os.path.expanduser('~'), ".thunderbird/profiles.ini")
            if os.path.exists(tbProfilePath):
                self.logger.debug("Profile exists")
            else:
                raise Exception("MailClientThunderbirdGuestSide::open: no Thunderbird profile are deposited")

            # check for thunderbird exe and start it.
            self.window_manager.start('thunderbird', '*Thunderbird', ['-P', 'default'])

            self.logger.debug("Window should now be opened")

        except Exception as e:
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " error")
            self.logger.error("MailClientThunderbirdGuestSide::open: " + str(e))
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
            self.logger.error("MailClientThunderbirdGuestSide::open: " + str(e))
            self.logger.error("no password window appeard")
            # send some information about the instantMessenger state

        # - TODO: 2 catch-blocks for the same exception?
        except Exception as e:
            self.logger.info(
                "MailClientThunderbirdGuestSide::open: Close all open windows and clear the MailClientThunderbirdGuestSide list")
            self.window_manager.close('*Thunderbird*')
            # for obj in self.agent_object.applicationWindow[self.module_name]:
            #    self.agent_obj.applicationWindow[self.module_name].remove(obj)
            # set a crushed flag.
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " error")
            self.logger.error(
                "Error in " + self.__class__.__name__ + "::open" + ": MailClientThunderbird is crushed: " + str(e))

    def close(self, args):
        """Close one given window by window_id"""
        self.logger.info(self.__class__.__name__ + "::close ")
        # close all windows
        self.window_manager.close('*Thunderbird*')
        self.logger.debug("kill open thunderbird windows!")

    def send_mail(self, args):
        """
        Send email to receiver.

        @param receiver - Email address.
        @param subject - Subject of the email.
        @param message - Message of the email.
        @param attachment_path_list: (Optional) list of paths for files to attach to the mail.
        """
        try:
            self.logger.info("function: MailClientThunderbirdGuestSide::send_mail")
            ad = ph.base64unpickle(args)

            ################
            receiver = ad["receiver"]
            self.logger.debug("receiver " + receiver)

            ##subject##
            subject = ad["subject"]
            self.logger.debug("subject " + subject)

            ##message##
            message = ad["message"]
            self.logger.debug("message " + message)

            attachment_string = None
            if 'attachment_string' in ad:
                attachment_string = ad["attachment_string"]
                self.logger.debug("attachment_string " + attachment_string)

            ################
            # to = receiver # search if to, cc, bcc is in reciever and split
            self.logger.debug("open email window")

            if attachment_string is None:
                self.window_manager.start(
                    'thunderbird', args=['-compose', '"to=%s,subject=\'%s\',body=\'%s\'"' % (receiver, subject, message)]
                )
            else:
                self.window_manager.start(
                    'thunderbird', args=['-compose', '"to=%s,subject=\'%s\',body=\'%s\',attachment=\'%s\'"' %
                                         (receiver, subject, message, attachment_string)]
                )

            self.logger.debug("email window is here")

            composeWindowTitle = "*%s" % subject
            self.window_manager.waitforwindow(composeWindowTitle, 10)

            self.window_manager.sendkeys('<ctrl><enter>')
            #TODO switch to pywinauto, ...
        except Exception as e:
            self.logger.error(lineno() + str(e))

        self.logger.debug("send up the message")

        try:
            self.window_manager.waitforwindow('Send Message')
            time.sleep(10)
            self.logger.debug("Press enter to send the message")
            self.window_manager.sendkeys('<enter>')
            # TODO switch to pywinauto, ...

        except Exception as e:
            self.logger.error(lineno() + "MailClientThunderbird::sendMail: " + str(e))

        self.logger.info("wait 10 second for the smtp pasword window to appear")

        # - Wait for password window
        tbPasswordWindowTitle = 'SMTP Server Password Required'
        time.sleep(10)
        isWindowOpen = self.window_manager.waitforwindow(tbPasswordWindowTitle)
        if not isWindowOpen:
            self.logger.error("MailClientThunderbird::open No window named '%s'" % tbPasswordWindowTitle)
            self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " error")
            return

        # - Insert Password
        try:
            self.logger.info("password window appeared")
            self.window_manager.text('SMTP Server Password Required', 'txt0', self.password)
            self.window_manager.focus('SMTP Server Password Required')
            keys_combo = "<tab>" + "<space>" + "<enter>"
            self.window_manager.sendkeys(keys_combo)
            # TODO switch to pywinauto, ...
            self.logger.info("the password should now be inserted")

        except Exception as e:
            self.logger.info("MailClientThunderbirdGuestSide::send_mail: " + str(e))
            self.logger.info("no password window appeard")

        # after all is finished
        self.agent_object.send("application " + self.module_name + " " + str(self.imParent.window_id) + " ready")

    def loadMailboxData(self, args):
        '''
        stub implementation in order for the program to not crash when run on a linux machine
        added by Thomas Schaefer in 2019
        :param args:
        :return:
        '''
        self.logger.info("This functionality is not yet implemented for Linux!")


class MailClientThunderbirdGuestSide(ApplicationGuestSide):
    """<MailClient> implementation of the guest side.

    Usually Windows, Linux guest's
    class attributes
    window_id - The ID for the opened object
    """

    def __init__(self, agent_obj, logger):
        super(MailClientThunderbirdGuestSide, self).__init__(agent_obj, logger)
        try:
            self.module_name = "mailClientThunderbird"
            self.timeout = None
            self.window_is_crushed = None
            self.window_id = None
            self.agent_object = agent_obj
            # settings for the thunderbird profile
            self.full_name = None
            self.email = None
            # self.password = None
            self.username = None
            self.thunderbird_app = None
            self.thunderbird_window = None

            if platform.system() == "Windows":
                self.mailClientApp = MailClientThunderbirdWindowsGuestSide(agent_obj, logger, self)
            elif platform.system() == "Linux":
                self.mailClientApp = MailClientThunderbirdLinuxGuestSide(agent_obj, logger, self)
            else:
                raise NotImplemented("MailClientThunderbird not implemented for system: " + platform.system())

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

    def send_mail(self, args):
        """
        Send email to receiver.

        @param receiver - Email address.
        @param subject - Subject of the email.
        @param message - Message of the email.
        @param attachment_path_list: (Optional) list of paths for files to attach to the mail.

        """
        self.mailClientApp.send_mail(args)

    def set_session_password(self, args):
        self.mailClientApp.set_session_password(args)

    def add_imap_account(self, args):
        self.mailClientApp.add_imap_account(args)

    def add_pop3_account(self, args):
        self.mailClientApp.add_pop3_account(args)

    def loadMailboxData(self, args):
        """
        Loading predefined Mails into thunderbird standard mailbox

        @param
        @param
        """
        self.mailClientApp.loadMailboxData(args)


###############################################################################
# Commands to parse on guest side
###############################################################################
class MailClientThunderbirdGuestSideCommands(ApplicationGuestSideCommands):
    """
    Class with all commands for one application.

    call the ask method for an object. The call will be done by a thread, so if the timeout is
    reached, the open application will be closed and opened again.
    Static only.
    """

    @staticmethod
    def commands(agent_obj, obj, cmd):  # commands(obj, cmd) obj from list objlist[window_id] win id in cmd[1]?
        try:
            agent_obj.logger.info("static function MailClientThunderbirdThunderbirdGuestSideCommands::commands")
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
                            "MailClientThunderbirdGuestSideCommands::commands: Close all open windows and " + "clear the MailClientThunderbird list")
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
            raise Exception("Error in MailClientThunderbirdGuestSideCommands::commands " + str(e))
