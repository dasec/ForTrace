import time
import logging
import hashlib
import subprocess
import random
import os
from datetime import date

try:
    from fortrace.core.vmm import Vmm
    from fortrace.utility.logger_helper import create_logger
    from fortrace.core.vmm import GuestListener
    from fortrace.core.reporter import Reporter

except ImportError as ie:
    print("Import error! in scenarioHelper.py " + str(ie))
    exit(1)

class Scenario:
    Reporter = None
    guest = None
    activeUser = None
    nextUser = None
    logger = None
    # tracking the state of some services enables the avoidance of errors when trying to delete related files
    status_eventLog = None
    # Service status when the system boots the next time
    status_eventLog_nb = None
    # Different Application Objects, to avoid creating a new ones every time
    veracrypt_obj = None
    browser_obj = None
    mail_obj = None

    def __init__(self, logger, reporter, guest):
        print("initializing Scenario.")
        self.guest = guest
        self.Reporter = reporter
        self.activeUser = "fortrace"
        self.nextUser = "fortrace"
        self.logger = logger
        self.status_eventLog = True
        self.status_eventLog_nb = True

    ##### User management functions #####
    def addUser(self, user, password, art_type=""):
        """
        Adds new user to the system
        @param user: username
        @param password: password of the user
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        userManagement_obj = self.guest.application("userManagement", {})
        self.logger.info("creating new user {0} with password {1}".format(user, password))
        userManagement_obj.addUser(user, password)
        while userManagement_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            self.logger.debug("Adding user creation event to Report")
            self.Reporter.add("usermanagement",
                              "[{0} {1}] User {2} created new user: {3}; pass: {4}".format(self.guest.datetime, self.guest.timezone, self.activeUser, user, password))

    def changeUser(self, user, password, art_type=""):
        """
        Change the user that will be automatically logged on to, when the system is rebooted
        @param user: username
        @param password: password of the user
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        userManagement_obj = self.guest.application("userManagement", {})
        self.logger.info("Changing user context to user {0}".format(user))
        userManagement_obj.changeUser(user, password)
        while userManagement_obj.is_busy:
            time.sleep(2)
        self.nextUser = user
        if art_type.upper() == "NEEDLE":
            self.logger.debug("Adding user change event to Report")
            self.Reporter.add("usermanagement",
                              "[{0} {1}] User context will be changed from {2} to: {3} on next reboot".format(self.guest.datetime, self.guest.timezone, self.activeUser,
                                                                                                    self.nextUser))

    def deleteUser(self, user, d_type, art_type=""):
        """
        Deletes the user from the system
        @param user: user to delete
        @param d_type: type of handling the user files ("keep", "delete", or "secure" delete)
        @param art_type: artifact type, choose "needle" if the event should appear in the final report or leave empty
        """
        self.logger.info("delete User {0}; File deletion type: {1}".format(user, d_type))
        self.logger.debug("Current User is {0}".format(self.activeUser))
        if self.activeUser == user:
            self.logger.error("User {0} cannot delete itself!".format(self.activeUser))
        # elif user == "fortrace":
        #     self.logger.error("User fortrace cannot be deleted!")
        else:
            userManagement_obj = self.guest.application("userManagement", {})
            userManagement_obj.deleteUser(user, d_type)
            while userManagement_obj.is_busy:
                time.sleep(2)
            if art_type.upper() == "NEEDLE":
                self.logger.debug("Adding user deletion event to Report")
                self.Reporter.add("usermanagement",
                                  "[{0} {1}] User {2} deleted user: {3}; File deletion: {4}"
                                  .format(self.guest.datetime, self.guest.timezone, self.activeUser, user, d_type))

    ##### Registry anti-forensics functions #####
    def disableRecycleBin(self, status="1", art_type=""):
        """
        Disables the usage of the Recycle Bin for the active user.
        @param status: "1" - disable, "0" - enable
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        antiForensics_obj = self.guest.application("antiForensics", {})
        self.logger.info("disabling recycle Bin")
        antiForensics_obj.disableRecycleBin(status)
        while antiForensics_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            stat_str = ""
            if status == "1":
                stat_str = "disabled"
            if status == "0":
                stat_str = "enabled"
            self.logger.debug("Adding Registry change to report")
            self.Reporter.add("anti-forensics",
                              "[{0} {1}] User {2} {3}  its Recycle Bin".format(self.guest.datetime, self.guest.timezone, self.activeUser, stat_str))

    def disablePrefetch(self, status="1", art_type=""):
        """
        Disables the system wide creation of Prefetch files
        @param status: "1" - disable, "0" - enable
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        antiForensics_obj = self.guest.application("antiForensics", {})
        self.logger.info("disabling Creation of Prefetch data")
        antiForensics_obj.disablePrefetch(status)
        while antiForensics_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            stat_str = ""
            if status == "1":
                stat_str = "disabled"
            if status == "0":
                stat_str = "enabled"
            self.logger.debug("Adding Registry change to report")
            self.Reporter.add("anti-forensics",
                              "[{0} {1}] User {2} {3} system wide creation of Prefetch files".format(self.guest.datetime, self.guest.timezone, self.activeUser, stat_str))

    def disableThumbcache(self, status="1", art_type=""):
        """
        Disable the creation of entries in the Thumbcache databases
        @param status: "1" - disable, "0" - enable
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        antiForensics_obj = self.guest.application("antiForensics", {})
        self.logger.info("disabling Creation of Thumbcache data")
        antiForensics_obj.disableThumbcache(status)
        while antiForensics_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            stat_str = ""
            if status == "1":
                stat_str = "disabled"
            if status == "0":
                stat_str = "enabled"
            self.logger.debug("Adding Registry change to report")
            self.Reporter.add("anti-forensics",
                              "[{0} {1}] User {2} {3} its Thumbcache".format(self.guest.datetime, self.guest.timezone, self.activeUser, stat_str))

    def disableRecentFiles(self, status="1", art_type=""):
        """
        Disable the creation of RecentDocs entries in the Registry, the creation of Jump list files and the Recently
        used entries in the Explorer
        @param status: "1" - disable, "0" - enable
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        antiForensics_obj = self.guest.application("antiForensics", {})
        self.logger.info("disabling Creation of Recent File entries")
        antiForensics_obj.disableRecentFiles(status)
        while antiForensics_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            stat_str = ""
            if status == "1":
                stat_str = "disabled"
            if status == "0":
                stat_str = "enabled"
            self.logger.debug("Adding Registry change to report")
            self.Reporter.add("anti-forensics",
                              "[{0} {1}] User {2} {3} its Recent files".format(self.guest.datetime, self.guest.timezone,
                                                                               self.activeUser, stat_str))


    def disableEventLog(self, status="1", art_type=""):
        """
        Disable the the Event Log service on the guest. Necessary to delete the Event Log files.
        Note: Does not(!) stop the event logging, and creates traces within the event log, if it is not deleted!
        @param status: "1" - disable, "0" - enable
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        stat_str = ""
        if status == "1":
            stat_str = "disabled"
            self.status_eventLog_nb = False
        if status == "0":
            stat_str = "enabled"
            self.status_eventLog_nb = True
        antiForensics_obj = self.guest.application("antiForensics", {})
        self.logger.info("disabling Eventlog: " + status)
        antiForensics_obj.disableEventLog(status)
        while antiForensics_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            self.logger.debug("Adding Registry change to report")
            self.Reporter.add("anti-forensics",
                              "[{0} {1}] User {2} {3} the Event Log Service".format(self.guest.datetime, self.guest.timezone, self.activeUser, stat_str))

    def disableUserAssist(self, status="1", art_type=""):
        """
        Disables the creation of new entries in the UserAssist key within the Registry
        @param status: "1" - disable, "0" - enable
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        antiForensics_obj = self.guest.application("antiForensics", {})
        self.logger.info("disable UserAssist:" + status)
        antiForensics_obj.disableUserAssist(status)
        while antiForensics_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            stat_str = ""
            if status == "1":
                stat_str = "disabled"
            if status == "0":
                stat_str = "enabled"
            self.logger.debug("Adding Registry change to report")
            self.Reporter.add("anti-forensics",
                              "[{0} {1}] User {2} {3} the creation of User Assist entries for its account".format(self.guest.datetime, self.guest.timezone,
                                  self.activeUser, stat_str))

    def disableHibernation(self, status="1", art_type=""):
        """
        Disables the system hibernation
        Note: System hibernation cannot be enabled on a virtual guest, so it is already disabled by default
        @param status: "1" - disable, "0" - enable
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        antiForensics_obj = self.guest.application("antiForensics", {})
        self.logger.info("disabling creation of hibernation files: " + status)
        antiForensics_obj.disableHibernation(status)
        while antiForensics_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            stat_str = ""
            if status == "1":
                stat_str = "disabled"
            if status == "0":
                stat_str = "enabled"
            self.logger.debug("Adding Registry change to report")
            self.Reporter.add("anti-forensics",
                              "[{0} {1}] User {2} {3} the creation of hibernation files".format(self.guest.datetime, self.guest.timezone, self.activeUser, stat_str))

    def disablePagefile(self, status="1", art_type=""):
        """
        Disables the usage and creation of the Windows Pagefile
        @param status: "1" - disable, "0" - enable
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        antiForensics_obj = self.guest.application("antiForensics", {})
        self.logger.info("Changing the page file usage to: " + status)
        antiForensics_obj.disablePagefile(status)
        while antiForensics_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            stat_str = ""
            if status == "1":
                stat_str = "disabled"
            if status == "0":
                stat_str = "enabled"
            self.logger.debug("Adding Registry change to report")
            self.Reporter.add("anti-forensics",
                              "[{0} {1}] User {2} {3} the creation and usage of the page file".format(self.guest.datetime, self.guest.timezone, self.activeUser, stat_str))

    def clearEventLogEntries(self, logfile="all", art_type=""):
        """
        Clears all existing entries in the provided Event Log, or all entries in all Event Logs
        @param logfile: Logfile, where the entries should be deleted (name of the logfile or "all")
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        antiForensics_obj = self.guest.application("antiForensics", {})
        self.logger.info("Clearing event log file entries for: {0}".format(logfile))
        if self.status_eventLog:
            antiForensics_obj.clearEventLogEntries(logfile)
            while antiForensics_obj.is_busy:
                time.sleep(2)
            if art_type.upper() == "NEEDLE":
                self.logger.debug("Adding clearance to report")
                self.Reporter.add("anti-forensics",
                                  "[{0} {1}] User {2} cleared Event Log entries for logile(s): {3}".format(self.guest.datetime, self.guest.timezone, self.activeUser,
                                                                                                 logfile))
        else:
            self.logger.error("Event log entries cannot be deleted, if the Service is not running!")

    def clearEventLogFiles(self, art_type=""):
        """
        Secure deletes all Event Log files
        Note: Event Log service must be disable before!
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        antiForensics_obj = self.guest.application("antiForensics", {})
        self.logger.info("Deleting Event Log file(s)")
        if not self.status_eventLog:
            antiForensics_obj.clearEventLogFiles()
            while antiForensics_obj.is_busy:
                time.sleep(2)
            if art_type.upper() == "NEEDLE":
                self.logger.debug("Adding clearance to report")
                self.Reporter.add("anti-forensics",
                                  "[{0} {1}] User {2} deleted all Event Log files".format(self.guest.datetime, self.guest.timezone, self.activeUser))
        else:
            self.logger.error("Event log files cannot be deleted, while the Service is running!")

    def clearPrefetch(self, art_type=""):
        """
        Secure deletes all created Prefetch files
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        antiForensics_obj = self.guest.application("antiForensics", {})
        self.logger.info("Clearing prefetch data")
        antiForensics_obj.clearPrefetch()
        while antiForensics_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            self.logger.debug("Adding clearance to report")
            self.Reporter.add("anti-forensics",
                              "[{0} {1}] User {2} cleared Prefetch data".format(self.guest.datetime, self.guest.timezone, self.activeUser))

    def clearThumbcache(self, user="", art_type=""):
        """
        Secure deletes all Thumbcache files for the provided user
        Note: Deleting the own Thumbcache files may not work as expected, since some files are permanently in access when
        the service is running.
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        antiForensics_obj = self.guest.application("antiForensics", {})
        self.logger.info("Clearing prefetch data")
        if user == "":
            user = self.activeUser
        if user == self.activeUser:
            self.logger.info(
                "WARNING: Deleting own tumbcache files, while Thumbcache is not disabled may cause problems! Be sure Thumbcache is disabled when using this function!")
        antiForensics_obj.clearThumbcache(user)
        while antiForensics_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            self.logger.debug("Adding clearance to report")
            self.Reporter.add("anti-forensics",
                              "[{0} {1}] User {2} deleted Thumbcache files for user {3}".format(self.guest.datetime, self.guest.timezone, self.activeUser, user))

    def clearJumpLists(self, user="", art_type=""):
        """
        Secure deletes all Jumplists for the provided user
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        antiForensics_obj = self.guest.application("antiForensics", {})
        self.logger.info("Clearing Jumplists")
        if user == "":
            user = self.activeUser
        antiForensics_obj.clearJumpLists(user)
        while antiForensics_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            self.logger.debug("Adding clearance to report")
            self.Reporter.add("anti-forensics",
                              "[{0} {1}] User {2} deleted Jumplist files for user {3}".format(self.guest.datetime, self.guest.timezone, self.activeUser, user))

    def clearUserAssist(self, art_type=""):
        """
        Clears the UserAssist key and all its content within the Registry
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        antiForensics_obj = self.guest.application("antiForensics", {})
        self.logger.info("Clearing UserAssist entries")
        antiForensics_obj.clearUserAssist()
        while antiForensics_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            self.logger.debug("Adding clearance to report")
            self.Reporter.add("anti-forensics",
                              "[{0} {1}] User {2} deleted its UserAssist entries in the Registry".format(self.guest.datetime, self.guest.timezone, self.activeUser))

    def clearRecentDocs(self, art_type=""):
        """
        Clears the RecentDocs key and all its content within the Registry
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        antiForensics_obj = self.guest.application("antiForensics", {})
        self.logger.info("Clearing RecentDocs entries")
        antiForensics_obj.clearRecentDocs()
        while antiForensics_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            self.logger.debug("Adding clearance to report")
            self.Reporter.add("anti-forensics",
                              "[{0} {1}] User {2} deleted its RecentDocs entries in the Registry".format(self.guest.datetime, self.guest.timezone, self.activeUser))

    def setRegistryKey(self, key, val_type, val_name, val, art_type=""):
        """
        Creates or updates the given Registry key value
        @param key: Registry key
        @param val_type: data type of the created value
        @param val_name: name of the value
        @param val: data of the value
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        antiForensics_obj = self.guest.application("antiForensics", {})
        self.logger.info("Clearing RecentDocs entries")
        antiForensics_obj.setRegistryKey(key, val_type, val_name, val)
        while antiForensics_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            self.logger.debug("Adding clearance to report")
            self.Reporter.add("registry",
                              "[{0} {1}] User {2} set Registry value {3}\\{4} to {5}".format(self.guest.datetime, self.guest.timezone, self.activeUser, key, val_name, val))

    def deleteRegistryKey(self, key, value="", art_type=""):
        """
        Deletes the provided Registry key or key value
        @param key: Registry key
        @param value: key value (optional)
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        antiForensics_obj = self.guest.application("antiForensics", {})
        self.logger.info("Deleting Registry Key")
        if value == "":
            self.logger.info("Deleting Registry Key {0}")
            antiForensics_obj.deleteRegistryKey(key)
        else:
            self.logger.info("Deleting Registry Key {0} - value {1}".format(key, value))
            antiForensics_obj.deleteRegistryKey(key, value)
        while antiForensics_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            self.logger.debug("Adding clearance to report")
            self.Reporter.add("registry",
                              "[{0} {1}] User {2} deleted Registry key/value {3}\{4}".format(self.guest.datetime, self.guest.timezone, self.activeUser, key, value))

    ##### file management functions #####
    def recycle(self, path, art_type=""):
        """
        Moves the provided file or folder to the Recycle Bin
        @param path: path of the file/directory to be deleted
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        fileManagement_obj = self.guest.application("fileManagement", {})
        self.logger.info("Moving {0} to recycle bin".format(path))
        fileManagement_obj.recycle(path)
        while fileManagement_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            self.logger.debug("Adding recycling to report")
            self.Reporter.add("filemanagement",
                              "[{0} {1}] User {2} moved {3} to Recycle Bin".format(self.guest.datetime, self.guest.timezone, self.activeUser, path))

    def emptyRecycleBin(self, art_type=""):
        """
        Empties the Recycle bin for the current user
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        fileManagement_obj = self.guest.application("fileManagement", {})
        self.logger.info("Emptying recycle bin")
        fileManagement_obj.emptyRecycleBin()
        while fileManagement_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            self.logger.debug("Adding action to report")
            self.Reporter.add("filemanagement",
                              "[{0} {1}] User {2} emptied its Recycle Bin for all drives".format(self.guest.datetime, self.guest.timezone, self.activeUser))

    def secureDelete(self, path, art_type=""):
        """
        Securely deletes the provided file or directory
        @param path: path of the file/directory to be deleted
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        fileManagement_obj = self.guest.application("fileManagement", {})
        self.logger.info("Seure deleting {0}".format(path))
        fileManagement_obj.secureDelete(path)
        while fileManagement_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            if not fileManagement_obj.has_error:
                self.logger.debug("Adding deletion process to report")
                self.Reporter.add("filemanagement",
                                  "[{0} {1}] User {2} secure deleted: {3}".format(self.guest.datetime, self.guest.timezone, self.activeUser, path))
            else:
                self.logger.error("secure deletion was not possible!")

    def smbCopy(self, source_path, target_path, share, user, password, art_type=""):
    #def smbCopy(self, source_path, target_path, user, password, art_type=""):
        """
        Copy Files/directories to or from a smb share. SMB path has to be comlete in form of "\\<share>\<path_to_file>
        @param source_path: Source file(s)/directory
        @param target_path: Target file(s)/directory
        @param share: SMB share to connect to
        @param user: user for SMB connection
        @param password: password of the user
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        fileTransfer_obj = self.guest.application("fileTransfer", {})
        self.logger.info("Transfering(SMB) files from {0} to {1}".format(source_path, target_path))
        self.logger.info("Credentials: user: {0} - password: {1}".format(user, password))
        fileTransfer_obj.smbCopy(source_path, target_path, share, user, password)
        # , share)
        while fileTransfer_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            if not fileTransfer_obj.has_error:
                self.logger.debug("Adding deletion process to report")
                self.Reporter.add("filemanagement",
                                  "[{0} {1}] User {2} copied file(s) from {3} to {4}".format(self.guest.datetime, self.guest.timezone, self.activeUser, source_path,
                                                                                   target_path))
            else:
                self.logger.error("smbCopy failed!")

    def winCopy(self, source_path, target_path, art_type=""):
        fileTransfer_obj = self.guest.application("fileTransfer", {})
        self.logger.info("Transfering(SMB) files from {0} to {1}".format(source_path, target_path))
        fileTransfer_obj.winCopy(source_path, target_path)
        while fileTransfer_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            if not fileTransfer_obj.has_error:
                self.logger.debug("Adding deletion process to report")
                self.Reporter.add("filemanagement",
                                  "Copied file(s) from {0} to {1}".format(source_path,target_path))
            else:
                self.logger.error("winCopy failed!")


    def openSmb(self, drive, path, username, password):
        fileTransfer_obj = self.guest.application("fileTransfer", {})
        self.logger.info("Opening connection for guest at {0} with share found at {1}".format(drive, path))
        fileTransfer_obj.openSmb(drive, path, username, password)
        while fileTransfer_obj.is_busy:
            time.sleep(2)

    def closeSmb(self, drive):
        fileTransfer_obj = self.guest.application("fileTransfer", {})
        self.logger.info("Closing connection for guest at {0}".format(drive))
        fileTransfer_obj.closeSmb(drive)
        while fileTransfer_obj.is_busy:
            time.sleep(2)

    def copy(self, source_path, target_path, art_type=""):
        """
        Copies a files on the guest
        @param source_path: path of the source file/folder
        @param target_path: path of the destination file/folder
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        self.logger.info("copying files from {0} to {1}".format(source_path, target_path))
        self.guest.guestCopy(source_path, target_path)
        time.sleep(2)
        if art_type.upper() == "NEEDLE":
            self.logger.debug("Adding deletion process to report")
            self.Reporter.add("filemanagement",
                              "[{0} {1}] User {2} copied file(s) from {3} to {4}".format(self.guest.datetime, self.guest.timezone, self.activeUser, source_path,
                                                                               target_path))

    # Function causes a 'module' object has no attribute 'move' error
    # def move(self, source_path, target_path, art_type=""):
    #     """
    #     Moves a files on the guest
    #     Note: This function assumes the copy process worked, ensure to use correct paths!
    #     @param source_path: path of the source file/folder
    #     @param target_path: path of the destination file/folder
    #     @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
    #     """
    #     self.logger.info("copying files from {0} to {1}".format(source_path, target_path))
    #     guest.guestMove(source_path, target_path)
    #     time.sleep(2)
    #     if art_type.upper() == "NEEDLE":
    #         self.logger.debug("Adding deletion process to report")
    #         self.Reporter.add("filemanagement",
    #                           "User {0} moved file(s) from {1} to {2}".format(self.activeUser, source_path,
    #                                                                            target_path))

    def openFile(self, path, art_type=""):
        """
        Opens a file with its default application if available
        @param path: path of the file
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        fileManagement_obj = self.guest.application("fileManagement", {})
        self.logger.info("opening file {0}".format(path))
        fileManagement_obj.openFile(path)
        while fileManagement_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            self.logger.debug("Adding recycling to report")
            self.Reporter.add("filemanagement",
                              "[{0} {1}] User {2} opened file {3}".format(self.guest.datetime, self.guest.timezone, self.activeUser, path))

    def writeTextFile(self, path, content, art_type=""):
        """
        writes provided content to a new text file
        @param path: path of the file
        @param content: content of the file
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        fileManagement_obj = self.guest.application("fileManagement", {})
        self.logger.info("opening file {0}".format(path))
        fileManagement_obj.writeTextFile(path, content)
        while fileManagement_obj.is_busy:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            self.logger.debug("Adding recycling to report")
            self.Reporter.add("filemanagement",
                              "[{0} {1}] User {2} created text file {3} with content {4}".format(self.guest.datetime, self.guest.timezone, self.activeUser, path, content))

    ####  Veracrypt functions ####
    def createContainer(self, cont_path, cont_size, password, art_type=""):
        """
        Creates a new VeraCrypt Container
        @param cont_path: target where the container gets created
        @param cont_size: size of the container
        @param password: password for the container
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        self.logger.info("Creating VeraCrypt container")
        if self.veracrypt_obj is None:
            self.veracrypt_obj = self.guest.application("veraCryptWrapper", {})
        vc_format_path = r'"C:\Program Files\VeraCrypt\VeraCrypt Format.exe"'
        self.veracrypt_obj.createContainer(vc_format_path, cont_path, cont_size, password)
        time.sleep(5)
        if art_type.upper() == "NEEDLE":
            self.logger.debug("Adding container creation  to report")
            self.Reporter.add("veracrypt",
                              "[{0} {1}] User {2} created VeraCrypt container at {3} with size {4} and password {5}".format(
                                  self.guest.datetime, self.guest.timezone, self.activeUser, cont_path, cont_size, password))

    def mountContainer(self, cont_path, password, mount_point, art_type=""):
        """
        Mounts the VeraCrypt container at the provided destination to a provided Drive letter
        The password of the container will be saved as a text file in the creating users documents directory
        @param cont_path: path of the container that is to be mounted
        @param password: password of the VeraCrypt container
        @param mount_point: Drive letter, the container will be mounted to
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        self.logger.info("Mounting VeraCrypt container at {0}".format(mount_point))
        if self.veracrypt_obj is None:
            self.veracrypt_obj = self.guest.application("veraCryptWrapper", {})
        vc_path = r'"C:\Program Files\VeraCrypt\VeraCrypt.exe"'
        self.veracrypt_obj.mountContainer(vc_path, cont_path, password, mount_point)
        time.sleep(5)
        if art_type.upper() == "NEEDLE":
            self.logger.debug("Adding container mount  to report")
            self.Reporter.add("veracrypt",
                              "[{0} {1}] User {2} mounted VeraCrypt container at {3} as {4}:".format(self.guest.datetime, self.guest.timezone, self.activeUser, cont_path,
                                                                                           mount_point))

    def copyToContainer(self, src_path, mount_point, art_type=""):
        """
        Copies the selected file/directory to the mounted container
        @param src_path: path of the files/directories to be mounted
        @param mount_point: drive letter of the mounted container
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        self.logger.info("Copying to VeraCrypt container at {0}".format(mount_point))
        if self.veracrypt_obj is None:
            self.veracrypt_obj = self.guest.application("veraCryptWrapper", {})
        target = "{0}:".format(mount_point)
        self.veracrypt_obj.copyToContainer(src_path, target)
        time.sleep(5)
        if art_type.upper() == "NEEDLE":
            self.logger.debug("Adding copy operation to report")
            self.Reporter.add("veracrypt",
                              "[{0} {1}] User {2} copied {3} to VeraCrypt container mounted at {4}:".format(self.guest.datetime, self.guest.timezone, self.activeUser,
                                                                                                  src_path,
                                                                                                  mount_point))

    def dismountContainer(self, mount_point, art_type=""):
        """
        Unmount the container, which is currently mounted at the provided drive letter
        @param mount_point: drive letter of the mounted container
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        self.logger.info("Unmounting VeraCrypt container at {0}".format(mount_point))
        if self.veracrypt_obj is None:
            self.veracrypt_obj = self.guest.application("veraCryptWrapper", {})
        vc_path = "\"C:\\Program Files\\VeraCrypt\\VeraCrypt.exe\""
        self.veracrypt_obj.unmountContainer(vc_path, mount_point)
        time.sleep(5)
        if art_type.upper() == "NEEDLE":
            self.logger.debug("Adding dismount operation to report")
            self.Reporter.add("veracrypt",
                              "[{0} {1}] User {2} dismounted VeraCrypt container, which was mounted as {3}: ".format(
                                  self.guest.datetime, self.guest.timezone, self.activeUser, mount_point))

    ##### Browser functions #####
    def browserOpen(self, url, art_type=""):
        """
        Opens Firefox and opens the provided website
        @param url: website to browse to
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        self.logger.info("Opening Browser")
        if self.browser_obj is None:
            self.browser_obj = self.guest.application("webBrowserFirefox", {'webBrowser': "firefox"})
        self.browser_obj.open(url=url)
        while not self.browser_obj.is_opened:
            time.sleep(2)
        if art_type.upper() == "NEEDLE":
            self.logger.debug("Adding browsing event to report")
            self.Reporter.add("browsings",
                              "[{0} {1}] User {2} opened browser at {3}".format(self.guest.datetime, self.guest.timezone, self.activeUser, url))

    def browserBrowseTo(self, url, art_type=""):
        """
        Browses to the provided website. The Browser needs to be opened before
        @param url: website to browse to
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        self.logger.info("Opening Browser")
        if self.browser_obj is None:
            self.logger.error("Browser not opened! Use browserOpen to open a new window!")
        elif not self.browser_obj.is_opened:
            self.logger.error("Browser not opened! Use browserOpen to open a new window!")
        else:
            self.browser_obj.browse_to(url)
            while self.browser_obj.is_busy is True:
                time.sleep(2)
            if art_type.upper() == "NEEDLE":
                self.logger.debug("Adding browsing event to report")
                self.Reporter.add("browsings",
                                  "[{0} {1}] User {2} browsed to {3}".format(self.guest.datetime, self.guest.timezone, self.activeUser, url))

    def browserClose(self, art_type=""):
        """
        Closes the current Browser object
        @param art_type: type of the artifact, choose "needle" if the event should appear in the final report or leave empty
        """
        self.logger.info("Closing Browser")
        if self.browser_obj is None:
            self.logger.error("Browser not opened! Use browserOpen to open a new window!")
        elif not self.browser_obj.is_opened:
            self.logger.error("Browser not opened! Use browserOpen to open a new window!")
        else:
            self.browser_obj.close()
            # while self.browser_obj.is_opened is True:
            #     time.sleep(2)
            time.sleep(5)
            if art_type.upper() == "NEEDLE":
                self.logger.debug("Adding browsing event to report")
                self.Reporter.add("browsings",
                                  "[{0} {1}] User {2} closed browser".format(self.guest.datetime, self.guest.timezone, self.activeUser))

    # Missing Browser functions may be added in future

    ##### Mail functions #####
    # May be added in future

    ##### Printer functions #####
    # May be added in future

    ##### Instant Messenger functions #####
    # May be added in future

    ##### cleanUp functions #####
    def initClean(self):
        """
        Tries to reduce the artifacts created during template creation.
        Cleans Registry and Prefetch directory.
        """
        self.logger.debug("Cleaning Template artifacts")
        self.guest.initClean()
        time.sleep(120)
        self.logger.debug("Adding initClean to report")
        self.Reporter.add("chronological",
                          "[{0} {1}] User {2} used initial clean function".format(self.guest.datetime, self.guest.timezone, self.activeUser))

    def cleanUp(self, mode="auto"):
        """
        Tries to reduce the artifacts created during scenario execution. run as las command before shutdown
        Note: To remove all traces, use manual mode and delete the fortrace folder from the last users Desktop!
                To do so follow the description under /install_tools/cleanUp_manual.txt
        @param mode:    "manual" - do not shutdown system automatically for manual cleanup finalization
                        "auto" - automatic shutdown after cleanup finished
        """
        self.logger.debug("Cleaning Template artifacts")
        self.guest.cleanUp(mode)
        self.logger.info("Cleanup started, this may take a few minutes.")
        self.logger.info("For best results manual deletion ")
        while self.guest.isGuestPowered():
            self.logger.info("wait for system shutdown")
            time.sleep(5)
        self.logger.debug("Adding shutdown to report")
        self.Reporter.add("chronological",
                          "[{0} {1}] System shut down by user {2}".format(self.guest.datetime, self.guest.timezone, self.activeUser))
        self.logger.debug("Adding cleanUp to report")
        self.Reporter.add("chronological",
                          "[{0} {1}] User {2} used cleanUp  function".format(self.guest.datetime, self.guest.timezone, self.activeUser))

    ##### power management functions #####
    def reboot(self, boot_time=None):
        """
        Reboots the guest system with the provided startup time
        @param boot_time: boot time in format "%Y-%m-%d %H:%M:%S" or None to keep current time
        """
        self.guest.shutdown("keep")
        while self.guest.isGuestPowered():
            time.sleep(5)
        self.logger.info("booting system with boottime: {0}".format(boot_time))
        self.guest.start(boot_time)
        self.guest.waitTillAgentIsConnected()
        self.guest.guestTime()
        time.sleep(2)
        self.guest.guestTimezone()
        time.sleep(2)
        self.activeUser = self.nextUser
        self.status_eventLog = self.status_eventLog_nb
        self.logger.debug("System time after reboot is: {0}".format(self.guest.datetime))
        self.logger.debug("Adding reboot to report")
        self.Reporter.add("chronological",
                          "[{0} {2}] System rebooted, active User: {1}".format(self.guest.datetime, self.activeUser, self.guest.timezone))

    def shutdown(self):
        """
        Shuts down the guest system
        """
        self.guest.guestTime()
        time.sleep(2)
        self.guest.shutdown("keep")
        while self.guest.isGuestPowered():
            time.sleep(5)
        self.logger.debug("Adding shutdown to report")
        self.Reporter.add("chronological",
                          "[{0} {1}] System shut down by user {2}".format(self.guest.datetime, self.guest.timezone, self.activeUser))


def generate_file_sh256(filename, blocksize=2 ** 20):
    """
    Generates the SHA_256 hashsum of the given file
    @param filename: name of the file, the hashsum will calculated for
    @param blocksize: blocksize used during calculation
    """
    m = hashlib.sha256()
    with open(filename, "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest()


def wait(min=10, max=60):
    """
    Waits for a random amount of seconds in the provided interval
    Gives the user time to "think"
    @param min: minimum time to wait
    @param max: maximum time to wait
    """
    if min >= max:
        max = min + 30
    sleeptime = random.randint(min, max)
    time.sleep(sleeptime)
