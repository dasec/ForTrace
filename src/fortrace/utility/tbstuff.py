# Copyright (C) 2018 Sascha Kopp
# This file is part of fortrace - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.
# Utility functions for manipulating Thunderbird profiles

from __future__ import absolute_import
from fortrace.utility import osenvutil
from mozrunner import ThunderbirdRunner
from mozprofile import ThunderbirdProfile
import os
import sys
import re
import subprocess
import time
from six.moves import range


def locate_thunderbird_binary():
    """ This returns the path to the binary for thunderbird

    :return: string containing path to thunderbird binary
    """
    if sys.platform == "win32":
        if os.path.exists(r'C:\Program Files\Mozilla Thunderbird\Thunderbird.exe'):
            return r'C:\Program Files\Mozilla Thunderbird\Thunderbird.exe'
        elif os.path.exists(r'C:\Program Files (x86)\Mozilla Thunderbird\Thunderbird.exe'):
            return r'C:\Program Files (x86)\Mozilla Thunderbird\Thunderbird.exe'
    elif sys.platform.startswith("linux"):
        return "/usr/bin/thunderbird"


def add_account_config_to_profile(account_config):
    """ Use mozprofile to write account configurations to the prefs.js file.
        You will need to run Thunderbird to generate folders after using this method.

    :type account_config: dict
    :param account_config: a dictionary containing account configuration flags
    """
    tp = ThunderbirdProfile(profile=get_first_profile_folder(), restore=False)
    tp.set_preferences(account_config, "prefs.js")


def create_profile_folder_if_non_existent():
    if not has_profile():
        gen_profile_folder()


def has_profile():
    """ Checks if profile.ini exists.
        If yes assume that Thunderbird has a profile.

    :return: True, if profiles ini exists in default profile directory
    """
    if sys.platform == "win32":
        s = osenvutil.get_home_dir()
        s = os.path.join(s, "AppData\\Roaming\\Thunderbird\\profiles.ini")
        if os.path.exists(s):
            return True
        else:
            return False
    elif sys.platform.startswith("linux"):
        s = osenvutil.get_home_dir()
        s = os.path.join(s, ".thunderbird/profiles.ini")
        if os.path.exists(s):
            return True
        else:
            return False
    elif sys.platform == "darwin":
        raise NotImplementedError("No Mac OS X support!")
    else:
        raise NotImplementedError("Unsupported platform!")


def get_first_profile_folder():  # todo: detect the default profile instead, this is just hacky
    """ Returns path to the first profile found in profiles.ini.
        Always check if the file exists, before using this function.

    :return: None on error, the absolute path to the first profile
    """
    if sys.platform == "win32":
        s = osenvutil.get_home_dir()
        s = os.path.join(s, "AppData\\Roaming\\Thunderbird\\profiles.ini")
    elif sys.platform.startswith("linux"):
        s = osenvutil.get_home_dir()
        s = os.path.join(s, ".thunderbird/profiles.ini")
    elif sys.platform == "darwin":
        raise NotImplementedError("No Mac OS X support!")
    else:
        raise NotImplementedError("Unsupported platform!")
    pf = None
    with open(s, "r") as p:
        line = p.readline()  # type: str
        while line:
            if line.startswith("Path="):
                pf = line.split("=")[1].rstrip()
                break
            else:
                line = p.readline()
    if pf is not None:
        pf = os.path.join(s[:-13], pf)
        if sys.platform == "win32":
            pf = os.path.normpath(pf)  # prevent mixed path separators on win32, mozilla uses posix pathes
    return pf


def gen_profile_folder():
    b = locate_thunderbird_binary()
    subprocess.call([b, "-CreateProfile", "default"])
    success = False
    for _ in range(10):
        try:
            get_first_profile_folder() # try to get the profile folder to check if profile was generated
            success = True
        except IOError:
            time.sleep(1)
    if not success:
        raise RuntimeError("Generated profile could not be found!")


def run_thunderbird_for(time=5):
    """ Run Thunderbird for a short time to allow folder generation and profile updates or just to check Mail

    :param time: time in seconds to run tb
    """
    tr = ThunderbirdRunner()
    tr.start()
    tr.wait(time)
    tr.stop()


