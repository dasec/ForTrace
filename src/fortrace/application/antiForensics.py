# Copyright <Skeleton> (C) 2013-2014 Reinhard Stampp
# modified by Stephan Maltan in 2021
# This file is part of fortrace - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.

try:
    import logging
    import sys
    import platform
    import threading
    import subprocess
    import inspect  # for listing all method of a class
    import os
    import getpass
    import fortrace.utility.picklehelper as ph
    import fortrace.utility.guesttime as gt

    # base class VMM side
    from fortrace.application.application import ApplicationVmmSide
    from fortrace.application.application import ApplicationVmmSideCommands

    # base class guest side
    from fortrace.application.application import ApplicationGuestSide
    from fortrace.application.application import ApplicationGuestSideCommands
    from fortrace.utility.line import lineno

except ImportError as ie:
    print("Import error! in antiForensics.py " + str(ie))
    exit(1)


###############################################################################
# Host side implementation
###############################################################################
class AntiForensicsVmmSide(ApplicationVmmSide):
    """
    This class is a remote control on the host-side to control a real antiForensics
    running on a guest.
    """

    def __init__(self, guest_obj, args):
        """Set default attribute values only.
        @param guest_obj: The guest on which this application is running. (will be inserted from guest::application())
        @param args: containing
                 logger: Logger name for logging.
        """
        try:
            super(AntiForensicsVmmSide, self).__init__(guest_obj, args)
            self.logger.info("function: antiForensicsVmmSide::__init__")
            self.window_id = None

        except Exception as e:
            raise Exception(
                lineno() + " Error: antiForensicsHostSide::__init__ " + self.guest_obj.guestname + " " + str(e))

    def open(self):
        """Sends a command to open a antiForensics on the associated guest.
        """
        try:
            self.logger.info("function: AntiForensicsVmmSide::open")
            self.window_id = self.guest_obj.current_window_id
            self.guest_obj.send("application " + "antiForensics " + str(self.window_id) + " open ")  # some parameters

            self.guest_obj.current_window_id += 1

        except Exception as e:
            raise Exception("error AntiForensicsVmmSide::open: " + str(e))

    def close(self):
        """Sends a command to close a <antiForensics> on the associated guest.
        """
        try:
            self.logger.info("function: AntiForensicsVmmSide::close")
            self.guest_obj.send("application " + "antiForensics " + str(self.window_id) + " close ")
        except Exception as e:
            raise Exception("error AntiForensicsVmmSide:close()" + str(e))

    def disableRecycleBin(self, status):
        """
        Disable the Recycle Bin for the current user.
        Needs a reboot to take effect.
        @param status: "1"-Recycle Bin disabled, "0"-Recycle Bin enabled
        """
        if status == "1" or status == "0":
            ac = {"status": status}
            pcl_ac = ph.base64pickle(ac)
            pcl_ac = pcl_ac.decode()
            try:
                self.logger.info("function: AntiForensicsVmmSide:disableRecycleBin")
                pw_cmd = "application antiForensics " + str(self.window_id) + " disableRecycleBin " + pcl_ac
                self.is_busy = True
                self.guest_obj.send(pw_cmd)
            except Exception as e:
                raise Exception("error AntiForensicsVmmSide:disableRecycleBin() " + str(e))
        else:
            self.logger.error("function:AntiForensicsVmmSide:disableRecycleBin::invalid value for status")
            sys.exit("invalid value for function")

    def disableThumbcache(self, status):
        """
        Disable the creation of Thumbnails in the thumbnail_*.db files for the current user.
        Needs a reboot to take effect. This has no effect on Thumbache entries created when pictures are opened!
        @param status: "1"-Thumbcache disabled, "0"-Thumbcache enabled
        """
        if status == "1" or status == "0":
            ac = {"status": status}
            pcl_ac = ph.base64pickle(ac)
            pcl_ac = pcl_ac.decode()
            try:
                self.logger.info("function: AntiForensicsVmmSide:disableThumbcache")
                pw_cmd = "application antiForensics " + str(self.window_id) + " disableThumbcache " + pcl_ac
                self.is_busy = True
                self.guest_obj.send(pw_cmd)
            except Exception as e:
                raise Exception("error AntiForensicsVmmSide:disableThumbcache() " + str(e))
        else:
            self.logger.error("function:AntiForensicsVmmSide:disableRecycleBin::invalid value for status")
            sys.exit("invalid value for function")

    def disablePrefetch(self, status):
        """
        Disable the creation of Prefetch files systemwide.
        Needs a reboot to take effect.
        @param status: 1-Prefetch disabled, 0-Prefetch enabled
        """
        if status == "1" or status == "0":
            ac = {"status": status}
            pcl_ac = ph.base64pickle(ac)
            pcl_ac = pcl_ac.decode()
            try:
                self.logger.info("function:AntiForensicsVmmSide:disablePrefetch")
                pw_cmd = "application antiForensics " + str(self.window_id) + " disablePrefetch " + pcl_ac
                self.is_busy = True
                self.guest_obj.send(pw_cmd)
            except Exception as e:
                raise Exception("error AntiForensicsVmmSide:disablePrefetch() " + str(e))
        else:
            self.logger.error("function:AntiForensicsVmmSide:disablePrefetch::Invalid value for status")
            sys.exit("invalid value for function")

    def disableEventLog(self, status):
        """
        Disable the Event Log service systemwide
        Needs a reboot to take effect.
        WARNING: Disables the Event Log service and allows deletion of Event Log files, event logging itself remains active!
        @param status: 1-Event Log service disabled, 0-Event Log service enabled
        """
        if status == "1" or status == "0":
            ac = {"status": status}
            pcl_ac = ph.base64pickle(ac)
            pcl_ac = pcl_ac.decode()
            try:
                self.logger.info("function: AntiForensicsVmmSide:disableEventLog")
                pw_cmd = "application antiForensics " + str(self.window_id) + " disableEventLog " + pcl_ac
                self.is_busy = True
                self.guest_obj.send(pw_cmd)
            except Exception as e:
                raise Exception("error AntiForensicsVmmSide:disableEventLog() " + str(e))
        else:
            self.logger.error("function:AntiForensicsVmmSide:disableEventLog::Invalid value for status")
            sys.exit("invalid value for function")

    def disableUserAssist(self, status):
        """
        Disables the creation of entries within the userAssist key
        Needs a reboot to take effect.
        @param status: 1-User Assist disabled, 0-User Assist enabled
        """
        if status == "1" or status == "0":
            ac = {"status": status}
            pcl_ac = ph.base64pickle(ac)
            pcl_ac = pcl_ac.decode()
            try:
                self.logger.info("function: AntiForensicsVmmSide:disableUserAssist")
                pw_cmd = "application antiForensics " + str(self.window_id) + " disableUserAssist " +pcl_ac
                self.is_busy = True
                self.guest_obj.send(pw_cmd)
            except Exception as e:
                raise Exception("error AntiForensicsVmmSide:disableUserAssist() " + str(e))
        else:
            self.logger.error("function:AntiForensicsVmmSide:disableUserAssist::Invalid value for status")
            sys.exit("invalid value for function")

    def disableHibernation(self, status):
        """
        Disables the creation the hibernation file when the system goes to sleep
        Needs a reboot to take effect.
        NOTE: Can be used on every (Windows) System, but in most VM systems hibernation cannot be enabled
        @param status: 1 - hibernation disabled, 0 - hibernation
        """
        ac = {"status": status}
        pcl_ac = ph.base64pickle(ac)
        pcl_ac = pcl_ac.decode()
        if status == "1" or status == "0":
            try:
                self.logger.info("function: AntiForensicsVmmSide:disableHibernation")
                pw_cmd = "application antiForensics " + str(self.window_id) + " disableHibernation " + pcl_ac
                self.is_busy = True
                self.guest_obj.send(pw_cmd)
            except Exception as e:
                raise Exception("error AntiForensicsVmmSide:disableHibernation() " + str(e))
        else:
            self.logger.error("function:AntiForensicsVmmSide:disableHibernation::Invalid value for status")
            sys.exit("invalid value for function")

    def disablePagefile(self, status):
        """
        Disables the usage of the page file so it wont be created
        Needs a reboot to take effect.
        @param status: 1 - page file is disabled, 0 - page file is enabled
        """
        ac = {"status": status}
        pcl_ac = ph.base64pickle(ac)
        pcl_ac = pcl_ac.decode()
        if status == "1" or status == "0":
            try:
                self.logger.info("function: AntiForensicsVmmSide:disablePagefile")
                pw_cmd = "application antiForensics " + str(self.window_id) + " disablePagefile " + pcl_ac
                self.is_busy = True
                self.guest_obj.send(pw_cmd)
            except Exception as e:
                raise Exception("error AntiForensicsVmmSide:disablePagefile() " + str(e))
        else:
            self.logger.error("function:AntiForensicsVmmSide:disablePagefile::Invalid value for status")
            sys.exit("invalid value for function")

    def clearUserAssist(self):
        """
        Clears created UserAssist entries in the Registry for the current user
        """
        try:
            self.logger.info("function: AntiForensicsVmmSide:clearUserAssist")
            pw_cmd = "application antiForensics " + str(self.window_id) + " clearUserAssist"
            self.is_busy = True
            self.guest_obj.send(pw_cmd)
        except Exception as e:
            raise Exception("error AntiForensicsVmmSide:clearUserAssist: " + str(e))

    def clearRecentDocs(self):
        """
        Clears created RecentDocs entries from the Registry for the current user
        """
        try:
            self.logger.info("function: AntiForensicsVmmSide:clearRecentDocs")
            pw_cmd = "application antiForensics " + str(self.window_id) + " clearRecentDocs"
            self.is_busy = True
            self.guest_obj.send(pw_cmd)
        except Exception as e:
            raise Exception("error AntiForensicsVmmSide:clearRecentDocs: " + str(e))

    def disableRecentFiles(self, status):
        """
        Disable the creation of "Recent Files" in the Explorer, as well as the creation of "RecentDocs" Entries
        within the Registry and the creation of jump lists.
        @param status: 1-Recent Files disabled, 0-Recent Files enabled
        """
        if status == "1" or status == "0":
            ac = {"status": status}
            pcl_ac = ph.base64pickle(ac)
            pcl_ac = pcl_ac.decode()
            try:
                self.logger.info("function: AntiForensicsVmmSide:disableRecentFiles")
                pw_cmd = "application antiForensics " + str(self.window_id) + " disableRecentFiles " + pcl_ac
                self.is_busy = True
                self.guest_obj.send(pw_cmd)
            except Exception as e:
                raise Exception("error AntiForensicsVmmSide:disableRecentFiles() " + str(e))
        else:
            self.logger.error("function:AntiForensicsVmmSide:disableRecentFiles::Invalid value for status")
            sys.exit("invalid value for function")

    def clearEventLogEntries(self, logfile="all"):
        """
        Clears either all Event logs, or provided specific files
        WARNING: Only works, if Event Log Service is running!
        @param logfile: Logfile to delete ("all", "system", "security", "application", "setup")
        """
        ac = {"logfile": logfile}
        pcl_ac = ph.base64pickle(ac)
        pcl_ac = pcl_ac.decode()
        try:
            self.logger.info("function: AntiForensicsVmmSide:clearEventLog")
            pw_cmd = "application antiForensics " + str(self.window_id) + " clearEventLogEntries " + pcl_ac
            self.is_busy = True
            self.guest_obj.send(pw_cmd)
        except Exception as e:
            raise Exception("error AntiForensicsVmmSide:clearEventLog() " + str(e))

    def clearEventLogFiles(self):
        """
        Clears all event log files.
        Note: only working, when Event Log service is disabled!
        WARNING: This only works, if the Event Log service is not running!
        """
        try:
            self.logger.info("function: AntiForensicsVmmSide:clearEventLogFiles")
            pw_cmd = "application antiForensics " + str(self.window_id) + " clearEventLogFiles "
            self.is_busy = True
            self.guest_obj.send(pw_cmd)
        except Exception as e:
            raise Exception("error AntiForensicsVmmSide:clearEventLogFiles() " + str(e))

    def clearPrefetch(self):
        """
        Clears existing Prefetch files.
        """
        try:
            self.logger.info("function: AntiForensicsVmmSide:clearPrefetch")
            pw_cmd = "application antiForensics " + str(self.window_id) + " clearPrefetch"
            self.is_busy = True
            self.guest_obj.send(pw_cmd)
        except Exception as e:
            raise Exception("error AntiForensicsVmmSide:clearPrefetch() " + str(e))

    def clearThumbcache(self, user):
        """
        clear existing Thumbcache database files
        Recommendation: Use while target user in not logged in, or some files may not be deletable
        """
        ac = {"user": user}
        pcl_ac = ph.base64pickle(ac)
        pcl_ac = pcl_ac.decode()
        try:
            self.logger.info("function: AntiForensicsVmmSide:clearThumbcache")
            pw_cmd = "application antiForensics " + str(self.window_id) + " clearThumbcache " + pcl_ac
            self.is_busy = True
            self.guest_obj.send(pw_cmd)
        except Exception as e:
            raise Exception("error AntiForensicsVmmSide:clearThumbcache " + str(e))

    def clearJumpLists(self, user):
        """
        clear existing Jump list files for target user
        """
        ac = {"user": user}
        pcl_ac = ph.base64pickle(ac)
        pcl_ac = pcl_ac.decode()
        try:
            self.logger.info("function: AntiForensicsVmmSide:clearJumpLists")
            pw_cmd = "application antiForensics " + str(self.window_id) + " clearJumpLists " + pcl_ac
            self.is_busy = True
            self.guest_obj.send(pw_cmd)
        except Exception as e:
            raise Exception("error AntiForensicsVmmSide:clearJumpLists " + str(e))

    def setRegistryKey(self, key, val_type, val_name, val):
        """
        Allow the user to set any desired Registry key value
        @param key: name of the key
        @param val_type: value type, e.g. REG_DWORD
        @param val_name: name of the value to create/change
        @param val: value data, e.g. "0", "1"
        """
        ac = {"key": key,
              "val_type": val_type,
              "val_name": val_name,
              "val": val
              }

        pcl_ac = ph.base64pickle(ac)
        pcl_ac = pcl_ac.decode()
        try:
            self.logger.info("function: AntiForensicsVmmSide:setRegistryKey")
            pw_cmd = "application antiForensics " + str(self.window_id) + " setRegistryKey " + pcl_ac
            self.is_busy = True
            self.guest_obj.send(pw_cmd)
        except Exception as e:
            raise Exception("error AntiForensicsVmmSide:setRegistryKey " + str(e))

    def deleteRegistryKey(self, key, value=""):
        """
         Allow the user to delete any desired Registry key/value
         @param key: name of the key
         @param value: key value to delete (optional)
         """
        ac = {"key": key,
              "value": value}
        pcl_ac = ph.base64pickle(ac)
        pcl_ac = pcl_ac.decode()
        try:
            self.logger.info("function: AntiForensicsVmmSide:deleteRegistryKey")
            pw_cmd = "application antiForensics " + str(self.window_id) + " deleteRegistryKey " + pcl_ac
            self.is_busy = True
            self.guest_obj.send(pw_cmd)
        except Exception as e:
            raise Exception("error AntiForensicsVmmSide:deleteRegistryKey " + str(e))

