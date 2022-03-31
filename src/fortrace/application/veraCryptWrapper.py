# Copyright (C) 2013-2014 Reinhard Stampp
# This file is part of  - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.
# Added by Thomas Schaefer in 2019
from __future__ import absolute_import
from __future__ import print_function

import getpass
import time

try:
    import logging
    import os
    import sys
    import platform
    import threading
    import subprocess
    import inspect  # for listing all method of a class

    # base class VMM side
    from fortrace.application.application import ApplicationVmmSide
    from fortrace.application.application import ApplicationVmmSideCommands

    # base class guest side
    from fortrace.application.application import ApplicationGuestSide
    from fortrace.application.application import ApplicationGuestSideCommands
    from fortrace.utility.line import lineno

    #
    import fortrace.utility.picklehelper as ph
    import fortrace.utility.guesttime as gt

    # file copying
    from shutil import copyfile

except ImportError as ie:
    print(("Import error! in VeraCryptWrapper.py " + str(ie)))
    exit(1)


###############################################################################
# Host side implementation
###############################################################################
class VeraCryptWrapperVmmSide(ApplicationVmmSide):
    """
    This class is a remote control on the host-side to control a real <skeleton>
    running on a guest.
    """

    def __init__(self, guest_obj, args):
        """Set default attribute values only.
        @param guest_obj: The guest on which this application is running. (will be inserted from guest::application())
        @param args: containing
                 logger: Logger name for logging.
        """
        try:
            super(VeraCryptWrapperVmmSide, self).__init__(guest_obj, args)
            self.logger.info("function: VeraCryptWrapperVmmSide::__init__")
            self.window_id = None

        except Exception as e:
            raise Exception(lineno() + " Error: VeraCryptWrapperHostSide::__init__ " + self.guest_obj.guestname + " " + str(e))

    def open(self):
        """Sends a command to open a VeraCryptWrapper on the associated guest.
        """
        try:
            self.logger.info("function: VeraCryptWrapperVmmSide::open")
            self.window_id = self.guest_obj.current_window_id
            self.guest_obj.send("application " + "veraCryptWrapper " + str(self.window_id) + " open")  # some parameters

            self.guest_obj.current_window_id += 1

        except Exception as e:
            raise Exception("error VeraCryptWrapperVmmSide::open: " + str(e))

    def close(self):
        """Sends a command to close a VeraCryptWrapper on the associated guest.
        """
        try:
            self.logger.info("function: VeraCryptWrapperVmmSide::close")
            self.guest_obj.send("application " + "veraCryptWrapper " + str(self.window_id) + " close")
        except Exception as e:
            raise Exception("error VeraCryptWrapperVmmSide:close()" + str(e))

    def createContainer(self, executable, path, size, password, hash = "sha512", encryption = "serpent", filesystem = "FAT"):
        """ Creates an encrypted container with veracrypt
        """
        try:
            ac = {"path": path,
                  "size": size,
                  "password": password,
                  "hash": hash,
                  "encryption": encryption,
                  "filesystem": filesystem,
                  "executable": executable}
            self.logger.info("windowID: " + str(self.window_id))
            pcl_ac = ph.base64pickle(ac)
            pcl_ac = pcl_ac.decode()
            pw_cmd = "application veraCryptWrapper " + str(self.window_id) + " createContainer " + pcl_ac
            self.is_busy = True
            self.guest_obj.send(pw_cmd)
        except Exception as e:
            raise Exception("error: " + str(e))

    def mountContainer(self, executable, path, password, mount_point):
        """ Mounts an encrypted container with veracrypt
        """
        try:
            ac = {"path": path,
                  "password": password,
                  "executable": executable,
                  "mount_point": mount_point}
            self.logger.info("windowID: " + str(self.window_id))
            pcl_ac = ph.base64pickle(ac)
            pcl_ac = pcl_ac.decode()
            pw_cmd = "application veraCryptWrapper " + str(self.window_id) + " mountContainer " + pcl_ac
            self.is_busy = True
            self.guest_obj.send(pw_cmd)
        except Exception as e:
            raise Exception("error: " + str(e))

    def copyToContainer(self, src, dst):
        """ copy to an encrypted container with veracrypt
        """
        try:
            ac = {"src": src,
                  "dst": dst}
            self.logger.info("windowID: " + str(self.window_id))
            pcl_ac = ph.base64pickle(ac)
            pcl_ac = pcl_ac.decode()
            pw_cmd = "application veraCryptWrapper " + str(self.window_id) + " copyToContainer " + pcl_ac
            self.is_busy = True
            self.guest_obj.send(pw_cmd)
        except Exception as e:
            raise Exception("error: " + str(e))

    def unmountContainer(self, executable, mount_point):
        """ unmount an encrypted container with veracrypt
        """
        try:
            ac = {"executable": executable,
                  "mount_point": mount_point}
            self.logger.info("windowID: " + str(self.window_id))
            pcl_ac = ph.base64pickle(ac)
            pcl_ac = pcl_ac.decode()
            pw_cmd = "application veraCryptWrapper " + str(self.window_id) + " dismountContainer " + pcl_ac
            self.is_busy = True
            self.guest_obj.send(pw_cmd)
        except Exception as e:
            raise Exception("error: " + str(e))


