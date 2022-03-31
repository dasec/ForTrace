#!/usr/bin/python3
from __future__ import absolute_import
import sys
import os
import logging
import platform

pip_requ_file = "PIP_requirements.txt"
packet_requ_file = "packet_requirements.txt"

requ = "."
#requ = "Y:\Dokumente\git\fortrace"            # just for development stuff

# is current script user an admin / root
def isAdmin():
    try:
        import os
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0


def main():
    
    # Logger Stuff
    logger = logging.getLogger("fortrace-Installer")
    logger.setLevel(logging.DEBUG)
    fmttr = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y.%m.%d %H:%M:%S")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(fmttr)
    
    logger.addHandler(handler)
    logger.debug("test")
    
    # stop script if you are no admin
    if not isAdmin():
        logger.critical("You are not an admin. Run the installation as admin.")
	sys.exit(1)
        
    # Install required packages
    aptCmd = "apt-get --yes install {}"
    packetDepFile = os.path.join(requ, packet_requ_file)
    with open(packetDepFile, "r") as file:
        for line in file:
            prepCmd = aptCmd.format(line.strip())
            logger.debug("Running: {}".format(prepCmd))
            os.system(prepCmd)
    
    # Install pip dependencies
    pipCmd = "pip install -U {}"
    pipDepFile = os.path.join(requ, pip_requ_file)
    with open(pipDepFile, "r") as file:
        for line in file:
            prepCmd = pipCmd.format(line.strip())
            logger.debug("Running: {}".format(prepCmd))
            os.system(prepCmd)
    
    # Alternatve
    #inst_pip_requirements_cmd = "pip install -U --requirement {}".format(pip_requ_file)
    #logger.debug("Install pip requirement: {}".format(inst_pip_requirements_cmd))
    #os.system(inst_pip_requirements_cmd)
    
    # Setup tcpdump user rights
	
	

if __name__ == '__main__':
    main()
