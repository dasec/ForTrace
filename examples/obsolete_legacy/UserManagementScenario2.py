import time
import logging
import random
import hashlib
import subprocess

from fortrace.core.vmm import Vmm
from fortrace.utility.logger_helper import create_logger
from fortrace.core.vmm import GuestListener
from fortrace.core.reporter import Reporter

# set directory to export the image and the report
export_dir = "/home/fortrace/"


class Scenario:

    Reporter = None
    currentUser = None

    def __init__(self, reporter):
        print("initializing Scenario.")
        self.Reporter = reporter
        self.currentUser = "fortrace"

    def usercreate(self, user, password):
        userManagement_obj = guest.application("userManagement", {})
        self.Reporter.add("usermanagement", "User {0} created new user: {1}; pass: {2}".format(self.currentUser, user, password))
        userManagement_obj.addUser(user, password)
        while userManagement_obj.is_busy:
            time.sleep(2)
    def userchange(self, user, password):
        userManagement_obj = guest.application("userManagement", {})
        userManagement_obj.changeUser(user, password)
        while userManagement_obj.is_busy:
            time.sleep(2)
        self.currentUser = user
    def userdelete(self, user, d_type):
        if self.currentUser == user:
            print("User {0} cannot delete itself!".format(self.currentUser))
            print("User that should be deleted: {0}".format(user))
        elif user == "fortrace":
            print("User fortrace cannot be deleted!")
        else:
            userManagement_obj = guest.application("userManagement", {})
            self.Reporter.add("usermanagement", "User {0} deleted user: {1}; File deletion: {2}".format(self.currentUser, user, d_type))
            userManagement_obj.deleteUser(user, d_type)
            while userManagement_obj.is_busy:
                time.sleep(2)


def generate_file_sh256(filename, blocksize=2**20):
    m = hashlib.sha256()
    with open(filename, "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest()



sc = Scenario(Reporter())
vm_name = "WindowsUserTest{0}".format(random.randint(0, 9999))
author = "Stephan Maltan"
hostplatform = "windows"

sc.Reporter.add("imagename", vm_name)
sc.Reporter.add("author", author)
sc.Reporter.add("baseimage", hostplatform + "-template.qcow2")


logger = create_logger('fortraceManager', logging.DEBUG)
macsInUse = []
guests = []
guestListener = GuestListener(guests, logger)
virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
guest = virtual_machine_monitor1.create_guest(guest_name=vm_name, platform="windows")

# Wait for the VM to connect to the VMM
guest.waitTillAgentIsConnected()

# Start system and create new User
sc.usercreate("Fred", "Passw0r7")
sc.userchange("Fred", "Passw0r7")
guest.shutdown("keep")
while guest.isGuestPowered():
    time.sleep(5)

# start system as new user, delete the fortrace-user and create some other users
guest.start("2021-06-02 11:00:00")
guest.waitTillAgentIsConnected()
sc.usercreate("Percy", "Passw0r7")
sc.usercreate("Ron", "Passw0r7")
sc.userchange("Ron", "Passw0r7")

guest.shutdown("keep")
while guest.isGuestPowered():
    time.sleep(5)

# start system as Ron an delete the new users in different ways
guest.start("2021-06-02 11:00:00")
guest.waitTillAgentIsConnected()
sc.userdelete("George", "delete")
sc.userdelete("Fred", "delete")
sc.userdelete("Ron", "delete")
logger.info("##############################")
logger.info("#   Scenario completed       #")
logger.info("##############################")
time.sleep(600)
guest.shutdown("keep")
while guest.isGuestPowered():
    time.sleep(5)

# calculate hash value of the qcow2 image
logger.info("Calculating hash of the qcow2 file")
qcow2_path = "/data/fortrace-pool/backing/" + vm_name + ".qcow2"
sha256 = "qcow2_sha256: " + generate_file_sh256(qcow2_path)
logger.debug("Hash of the qcow2 file calculated")
sc.Reporter.add("hash", sha256)

# convert image to raw, so it can be distributed
logger.info("converting qcow2-file to raw")
raw_path = export_dir + vm_name + ".raw"
subprocess.call(["qemu-img", "convert", qcow2_path, raw_path])
logger.info("Image was converted to raw")

# calculate hash value of the raw image
logger.info("Calculating hash of the raw image")
sha256 = "raw_sha256: " + generate_file_sh256(raw_path)
logger.debug("Hash of the raw file calculated")
sc.Reporter.add("hash", sha256)

# create report
logger.info("Creating report")
sc.Reporter.generate()
