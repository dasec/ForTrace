# Copyright (C) 2013-2014 Reinhard Stampp
# This file is part of fortrace - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.
# Modified by Stephan Maltan in 2021

from __future__ import absolute_import
from __future__ import print_function
try:
    import logging
    import sys
    import platform
    import threading
    import subprocess
    import inspect  # for listing all method of a class
    import base64
    import re

    import six.moves.cPickle

    # base class VMM side
    from fortrace.application.application import ApplicationVmmSide
    from fortrace.application.application import ApplicationVmmSideCommands

    #
    import fortrace.utility.picklehelper as ph
    import fortrace.utility.guesttime as gt

    # base class guest side
    from fortrace.application.application import ApplicationGuestSide
    from fortrace.application.application import ApplicationGuestSideCommands
    from fortrace.utility.line import lineno

    # module specific imports
    import os.path
    import getpass

except ImportError as ie:
    print(("Import error! in userManagement.py " + str(ie)))
    exit(1)


###############################################################################
# Host side implementation
###############################################################################
class UserManagementVmmSide(ApplicationVmmSide):
    """
    This class is a remote control on the host-side to control a real <userManagement>
    running on a guest.
    """

    def __init__(self, guest_obj, args):
        """
        Set default attribute values only.
        @param guest_obj: The guest on which this application is running. (will be inserted from guest::application())
        @param args: containing
                 logger: Logger name for logging.
        """
        try:
            super(UserManagementVmmSide, self).__init__(guest_obj, args)
            self.logger.info("function: UserManagementVmmSide::__init__")
            self.window_id = None

        except Exception as e:
            raise Exception(
                lineno() + " Error: UserManagementHostSide::__init__ " + self.guest_obj.guestname + " " + str(e))

    def open(self):
        """
        Sends a command to open a userManagement on the associated guest.
        """
        try:
            self.logger.info("function: UserManagementVmmSide::open")
            self.window_id = self.guest_obj.current_window_id
            self.guest_obj.send("application " + "userManagement " + str(self.window_id) + " open ")  # some parameters

            self.guest_obj.current_window_id += 1

        except Exception as e:
            raise Exception("error UserManagementVmmSide::open: " + str(e))

    def close(self):
        """Sends a command to close a <userManagement> on the associated guest.
        """
        try:
            self.logger.info("function: UserManagementVmmSide::close")
            self.guest_obj.send("application " + "userManagement " + str(self.window_id) + " close ")
        except Exception as e:
            raise Exception("error UserManagementVmmSide:close()" + str(e))

    def addUser(self, user_name, password):
        """
        Creating a User on the guest system. Password should not exceed 14 characters
        @param user_name: Name ot the user to create
        @param password: password of the user to create
        """
        if len(password) < 15 or password is None:
            try:
                self.logger.info("function: UserManagementVmmSide:addUser")
                self.logger.debug("Adding user " + user_name + "; password: " + password)
                ac = {"usr_name": user_name,
                      "password": password}
                pcl_ac = ph.base64pickle(ac)
                pcl_ac = pcl_ac.decode()
                pw_cmd = "application userManagement " + str(self.window_id) + " addUser " + pcl_ac
                self.is_busy = True
                self.guest_obj.send(pw_cmd)
            except Exception as e:
                raise Exception("error UserManagementVmmSide:addUser " + str(e))
        else:
            self.logger.error(
                "function: UserManagementVmmSide::addUser failed: Password exeeds maximum supported length or no password is provided")

    def changeUser(self, user_name, password=None):
        """
        Change the user that will be logged in to after next reboot
        @param user_name: Name of the user that will be set at active
        @param password: Password of the user account
        """
        try:
            self.logger.info("function: UserManagementVmmSide:changeUser")
            self.logger.debug("Set " + user_name + "as default autostart user")
            ac = {"usr_name": user_name,
                  "password": password}
            pcl_ac = ph.base64pickle(ac)
            pcl_ac = pcl_ac.decode()
            pw_cmd = "application userManagement " + str(self.window_id) + " changeUser " + pcl_ac
            self.is_busy = True
            self.guest_obj.send(pw_cmd)
        except Exception as e:
            raise Exception("error UserManagementVmmSide:changeUser")

    def deleteUser(self, user_name, d_type):
        """
        Deleting a User on the guest system
        @param user_name: Name of the user to delete
        @param d_type: Type of deleting user data ("keep", "delete", "secure")
        """
        try:
            self.logger.info("function: UserManagementVmmSide:deleteUser")
            self.logger.debug("deleting user" + user_name + "; deletion type:" + d_type)
            ac = {"usr_name": user_name,
                  "del_type": d_type}
            pcl_ac = ph.base64pickle(ac)
            pcl_ac = pcl_ac.decode()
            pw_cmd = "application userManagement " + str(self.window_id) + " deleteUser " + pcl_ac
            self.is_busy = True
            self.guest_obj.send(pw_cmd)
        except Exception as e:
            raise Exception("error UserManagementVmmSide:deleteUser() " + str(e))


