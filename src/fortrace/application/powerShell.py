# Copyright (C) 2013-2014 Reinhard Stampp
# This file is part of fortrace - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.

from __future__ import absolute_import
from __future__ import print_function
try:
    import logging
    import sys
    import platform
    import threading
    import subprocess
    import inspect  # for listing all method of a class
    import shlex

    # base class VMM side
    from fortrace.application.application import ApplicationVmmSide
    from fortrace.application.application import ApplicationVmmSideCommands

    # base class guest side
    from fortrace.application.application import ApplicationGuestSide
    from fortrace.application.application import ApplicationGuestSideCommands
    from fortrace.utility.line import lineno

except ImportError as ie:
    print(("Import error! in powerShell.py " + str(ie)))
    exit(1)


###############################################################################
# Host side implementation
###############################################################################
class PowerShellVmmSide(ApplicationVmmSide):
    """
    This class is a remote control on the host-side to control a real PowerShell via cmd
    running on a guest. TODO - integrate usage of powershell console
    """

    def __init__(self, guest_obj, args):
        """Set default attribute values only.
        @param guest_obj: The guest on which this application is running. (will be inserted from guest::application())
        @param args: containing
                 logger: Logger name for logging.
        """
        try:
            super(PowerShellVmmSide, self).__init__(guest_obj, args)
            self.logger.info("function: PowerShellVmmSide::__init__")
            self.window_id = None
            self.window_is_crushed = None
            self.psc = None
            self.aut = None
            self.path = None

        except Exception as e:
            raise Exception(lineno() + " Error: PowerShellHostSide::__init__ " + self.guest_obj.guestname + " " + str(e))

    def open(self):
        """Opens powershell console; unused as of right now;
        """
        try:
            self.logger.info("function: PowerShellVmmSide::open")
            self.window_id = self.guest_obj.current_window_id
            self.guest_obj.send("application " + "powerShell " + str(self.window_id) + " open ")  # some parameters
            self.is_busy = True

           # temporarily disabled; only needed if powershell window is actually used
           # self.guest_obj.current_window_id += 1

        except Exception as e:
            raise Exception("error PowerShellVmmSide::open: " + str(e))

# TODO test "powershell transformation" for cmd (simply enter powershell without start or powershell command)
    # TODO add open2 and close2 functions

    def close(self):
        """ Unused function as of right now; closes powershell console window
        """
        try:
            self.logger.info("function: PowerShellVmmSide::close")
            self.guest_obj.send("application " + "powerShell " + str(self.window_id) + " close ")
            self.is_busy = True

        except Exception as e:
            raise Exception("error PowerShellVmmSide:close()" + str(e))

    def pscommand(self, psc):
        """
        singular powershell command can be transferred
        """
        #TODO implement
        try:
            self.psc = psc
            self.window_id = self.guest_obj.current_window_id
            self.logger.info("function: PowerShellVmmSide:: " + psc)
            self.guest_obj.send(
                "application " + "powerShell " + str(
                    self.window_id) + " pscommand " + self.psc)
            self.is_busy = True


#            self.guest_obj.current_window_id += 1
        except Exception as e:
            raise Exception("error PowerShellVmmSide::open: " + str(e))

    def disableUAC(self):
        try:
            self.window_id = self.guest_obj.current_window_id
            self.guest_obj.send(
                "application " + "powerShell " + str(
                    self.window_id) + " disableUAC ")

            self.is_busy = True


#            self.guest_obj.current_window_id += 1
        except Exception as e:
            raise Exception("error PowerShellVmmSide::open: " + str(e))

    def enableUAC(self):
        try:
            self.window_id = self.guest_obj.current_window_id
            self.guest_obj.send(
                "application " + "powerShell " + str(
                    self.window_id) + " enableUAC ")
            self.is_busy = True


#            self.guest_obj.current_window_id += 1
        except Exception as e:
            raise Exception("error PowerShellVmmSide::open: " + str(e))

    def autScripts(self, aut):
        try:
            # TODO add SCOPE parameter for potential use
            possibilities = ['Default', 'Restricted', 'RemoteSigned', 'AllSigned', 'Unrestricted', 'Bypass']

            if aut not in possibilities:
                self.logger.info("Chosen parameter not in list of possibilities: Default Restricted RemoteSigned"
                                 "AllSigned Unrestricted Bypass - Bypass chosen")
                aut = "Bypass"

            aut = "Set-ExecutionPolicy " + aut + " -Force"
            self.aut = aut

            self.logger.info("function: PowerShellVmmSide::autScripts")
            self.window_id = self.guest_obj.current_window_id
            self.guest_obj.send(
                "application " + "powerShell " + str(
                    self.window_id) + " autScripts " + self.aut)
            self.is_busy = True


