from __future__ import absolute_import
from __future__ import print_function
import os
import time


class MailAccount:
    # TODO ENUM Socket types
    def __init__(self, imap_server, smtp_server, email_address, password, user_name, full_name, socket_type, socket_type_smtp, auth_method_smtp):
        self.imap_server = imap_server
        self.smtp_server = smtp_server
        self.email_address = email_address
        self.password = password
        self.user_name = user_name
        self.full_name = full_name
        self.socket_type = socket_type
        self.socket_type_smtp = socket_type_smtp
        self.auth_method_smtp = auth_method_smtp


class Mail:
    def __init__(self, recipient, subject, body, attachment_path_list=None):
        self.recipient = recipient
        self.subject = subject
        self.body = body
        self.attachment_path_list = attachment_path_list


class NFSSettings:
    def __init__(self, host_vm_nfs_path, guest_vm_nfs_path):
        self.host_vm_nfs_path = host_vm_nfs_path
        self.guest_vm_nfs_path = guest_vm_nfs_path


class IllegalArgumentError(ValueError):
    pass


def send_mail(guest_vm, mail_account, mail, nfs_settings=None):
    if not isinstance(mail, Mail):
        raise IllegalArgumentError("Wrong object type. Please pass for the argument mail an instance of type Mail.")

    if not isinstance(mail_account, MailAccount):
        raise IllegalArgumentError("Wrong object type. Please pass for the argument mail_account an instance of type MailAccount.")

    if mail.attachment_path_list is not None:
        mail.attachment_path_list = _generate_path_list_for_guest_vm(mail.attachment_path_list, nfs_settings.guest_vm_nfs_path, nfs_settings.host_vm_nfs_path)

    # Set a password for the mail service
    guest_vm.set_session_password(mail_account.password)

    while guest_vm.is_busy:
        time.sleep(1)

    # Load new mails
    # Create a new profile to be used by thunderbird
    guest_vm.add_imap_account(mail_account.imap_server, mail_account.smtp_server, mail_account.email_address,
                              mail_account.user_name, mail_account.full_name, socket_type=mail_account.socket_type,
                              socket_type_smtp=mail_account.socket_type_smtp, auth_method_smtp=mail_account.auth_method_smtp)

    while guest_vm.is_busy:
        time.sleep(1)

    time.sleep(20)

    # Open thunderbird and check for mail
    guest_vm.open()

    while guest_vm.is_busy:
        time.sleep(1)
    # We are done close the application
    guest_vm.close()

    while guest_vm.is_busy:
        time.sleep(1)
    time.sleep(6)

    # Send a new mail by invoking thunderbird with special command line options
    guest_vm.send_mail(message=mail.body, subject=mail.subject, receiver=mail.recipient, attachment_path_list=mail.attachment_path_list)

    while guest_vm.is_busy:
        time.sleep(1)
    time.sleep(30)


def _generate_path_list_for_guest_vm(attachment_path_list, guest_vm_nfs_path, host_vm_nfs_path):
    validated_file_list = []
    for file_path in attachment_path_list:
        if host_vm_nfs_path is None:
            validated_file_list.append(file_path)
            #TODO implement check if file exists guest side; weaken/change NFS requirements completely
        else:
            if os.path.isfile(file_path):
                if os.path.dirname(file_path) == host_vm_nfs_path:
                    guest_vm_file_path = _generate_nfs_path_for_file_on_guest_vm(file_path, guest_vm_nfs_path)
                    validated_file_list.append(guest_vm_file_path)
                else:
                    print("ERROR: " + file_path + "is not located within the host nfs directory: " + host_vm_nfs_path)
            else:
                print("ERROR: " + file_path + " is not a valid file path.")
    return validated_file_list


def _generate_nfs_path_for_file_on_guest_vm(file_path, guest_vm_nfs_path):
    return os.path.normpath(guest_vm_nfs_path + os.path.basename(file_path))
