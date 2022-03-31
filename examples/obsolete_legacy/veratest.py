# added by Thomas Schaefer in 2019
# Testing the basic VeraCryptWrapper functionality

from __future__ import absolute_import
import time
import logging
import subprocess
from fortrace.core.vmm import Vmm
from fortrace.utility.logger_helper import create_logger
from fortrace.core.vmm import GuestListener

# Instanciate VMM and a VM
logger = create_logger('fortraceManager', logging.DEBUG)
macsInUse = []
guests = []
guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
guest = virtual_machine_monitor1.create_guest(guest_name="veratest", platform="windows")

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()

# Creating VeraCrypt Object to call functions on
veracrypt_obj = None
veracrypt_obj = guest.application("veraCryptWrapper", {})

#Kommt spaeter alles aus einer ini Datei
container_path = "C:\\Users\\Bill\\Desktop\\test.hc"
container_size = "100M"
container_pass = "passtest"
mount_point = "x"
veracrypt_exe = "\"C:\\Program Files\\VeraCrypt\\VeraCrypt.exe\""
veracrypt_format_exe = "\"C:\\Program Files\\VeraCrypt\\VeraCrypt Format.exe\""
data_path = "C:\\Users\\Bill\\Desktop\\"
data_filename = "test.txt"

#create test.txt
guest.shellExec('echo "Das hier soll Testinhalt sein" > C:\\Users\\Bill\\Desktop\\test.txt')
time.sleep(3)

veracrypt_obj.createContainer(veracrypt_format_exe, container_path, container_size, container_pass)
time.sleep(2)
veracrypt_obj.mountContainer(veracrypt_exe, container_path, container_pass, mount_point)
time.sleep(10)  # there might be timing issues
veracrypt_obj.copyToContainer(data_path + data_filename, mount_point.upper() + ':/' + data_filename)
time.sleep(2)
veracrypt_obj.unmountContainer(veracrypt_exe, mount_point)

time.sleep(3600)
