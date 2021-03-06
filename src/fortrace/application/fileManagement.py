# Copyright (C) 2013-2014 Reinhard Stampp
# This file is part of fortrace - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.
# created by Stephan Maltan in 2021

try:
    import logging
    import sys
    import platform
    import threading
    import subprocess
    import inspect  # for listing all method of a class
    import base64
    import re


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
    print("Import error! in fileManagement.py " + str(ie))
    exit(1)


###############################################################################
# Host side implementation
###############################################################################
class FileManagementVmmSide(ApplicationVmmSide):
    """
    This class is a remote control on the host-side to control a real <fileManagement>
    running on a guest.
    """

    def __init__(self, guest_obj, args):
        """Set default attribute values only.
        @param guest_obj: The guest on which this application is running. (will be inserted from guest::application())
        @param args: containing
                 logger: Logger name for logging.
        """
        try:
            super(FileManagementVmmSide, self).__init__(guest_obj, args)
            self.logger.info("function: FileManagementVmmSide::__init__")
            self.window_id = None

        except Exception as e:
            raise Exception(
                lineno() + " Error: FileManagementHostSide::__init__ " + self.guest_obj.guestname + " " + str(e))

    def open(self):
        """Sends a command to open a fileManagement on the associated guest.
        """
        try:
            self.logger.info("function: FileManagementVmmSide::open")
            self.window_id = self.guest_obj.current_window_id
            self.guest_obj.send("application " + "fileManagement " + str(self.window_id) + " open ")  # some parameters

            self.guest_obj.current_window_id += 1

        except Exception as e:
            raise Exception("error FileManagementVmmSide::open: " + str(e))

    def close(self):
        """Sends a command to close a <fileManagement> on the associated guest.
        """
        try:
            self.logger.info("function: FileManagementVmmSide::close")
            self.guest_obj.send("application " + "fileManagement " + str(self.window_id) + " close ")
        except Exception as e:
            raise Exception("error FileManagementVmmSide:close()" + str(e))

    def recycle(self, path):
        """
        Moves a given file or folder to the Recycle Bin
        @param path: File/Directory to delete
        """
        try:
            self.logger.info("function: FileManagementVmmSide:recycle")
            self.logger.debug("moving {0} to recycle bin".format(path))
            ac = {"path": path}
            pcl_ac = ph.base64pickle(ac)
            pcl_ac = pcl_ac.decode()
            pw_cmd = "application fileManagement " + str(self.window_id) + " recycle " + pcl_ac
            self.is_busy = True
            self.guest_obj.send(pw_cmd)
        except Exception as e:
            raise Exception("error FileManagementVmmSide:recycle() " + str(e))

    def emptyRecycleBin(self):
        """
        Empty the Recycle Bin for all disks
        """
        try:
            self.logger.info("function: FileManagementVmmSide:emptyRecycleBin")
            self.logger.debug("emptying recycle bin")
            pw_cmd = "application fileManagement " + str(self.window_id) + " emptyRecycleBin"
            self.is_busy = True
            self.guest_obj.send(pw_cmd)
        except Exception as e:
            raise Exception("error FileManagementVmmSide:emptyRecycleBin() " + str(e))

    def secureDelete(self, path):
        """
        Secure deletes the provided files/folders
        @param path: File/Directory to delete
        """
        try:
            self.logger.info("function: FileManagementVmmSide:secureDelete")
            self.logger.debug("secure deleting: {0}".format(path))
            ac = {"path": path}
            pcl_ac = ph.base64pickle(ac)
            pcl_ac = pcl_ac.decode()
            pw_cmd = "application fileManagement " + str(self.window_id) + " secureDelete " + pcl_ac
            self.is_busy = True
            self.guest_obj.send(pw_cmd)
        except Exception as e:
            raise Exception("error FileManagementVmmSide:secureDelete " + str(e))

    ##### simple Helper functions created for the validation scenario #####
    def writeTextFile(self, path, content):
        """
        Creates a new textfile and writes the content to it
        @param path: File/Directory to delete
        @param content: content to write
        """
        try:
            self.logger.info("function: FileManagementVmmSide:writeTextFile")
            self.logger.debug("writing Textfile at: {0}".format(path))
            ac = {"path": path,
                  "content": content}
            pcl_ac = ph.base64pickle(ac)
            pcl_ac = pcl_ac.decode()
            pw_cmd = "application fileManagement " + str(self.window_id) + " writeTextFile " + pcl_ac
            self.is_busy = True
            self.guest_obj.send(pw_cmd)
        except Exception as e:
            raise Exception("error FileManagementVmmSide:writeTextFile " + str(e))

    def openFile(self, path):
        """
        Opens a file with its types default application.
        @param path: path of the file
        """
        try:
            self.logger.info("function: FileManagementVmmSide:openFile")
            self.logger.debug("opening file at: {0}".format(path))
            ac = {"path": path}
            pcl_ac = ph.base64pickle(ac)
            pcl_ac = pcl_ac.decode()
            pw_cmd = "application fileManagement " + str(self.window_id) + " openFile " + pcl_ac
            self.is_busy = True
            self.guest_obj.send(pw_cmd)
        except Exception as e:
            raise Exception("error FileManagementVmmSide:openFile " + str(e))
