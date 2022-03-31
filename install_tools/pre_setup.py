#!/usr/bin/python3
import sys
import getpass
import os
import logging
import json
import subprocess
import platform


class Installer:
    """
    This class is used to install all prerequisites that are needed for fortrace. Additionally all paths and privileges
    that fortrace needs are created.
    """
    requ = os.path.dirname(__file__)
    logger = ""
    param = ""
    general = ""
    tcpdump = ""
    virtpools = ""
    netifaces = ""

    def __init__(self, logger, param):
        self.logger = logger
        self.param = param

    def load_config(self):
        """
        Load config file and read different sections into variables
        :return:
        """
        self.logger.info("[~] Loading configuration...")
        try:
            with open(os.path.join(self.requ, 'config.json')) as json_data_file:
                data = json.load(json_data_file)
                self.general = data['general']
                self.tcpdump = data['tcpdump']
                self.virtpools = data['libvirt-pools']
                self.netifaces = data['network-interfaces']
        except ValueError as e:
            self.logger.info("[X] Error while reading config file.")
            self.logger.error(e)
            sys.exit(1)
        else:
            self.logger.info("[+] Done loading configuration.")

    def install_sys_dep(self):
        """
        Checks which OS is running and calls corresponding function
        :return:
        """
        if platform.system() == "Linux":
            self.logger.debug("Linux OS found.")
            self.install_apt()
            if self.param == "vm":
                self.linux_autostart()
        elif platform.system() == "Windows":
            self.logger.debug("Windows OS found.")
            #self.install_msi()
            if self.param == "vm":
                self.windows_autostart()
        else:
            self.logger.error("[X] Your Operating System is not supported by fortrace.")
            sys.exit(1)

    def install_apt(self):
        """
        Install all dependencies specific to Linux Operating System
        Reads a file of all required packages and installs them through apt-get.
        :return:
        """
        self.logger.info("[~] Installing packet requirements over 'apt'...")
        try:
            aptCmd = "apt-get --yes -qqq install {}"
            packetDepFile = os.path.join(self.requ, self.general['packet-requirements'])
            with open(packetDepFile, "r") as file:
                for line in file:
                    prepCmd = aptCmd.format(line.strip())
                    self.logger.debug("Running: {}".format(prepCmd))
                    subprocess.call(prepCmd.split(), stdout=subprocess.PIPE)
        except OSError as e:
            self.logger.info("[X] Error while installing packet requirements.")
            self.logger.error(e)
            sys.exit(1)
        else:
            self.logger.info("[+] Installed 'apt' packet requirements.")

    def linux_autostart(self):
        """
        Creates autostart script for Ubuntu guest
        :return:
        """
        self.logger.info("[~] Creating autostart script in ~/.config/autostart")
        filename = 'agent.desktop'
        path = '/home/' + self.general['user'] + '/.config/autostart/'

        try:
            if not os.path.exists(path):
                self.logger.info("[i] Autostart path does not exist and will be created.")
                subprocess.call(["mkdir", path], stdout=subprocess.PIPE)
            with open(os.path.join(path, filename), 'w') as temp:
                temp.write('''\
#! /bin/bash
[Desktop Entry]
Type=Application
Terminal=false
Exec=gnome-terminal -e 'bash -c "python3 ''' + os.path.join(self.general['fortrace-path'],  "guest_tools/guestAgent.py") + '''; bash"'
Hidden=false
X-GNOME-Autostart-enabled=true
Name=Startup Script
Comment=
''')
        except OSError as e:
            self.logger.info("[X] Error while creating autorun script.")
            self.logger.error(e)
            sys.exit(1)
        else:
            self.logger.info("[+] Created autorun script.")

    def windows_autostart(self):
        """
        Creates autostart script for Windows guest
        :return:
        """
        self.logger.info("[-] Creating autostart for fortrace.")

        try:
            # create link in autostart folder, or scheduled task for guestAgent.py
            domain = os.environ['userdomain']
            user = getpass.getuser()
            #prepCmd = "schtasks /create /U {} /RU SYSTEM /SC BEIMSTART /TN adminAgent /TR C:\\Windows\\System32\\cmd.exe python {}".format(os.path.join(domain, user), os.path.join(self.general['fortrace-path'], "guest_tools/guestAgent.py"))
            #prepCmd = "schtasks /create /sc ONLOGON /tn fortrace /tr %HOMEPATH%\Desktop\fortrace\guest_tools\startGuestAgent.bat /f"
            #subprocess.call(prepCmd.split(), stdout=subprocess.PIPE)
            prepCmd2 = "schtasks /create /sc ONLOGON /tn fortrace2 /tr %HOMEPATH%\Desktop\fortrace\guest_tools\mountnfs.bat /f"
            subprocess.call(prepCmd2.split(), stdout=subprocess.PIPE)
            self.logger.info("doing something...")
        except OSError as e:
            # error
            self.logger.info("[X] Error while creating autostart entry.")
            self.logger.error(e)
        else:
            # success
            self.logger.info("[+] Created autostart entry.")

    def install_msi(self):
        """
        Install all dependencies specific to Windows Operating System
        :return:
        """
        self.logger.info("[~] Installing all necessary MSI packages.")
        # Nothing is needed here at the moment.
        self.logger.info("[+] MSI packages successfully installed.")

    def install_pip_dep(self):
        """
        Reads a file of all required pip packages and installs them through pip install.
        :return:
        """
        self.logger.info("[~] Installing pip requirements...")
        try:
            pipCmd = "pip3 install -U {}"
            pipDepFile = os.path.join(self.requ, self.general['pip-requirements'])
            with open(pipDepFile, "r") as file:
                for line in file:
                    if platform.system() == "Linux" and "pywin32" in line:
                        self.logger.info("Pywin32 skipped on Linux distro")
                        continue
                    elif platform.system() == "Windows" and "libvirt-python" in line:
                        self.logger.info("libvirt-python skipped on Windows")
                        continue
                    prepCmd = pipCmd.format(line.strip())
                    self.logger.debug("Running: {}".format(prepCmd))
                    subprocess.call(prepCmd.split(), stdout=subprocess.PIPE)
        except OSError as e:
            self.logger.info("[X] Error while installing pip packages.")
            self.logger.error(e)
            sys.exit(1)
        else:
            self.logger.info("[+] Successfuly installed pip requirements.")

    def install_sources(self):
        """
        This function calls 'setup.py' to install the framework source code onto the machine
        :return:
        """
        self.logger.info("[~] Installing fortrace framework...")
        try:
            if platform.system() == "Linux":
                self.logger.info("[~] Installing fortrace on Linux machine...")
                prepCmd = "python3 setup.py install --user"
                subprocess.call(prepCmd.split(), stdout=subprocess.PIPE)
               # ltmp = os.getcwd() + "/setup.py"
               # subprocess.check_call([sys.executable, ltmp, "install", "--user"])
               # subprocess.call(['python', 'setup.py', 'install', '--user'])
            elif platform.system() == "Windows":
                self.logger.info("[~] Installing fortrace on Windows machine...")
                tmp = os.getcwd() + "\setup.py"
                subprocess.check_call([sys.executable, tmp, "install", "--user"])
        except OSError as e:
            self.logger.info("[X] Error while installing fortrace framework.")
            self.logger.error(e)
            sys.exit(1)
        else:
            self.logger.info("[+] fortrace Framework installed successfully.")

    def setup_tcpdump(self):
        """
        Setup tcpdump user rights.
        :return:
        """
        self.logger.info("[~] Setting up tcpdump...")
        try:
            prepCmd = "setcap cap_net_raw,cap_net_admin=eip {}".format(self.tcpdump['path'])
            subprocess.call(prepCmd.split(), stdout=subprocess.PIPE)
        except OSError as e:
            self.logger.info("[X] Error setting up tcpdump")
            self.logger.error(e)
            sys.exit(1)
        else:
            self.logger.info("[+] Setting up tcpdump.")

    def setup_libivrt(self):
        """
        Adding groups and rights for libvirt as well as creating disk pools to work with.
        :return:
        """
        self.logger.info("[~] Adding disk pools for libvirt...")
        try:
            commands = ["groupadd libvirtd",
                        "usermod -a -G libvirtd {}".format(self.general['user']),
                        "mkdir {}".format(self.virtpools['path']),
                        "virsh pool-define fortrace-pool.xml",
                       # "virsh pool-define-as fortrace-pool dir - - - - {}/{}".format(self.virtpools['path'],
                                                    #                                self.virtpools['name']),
                        "virsh pool-build {}".format(self.virtpools['name']),
                        "virsh pool-start {}".format(self.virtpools['name']),
                        "virsh pool-autostart {}".format(self.virtpools['name']),
                       # "mkdir {}/{}/backing".format(self.virtpools['path'],
                                      #               self.virtpools['name']),
                        "virsh pool-define backing-pool.xml",
                        "virsh pool-build backing",
                        "virsh pool-start backing",
                        "virsh pool-autostart backing",

                        "usermod -a -G libvirt {}".format(self.general['user'])]
                       # "chown -R {} {}".format(self.general['user'],
                        #                        self.virtpools['path'])]
            for command in commands:
                prepCmd = command.strip()
                subprocess.call(prepCmd.split(), stdout=subprocess.PIPE)
        except OSError as e:
            self.logger.info("[X] Error while adding disk pools.")
            self.logger.error(e)
            sys.exit(1)
        else:
            self.logger.info("[+] Added disk pools for libvirt.")

    def setup_network_interfaces(self):
        """
        Sets up the needed network interfaces to later communicate with the vm.
        :return:
        """
        self.logger.info("[~] Adding network interfaces...")
        try:
            commands = ["virsh net-define {}".format(self.netifaces['public-interface-config-file']),
                        "virsh net-define {}".format(self.netifaces['private-interface-config-file']),
                        "virsh net-start {}".format(self.netifaces['public-interface-name']),
                        "virsh net-start {}".format(self.netifaces['private-interface-name']),
                        "virsh net-autostart {}".format(self.netifaces['public-interface-name']),
                        "virsh net-autostart {}".format(self.netifaces['private-interface-name'])]
            for command in commands:
                prepCmd = command.strip()
                subprocess.call(prepCmd.split(), stdout=subprocess.PIPE)
        except OSError as e:
            self.logger.info("[X] Error while adding network interfaces.")
            self.logger.error(e)
            sys.exit(1)
        else:
            self.logger.info("[+] Added network interfaces.")

    def checkuser(self):
        import os

        username = os.environ.get("SUDO_USER")

        #TODO: version using getpass.getuser currently only returns root -> is there an alternative within getpass?

        if username != self.general['user']:
            self.logger.info("[X] Wrong user logged in. Check configuration in config.json. Logged in user: "+username)
            sys.exit(1)
        else:
            self.logger.info("[+] User name checked. Proceeding with installation.")

    def run(self):
        """
        Here all functions for a full installation are called.
        :return:
        """

        # Preparations
        self.load_config()
        if platform.system() == "Linux":   #OS LINUX, FUNKTION FUER WINDOWS & LINUX
            self.checkuser()

        # Installs
        self.install_sys_dep()
        self.install_pip_dep()
        if platform.system() == "Windows":
            self.install_sources()

        # Check if installation is host or vm side
        if self.param == "host":
            # Setups
            self.setup_tcpdump()
            self.setup_libivrt()
            self.setup_network_interfaces()

            # Reboot to enable virt-manager user privileges
            # Python2.7: raw_input(); Python3.7: input()
           # answer = raw_input('Shell needs to be restarted for the changes to take effect. '
            #                   'Do you want to restart now?: [y/n]')
            #if not answer or answer[0].lower() != 'y':
             #   print('You did not indicate approval')
              #  exit(1)
            #else:
             #   os.system("reboot")
        elif self.param == "vm":
            self.logger.info("[X] Nothing to do inside vm.")
        else:
            self.logger.error("[X] Unknown Parameter {}".format(self.param))


def is_admin():
    """
    Determine if script is running as admin/root
    :return:
    """
    try:
        import os
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0


def create_logger():
    """
    Create a logger for sophisticated console output
    :return:
    """
    logger = logging.getLogger("fortrace-Installer")
    logger.setLevel(logging.DEBUG)
    fmttr = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y.%m.%d %H:%M:%S")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(fmttr)
    logger.addHandler(handler)
    return logger


def main():
    """
    Main Program where instantiations take place and necessary checks and validations are done.
    :return:
    """
    logger = create_logger()

    # stop script if you are not admin
    if not is_admin():
        logger.critical("You are not an admin. Run the installation as admin/root.")
        sys.exit(1)

    # Check Command Line parameter, if none is given set to "vm"
    param = sys.argv[1] if len(sys.argv) >= 2 else "vm"

    installer = Installer(logger, param)

    # Run actual installation
    installer.run()


if __name__ == '__main__':
    main()