#            self.guest_obj.current_window_id += 1
        except Exception as e:
            raise Exception("error PowerShellVmmSide::open: " + str(e))

    def installps(self, path):
        try:
            self.path = path
            self.window_id = self.guest_obj.current_window_id
            self.logger.info("function: PowerShellVmmSide:: " + path)
            self.guest_obj.send(
            "application " + "powerShell " + str(
                    self.window_id) + " installps " + self.path)

            self.is_busy = True

#            self.guest_obj.current_window_id += 1
        except Exception as e:
            raise Exception("error PowerShellVmmSide::open: " + str(e))

    def disableHistory(self):
        try:
            self.window_id = self.guest_obj.current_window_id
            self.guest_obj.send(
                "application " + "powerShell " + str(
                    self.window_id) + " disableHistory ")

            self.is_busy = True


 #           self.guest_obj.current_window_id += 1
        except Exception as e:
            raise Exception("error PowerShellVmmSide::open: " + str(e))

    def delHistory(self):
        try:
            self.window_id = self.guest_obj.current_window_id
            self.guest_obj.send(
                "application " + "powerShell " + str(
                    self.window_id) + " delHistory ")

            self.is_busy = True

#            self.guest_obj.current_window_id += 1
        except Exception as e:
            raise Exception("error PowerShellVmmSide::open: " + str(e))



###############################################################################
# Commands to parse on host side
###############################################################################
class PowerShellVmmSideCommands(ApplicationVmmSideCommands):
    """
    Class with all commands for PowerShell which will be received from the agent on the guest.

    Static only.
    """

    @staticmethod
    def commands(guest_obj, cmd):
        # cmd[0] = win_id; cmd[1] = state
        module_name = "powerShell"
        guest_obj.logger.debug("PowerShellVmmSideCommands::commands: " + cmd)
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
class PowerShellGuestSide(ApplicationGuestSide):
    """PowerShell implementation of the guest side.

    Usually Windows guest - not tested on Linux powershell implementations
    class attributes
    window_id - The ID for the opened object
    """

    def __init__(self, agent_obj, logger):
        super(PowerShellGuestSide, self).__init__(agent_obj, logger)
        try:
            self.module_name = "powerShell"
            self.timeout = None
            self.window_is_crushed = None
            self.window_id = None
            self.agent_object = agent_obj
            self.psc = None
            self.aut = None
            self.path = None

        except Exception as e:
            raise Exception("Error in " + self.__class__.__name__ +
                            ": " + str(e))

    def open(self, args):
        """
        Open a PowerShell console window - currently not used in further functions

        return:
        Send to the host in the known to be good state:
        'application PowerShell window_id open'.
        'application PowerShell window_id ready'.
        in the error state:
        'application PowerShell window_id error'.
        additionally the 'window_is_crushed' attribute is set; so the next
        call will open a new window.

        """
        #TODO via arg decide if console or cmd transform; cmd transform test if subprocess call still works
        try:
            arguments = args.split(" ")
            #var = arguments[0]
            #var2 = arguments[1]

            self.logger.info(self.module_name + "GuestSide::open")
            subprocess.call(["start", "powershell"], shell=True)
            # send some information about the PowerShell state
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " opened")

            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            self.window_is_crushed = False
        except Exception as e:
            self.logger.info("PowerShellGuestSide::open: Close all open windows and clear the powershell list")
#            subprocess.call(["taskkill", "/IM", "powerShell.exe", "/F"])
            # for obj in self.agent_object.applicationWindow[self.module_name]:
            #    self.agent_obj.applicationWindow[self.module_name].remove(obj)
            # set a crushed flag.
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Error in " + self.__class__.__name__ + "::open" + ": selenium is crushed: " + str(e))

    def close(self, args=None):
        """Close one given window by window_id"""
        #TODO IF ps console open, then, else exit/quit
        subprocess.call(["taskkill", "/IM", "powershell.exe", "/F"])
        self.logger.info(self.__class__.__name__ +
                         "::close ")
        self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " opened")

        self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
        self.window_is_crushed = False

    def pscommand(self, psc):
        """
        singular powershell command can be executed
        """
        try:
            tmp = shlex.split(psc)
            #temp
            #print(tmp)
            self.logger.info(self.module_name + "GuestSide::pscommand")
#            self.logger.debug("powershell command: " + psc)
            subprocess.call(["powershell"] + tmp)
            # send some information about the PowerShell state
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " opened")
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            #subprocess.Popen(["powershell"] + tmp)

        except Exception as e:
            self.logger.info(
                "PowerShellGuestSide::pscommand: Can't execute command")
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")

    def disableUAC(self, args):
        try:
            # TODO requires restart -> alternative?