###############################################################################
# Commands to parse on host side
###############################################################################
class AntiForensicsVmmSideCommands(ApplicationVmmSideCommands):
    """
    Class with all commands for <antiForensics> which will be received from the agent on the guest.

    Static only.
    """
    @staticmethod
    def commands(guest_obj, cmd):
        # cmd[0] = win_id; cmd[1] = state
        module_name = "antiForensics"
        guest_obj.logger.debug("antiForensicsVmmSideCommands::commands: " + cmd)
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
class AntiForensicsGuestSide(ApplicationGuestSide):
    """antiForensics implementation of the guest side.
    Usually Windows guest's
    class attributes
    window_id - The ID for the opened object
    """

    def __init__(self, agent_obj, logger):
        super(AntiForensicsGuestSide, self).__init__(agent_obj, logger)
        try:
            self.module_name = "antiForensics"
            self.timeout = None
            self.window_is_crushed = None
            self.window_id = None
            self.agent_object = agent_obj

        except Exception as e:
            raise Exception("Error in " + self.__class__.__name__ +
                            ": " + str(e))

    def open(self, args):
        """
        Open a antiForensics object and save the antiForensics object with an id in a dictionary.
        Set page load timeout to 30 seconds.

        return:
        Send to the host in the known to be good state:
        'application <antiForensics> window_id open'.
        'application <antiForensics> window_id ready'.
        in the error state:
        'application <antiForensics> window_id error'.
        additionally the 'window_is_crushed' attribute is set; so the next
        call will open a new window.

        """
        try:
            arguments = args.split(" ")
            var = arguments[0]
            var2 = arguments[1]

            self.logger.info(self.module_name + "GuestSide::open")
            if var == "type":
                self.logger.debug("wait for start antiForensics...")
                # start application <skeletion>
                self.logger.debug("started!")
            elif var == "type2":
                self.logger.debug("wait for start antiForensics...")
                # start application <skeletion>
                self.logger.debug("started!")
            else:
                self.logger.error("skeletion type " + var +
                                  " not implemented")
                return

            # send some information about the antiForensics state
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " opened")
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            self.window_is_crushed = False
        except Exception as e:
            self.logger.info("antiForensicsGuestSide::open: Close all open windows and clear the antiForensics list")
            subprocess.call(["taskkill", "/IM", "antiForensics.exe", "/F"])
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

    def disableRecycleBin(self, args):
        """
        Disable the usage of the Recycle Bin for the current user
        """
        self.logger.info(self.__class__.__name__ +
                         "::disableRecycleBin ")
        ad = ph.base64unpickle(args)
        status = ad["status"]
        if platform.system() == "Windows":
            self.agent_object.send(
            "application " + self.module_name + " " + str(self.window_id) + " disabling Recycle Bin")
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
            # Computer\HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\BitBucket\Volume\
            #set the necessary Registry value
            key = r"HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer"
            val_name = "NoRecycleFiles"
            val_type = "REG_DWORD"
            self.__setRegistryValue(key, val_type, val_name, status)
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            self.window_is_crushed = False
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported")

    def disablePrefetch(self, args):
        """
        Disable creation of Prefetch files
        """
        self.logger.info(self.__class__.__name__ +
                         "::disablePrefetcher")
        ad = ph.base64unpickle(args)
        status = ad["status"]
        enable = ""
        sysmain = ""
        if platform.system() == "Windows":
            if status == "1":
                #enable = "0"
                sysmain = "4"  # 4 means disabled
            elif status == "0":
                #enable = "3"
                sysmain = "2" # 2 means automatic startup
            self.agent_object.send(
                "application " + self.module_name + " " + str(self.window_id) + " Changing Creation of Prefetch files")
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
            #self.logger.debug(self.__class__.__name__ +
            #                  "::Set EnablePrefetcher to: " + enable)
            #key = r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters"
            #val_name = "EnablePrefetcher"
            #val_type = "REG_DWORD"
            #self.__setRegistryValue(key, val_type, val_name, enable)
            self.logger.debug(self.__class__.__name__ +
                              "::Set SysMain Service start to: " + sysmain)
            key2 = r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\SysMain"
            val2_name = "start"
            val2_type = "REG_DWORD"
            self.__setRegistryValue(key2, val2_type, val2_name, sysmain)
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            self.window_is_crushed = False
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported")

    def disableEventLog(self, args):
        """
        Disable creation of Logfiles
        """
        self.logger.info(self.__class__.__name__ +
                         "::disableEventLog")
        ad = ph.base64unpickle(args)
        status = ad["status"]
        if platform.system() == "Windows":
            # choose the correct value for the Registry value to set
            start = ""
            if status == "1":
                start = "4"
            elif status == "0":
                start = "2"
            # set the Registry value
            key = r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\EventLog"
            val_name = "start"
            val_type = "REG_DWORD"
            self.agent_object.send(
                "application " + self.module_name + " " + str(self.window_id) + " disabling Event Log service")
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
            self.__setRegistryValue(key, val_type, val_name, start)
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            self.window_is_crushed = False
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported")

    def disableThumbcache(self, args):
        """
        Disables the creation of Thumbcache entries when using the Exporer
        """
        self.logger.info(self.__class__.__name__ +
                         "::disableThumbcache")
        ad = ph.base64unpickle(args)
        status = ad["status"]
        if platform.system() == "Windows":
            self.agent_object.send(
                "application " + self.module_name + " " + str(self.window_id) + " disabling Creation of Thumbcache")
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
            # Disable Creation of Thumbcache entries
            key3 = r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
            val32_name = "DisableThumbnails"
            val_type = "REG_DWORD"
            self.logger.debug(self.__class__.__name__ + "::setting value")
            self.__setRegistryValue(key3, val_type, val32_name, status)
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            self.window_is_crushed = False
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported")

    def disableUserAssist(self, args):
        self.logger.info(self.__class__.__name__ +
                         "::disableUserAssist")
        ad = ph.base64unpickle(args)
        status = ad["status"]
        if platform.system() == "Windows":
            # invert the status argument to get the correct value for the Registry
            track = ""
            if status == "1":
                track = "0"
            if status == "0":
                track = "1"
            self.agent_object.send(
                "application " + self.module_name + " " + str(self.window_id) + " changing Creation of UserAssist entries")
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
            self.logger.debug(self.__class__.__name__ + "::Set Start_TrackProgs to " + track)
            self.logger.debug(self.__class__.__name__ + "::Set Start_TrackEnabled to " + track)
            # set the necessary Registry values
            key = r"HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
            val_name = "Start_TrackProgs"
            val2_name = "Start_TrackEnabled"
            val_type = "REG_DWORD"
            self.__setRegistryValue(key, val_type, val_name, track)
            self.__setRegistryValue(key, val_type, val2_name, track)
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            self.window_is_crushed = False
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported")

    def clearUserAssist(self, args=None):
        self.logger.info(self.__class__.__name__ +
                         "::clearUserAssist")
        if platform.system() == "Windows":
            self.logger.debug(self.__class__.__name__ + "::Clearing existing UserAssist entries")
            key = r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist"
            try:
                self.agent_object.send(
                    "application " + self.module_name + " " + str(self.window_id) + " clearing UserAssist entries")
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
                # Delete the UserAssist Registry Key
                self.__deleteRegistryKey(key)
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
                self.window_is_crushed = False
            except Exception as e:
                self.window_is_crushed = True
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
                self.logger.error("Could not delete UserAssist entries:" + lineno() + ' ' + str(e))

        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported")

    def clearRecentDocs(self, args=None):
        self.logger.info(self.__class__.__name__ +
                         "::clearRecentDocs")
        if platform.system() == "Windows":
            self.logger.debug(self.__class__.__name__ + "::Clearing existing RecentDocs entries")
            try:
                self.agent_object.send(
                    "application " + self.module_name + " " + str(self.window_id) + " clearing RecentDocs entries")
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
                # Delete the RecentDocs Registry Key
                key = r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs"
                self.__deleteRegistryKey(key)
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
                self.window_is_crushed = False
            except Exception as e:
                self.window_is_crushed = True
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
                self.logger.error("Could not delete RecentDocs entries:" + lineno() + ' ' + str(e))
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported")

    def disableRecentFiles(self, args):
        self.logger.info(self.__class__.__name__ +
                         "::disableRecentFiles")
        ad = ph.base64unpickle(args)
        status = ad["status"]
        # invert the status argument to get the correct value for the Registry
        if platform.system() == "Windows":
            track_docs = ""
            if status == "1":
                track_docs = "0"
            elif status == "0":
                track_docs = "1"
            self.agent_object.send(
                "application " + self.module_name + " " + str(self.window_id) + " disabling Creation of RecentFiles Entries")
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
            self.logger.debug(self.__class__.__name__ + "::Set Start_TrackDocs to " + track_docs)
            key = r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
            val_name = "Start_TrackDocs"
            val_type = "REG_DWORD"
            self.__setRegistryValue(key, val_type, val_name, track_docs)
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            self.window_is_crushed = False
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported")

    def disablePagefile(self, args):
        self.logger.info(self.__class__.__name__ +
                         "::disablePagefile")
        ad = ph.base64unpickle(args)
        status = ad["status"]
        if platform.system() == "Windows":
            self.agent_object.send(
                "application " + self.module_name + " " + str(
                    self.window_id) + " disabling usage of the page file")
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
            self.logger.debug(self.__class__.__name__ + "::Set ClearPageFileAtShutdown to " + status)
            # Disable usage of page file (according to MS this can affect the performance)
            key3 = r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
            val3_name = "PagingFiles"
            val3_type = "REG_MULTI_SZ"
            set_status = ""
            if status == "1":
                set_status = ""
            if status == "0":
                set_status = r"?:\pagefile.sys"
            self.__setRegistryValue(key3, val3_type, val3_name, set_status)
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            self.window_is_crushed = False
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported")

    def disableHibernation(self, args):
        self.logger.info(self.__class__.__name__ +
                         "::disableHibernation")
        ad = ph.base64unpickle(args)
        status = ad["status"]
        if platform.system() == "Windows":
            hibernate = ""
            if status == "1":
                hibernate = "0"
            if status == "0":
                hibernate = "1"
            self.agent_object.send(
                "application " + self.module_name + " " + str(
                    self.window_id) + " disabling Creation of hibernation file")
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
            self.logger.debug(self.__class__.__name__ + "::Set HibernateEnabled to " + hibernate)
            key = r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Power"
            val_name = "HibernateEnabled"
            val_type = "REG_DWORD"
            self.__setRegistryValue(key, val_type, val_name, hibernate)
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            self.window_is_crushed = False
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported")

    def clearEventLogEntries(self, args=None):
        """
        Clear either all Event Log files or specific provided ones
        Note: Event Log Entries can only be cleared if it wasn't disabled
        """
        self.logger.info(self.__class__.__name__ +
                         "::clearEventLog")
        ad = ph.base64unpickle(args)
        logfile = ad["logfile"]
        if platform.system() == "Windows":
            # delete all log entries
            if logfile.upper() == "ALL":
                self.logger.debug(self.__class__.__name__ +
                                 "::clearing complete event log")
                try:
                    self.agent_object.send(
                        "application " + self.module_name + " " + str(
                            self.window_id) + " Clearing Event Log entries")
                    self.agent_object.send(
                        "application " + self.module_name + " " + str(
                            self.window_id) + " WARNING: This function won't work if the eventLog was disabled before. In this Case use clearEventLogFiles instead (deletes the Event Log files")
                    self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
                    cmd = r"for /f %x in ('wevtutil enum-logs') do wevtutil clear-log %x"
                    subprocess.call(["CMD", "/c", cmd])
                    # update guest time on host
                    gTime = gt.getGuestTime()
                    self.agent_object.send("time {0}".format(gTime))
                    self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
                    self.window_is_crushed = False
                except Exception as e:
                    self.window_is_crushed = True
                    self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
                    self.logger.error(
                        "Could not delete all event log entries: " + lineno() + ' ' + str(e))
            # Only delete entries for the specified log
            else:
                self.logger.debug(self.__class__.__name__ +
                                 "::clearing {0} log".format(logfile))
                try:
                    self.agent_object.send(
                        "application " + self.module_name + " " + str(
                            self.window_id) + " Clearing Event Log: " + logfile)
                    self.agent_object.send(
                        "application " + self.module_name + " " + str(
                            self.window_id) + " WARNING: Deleting individual Event Logs is only working id the Event Log Service is still running!")
                    self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
                    subprocess.call(["CMD", "/c", "wevtutil", "cl", logfile])
                    self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
                    self.window_is_crushed = False
                except Exception as e:
                    self.window_is_crushed = True
                    self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
                    self.logger.error(
                        "Could not delete event log entries for {0}: ".format(logfile) + lineno() + ' ' + str(e))
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported")

    def clearEventLogFiles(self, args=None):
        """
        Clear either all Event Log files or specific provided ones
        Note: Event Log Files can only be cleared if the Service was disabled before
        """
        self.logger.info(self.__class__.__name__ +
                         "::clearEventLogFiles")
        if platform.system() == "Windows":
            self.logger.debug(self.__class__.__name__ +
                             "::deleting all log files")
            try:
                self.agent_object.send(
                    "application " + self.module_name + " " + str(
                        self.window_id) + " Clearing Event Log files")
                self.agent_object.send(
                    "application " + self.module_name + " " + str(
                        self.window_id) + " WARNING: This function won't work if the eventLog is still running. In this Case use clearEventLogEntries instead (keeps the Event Log files)")
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
                sysdrive = os.getenv("SystemDrive")
                # Secure delete all files in the log path
                log_p = "{0}\\Windows\\System32\\winevt\\Logs\\*".format(sysdrive)
                self.__secureDelete(log_p)
                # update guest time on host
                gTime = gt.getGuestTime()
                self.agent_object.send("time {0}".format(gTime))
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
                self.window_is_crushed = False
            except Exception as e:
                self.window_is_crushed = True
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
                self.logger.error(
                    "Could not delete all event log files: " + lineno() + ' ' + str(e))
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported")

    def clearPrefetch(self, args=None):
        """
        Clears existing Prefetch data
        """
        self.logger.info(self.__class__.__name__ +
                         "::clearPrefetch")
        if platform.system() == "Windows":
            sysdrive = os.getenv("SystemDrive")
            prefetch_p = "{0}\\Windows\\Prefetch".format(sysdrive)
            try:
                self.agent_object.send(
                    "application " + self.module_name + " " + str(
                        self.window_id) + " Deleting Prefetch files")
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
                self.logger.debug(self.__class__.__name__ + "::Deleting Prefetch Data")
                # secure delete all files in the prefetch directory
                self.__secureDelete(prefetch_p)
                # update guest time on host
                gTime = gt.getGuestTime()
                self.agent_object.send("time {0}".format(gTime))
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
                self.logger.debug(self.__class__.__name__ + "::Prefetch data deleted securely")
            except Exception as e:
                self.window_is_crushed = True
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " secure deletion of Prefetch data was not possible")
                self.logger.error("Could not delete files:: " + lineno() + ' ' + str(e))
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported")

    def clearJumpLists(self, args=None):
        """
        Clears existing Jumplist data
        """
        self.logger.info(self.__class__.__name__ +
                         "::clearJumpLists")
        if platform.system() == "Windows":
            ad = ph.base64unpickle(args)
            userdel = ad["user"]
            sysdrive = os.getenv("SystemDrive")
            auto_jumplist_p = "{0}\\Users\\{1}\\AppData\\Roaming\\Microsoft\\Windows\\Recent\\AutomaticDestinations".format(sysdrive, userdel)
            custom_jumplist_p = "{0}\\Users\\{1}\\AppData\\Roaming\\Microsoft\\Windows\\Recent\\CustomDestinations".format(sysdrive, userdel)
            try:
                self.agent_object.send(
                    "application " + self.module_name + " " + str(
                        self.window_id) + " Deleting Jump list files")
                # Secure delete the AutomaticDestinations folder, followed by the CustomDestinations Folder
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
                self.logger.debug(self.__class__.__name__ + "::Deleting automatic Jump list Data")
                self.__secureDelete(auto_jumplist_p)
                self.logger.debug(self.__class__.__name__ + "::Deleting custom Jump list Data")
                self.__secureDelete(custom_jumplist_p)
                # update guest time on host
                gTime = gt.getGuestTime()
                self.agent_object.send("time {0}".format(gTime))
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
                self.logger.debug(self.__class__.__name__ + "::Jump list data deleted securely")
            except Exception as e:
                self.window_is_crushed = True
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " secure deletion of Jump list data was not possible")
                self.logger.error("Could not delete files:: " + lineno() + ' ' + str(e))
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported")

    def clearThumbcache(self, args=None):
        self.logger.info(self.__class__.__name__ +
                         "::clearThumbcache")
        if platform.system() == "Windows":
            sysdrive = os.getenv("SystemDrive")
            ad = ph.base64unpickle(args)
            userdel = ad["user"]
            user = getpass.getuser()
            if userdel == "":
                userdel = user
            sdelete_p = "{0}\\Users\\{1}\\Desktop\\fortrace\\contrib\\windows-utils\\sdelete64.exe".format(sysdrive, user)
            thumbcache_p = "{0}\\Users\\{1}\\AppData\\Local\\Microsoft\\Windows\\Explorer\\thumbcache_*".format(sysdrive, userdel)
            try:
                self.agent_object.send(
                    "application " + self.module_name + " " + str(
                        self.window_id) + " Deleting Thumbcache files")
                # Some files may be in access, even if the thumbnail creation is disabled. Therefore it is recommended to clear the Thumbcache out of another users context
                self.agent_object.send(
                    "application " + self.module_name + " " + str(
                        self.window_id) + "WARNING: Either disable the Thumbcache before deletion or call the deletion function from another user. Otherwise some Files may be blocked")
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
                self.logger.debug(self.__class__.__name__ + "::Deleting Thumbcache Data")
                # It is planned to verify, if the path to delete really exists- Wildcards will cause problems there, so the deletion in made within the function
                # Secure delete thumbcache databases
                # -s Recurse subdirectories (if directory)
                # -p Number of times to overwrite
                # -r Remove Read-Only attribute.
                # -q run without listing deleted files
                subprocess.call([sdelete_p, "-s", "-r", "-q", "-p", "3", "-nobanner", "-accepteula", thumbcache_p])
                # update guest time on host
                gTime = gt.getGuestTime()
                self.agent_object.send("time {0}".format(gTime))
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
                self.logger.debug(self.__class__.__name__ + "::Thumbcache files deleted securely")
            except Exception as e:
                self.window_is_crushed = True
                self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
                self.agent_object.send("application " + self.module_name + " " + str(
                    self.window_id) + " secure deletion of Thumbcache data was not possible")
                self.logger.error("Could not delete files:: " + lineno() + ' ' + str(e))
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported")

    def setRegistryKey(self, args):
        """
        This functions allows to set any registry key wanted by the user
        """
        self.logger.info(self.__class__.__name__ +
                         "::setRegistryKey")
        ad = ph.base64unpickle(args)
        key = ad["key"]
        val_type = ad["val_type"]
        val_name = ad["val_name"]
        val = ad["val"]
        if platform.system() == "Windows":
            self.agent_object.send(
                "application " + self.module_name + " " + str(
                    self.window_id) + " setting Registry Key " + key + " " + val_type + " " + val_name + " " + val)
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
            # Set the Registry key value, that was handed over
            self.logger.debug(self.__class__.__name__ + "::Setting Registry key")
            self.__setRegistryValue(key, val_type, val_name, val)
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            self.window_is_crushed = False
        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported")

    def deleteRegistryKey(self, args):
        """
        Deletes target Registry key
        """
        self.logger.info(self.__class__.__name__ +
                         "::deleteRegistryKey")
        ad = ph.base64unpickle(args)
        key = ad["key"]
        value = ad["value"]
        if platform.system() == "Windows":
            self.agent_object.send(
                "application " + self.module_name + " " + str(
                    self.window_id) + " deleting Registry Key " + key + " - value: " + value)
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
            self.logger.debug(self.__class__.__name__ + "::Setting Registry key")
            # If no value was given, then delete the Registry key
            if value == "":
                self.__deleteRegistryKey(key)
            # else delete the provided value
            else:
                self.__deleteRegistryKey(key, value)
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            self.window_is_crushed = False

        else:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Unknown System Platform, only Windows is supported")

    def __deleteRegistryKey(self, key, value=None):
        """
        Delete the provided Registry Entry (key/value)
        """
        self.logger.info(self.__class__.__name__ + "::SetRegistryValue")
        self.logger.debug(self.__class__.__name__ + "::entry:" + key)
        try:
            # Differ, if a value was provided, or not
            if value is None:
                subprocess.call(["CMD", "/c", "reg", "delete", key, "/f"])
            else:
                subprocess.call(["CMD", "/c", "reg", "delete", key, "/v", value, "/f"])
            # update guest time on host
            gTime = gt.getGuestTime()
            self.agent_object.send("time {0}".format(gTime))
        except Exception as e:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Could not set Registry Key:" + lineno() + ' ' + str(e))

    def __setRegistryValue(self, key, val_type, val_name, val):
        """
        Set provided Registry Key value
        """
        self.logger.info(self.__class__.__name__ + "::SetRegistryValue")
        self.logger.debug(self.__class__.__name__ + "::key:" + key)
        self.logger.debug(self.__class__.__name__ + "::type:" + val_type)
        self.logger.debug(self.__class__.__name__ + "::name:" + val_name)
        self.logger.debug(self.__class__.__name__ + "::value:" + val)
        # Set the provided Registry value
        try:
            # Parameter:
            # /v Key value
            # /t Value type
            # /d Value data
            # /f Overwrite existing data
            subprocess.call(["CMD", "/c", "REG", "ADD", key, "/v", val_name, "/t", val_type, "/d", val, "/f"])
            # update guest time on host
            gTime = gt.getGuestTime()
            self.agent_object.send("time {0}".format(gTime))
        except Exception as e:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Could not set Registry Key:" + lineno() + ' ' + str(e))

    def __secureDelete(self, path):
        """
        Secure deletion of a directory using the cipher command
        @param path: file(s) to delete
        """
        self.logger.info(self.__class__.__name__ +
                        "::__secureDelete")
        self.logger.debug(self.__class__.__name__ +
                        "::deleting file(s)" + path)
        sysdrive = os.getenv("SystemDrive")
        user = getpass.getuser()
        sdelete_p = "{0}\\Users\\{1}\\Desktop\\fortrace\\contrib\\windows-utils\\sdelete64.exe".format(sysdrive, user)
        try:
            self.logger.debug(self.__class__.__name__ + "::Secure Deleting file(s). This may taka a while...")
            self.agent_object.send("application " + self.module_name + " " + str(
                self.window_id) + "Secure Deleting user files. This may taka a while...")
            # Secure delete Files at provided path
            # -s Recurse subdirectories (if directory)
            # -p Number of times to overwrite
            # -r Remove Read-Only attribute.
            # -q run without listing deleted files
            subprocess.call([sdelete_p, "-s", "-r", "-q", "-p", "1", "-nobanner", "-accepteula", path])
            self.logger.debug(self.__class__.__name__ + "::File(s) deleted securely")
        except Exception as e:
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " secure deletion of file(s) was not possible")
            self.logger.error("Could not delete file(s):: " + lineno() + ' ' + str(e))
###############################################################################
# Commands to parse on guest side
###############################################################################
class AntiForensicsGuestSideCommands(ApplicationGuestSideCommands):
    """
    Class with all commands for one application.

    call the ask method for an object. The call will be done by a thread, so if the timeout is
    reached, the open application will be closed and opened again.
    Static only.
    """

    @staticmethod
    def commands(agent_obj, obj, cmd):  # commands(obj, cmd) obj from list objlist[window_id] win id in cmd[1]?
        try:
            agent_obj.logger.info("static function antiForensicsGuestSideCommands::commands")
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
                    tmp_thread.join(50)  # Wait until the thread is completed
                    if tmp_thread.is_alive():
                        # close antiForensics and set obj to crashed
                        agent_obj.logger.error("thread is alive... time outed")
                        agent_obj.logger.info(
                            "antiForensicsGuestSideCommands::commands: Close all open windows and " + "clear the antiForensics list")
                        subprocess.call(["taskkill", "/IM", "antiForensics.exe", "/F"])
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
            raise Exception("Error in antiForensicsGuestSideCommands::commands " + str(e))
