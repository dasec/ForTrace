from __future__ import absolute_import
import subprocess
import inspect
import threading
from time import sleep

from fortrace.application.application import ApplicationVmmSide
from fortrace.application.application import ApplicationVmmSideCommands
from fortrace.application.application import ApplicationGuestSide
from fortrace.application.application import ApplicationGuestSideCommands
from fortrace.utility.line import lineno


###############################################################################
# Host side implementation
###############################################################################
class DeployerVmmSide(ApplicationVmmSide):
    """
    This class is a remote control on the host-side to
    install new programs and change their configuration.
    """

    def __init__(self, guest_obj, args):
        """Set default attribute values only.
        @param guest_obj: The guest on which this application is running. (will be inserted from guest::application())
        @param args: containing
                 logger: Logger name for logging.
        """
        try:
            super(DeployerVmmSide, self).__init__(guest_obj, args)
            self.logger.info("function: DeployerVmmSide::__init__")

        except Exception as e:
            raise Exception(lineno() + " Error: DeployerVmmSide::__init__ "
                            + self.guest_obj.guestname + " " + str(e))

    def deploy(self, iso_path):
        """Deploy a new program"""

        try:
            self.logger.info("DeployerVmmSide::deploy inserting CD image")
            self.guest_obj.insertCD(iso_path)

            # - wait a few seconds, giving the guest os enough time to mount the cd volume
            sleep(5)

            self.logger.info("function: DeployerVmmSide::deploy insertion done, execute deployment")
            self.guest_obj.send("application " + "deployer " + " deploy ")
            self.is_busy = True

        except Exception as e:
            raise Exception("error DeployerVmmSide::open: " + str(e))

    def open(self):
        """
        Abstact method, which all child classes have to overwrite.
        """
        raise NotImplementedError

    def close(self):
        """
        Abstact method, which all child classes have to overwrite.

        Close an instance of an application.
        """
        raise NotImplementedError


###############################################################################
# Commands to parse on host side
###############################################################################
class DeployerVmmSideCommands(ApplicationVmmSideCommands):
    """
    Class with all commands for <Deployer> which will be received from the agent on the guest.

    Static only.
    """

    @staticmethod
    def commands(guest_obj, cmd):
        # cmd[0] = win_id; cmd[1] = state
        guest_obj.logger.info("function: DeployerVmmSideCommands::commands")
        module_name = "deployer"
        guest_obj.logger.debug("DeployerVmmSideCommands::commands: " + cmd)
        try:
            if "ready" == cmd:
                guest_obj.logger.debug("in ready")
                guest_obj.logger.info(module_name + " is_ready = true")
                deployObj = guest_obj.applicationWindow[module_name][0]
                deployObj.is_ready = True
                deployObj.is_busy = False

            if "error" == cmd:
                guest_obj.logger.debug("in error")
                guest_obj.logger.info(module_name + " has_error = True")
                deployObj = guest_obj.applicationWindow[module_name][0]
                deployObj.has_error = True

        except Exception as e:
            raise Exception(module_name + "_host_side_commands::commands " + str(e))


###############################################################################
# Guest side implementation
###############################################################################
class DeployerGuestSide(ApplicationGuestSide):
    """<Deployer> implementation of the guest side.

    Usually Windows, Linux guest's
    class attributes
    window_id - The ID for the opened object
    """

    def __init__(self, agent_obj, logger):
        super(DeployerGuestSide, self).__init__(agent_obj, logger)
        try:
            self.module_name = "deployer"
            self.agent_object = agent_obj

        except Exception as e:
            raise Exception("Error in " + self.__class__.__name__ +
                            ": " + str(e))

    def deploy(self, args):
        """
        Starts the deployment process by executing the setup.py from the cd drive.

        return:
        Send to the host in the known to be good state:
            'application <Deployer> window_id open'.
            'application <Deployer> window_id ready'.
        in the error state:
            'application <Deployer> window_id error'.

        """

        try:
            arguments = args.split(" ")
            # installationPath = arguments[0]

            self.logger.info("function: Deployer::open")
            self.logger.debug("Deployment process starts now -> execute setup.py")

            if self.agent_object.operatingSystem == "windows":
                subprocess.call(['python', 'D:\\\\setup.py'])
            elif self.agent_object.operatingSystem == "linux":
                subprocess.call(['python', '/media/fortrace/CDROM/setup.py'])
            else:
                raise Exception(
                    lineno() + " Error: DeployerGuestSide::__deploy__ unkown operating system: " + self.agent_object.operatingSystem)

            self.agent_object.send("application " + self.module_name + " ready")

        except Exception as e:
            self.agent_object.send("application " + self.module_name + " error")
            self.logger.error("Deployer::open: " + str(e))
            return

    def open(self):
        """
        Abstact method, which all child classes have to overwrite.
        """
        raise NotImplementedError

    def close(self):
        """
        Abstact method, which all child classes have to overwrite.
        """
        raise NotImplementedError


###############################################################################
# Commands to parse on guest side
###############################################################################
class DeployerGuestSideCommands(ApplicationGuestSideCommands):
    """
    Class with all commands for one application.

    call the ask method for an object. The call will be done by a thread, so if the timeout is
    reached, the open application will be closed and opened again.
    Static only.

    """

    @staticmethod
    def commands(agent_obj, obj, cmd):  # commands(obj, cmd) obj from list objlist[window_id] win id in cmd[1]?
        try:
            agent_obj.logger.info("static function DeployerGuestSideCommands::commands")
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
                    tmp_thread.join(600)  # Wait until the thread is completed

                    if tmp_thread.is_alive():
                        # process does not respond, kill it

                        agent_obj.logger.error("thread is alive... time outed")
                        agent_obj.logger.info("DeployerGuestSideCommands::commands: Close all open windows")
                        # TODO: kill setup.py

                        # set a crushed flag.
                        obj.is_opened = False
                        obj.is_busy = False
                        obj.has_error = True

                        agent_obj.logger.info("application " + module + " error")
                        agent_obj.send("application " + module + " error")

            if not method_found:
                raise Exception("Method " + method_string + " is not defined!")
        except Exception as e:
            raise Exception("Error in DeployerGuestSideCommands::commands " + str(e))