###############################################################################
# Commands to parse on host side
###############################################################################
class UserManagementVmmSideCommands(ApplicationVmmSideCommands):
    """
    Class with all commands for <userManagement> which will be received from the agent on the guest.
    Static only.
    """

    @staticmethod
    def commands(guest_obj, cmd):
        # cmd[0] = win_id; cmd[1] = state
        module_name = "userManagement"
        guest_obj.logger.debug("UserManagementVmmSideCommands::commands: " + cmd)
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
class UserManagementGuestSide(ApplicationGuestSide):
    """<userManagement> implementation of the guest side.

    Usually Windows, Linux guest's
    class attributes
    window_id - The ID for the opened object
    """

    def __init__(self, agent_obj, logger):
        super(UserManagementGuestSide, self).__init__(agent_obj, logger)
        try:
            self.module_name = "userManagement"
            self.timeout = None
            self.window_is_crushed = None
            self.window_id = None
            self.agent_object = agent_obj

        except Exception as e:
            raise Exception("Error in " + self.__class__.__name__ +
                            ": " + str(e))

    def open(self, args):
        """
        Open a <userManagement> and save the userManagement object with an id in a dictionary.
        Set page load timeout to 30 seconds.

        return:
        Send to the host in the known to be good state:
        'application <userManagement> window_id open'.
        'application <userManagement> window_id ready'.
        in the error state:
        'application <userManagement> window_id error'.
        additionally the 'window_is_crushed' attribute is set; so the next
        call will open a new window.

        """
        try:
            arguments = args.split(" ")
            var = arguments[0]
            var2 = arguments[1]

            self.logger.info(self.module_name + "GuestSide::open")
            if var == "type":
                self.logger.debug("wait for start UserManagement...")
                # start application <skeletion>
                self.logger.debug("started!")
            elif var == "type2":
                self.logger.debug("wait for start UserManagement...")
                # start application <skeletion>
                self.logger.debug("started!")
            else:
                self.logger.error("skeletion type " + var +
                                  " not implemented")
                return

            # send some information about the userManagement state
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " opened")

            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            self.window_is_crushed = False
        except Exception as e:
            self.logger.info("UserManagementGuestSide::open: Close all open windows and clear the userManagement list")
            subprocess.call(["taskkill", "/IM", "userManagement.exe", "/F"])
            # for obj in self.agent_object.applicationWindow[self.module_name]:
            #    self.agent_obj.applicationWindow[self.module_name].remove(obj)
            # set a crushed flag.
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Error in " + self.__class__.__name__ + "::open" + ": selenium is crushed: " + str(e))

    def close(self):
        """Close one given window by window_id"""
        self.logger.info(self.__class__.__name__ +
                         "::close ")
        self.seleniumDriver.quit()

    def addUser(self, args):
        """
        add a new user account to guest and prepare fortrace installation for that user
        """
        self.logger.info(self.__class__.__name__ +
                         "::addUser ")
        ad = ph.base64unpickle(args)
        user = ad["usr_name"]
        password = ad["password"]
        if platform.system() == "Windows":
            self.agent_object.send(
                "application " + self.module_name + " " + str(self.window_id) + " creating user: " + user + " - password: " + password)
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
            self.__createUser(user, password)
            # add new user to group administrators
            group = self.__getAdmingroupname()
            self.__groupAdd(user, group)
            # create user home directory
            self.__createHomeDir(user, password)
            # copy fortrace data to new users Desktop and enable script execution on first login
            self.__copyInstallationFiles(user, password)
            # set new user as active
            self.logger.info(self.__class__.__name__ +
                             "::User created ")
            # update guest timestamp
            gTime = gt.getGuestTime()
            self.agent_object.send("time {0}".format(gTime))
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            self.window_is_crushed = False
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported at the moment")

    # TODO: Add option to change user dynamical
    def changeUser(self, args):
        """
        Change the user, that will be logged in when the system starts up next time.
        """
        self.logger.info(self.__class__.__name__ +
                         "::changeUser")
        ad = ph.base64unpickle(args)
        user = ad["usr_name"]
        password = ad["password"]
        if platform.system() == "Windows":
            if password is None:
                password = ""
            logon_path = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon"
            try:
                self.agent_object.send(
                    "application " + self.module_name + " " + str(self.window_id) + " Changing active User on next reboot to: " + user)
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
                subprocess.call(["CMD", "/c", "reg", "ADD", logon_path, "/v", "AutoAdminLogon", "/t", "REG_SZ", "/d", "1", "/f"])
                subprocess.call(["CMD", "/c", "reg", "ADD", logon_path, "/v", "DefaultUserName", "/t", "REG_SZ", "/d", user, "/f"])
                subprocess.call(["CMD", "/c", "reg", "ADD", logon_path, "/v", "DefaultPassword", "/t", "REG_SZ", "/d", password, "/f"])
                #update Guest timestamp
                gTime = gt.getGuestTime()
                self.agent_object.send("time {0}".format(gTime))
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
                self.window_is_crushed = False
            except Exception as e:
                self.window_is_crushed = True
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
                self.logger.error("Could not set " + user + " as default autostart user: " + lineno() + ' ' + str(e))
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported at the moment")

    def deleteUser(self, args):
        """
        Delete user from the system
        """
        self.logger.info(self.__class__.__name__ +
                         "::DeleteUser")
        # extract Arguments
        ad = ph.base64unpickle(args)
        user = ad["usr_name"]
        d_type = ad["del_type"]
        if platform.system() == "Windows":
            self.logger.debug(self.__class__.__name__ + "::DeletionType: " + d_type)
            status = False
            # Check if user is currently logged in
            identity = getpass.getuser()
            if identity.upper() == user.upper():
                self.logger.error("User cannot delete itself")
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " user cannot delete itself")
            # Delete user
            else:
                self.agent_object.send(
                    "application " + self.module_name + " " + str(self.window_id) + " Deleting User: " + user + " - deletion type: " + d_type)
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
                try:
                    subprocess.call(["CMD", "/c", "net", "user", user, "/delete"])
                    self.logger.debug(self.__class__.__name__ + "::UserDeleted")
                    status = True
                except Exception as e:
                    self.window_is_crushed = True
                    self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
                    self.logger.error("Could not delete user " + user + ": " + str(e))

            # delete files after deleting the user
            if status:
                self.logger.info(self.__class__.__name__ + "::DeleteUserFiles of user: {0}".format(user))
                sysdrive = os.getenv("SystemDrive")
                user_fortrace_path = "{0}\\Users\\{1}\\Desktop\\fortrace".format(sysdrive, user)
                user_fortrace_autostart = "{0}\\Users\\{1}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\startGuestAgent.lnk".format(sysdrive, user)
                user_fortrace_python = "{0}\\Users\\{1}\\AppData\\Roaming\\Python".format(sysdrive, user)
                homeDir = "{0}\\Users\\{1}".format(sysdrive, user)
                # secure delete fortrace-data to reduce artifacts
                try:
                    self.logger.debug(self.__class__.__name__ + "::deleting fortrace directory")
                    self.__secureDelete(user_fortrace_path)
                    self.logger.debug(self.__class__.__name__ + "::fortrace directory deleted")
                    self.logger.debug(self.__class__.__name__ + "::deleting autostart link")
                    # sdelete cannot delete a symbolic link
                    subprocess.call(["CMD", "/c", "del", user_fortrace_autostart, "/f", "/q"])
                    #self.__secureDeleteDirectory("\"{0}\"".format(user_fortrace_autostart))
                    #self.__secureDelete(user_fortrace_autostart)
                    self.logger.debug(self.__class__.__name__ + "::Link deleted")
                    self.logger.debug(self.__class__.__name__ + "::deleting Python site-packages")
                    self.__secureDelete(user_fortrace_python)
                    self.logger.debug(self.__class__.__name__ + "::Python site-packages deleted")
                except Exception as e:
                    self.window_is_crushed = True
                    self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
                    self.logger.error("Could not autostart-Link " + user + ": " + str(e))

                # Decide how to handle user home directory
                if d_type.upper() == "KEEP":
                    self.logger.debug(self.__class__.__name__ + "::DeleteUserFiles(NONE)")
                elif d_type.upper() == "DELETE":
                    self.logger.debug(self.__class__.__name__ + "::DeleteUserFiles(regular)")
                    self.__deleteDirectory(homeDir)
                elif d_type.upper() == "SECURE":
                    self.logger.debug(self.__class__.__name__ + "::DeleteUserFiles(secure)")
                    self.__secureDelete(homeDir)
                    # TODO: remove workaround to delete undeletable AppData Dirs
                    subprocess.call(["CMD", "/c", "rd", "/s", "/q", homeDir])
                    # execute SDelete twice to ensure the Appdata\local directory is deleted as well
                else:
                    self.logger.error("Wrong Parameter for user file deletion. Keeping user files!")
            gTime = gt.getGuestTime()
            self.agent_object.send("time {0}".format(gTime))
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            self.window_is_crushed = False

    def __createUser(self, user, password):
        """
        Create a new user account on the system
        @param user: Name of the new user
        @param password: Password of the new user
        """
        try:
            subprocess.call(["CMD", "/c", "NET", "USER", user, password, "/ADD"])
        except Exception as e:
            self.logger.error("adding user failed: " + lineno() + ' ' + str(e))

    def __groupAdd(self, user, group):
        # Todo: group remove
        """
        Add a user to a existing group
        @param user: Username to add
        @param group: Name of the group to that the user will be added
        """
        self.logger.info(self.__class__.__name__ +
                         "::groupAdd")
        try:
            subprocess.call(["CMD", "/c", "NET", "LOCALGROUP", group, user, "/ADD"])
        except Exception as e:
            self.logger.error("CMD", "/c", "User " + user + "could not be added to group " + group + ": " + lineno() + ' ' + str(e))

    def __createHomeDir(self, user, password):
        """
        Create the user directory on the system
        @param user: Name of the new user
        @param password: Password of the new user
        """
        self.logger.info(self.__class__.__name__ +
                         "::createHomeDir")
        # check if Home-Directory already exists
        # check for system drive letter
        sysdrive = os.getenv("SystemDrive")
        if os.path.exists(sysdrive + ":\\Users\\" + user):
            self.logger.debug(self.__class__.__name__ +
                              "::HomeDir is already existing")
            return
        else:
            # force creation of user directories by running command in user context
            currentUser = getpass.getuser()
            psexec_p = sysdrive + "\\Users\\{0}\\Desktop\\fortrace\\contrib\\windows-utils\\PsExec64.exe".format(currentUser)
            wmic_p = sysdrive + "\\Windows\\system32\\wbem\\wmic"
            try:
                # opens an Windows Management Instrumentation session, which is directly closed again
                # this is enough to create the new users home directory
                # Parameter:
                # -u: User
                # -p: Password
                # -nobanner/-accepteula: suppress unnecessary output
                subprocess.call([psexec_p, "-u", user, "-p", password, "-nobanner", "-accepteula", wmic_p, "QUIT"])
            except Exception as e:
                self.logger.error("Creating Home Directory for user " + user + "failed: " + lineno() + ' ' + str(e))

    def __copyInstallationFiles(self, user, password):
        """
        Copy the fortrace folder to a new users desktop, so it can be installed and executed
        @param user: Name of the new user
        @param password: Password of the new user
        """
        self.logger.info(self.__class__.__name__ +
                         "::copyInstallationFiles")
        sysdrive = os.getenv("SystemDrive")
        currentUser = getpass.getuser()
        fortrace_p = sysdrive + "\\Users\\{0}\\Desktop\\fortrace".format(currentUser)
        fortrace_target_p = sysdrive + "\\Users\\{0}\\Desktop\\fortrace\\".format(user)
        try:
            # Parameter:
            # /c ignore errors
            # /e copies all subdirectories, including emtpy ones
            # /y overwrites existing files
            # /q supresses output
            subprocess.call(["CMD", "/c", "Xcopy", fortrace_p, fortrace_target_p, "/c", "/e", "/y", "/q"])
        except Exception as e:
            self.logger.error("Copying fortrace data to new users Desktop failed: " + lineno() + ' ' + str(e))
        self.logger.info(self.__class__.__name__ +
                         "::CreateStartupLink")
        # set necessary paths for Link creation
        link_dir = "{0}\\Users\\{1}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup".format(
            sysdrive, user)
        link_name = sysdrive + "\\Users\\{0}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\Installfortrace.lnk".format(
            user)
        link_target = sysdrive + "\\Users\\{0}\\Desktop\\fortrace\\install_tools\\autoinstall.bat".format(user)
        psexec_p = sysdrive + "\\Users\\{0}\\Desktop\\fortrace\\contrib\\windows-utils\\PsExec64.exe".format(currentUser)

        try:
            os.mkdir(link_dir)
            subprocess.call(
                [psexec_p, "-u", user, "-p", password, "-nobanner", "-accepteula", "cmd", "/c", "MKLINK", link_name,
                 link_target])
        except Exception as e:
            self.logger.error("Link for automatic installation could not be created: " + lineno() + ' ' + str(e))

    def __disablePasswordExpiration(self, user):
        """
        Disable the password expiration for a new user
        @param user: Name of the user account for that the expiration should be disabled
        Function is not in use at the moment, keep if "expired password" Error appears again
        """
        self.logger.info(self.__class__.__name__ +
                         "::disablePasswordExpiration")
        try:
            subprocess.call(["CMD", "/c", "WMIC", "USERACCOUNT", "WHERE", "NAME=\'{0}\'".format(user), "SET",
                             "PasswordExpires=FALSE"])
        except Exception as e:
            self.logger.error("disabling Passwort expiration was not possible: " + lineno() + ' ' + str(e))

    def __getAdmingroupname(self):
        """
       Identify the default system language and therefore return the name of the Admin-group
       """
        self.logger.info(self.__class__.__name__ +
                        "::getAdminGroupName")
        language_code = 0
        group = "Administrators"
        try:
            # Get system language and extract the language code
            output = subprocess.check_output(["CMD", "/c", "WMIC", "OS", "GET", "oslanguage"])
            output = str(output)
            language_code = re.findall(r'\d+', output)[0]
        except Exception as e:
            self.logger.error("Language could not be read from system: " + lineno() + ' ' + str(e))
        if language_code == 0:
            self.logger.error("No Language Code was extracted")
            self.logger.debug("::Returning default language group Administrators")
            group = "Administrators"
            return group
        elif language_code == "1031":
            self.logger.info("::System language is german")
            self.logger.debug("::Returning group Administratoren")
            group = "Administratoren"
            return group
        elif language_code == "1033":
            self.logger.info("::System language is english")
            self.logger.debug("::Returning group Administrators")
            group = "Administrators"
            return group
        else:
            # installation should be english, therefore the default group will be Administrators
            self.logger.error("unsupported system language code \"{0}\", trying to use default group".format(language_code))
            self.logger.debug("::Returning default language group Administrators")
            group = "Administrators"
            return group

    def __deleteDirectory(self, directory):
        """
        Removes target directory
        @param directory: target directory to delete
        """
        try:
            subprocess.call(["CMD", "/c", "rmdir", directory, "/S", "/Q"])
            self.logger.debug(self.__class__.__name__ + "::userfiles deleted")
        except Exception as e:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Could not delete userfiles:: " + lineno() + ' ' + str(e))

    def __secureDelete(self, target):
        """
        Secure deletion of a file or directory using the cipher command
        @param target: Target to delete
        """
        self.logger.info(self.__class__.__name__ +
                        "::secureDelete")
        self.logger.debug(self.__class__.__name__ +
                        "::securely deleting" + target)
        sysdrive = os.getenv("SystemDrive")
        user = getpass.getuser()
        sdelete_p = "{0}\\Users\\{1}\\Desktop\\fortrace\\contrib\\windows-utils\\sdelete64.exe".format(sysdrive, user)
        try:
            self.logger.debug(self.__class__.__name__ + "::Secure Deleting user files. This may taka a while...")
            self.agent_object.send("application " + self.module_name + " " + str(
                self.window_id) + "Secure Deleting user files. This may taka a while...")
            self.agent_object.send("application " + self.module_name + " " + str(
                self.window_id) + "Secure Deleting {0}".format(target))
            # Secure delete Files at provided path
            # -s Recurse subdirectories (if directory)
            # -p Number of times to overwrite
            # -r Remove Read-Only attribute.
            # -q run without listing deleted files
            subprocess.call([sdelete_p, "-s", "-r", "-q", "-p", "1", "-nobanner", "-accepteula", target])
        except Exception as e:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " secure deletion was not possible")
            self.logger.error("Could not delete target:: " + lineno() + ' ' + str(e))