def gen_common():
    profiledir = get_first_profile_folder()
    mailfolder = os.path.join(profiledir, "/Mail/Local Folders")
    tb_mail_folder = str(os.path.join(profiledir, "Mail"))
    tb_imap_mail_folder = str(os.path.join(profiledir, "ImapMail"))
    common = {
        "calendar.integration.notify": False,
        "mail.append_preconfig_smtpservers.version": 2,
        "mail.root.imap": tb_imap_mail_folder,  # probably not needed and will be auto generated
        "mail.root.imap-rel": "[ProfD]ImapMail",
        "mail.root.none": tb_mail_folder,  # probably not needed and will be auto generated
        "mail.root.none-rel": "[ProfD]Mail",
        "mail.server.server1.directory": mailfolder,
        "mail.server.server1.directory-rel": "[ProfD]Mail/Local Folders",
        "mail.server.server1.hostname": "Local Folders",
        "mail.server.server1.name": "Lokale Ordner",
        "mail.server.server1.storeContractID": "@mozilla.org/msgstore/berkeleystore;1",
        "mail.server.server1.type": "none",
        "mail.server.server1.userName": "nobody",
        "mail.winsearch.firstRunDone": True,
        "mail.shell.checkDefaultClient": False,
    }
    return common


def gen_imap_account(account_number, server_number, smtp_number, imap_server, smtp_server, email_address, username,
                     full_name="John Doe", socket_type=3, socket_type_smtp=2, auth_method_smtp=3):
    """ Generates entries for an imap account.

    :param account_number: refers to the id section
    :param server_number: refers to the server section
    :param smtp_number: refers to the smtp section
    :param imap_server: address of the mail server
    :param smtp_server: address of the smtp server
    :param email_address: email address of user
    :param username: username to login, usually the email address
    :param full_name: user full name
    :param smtp_description: description for the smtp server
    :param socket_type: 0 No SSL, 1 StartTLS, 2 SSL/TLS
    :param socket_type_smtp: same as socket_type
    :param auth_method_smtp: corresponds to the password exchange method for smtp
    :return: dictionary containing the config
    """
    no = account_number  # account number
    serverno = server_number
    smtpno = smtp_number
    profiledir = get_first_profile_folder()
    # tbMailFolder = str(os.path.join(profiledir, "Mail"))
    # tbImapMailFolder = str(os.path.join(profiledir, "ImapMail"))
    # imap_server = imap_server
    # smtp_server = smtp_server
    email = email_address
    # username = email_address
    tb_imap_mail_server_folder = os.path.join(profiledir, "ImapMail", imap_server)
    imap_base_folder = "imap://" + email
    # smtp_description = smtp_description
    # full_name = full_name
    account = {
        # "calendar.integration.notify": False,
        "mail.account.account" + str(no) + ".identities": "id" + str(no),  # should probably contain multiple identities
        "mail.account.account" + str(no) + ".server": "server" + str(serverno),
        "mail.accountmanager.accounts": "account" + str(no),  # should probably contain multiple accounts
        "mail.accountmanager.defaultaccount": "account" + str(no),
        # "mail.append_preconfig_smtpservers.version": 2,
        # "mail.identity.id" + str(no) + ".full_name": full_name,
        # "mail.identity.id" + str(no) + ".reply_on_top": 1,
        # "mail.identity.id" + str(no) + ".smtpServer": "smtp" + str(smtpno),
        # "mail.identity.id" + str(no) + ".useremail": email,
        # "mail.identity.id" + str(no) + ".valid": True,
        # "mail.root.imap": tbImapMailFolder,
        # "mail.root.imap-rel": "[ProfD]ImapMail",
        # "mail.root.none": tbMailFolder,
        # "mail.root.none-rel": "[ProfD]Mail",
        "mail.identity.id" + str(no) + ".archive_folder": imap_base_folder + "Archives",
        "mail.identity.id" + str(no) + ".doBcc": False,
        "mail.identity.id" + str(no) + ".doBccList": "",
        "mail.identity.id" + str(no) + ".draft_folder": imap_base_folder + "Drafts",
        "mail.identity.id" + str(no) + ".drafts_folder_picker_mode": "0",
        "mail.identity.id" + str(no) + ".encryption_cert_name": "",
        "mail.identity.id" + str(no) + ".encryptionpolicy": 0,
        "mail.identity.id" + str(no) + ".escapedVCard": "",
        "mail.identity.id" + str(no) + ".fcc_folder": imap_base_folder + "/Sent",
        "mail.identity.id" + str(no) + ".fcc_folder_picker_mode": "0",
        "mail.identity.id" + str(no) + ".fullName": full_name,
        "mail.identity.id" + str(no) + ".organization": "",
        "mail.identity.id" + str(no) + ".reply_on_top": 1,
        "mail.identity.id" + str(no) + ".reply_to": "",
        "mail.identity.id" + str(no) + ".sign_mail": False,
        "mail.identity.id" + str(no) + ".signing_cert_name": "",
        "mail.identity.id" + str(no) + ".smtpServer": "smtp" + str(smtpno),
        "mail.identity.id" + str(no) + ".stationery_folder": imap_base_folder + "/Templates",
        "mail.identity.id" + str(no) + ".tmpl_folder_picker_mode": "0",
        "mail.identity.id" + str(no) + ".useremail": email,
        "mail.identity.id" + str(no) + ".valid": True,
        # "mail.server.server" + str(serverno) + ".authMethod": auth_method,
        "mail.server.server" + str(serverno) + ".check_new_mail": True,
        "mail.server.server" + str(serverno) + ".directory": tb_imap_mail_server_folder,
        # probably not needed and will be auto generated
        "mail.server.server" + str(serverno) + ".directory-rel": "[ProfD]ImapMail/" + imap_server,
        "mail.server.server" + str(serverno) + ".hostname": imap_server,
        "mail.server.server" + str(serverno) + ".login_at_startup": True,
        "mail.server.server" + str(serverno) + ".name": email,
        "mail.server.server" + str(serverno) + ".namespace.personal": "\"\"",
        "mail.server.server" + str(serverno) + ".socketType": socket_type,
        "mail.server.server" + str(serverno) + ".spamActionTargetAccount": imap_base_folder,
        "mail.server.server" + str(serverno) + ".storeContractID": "@mozilla.org/msgstore/berkeleystore;1",
        "mail.server.server" + str(serverno) + ".type": "imap",
        "mail.server.server" + str(serverno) + ".userName": username,
        "mail.smtpserver.smtp" + str(smtpno) + ".authMethod": auth_method_smtp,
        "mail.smtpserver.smtp" + str(smtpno) + ".hostname": smtp_server,
        #"mail.smtpserver.smtp" + str(smtpno) + ".port": 465,
        "mail.smtpserver.smtp" + str(smtpno) + ".try_ssl": socket_type_smtp,
        "mail.smtpserver.smtp" + str(smtpno) + ".username": username,
        "mail.smtpservers": "smtp" + str(smtpno),
        "mail.shell.checkDefaultClient": False,
        "mail.winsearch.firstRunDone": True,
        "mail.startup.enabledMailCheckOnce": True,
        "mail.warn_on_send_accel_key": False
        # "mail.shell.checkDefaultClient": False,
    }
    if socket_type == 0:
        account["mail.server.server" + str(serverno) + ".port"] = 143
        account["mail.smtpserver.smtp" + str(smtpno) + ".port"] = 25
    elif socket_type == 2:
        account["mail.server.server" + str(serverno) + ".port"] = 143
        account["mail.smtpserver.smtp" + str(smtpno) + ".port"] = 587
    elif socket_type == 3:
        account["mail.server.server" + str(serverno) + ".port"] = 993
        account["mail.smtpserver.smtp" + str(smtpno) + ".port"] = 587
    return account