#            tmp = shlex.split("Set-ItemProperty -path 'HKLM:/Software/Microsoft/Windows/CurrentVersion/policies/system'"
 #                             " -Name 'EnableLUA' -value 0")
            tmp = shlex.split("New-ItemProperty -Path "
                              "'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\policies\\system'"
                              " -Name 'EnableLUA' -PropertyType 'DWord' -Value 0 -Force")
            #temp
            #print(tmp)
            self.logger.info(self.module_name + "GuestSide::disableUAC")
 #           self.logger.debug("powershell command: " + tmp)
            subprocess.call(["powershell"] + tmp)
            # send some information about the PowerShell state
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " opened")

            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")

        except Exception as e:
            self.logger.info(
                "PowerShellGuestSide::disableUAC: Can't execute command")
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")

    def enableUAC(self, args):
        try:
            # TODO requires restart -> alternative?
            tmp = shlex.split("New-ItemProperty -Path "
                              "'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\policies\\system'"
                              " -Name 'EnableLUA' -PropertyType 'DWord' -Value 1 -Force")
            #temp
            #print(tmp)
            self.logger.info(self.module_name + "GuestSide::enableUAC")
  #          self.logger.debug("powershell command: " + tmp)
            subprocess.call(["powershell"] + tmp)
            # send some information about the PowerShell state
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " opened")

            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")

        except Exception as e:
            self.logger.info(
                "PowerShellGuestSide::enableUAC: Can't execute command")
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")

    def autScripts(self, aut):
        try:
            tmp = shlex.split(aut)
            #temp
            #print(tmp)
            self.logger.info(self.module_name + "GuestSide::autScripts")
   #         self.logger.debug("powershell command: " + tmp)
            subprocess.call(["powershell"] + tmp)
            # send some information about the PowerShell state
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " opened")

            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
        except Exception as e:
            self.logger.info(
                "PowerShellGuestSide::delHistory: Can't execute command")
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")

    def installps(self, path):
        try:
            tmp = path
            #temp
            #print(tmp)
            self.logger.info(self.module_name + "GuestSide::installps")
    #        self.logger.debug("powershell command: install " + tmp)
            subprocess.call(["powershell", "Start-Process", "-Wait", "-ArgumentList", "'/silent'", "-PassThru", "-FilePath ", tmp])
            # send some information about the PowerShell state
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " opened")

            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            #subprocess.Popen(["powershell"] + tmp)


        except Exception as e:
            self.logger.info(
                "PowerShellGuestSide::installps: Can't execute command")
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")

    def disableHistory(self, args):
        try:
            #tmp1 = shlex.split("remove-module psreadline")
            tmp2 = shlex.split("Set-PSReadlineOption -HistorySaveStyle SaveNothing")
            #temp
            #print(tmp)
           # subprocess.call(["powershell"] + tmp1)
            self.logger.info(self.module_name + "GuestSide::disableHistory")
            #self.logger.debug("powershell command: " + tmp1)
     #       self.logger.debug("powershell command: " + tmp2)
            #TODO test if wait is needed or any other timing is needed here
            subprocess.call(["powershell"] + tmp2)
            # send some information about the PowerShell state
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " opened")

            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
        except Exception as e:
            self.logger.info(
                "PowerShellGuestSide::disableHistory: Can't execute command")
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")

    def delHistory(self, args):
        try:
            tmp = shlex.split("del (Get-PSReadlineOption).HistorySavePath")
            #temp
            #print(tmp)
            self.logger.info(self.module_name + "GuestSide::delHistory")
      #      self.logger.debug("powershell command: " + tmp)
            subprocess.call(["powershell"] + tmp)
            # send some information about the PowerShell state
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " opened")

            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")

        except Exception as e:
            self.logger.info(
                "PowerShellGuestSide::delHistory: Can't execute command")
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")


###############################################################################
# Commands to parse on guest side
###############################################################################
class PowerShellGuestSideCommands(ApplicationGuestSideCommands):
    """
    Class with all commands for one application.

    call the ask method for an object. The call will be done by a thread, so if the timeout is
    reached, the open application will be closed and opened again.
    Static only.
    """

    @staticmethod
    def commands(agent_obj, obj, cmd):  # commands(obj, cmd) obj from list objlist[window_id] win id in cmd[1]?
        try:
            agent_obj.logger.info("static function PowerShellGuestSideCommands::commands")
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
                    tmp_thread.join(500)  # Wait until the thread is completed
                    if tmp_thread.is_alive():
                        # close powershell and set obj to crashed
                        agent_obj.logger.error("thread is alive... time outed")
                        agent_obj.logger.info(
                            "PowerShellGuestSideCommands::commands: Close all open windows and " + "clear the PowerShell list")
                       # subprocess.call(["taskkill", "/IM", "PowerShell.exe", "/F"])
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
            raise Exception("Error in PowerShellGuestSideCommands::commands " + str(e))