###############################################################################
# Commands to parse on guest side
###############################################################################
class UserManagementGuestSideCommands(ApplicationGuestSideCommands):
    """
    Class with all commands for one application.

    call the ask method for an object. The call will be done by a thread, so if the timeout is
    reached, the open application will be closed and opened again.
    Static only.
    """

    @staticmethod
    def commands(agent_obj, obj, cmd):  # commands(obj, cmd) obj from list objlist[window_id] win id in cmd[1]?
        try:
            agent_obj.logger.info("static function UserManagementGuestSideCommands::commands")
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
                    # increased timeout for secure  deletion of user files
                    tmp_thread.join(3600)  # Wait until the thread is completed
                    if tmp_thread.is_alive():
                        # close userManagement and set obj to crashed
                        agent_obj.logger.error("thread is alive... time outed")
                        agent_obj.logger.info(
                            "UserManagementGuestSideCommands::commands: Close all open windows and " + "clear the userManagement list")
                        subprocess.call(["taskkill", "/IM", "userManagement.exe", "/F"])
                        for obj in agent_obj.applicationWindow[module]:
                            agent_obj.applicationWindow[module].remove(obj)
                        # set a crushed flag.
                        obj.is_opened = False
                        obj.is_busy = False
                        obj.has_error = True

                        agent_obj.logger.info("application " + module + " " + str(window_id) + " error")
                        agent_obj.send("application " + module + " " + str(window_id) + " error")

            if not method_found:
                raise Exception("Method " + method_string + " is not defined!")
        except Exception as e:
            raise Exception("Error in UserManagementGuestSideCommands::commands " + str(e))