def gen_pop_account(account_number, server_number, smtp_number, pop_server, smtp_server, email_address, username,
                    full_name="John Doe",
                    smtp_description="Google Mail", socket_type=3, auth_method=3, socket_type_smtp=3, auth_method_smtp=3):
    """ Generates entries for an pop3 account.

        :param account_number: refers to the id section
        :param server_number: refers to the server section
        :param smtp_number: refers to the smtp section
        :param pop_server: address of the mail server
        :param smtp_server: address of the smtp server
        :param email_address: email address of user
        :param username: username to login, usually the email address
        :param full_name: user full name
        :param smtp_description: description for the smtp server
        :param socket_type: 0 No SSL, 1 StartTLS, 2 SSL/TLS
        :param socket_type_smtp: same as socket_type
        :param auth_method: corresponds to the password exchange method, pop supports other/additional methods than imap
        :param auth_method_smtp: corresponds to the password exchange method for the smtp server
        :return: dictionary containing the config
        """
    no = account_number
    smtpno = smtp_number
    serverno = server_number
    profiledir = get_first_profile_folder()
    # full_name = full_name
    email = email_address
    mail_server = pop_server
    # username = email_address  # todo: common for public email servers, better to add parameter for it
    # smtp_description = smtp_description
    # smtp_server = smtp_server
    tb_pop_mail_server_folder = os.path.join(profiledir, "Mail", mail_server)
    mailbox = "mailbox://" + email.replace("@", "%40") + "@" + mail_server
    ac = {
        "mail.account.account" + str(no) + ".server": "server" + str(serverno),
        "mail.account.account" + str(no) + ".identities": "id" + str(no),
        # should probably contain multiple identities
        "mail.accountmanager.accounts": "account" + str(no),  # should probably contain multiple servers
        "mail.accountmanager.defaultaccount": "account" + str(no),
        "mail.identity.id" + str(no) + ".archive_folder": mailbox + "/Archives",
        "mail.identity.id" + str(no) + ".doBcc": False,
        "mail.identity.id" + str(no) + ".doBccList": "",
        "mail.identity.id" + str(no) + ".draft_folder": mailbox + "/Drafts",
        "mail.identity.id" + str(no) + ".drafts_folder_picker_mode": "0",
        "mail.identity.id" + str(no) + ".encryption_cert_name": "",
        "mail.identity.id" + str(no) + ".encryptionpolicy": 0,
        "mail.identity.id" + str(no) + ".escapedVCard": "",
        "mail.identity.id" + str(no) + ".fcc_folder": mailbox + "/Sent",
        "mail.identity.id" + str(no) + ".fcc_folder_picker_mode": "0",
        "mail.identity.id" + str(no) + ".fullName": full_name,
        "mail.identity.id" + str(no) + ".organization": "",
        "mail.identity.id" + str(no) + ".reply_on_top": 1,
        "mail.identity.id" + str(no) + ".reply_to": "",
        "mail.identity.id" + str(no) + ".sign_mail": False,
        "mail.identity.id" + str(no) + ".signing_cert_name": "",
        "mail.identity.id" + str(no) + ".smtpServer": "smtp" + str(smtpno),
        "mail.identity.id" + str(no) + ".stationery_folder": mailbox + "/Templates",
        "mail.identity.id" + str(no) + ".tmpl_folder_picker_mode": "0",
        "mail.identity.id" + str(no) + ".useremail": email,
        "mail.identity.id" + str(no) + ".valid": True,
        "mail.server.server" + str(serverno) + ".authMethod": auth_method,
        "mail.server.server" + str(serverno) + ".applyToFlaggedMessages": False,
        "mail.server.server" + str(serverno) + ".check_new_mail": True,
        "mail.server.server" + str(serverno) + ".cleanupBodies": False,
        "mail.server.server" + str(serverno) + ".daysToKeepBodies": 30,
        "mail.server.server" + str(serverno) + ".daysToKeepHdrs": 30,
        "mail.server.server" + str(serverno) + ".delete_mail_left_on_server": True,
        "mail.server.server" + str(serverno) + ".directory": tb_pop_mail_server_folder,
        "mail.server.server" + str(serverno) + ".directory-rel": "[ProfD]Mail/" + mail_server,
        "mail.server.server" + str(serverno) + ".downloadByDate": False,
        "mail.server.server" + str(serverno) + ".downloadUnreadOnly": False,
        "mail.server.server" + str(serverno) + ".download_on_biff": True,
        "mail.server.server" + str(serverno) + ".hostname": mail_server,
        # was different than realhostname, maybe unused
        "mail.server.server" + str(serverno) + ".keepUnreadOnly": False,
        "mail.server.server" + str(serverno) + ".leave_on_server": True,
        "mail.server.server" + str(serverno) + ".login_at_startup": True,
        "mail.server.server" + str(serverno) + ".name": email_address,
        "mail.server.server" + str(serverno) + ".numHdrsToKeep": 2000,
        "mail.server.server" + str(serverno) + ".num_days_to_leave_on_server": 14,
        #"mail.server.server" + str(serverno) + ".port": 995,
        "mail.server.server" + str(serverno) + ".realhostname": mail_server,
        "mail.server.server" + str(serverno) + ".socketType": socket_type,
        "mail.server.server" + str(serverno) + ".spamActionTargetAccount": mailbox,
        "mail.server.server" + str(serverno) + ".storeContractID": "@mozilla.org/msgstore/berkeleystore;1",
        "mail.server.server" + str(serverno) + ".type": "pop3",
        "mail.server.server" + str(serverno) + ".userName": username,
        "mail.smtpserver.smtp" + str(smtpno) + ".authMethod": auth_method_smtp,
        "mail.smtpserver.smtp" + str(smtpno) + ".description": smtp_description,
        "mail.smtpserver.smtp" + str(smtpno) + ".hostname": smtp_server,
        #"mail.smtpserver.smtp" + str(smtpno) + ".port": 465,
        "mail.smtpserver.smtp" + str(smtpno) + ".try_ssl": socket_type_smtp,
        "mail.smtpserver.smtp" + str(smtpno) + ".username": username,
        "mail.smtpservers": "smtp" + str(smtpno),  # should probably contain multiple servers
    }
    if socket_type == 0:
        ac["mail.server.server" + str(serverno) + ".port"] = 110
        ac["mail.smtpserver.smtp" + str(smtpno) + ".port"] = 587
    elif socket_type == 2:
        ac["mail.server.server" + str(serverno) + ".port"] = 110
        ac["mail.smtpserver.smtp" + str(smtpno) + ".port"] = 587
    elif socket_type == 3:
        ac["mail.server.server" + str(serverno) + ".port"] = 995
        ac["mail.smtpserver.smtp" + str(smtpno) + ".port"] = 465
    return ac