###############################################################################
# Commands to parse on host side
###############################################################################
class FileManagementVmmSideCommands(ApplicationVmmSideCommands):
    """
    Class with all commands for <fileManagement> which will be received from the agent on the guest.

    Static only.
    """

    @staticmethod
    def commands(guest_obj, cmd):
        # cmd[0] = win_id; cmd[1] = state
        module_name = "fileManagement"
        guest_obj.logger.debug("FileManagementVmmSideCommands::commands: " + cmd)
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
class FileManagementGuestSide(ApplicationGuestSide):
    """
    fileManagement implementation of the guest side.

    Usually Windows, Linux guest's
    class attributes
    window_id - The ID for the opened object
    """

    def __init__(self, agent_obj, logger):
        super(FileManagementGuestSide, self).__init__(agent_obj, logger)
        try:
            self.module_name = "fileManagement"
            self.timeout = None
            self.window_is_crushed = None
            self.window_id = None
            self.agent_object = agent_obj

        except Exception as e:
            raise Exception("Error in " + self.__class__.__name__ +
                            ": " + str(e))

    def open(self, args):
        """
        Open a <fileManagement> and save the fileManagement object with an id in a dictionary.
        Set page load timeout to 30 seconds.

        return:
        Send to the host in the known to be good state:
        'application <fileManagement> window_id open'.
        'application <fileManagement> window_id ready'.
        in the error state:
        'application <fileManagement> window_id error'.
        additionally the 'window_is_crushed' attribute is set; so the next
        call will open a new window.

        """
        try:
            arguments = args.split(" ")
            var = arguments[0]
            var2 = arguments[1]

            self.logger.info(self.module_name + "GuestSide::open")
            if var == "type":
                self.logger.debug("wait for start FileManagement...")
                # start application <skeletion>
                self.logger.debug("started!")
            elif var == "type2":
                self.logger.debug("wait for start FileManagement...")
                # start application <skeletion>
                self.logger.debug("started!")
            else:
                self.logger.error("skeletion type " + var +
                                  " not implemented")
                return

            # send some information about the fileManagement state
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " opened")

            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            self.window_is_crushed = False
        except Exception as e:
            self.logger.info("FileManagementGuestSide::open: Close all open windows and clear the fileManagement list")
            subprocess.call(["taskkill", "/IM", "fileManagement.exe", "/F"])
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

    def recycle(self, args):
        """
        Moves the files/directories at the transferred path to the Recycle Bin
        """
        self.logger.info(self.__class__.__name__ +
                         "::recylce")
        ad = ph.base64unpickle(args)
        path = ad["path"]
        if platform.system() == "Windows":
            try:
                self.agent_object.send(
                    "application " + self.module_name + " " + str(self.window_id) + " Recycling File(s): " + path)
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
                if os.path.exists(path) == False:
                    raise Exception("Path does not exist!")
                subprocess.call(["powershell", "Remove-ItemSafely", path])
                # update guest time on host
                gTime = gt.getGuestTime()
                self.agent_object.send("time {0}".format(gTime))
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
                self.window_is_crushed = False
            except Exception as e:
                self.window_is_crushed = True
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
                self.logger.error(
                    "Could not move " + path + " to recycle bin: " + lineno() + ' ' + str(e))
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported at the moment")

    def emptyRecycleBin(self, args=None):
        """
        Empty the recycle bin for all drives
        """
        self.logger.info(self.__class__.__name__ +
                         "::emptyRecycleBin")
        if platform.system() == "Windows":
            try:
                self.agent_object.send(
                    "application " + self.module_name + " " + str(self.window_id) + " Emptying Recycle Bin ")
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
                subprocess.call(["powershell", "Clear-RecycleBin", "-Force"])
                # update guest time on host
                gTime = gt.getGuestTime()
                self.agent_object.send("time {0}".format(gTime))
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
                self.window_is_crushed = False
            except Exception as e:
                self.window_is_crushed = True
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
                self.logger.error(
                    "Could not empty recycle bin: " + lineno() + ' ' + str(e))
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported at the moment")

    def secureDelete(self, args):
        """
        Secure deletion of a file or directory using SDelete
        @param path: Target to delete
        """
        ad = ph.base64unpickle(args)
        path = ad["path"]
        if platform.system() == "Windows":
            self.logger.info(self.__class__.__name__ +
                             "::secureDelete")
            self.logger.debug(self.__class__.__name__ +
                              "::deleting file/directory" + path)
            sysdrive = os.getenv("SystemDrive")
            user = getpass.getuser()
            sdelete_p = "{0}\\Users\\{1}\\Desktop\\fortrace\\contrib\\windows-utils\\sdelete64.exe".format(sysdrive, user)
            try:
                self.agent_object.send(
                    "application " + self.module_name + " " + str(self.window_id) + " Secure deleting File(s): " + path)
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
                # check if target exists
                #if os.path.exists(path) == False:
                #    raise Exception("Path does not exist!")
                self.logger.debug(self.__class__.__name__ + "::Secure Deleting files. This may taka a while...")
                self.agent_object.send("application " + self.module_name + " " + str(
                    self.window_id) + "Secure deleting files. This may taka a while...")
                # Secure delete Files at provided path
                # -s Recurse subdirectories (if directory)
                # -p Number of times to overwrite
                # -r Remove Read-Only attribute.
                # -q run without listing deleted files
                subprocess.call([sdelete_p, "-s", "-r", "-q", "-p", "1", "-nobanner", "-accepteula", path])
                # update guest time on host
                gTime = gt.getGuestTime()
                self.agent_object.send("time {0}".format(gTime))
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
                self.logger.debug(self.__class__.__name__ + "::Files deleted securely")
            except Exception as e:
                self.window_is_crushed = True
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
                self.agent_object.send("application " + self.module_name + " " + str(
                    self.window_id) + " secure deletion of files was not possible")
                self.logger.error("Could not delete files:: " + lineno() + ' ' + str(e))
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported at the moment")

    ##### Helper functions included for validation scenario #####
    def writeTextFile(self, args):
        """
        Writes given string to text file
        """
        self.logger.info(self.__class__.__name__ +
                         "::emptyRecycleBin")
        if platform.system() == "Windows":
            try:
                ad = ph.base64unpickle(args)
                path = ad["path"]
                content = ad["content"]
                self.agent_object.send(
                    "application " + self.module_name + " " + str(self.window_id) + " Writing to textfile ")
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
                f = open(path, "w+")
                f.write("{0}\r\n".format(content))
                f.close()
                # update guest time on host
                gTime = gt.getGuestTime()
                self.agent_object.send("time {0}".format(gTime))
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
                self.window_is_crushed = False
            except Exception as e:
                self.window_is_crushed = True
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
                self.logger.error(
                    "Could not create Textfile: " + lineno() + ' ' + str(e))
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported at the moment")

    def openFile(self, args):
        """
        Open specified file with its default application
        """
        self.logger.info(self.__class__.__name__ +
                         "::openFile")
        if platform.system() == "Windows":
            try:
                ad = ph.base64unpickle(args)
                path = ad["path"]
                self.agent_object.send(
                    "application " + self.module_name + " " + str(self.window_id) + " open file ")
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
                #subprocess.call(["CMD", "/C", "START", "/B", path])
                subprocess.call(["CMD", "/c", path])
                # update guest time on host
                gTime = gt.getGuestTime()
                self.agent_object.send("time {0}".format(gTime))
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
                self.window_is_crushed = False
            except Exception as e:
                self.window_is_crushed = True
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
                self.logger.error(
                    "Could not open file: " + lineno() + ' ' + str(e))
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported at the moment")


###############################################################################
# Commands to parse on guest side
###############################################################################
class FileManagementGuestSideCommands(ApplicationGuestSideCommands):
    """
    Class with all commands for one application.

    call the ask method for an object. The call will be done by a thread, so if the timeout is
    reached, the open application will be closed and opened again.
    Static only.
    """

    @staticmethod
    def commands(agent_obj, obj, cmd):  # commands(obj, cmd) obj from list objlist[window_id] win id in cmd[1]?
        try:
            agent_obj.logger.info("static function FileManagementGuestSideCommands::commands")
            agent_obj.logger.debug("command to parse: " + cmd)
            com = cmd.split(" ")
            args = ""
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
                    tmp_thread.join(1800)  # Wait until the thread is completed
                    if tmp_thread.is_alive():
                        # close fileManagement and set obj to crashed
                        agent_obj.logger.error("thread is alive... time outed")
                        agent_obj.logger.info(
                            "FileManagementGuestSideCommands::commands: Close all open windows and " + "clear the fileManagement list")
                        subprocess.call(["taskkill", "/IM", "fileManagement.exe", "/F"])
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
            raise Exception("Error in FileManagementGuestSideCommands::commands " + str(e))