###############################################################################
# Commands to parse on host side
###############################################################################
class VeraCryptWrapperVmmSideCommands(ApplicationVmmSideCommands):
    """
    Class with all commands for <skeleton> which will be received from the agent on the guest.

    Static only.
    """

    @staticmethod
    def commands(guest_obj, cmd):
        # cmd[0] = win_id; cmd[1] = state
        module_name = "veraCryptWrapper"
        guest_obj.logger.debug("VeraCryptWrapperVmmSideCommands::commands: " + cmd)
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
class VeraCryptWrapperGuestSide(ApplicationGuestSide):
    """<skeleton> implementation of the guest side.

    Usually Windows, Linux guest's
    class attributes
    window_id - The ID for the opened object
    """

    def __init__(self, agent_obj, logger):
        super(VeraCryptWrapperGuestSide, self).__init__(agent_obj, logger)
        try:
            self.module_name = "veraCryptWrapper"
            self.timeout = None
            self.window_is_crushed = None
            self.window_id = None
            self.agent_object = agent_obj

            #self.veraCryptApp = VeraCryptWrapperGuestSide(agent_obj, logger, self)

        except Exception as e:
            raise Exception("Error in " + self.__class__.__name__ +
                            ": " + str(e))

    def open(self, args):
        """
        Open a <skeleton> and save the skeleton object with an id in a dictionary.
        Set page load timeout to 30 seconds.

        return:
        Send to the host in the known to be good state:
        'application <skeleton> window_id open'.
        'application <skeleton> window_id ready'.
        in the error state:
        'application <skeleton> window_id error'.
        additionally the 'window_is_crushed' attribute is set; so the next
        call will open a new window.

        """
        try:
            arguments = args.split(" ")

            self.logger.info(self.module_name + "GuestSide::open")

            # send some information about the skeleton state
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " opened")

            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            self.window_is_crushed = False
        except Exception as e:
            self.logger.info("VeraCryptWrapperGuestSide::open: Close all open windows and clear the VeraCryptWrapper list")
            subprocess.call(["taskkill", "/IM", "veraCryptWrapper.exe", "/F"])
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
        # self.seleniumDriver.quit()

    def createContainer(self, args):
        '''
        Create a VeraCrypt container with vairous parameters
        :param args: contains the parameters for creating the container
        :return:
        '''
        # implementation
        self.logger.info("creating veracrypt container")
        ad = ph.base64unpickle(args)
        user = getpass.getuser()
        ################
        path = ad["path"]
        size = ad["size"]
        password = ad["password"]
        hash = ad["hash"]
        encryption = ad["encryption"]
        filesystem = ad["filesystem"]
        executable = ad["executable"]
        #################
        self.logger.debug("Executable: " + executable)
        self.logger.debug("Path: " + path)
        self.logger.debug("Size " + size)
        self.logger.debug("Password: " + password)
        self.logger.debug("Hash: " + hash)
        self.logger.debug("Encryption: " + encryption)
        self.logger.debug("Filesystem: " + filesystem)
        #cmd = '"C:\\Program Files\\VeraCrypt\\VeraCrypt Format.exe" /create ' + path + ' /password ' + password + ' /hash ' + hash + ' /encryption ' + encryption + ' /filesystem ' + filesystem + ' /size ' + size + ' /force /quit preferences /silent"'
        #cmd = executable + ' /create ' + path + ' /password ' + password + ' /hash ' + hash + ' /encryption ' + encryption + ' /filesystem ' + filesystem + ' /size ' + size + ' /force /quit preferences /silent"'
        cmd = "{0} /create {1} /password {2} /hash {3} /encryption {4} /filesystem {5} /size {6} /force /quit preferences /silent".format(executable, path, password, hash, encryption, filesystem, size)
        self.logger.debug("command: " + cmd)
        try:
            user = getpass.getuser()
            self.logger.debug("Write password to file")
            f = open(r"C:\Users\{0}\Documents\container.txt".format(user), "w+")
            f.write(r"{0}\r\n".format(password))
            f.close()

            #run command line
            #caution, shell=True can be an issue if input is untrusted
            self.logger.debug("create container")
            subprocess.call(cmd, shell=True)
            self.logger.info("container successfully created")
            # update guest timestamp
            gTime = gt.getGuestTime()
            self.agent_object.send("time {0}".format(gTime))
        except Exception as e:
            self.logger.error("creating container failed: " + lineno() + ' ' + str(e))

    def mountContainer(self, args):
        '''
        Mounting a VeraCrypt container to a given moint point.
        :param args: containing the parameters for mounting the container like the path to the container, password, veracrypt executable and mount point
        :return:
        '''
        self.logger.info("mounting veracrypt container")
        ad = ph.base64unpickle(args)

        ################
        path = ad["path"]
        password = ad["password"]
        executable = ad["executable"]
        mount_point = ad["mount_point"]
        ################
        self.logger.debug("path:" + path)
        self.logger.debug("password:" + executable)
        self.logger.debug("executable:" + executable)
        self.logger.debug("mount:" + mount_point)
        #veracrypt /v myvolume.tc /l x /a /p MyPassword /e /b
        #cmd = '"C:\\Program Files\\VeraCrypt\\VeraCrypt.exe" /v ' + path + ' /l x /a /p ' + password + ' /e /q'
        #cmd = executable + ' /v ' + path + ' /l ' + mount_point + ' /a /p ' + password + ' /e /q'
        cmd = "{0} /v {1} /l {2} /a /p {3} /e /q".format(executable, path, mount_point, password)
        self.logger.debug("command: " + cmd)
        try:
            subprocess.call(cmd, shell=True)
            self.logger.info("container successfully mounted")
            # update guest timestamp
            gTime = gt.getGuestTime()
            self.agent_object.send("time {0}".format(gTime))
            time.sleep(10)
        except Exception as e:
            self.logger.error("mounting container failed: " + lineno() + ' ' + str(e))

    def copyToContainer(self, args):
        '''
        Copy a file from a specific path to a specific path
        :param args: holding src as source path of file to be copied and dst as destination where file should be saved.
        :return:
        '''
        self.logger.info("copy to container")
        ad = ph.base64unpickle(args)

        ################
        src = ad["src"]
        dst = ad["dst"]
        ################
        # WARNING: Workaround for the Windows-Thesis
        if platform.system() == "Windows":
            try:
                self.agent_object.send(
                    "application " + self.module_name + " " + str(self.window_id) + " copying files to container ")
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
                subprocess.call(["CMD", "/c", "copy", src, dst])
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
                self.window_is_crushed = False
            except Exception as e:
                self.window_is_crushed = True
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
                self.logger.error(
                    "Could not empty recycle bin: " + lineno() + ' ' + str(e))
        else:
            try:
                copyfile(src, dst)
                os.remove(src)
                self.logger.info("File successfully copied to encrypted container")
                # update guest timestamp
                gTime = gt.getGuestTime()
                self.agent_object.send("time {0}".format(gTime))
            except Exception as e:
                self.logger.error("copying to container failed: " + lineno() + ' ' + str(e))

    def dismountContainer(self, args):
        '''
        Dismounting a container to finish the operations of VeraCrypt
        :param args: executable = path to veracrypt.exe; mount_point = drive letter of container to be dismounted.
        :return:
        '''
        self.logger.info("unmount container")
        ad = ph.base64unpickle(args)

        ################
        executable = ad["executable"]
        mount_point = ad["mount_point"]
        ################

        # cmd = executable + ' /q /d ' + mount_point
        cmd = "{0} /q /d {1}".format(executable, mount_point)
        try:
            subprocess.call(cmd, shell=True)
            time.sleep(10)
            # update guest timestamp
            gTime = gt.getGuestTime()
            self.agent_object.send("time {0}".format(gTime))
            self.logger.info("container successfully dismounted")
        except Exception as e:
            self.logger.error("dismounting container failed: " + lineno() + ' ' + str(e))


###############################################################################
# Commands to parse on guest side
###############################################################################
class VeraCryptWrapperGuestSideCommands(ApplicationGuestSideCommands):
    """
    Class with all commands for one application.

    call the ask method for an object. The call will be done by a thread, so if the timeout is
    reached, the open application will be closed and opened again.
    Static only.
    """

    @staticmethod
    def commands(agent_obj, obj, cmd):  # commands(obj, cmd) obj from list objlist[window_id] win id in cmd[1]?
        try:
            agent_obj.logger.info("static function VeraCryptWrapperGuestSideCommands::commands")
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
                    tmp_thread.join(50)  # Wait until the thread is completed
                    if tmp_thread.is_alive():
                        # close skeleton and set obj to crashed
                        agent_obj.logger.error("thread is alive... time outed")
                        agent_obj.logger.info(
                            "VeraCryptWrapperGuestSideCommands::commands: Close all open windows and " + "clear the VeraCryptWrapper list")
                        subprocess.call(["taskkill", "/IM", "veraCryptWrapper.exe", "/F"])
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
            raise Exception("Error in VeraCryptWrapperGuestSideCommands::commands " + str(e))