def find_next_free_profile_id():
    """ Count account id numbers till a free one is found
        If this returns 1 the common section is still missing.

    :rtype: int
    :return: next free slot
    """
    p = ThunderbirdProfile(get_first_profile_folder())
    s = p.summary()
    cnt = 1
    while True:
        if s.count("id" + str(cnt)) > 0:
            cnt += 1
        else:
            break
    return cnt


def find_next_free_smtp_id():
    """ Count smtp id numbers till a free one is found

    :rtype: int
    :return: next free slot
    """
    p = ThunderbirdProfile(get_first_profile_folder())
    s = p.summary()
    cnt = 1
    while True:
        if s.count("smtp" + str(cnt)) > 0:
            cnt += 1
        else:
            break
    return cnt


def find_next_free_server_id():
    """ Count server id numbers till a free one is found

    :rtype: int
    :return: next free slot
    """
    p = ThunderbirdProfile(get_first_profile_folder())
    s = p.summary()
    cnt = 1
    while True:
        if s.count("server" + str(cnt)) > 0:
            cnt += 1
        else:
            break
    return cnt


def get_default_calendar_guid():
    """ Returns the guid of the default calendar
        This will only work if Thunderbird was started at least one time.

    :rtype: str
    :return: string guid or trow index error on unsuccessful try
    """
    p = ThunderbirdProfile(get_first_profile_folder())
    s = p.summary()
    rval = re.findall(
        '(?<=calendar\.registry\.)([0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})(?=\.calendar-main-default:)',
        s)[0]  # todo: actually look for the True value here
    return rval
