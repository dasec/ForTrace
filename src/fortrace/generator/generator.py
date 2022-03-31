# Copyright (C) 2019-20 Marcel Meuter
# This file is part of fortrace - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.
from __future__ import absolute_import
import logging
import random
import sys
import time
import paramiko
import yaml
import threading
import xml.etree.ElementTree as ET

from fortrace.application.mail_interface import MailAccount, Mail, send_mail, NFSSettings
from fortrace.utility.logger_helper import create_logger
from six.moves import range
from fortrace.utility.dumpgen import guest_dump


class Generator(object):
    """
    The generator can generate a randomized set of actions (simulated user activity) from a user supplied configuration
    file as well as execute the actions on a specified virtual machine afterwards in order to create and capture
    network traffic.
    """

    def __init__(self, guest, path, logger=None, seed=None):
        """

        :param guest:
        :param path:
        :param logger:
        """
        self.guest = guest
        self._logger = logger
        self.actions = []
        self.collections = {'mail': {'default': {}}, 'chat': {'default': {}},
                            'http': {'default': []}, 'printer': {'default': []}, 'smb': {'default': []},
                            'malware': {'default': []}}
        self.settings = {}
        self.dumps = []

        self.browser = None

        if self._logger is None:
            self._logger = create_logger('generator', logging.INFO)

        # Parse YAML config.
        try:
            with open(path, 'r') as f:
                self.config = yaml.safe_load(f)
        except (IOError, yaml.YAMLError) as error:
            self._logger.error('[-] Could not find or parse config file %s: %s', path, error)
            sys.exit(1)

        # Check if user specified a seed to be used for randomization.
        # Does not override the seed passed as an argument
        if 'seed' in self.config and seed is None:
            self._logger.info('[~] Using the specified seed: %d.', self.config['seed'])
            seed = self.config['seed']

        random.seed(seed)

        # Check if minimum requirements are fulfilled.
        if 'hay' not in self.config or 'needles' not in self.config:
            self._logger.error('[-] Config file does not contain both hay and needle sections.')
            sys.exit(1)

        # Load collections for different applications.
        self._logger.info('[~] Loading collections.')
        self._load_collections()

        # Setup needed objects for applications.
        self._logger.info('[~] Setup applications.')
        self._setup_applications()

        self._logger.info('[~] Generating randomized action suite.')

        items = []
        if self.config['hay'] is not None:
            items += list(self.config['hay'].items())

        if self.config['needles'] is not None:
            items += list(self.config['needles'].items())
        # Collect actions used for the hay and needle(s).

        if 'dumps' not in self.config:
            self._logger.info("[~] No dumps specified")

        elif self.config['dumps'] is not None:
            self.dumps += list(self.config['dumps'].items())

        for key, entry in items:
            # Generate action with specified parameters and generated missing parameters if needed.
            self.actions.extend(self._generate_action(key, entry))
            self._logger.info('\t Created %s set.', key)

        # Randomize action suite.
        random.shuffle(self.actions, random.random)

        # Generate action suite from config.
        self._logger.info('[+] Generated randomized action suite.')

    def shutdown(self):
        """
        Shutdowns the generator as well as the started applications within the virtual machine.
        """
        self._shutdown_browser()

    def execute(self):
        """
        Executes the previously generated set of actions.
        """
        for action in self.actions:
            print(str(action))
            self._logger.info('[~] Executing %s.', action)
            self._execute_action(action)

    def execute_dumps(self):
        if self.dumps is not None:
            for dump, details in self.dumps:
                #print(dump)
                #print(details['dump-path'])
                guest_dump(self.guest.guestname, details['dump-path'], details['dump-type'])
                self._logger.info("[~] Creating dump...")
        else:
            self._logger.info("[~] No dumps specified...")

    def _execute_action(self, action):
        """
        Executes a single action.
        :param action:
        :return:
        """
        if action['type'] == 'http':
            self._execute_action_http(action)
        elif action['type'] == 'mail':
            self._execute_action_mail(action)
        elif action['type'] == 'chat':
            pass
        elif action['type'] == 'printer':
            self._execute_action_printer(action)
        elif action['type'] == 'smb':
            self._execute_action_smb(action)
        elif action['type'] == 'malware':
            self._execute_action_malware(action)

        # Wait for a randomized interval.
        time.sleep(random.randint(1, 5))

    def _execute_action_http(self, action):
        """
        Executes a http(s) (browser) action.
        :param action:
        :return:
        """
        browser = self._get_browser()

        # Open URL.
        browser.open(url=action['url'])

        while browser.is_busy is True:
            self._logger.debug("[~] Firefox is busy.")
            time.sleep(1)

        self._logger.info('[+] HTTP: Opened URL %s.', action['url'])
        time.sleep(5)

    def _start_malware_server(self, config, action):
        """
        Starts the malware server on the malware service vm via ssh
        :param config: Name of the configuration file on the server to be executed.
        :param action:
        :return:
        """
        malware_config = self.config['applications'][action['application']]
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(malware_config['service-vm'], username="fortrace-service", password="$Anfang01")
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("cd C:\users\fortrace-service\Desktop & MalwareServer.exe config" + config)
        exit_status = ssh_stdout.channel.recv_exit_status()
        print("Malware Server: Exit Code", exit_status)
        print("cd C:\users\fortrace-service\Desktop & MalwareServer.exe config" + config)
        print("-----------------------------------------------\n")
        print(ssh_stdout.read())
        print("\n---------------------------------------------\n")
        return

    def _execute_action_malware(self, action):
        """
        Executes a malware action.
        :param action:
        :return:
        """
        print("Malware is executed")
        malware_config = self.config['applications'][action['application']]
        lines = []
        configs = 0
        with open(action['config'], 'r') as f:
            lines = f.read().splitlines()

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(malware_config['service-vm'], username="fortrace-service", password="$Anfang01")
        ftp = ssh.open_sftp()
        try:
            ftp.stat("C:\users\fortrace-service\Desktop\config" + str(configs))
            ftp.remove("C:\users\fortrace-service\Desktop\config" + str(configs))
        except:
            pass
        ftp.close()
        for i in lines:
            if i == "BrowserDownload":
                serverThread = threading.Thread(target=self._start_malware_server, args=[str(configs), action])
                serverThread.start()
                configs = configs + 1
                ftp = ssh.open_sftp()
                try:
                    ftp.stat("C:\users\fortrace-service\Desktop\config" + str(configs))
                    ftp.remove("C:\users\fortrace-service\Desktop\config" + str(configs))
                except:
                    pass
                ftp.close()
                browser = self._get_browser()
                browser.open(url=malware_config['service-vm'] + ":" + str(malware_config['service-port']) + "/" + malware_config['name'])
                while browser.is_busy:
                    time.sleep(2)
                time.sleep(120)
                browser.press_tab_test()
                time.sleep(60)
                browser.press_enter_test()
                time.sleep(60)
                self.guest.shellExec(malware_config['path'] +  "\\"+ malware_config['name'] + " dnsServer=" + malware_config['dnsServer']  + " webServer=" + malware_config ['webServer'] + " webPort=" + str(malware_config['webPort']) + " Beacon=" + str(malware_config['beacon']))
                serverThread.join()
                time.sleep(10)
            elif i == "CurlDownload":
                serverThread = threading.Thread(target=self._start_malware_server, args=[str(configs), action])
                serverThread.start()
                configs = configs + 1
                ftp = ssh.open_sftp()
                try:
                    ftp.stat("C:\users\fortrace-service\Desktop\config" + str(configs))
                    ftp.remove("C:\users\fortrace-service\Desktop\config" + str(configs))
                except:
                    pass
                ftp.close()
                self.guest.shellExec("cd " + malware_config['path'] + " && curl -O " +  malware_config['service-vm'] + ":"  + str(malware_config['service-port']) + "/" + malware_config['name'] + " && " + malware_config['path'] + "\\" + malware_config['name'] + " dnsServer=" + malware_config['dnsServer'] + " webServer=" + malware_config['webServer'] + " webPort="  + str(malware_config['webPort']) + " Beacon=" + str(malware_config['beacon']))
                time.sleep(20)
                serverThread.join()
            elif i == "MailExecution":
                serverThread = threading.Thread(target=self._start_malware_server, args=[str(configs), action])
                serverThread.start()
                configs = configs + 1
                ftp = ssh.open_sftp()
                try:
                    ftp.stat("C:\users\fortrace-service\Desktop\config" + str(configs))
                    ftp.remove("C:\users\fortrace-service\Desktop\config" + str(configs))
                except:
                    pass
                ftp.close()
                mail = self.guest.application("mailClientThunderbird", {})
                mail.set_session_password("fortrace")
                while mail.is_busy:
                    time.sleep(1)
                mail.add_pop3_account("pop3.web.de", "smtp.web.de", "theo.11111@web.de", "theo.11111", "Theo Tester", "Example", 2, 3, 2, 3)
                while mail.is_busy:
                    time.sleep(1)
                mail.open()
                while mail.is_busy:
                    time.sleep(1)
                mail.close()
                while mail.is_busy:
                    time.sleep(1)
                time.sleep(80)
                self.guest.shellExec("cd " + malware_config['path'] + " && curl -O " +  malware_config['service-vm'] + ":"  + str(malware_config['service-port']) + "/" + malware_config['name'])
                time.sleep(30)
                if 'email' in action:
                    tree = ET.parse(action['email'])
                    root = tree.getroot()
                    for item in root:
                        typ = item[0].text
                        from_name = item[1].text
                        from_ad = item[2].text
                        to_name = item[3].text
                        to_ad = item[4].text
                        user = item[5].text
                        server = item[6].text
                        timestamp = item[7].text
                        subject = item[8].text
                        message = item[9].text
                        attachments = []
                        try:
                            for attachment in item[10]:
                                attachments.append(attachment.text)
                        except IndexError:
                            pass
                        mail.loadMailboxData(typ, from_name, from_ad, to_name, to_ad, user, server, timestamp, subject, message, attachments)
                time.sleep(60)
                print("Execute")
                self.guest.shellExec("cd " + malware_config['path'] + " && " + malware_config['path'] + "\\" + malware_config['name'] + " dnsServer=" + malware_config['dnsServer'] + " webServer=" + malware_config['webServer'] + " webPort="  + str(malware_config['webPort']) + " Beacon=" + str(malware_config['beacon']))
                time.sleep(20)
                serverThread.join()
            elif i == "Reboot":
                self.guest.shutdown('keep')
                serverThread = threading.Thread(target=self._start_malware_server, args=[str(configs), action])
                configs = configs + 1
                ftp = ssh.open_sftp()
                try:
                    ftp.stat("C:\users\fortrace-service\Desktop\config" + str(configs))
                    ftp.remove("C:\users\fortrace-service\Desktop\config" + str(configs))
                except:
                    pass
                ftp.close()
                while self.guest.isGuestPowered():
                    time.sleep(1)
                serverThread.start()
                self.guest.start("2021-06-02 11:00:00")
                self.guest.waitTillAgentIsConnected()
                serverThread.join()
                time.sleep(10)
            else:
                ftp = ssh.open_sftp()
                file = ftp.file("C:\users\fortrace-service\Desktop\config" + str(configs), "a", -1)
                file.write(i + "\n")
                ftp.close()
        ssh.close()

    def _execute_action_mail(self, action):
        """
        Executes a mail action.
        :param action:
        :return:
        """
        # Create new mail application.
        mailer = self.guest.application("mailClientThunderbird", {})

        # Set mail configuration for application from config file.
        mail_account_config = self.config['applications'][action['application']]
        mail = Mail(action['recipient'], action['subject'], action['message'], action['attachments'])
        mail_account = MailAccount(
            mail_account_config['imap_hostname'],
            mail_account_config['smtp_hostname'],
            mail_account_config['email'],
            mail_account_config['password'],
            mail_account_config['username'],
            mail_account_config['full_name'],
            mail_account_config['socket_type'],
            mail_account_config['socket_type_smtp'],
            mail_account_config['auth_method_smtp']
        )

        send_mail(mailer, mail_account, mail, self.settings['nfs'])
        self._logger.info('[+] Mail: Send mail from %s to %s.', mail_account_config['email'], action['recipient'])

    def _execute_action_chat(self, action):
        """
        Executes a chat action.
        :param action:
        :return:
        """
        raise NotImplementedError("This function is not implemented yet.")

    def _execute_action_printer(self, action):
        """
        Executes a printer action.
        :param action:
        :return:
        """
        # TODO: Refactor printing functionality to own "Printer" class. How to properly address the printer which should
        # be used? Do we want to initialize different printers?

        # TODO: remomve obsolete code

        printer = self.guest.application("windowsPrinter", {})

        printer.print_document(action['file'])

        #self.guest.shellExec('notepad.exe /p "{}"'.format(action['file']))
        self._logger.info('[+] Printer: Send file %s to printer.', action['file'])
        time.sleep(5)

    def _execute_action_smb(self, action):
        """
        Executes a SMB action.
        :param action:
        :return:
        """
        samba = self.guest.application("fileTransfer", {})
        
        for _file in action['files']:
            samba.smbCopy(_file, self.config['applications'][action['application']]['destination'],
                               self.config['applications'][action['application']]['username'],
                               self.config['applications'][action['application']]['password'])
            self._logger.info('[+] SMB: Send file %s to %s.', _file,
                              self.config['applications'][action['application']]['destination'])


    def _generate_action(self, key, entry):
        """

        :param key: Unique identifier of the entry.
        :param entry: The entry in form of a dictionary itself.
        :return: Returns a action dictionary with filled in (randomized) parameters.
        """
        if entry['application'] == 'http':
            action_type = 'http'
        else:
            # Check if application configuration exists for the action.
            if entry['application'] not in self.config['applications']:
                self._logger.error('[-] No application configuration found for %s, which is required by %s.',
                                   entry['application'], key)
                sys.exit(1)

            # We can resolve the action type of the entry by the application linked to it.
            action_type = self.config['applications'][entry['application']]['type']

        if action_type == 'http':
            return self._generate_action_http(entry)
        if action_type == 'mail':
            return self._generate_action_mail(entry)
        elif action_type == 'chat':
            return self._generate_action_chat(entry)
        elif action_type == 'printer':
            return self._generate_action_printer(entry)
        elif action_type == 'smb':
            return self._generate_action_smb(entry)
        elif action_type == 'malware':
            return self._generate_action_malware(entry)
            
    def _generate_action_http(self, entry):
        """
        Generates http(s) action(s) by combining the specified parameters with randomized (default) values.
        :param entry:
        :return: List of actions.
        """
        actions = []

        if 'collection' in entry:
            if entry['collection'] in self.collections['http']:
                collection = self.collections['http'][entry['collection']]
            else:
                collection = self.collections['http']['default']
        else:
            collection = self.collections['http']['default']

        for _ in range(0, entry['amount']):
            if 'url' in entry:
                url = entry['url']
            else:
                if len(collection) > 0:
                    url = random.choice(collection)
                else:
                    url = random.choice(self.collections['http']['default'])

            actions.append(
                {'type': 'http', 'url': url})

        return actions
    
    def _generate_action_malware(self, entry):
        """
        Generates malware action(s) by combining the specified parameters.
        :param entry:
        :return: List of actions.
        """
        actions = []
        if 'collection' in entry:
            if entry['collection'] in self.collections['malware']:
                collection = self.collections['malware'][entry['collection']]
            else:
                collection = self.collections['malware']['default']
        if 'commands' in collection:
            for i in collection['commands']:
                if 'email' in collection:
                    actions.append({'type': 'malware', 'application': entry['application'], 'config': i, 'email': collection['email']})
                else:
                    actions.append({'type': 'malware', 'application': entry['application'], 'config': i})
        return actions


    def _generate_action_mail(self, entry):
        """
        Generates mail action(s) by combining the specified parameters with randomized (default) values.
        :param entry:
        :return: List of actions.
        """
        actions = []

        if 'collection' in entry:
            if entry['collection'] in self.collections['mail']:
                collection = self.collections['mail'][entry['collection']]
            else:
                collection = self.collections['mail']['default']
        else:
            collection = self.collections['mail']['default']

        for _ in range(0, entry['amount']):
            if 'subject' in entry:
                subject = entry['subject']
            else:
                if len(collection['subjects']) > 0:
                    subject = random.choice(collection['subjects'])
                else:
                    subject = random.choice(self.collections['mail']['default']['recipients'])

            if 'recipient' in entry:
                recipient = entry['recipient']
            else:
                if len(collection['recipients']) > 0:
                    recipient = random.choice(collection['recipients'])
                else:
                    recipient = random.choice(self.collections['mail']['default']['recipients'])

            if 'message' in entry:
                message = entry['message']
            else:
                if len(collection['messages']) > 0:
                    message = random.choice(collection['messages'])
                else:
                    message = random.choice(self.collections['mail']['default']['messages'])

            if 'attachments' in entry:
                attachments = entry['attachments']
            else:
                if len(collection['attachments']) > 0:
                    attachments = [random.choice(collection['attachments'])]
                else:
                    attachments = [random.choice(self.collections['mail']['default']['attachments'])]

            actions.append(
                {'type': 'mail',
                 'application': entry['application'],
                 'recipient': recipient,
                 'subject': subject,
                 'message': message,
                 'attachments': attachments})

        return actions

    def _generate_action_chat(self, entry):
        """
        Generates chat action(s) by combining the specified parameters with randomized (default) values.
        :param entry:
        :return: List of actions.
        """
        actions = []

        if 'collection' in entry:
            if entry['collection'] in self.collections['chat']:
                collection = self.collections['chat'][entry['collection']]
            else:
                collection = self.collections['chat']['default']
        else:
            collection = self.collections['chat']['default']

        for _ in range(0, entry['amount']):
            if 'recipient' in entry:
                recipient = entry['recipient']
            else:
                if len(collection['recipients']) > 0:
                    recipient = random.choice(collection['recipients'])
                else:
                    recipient = random.choice(self.collections['chat']['default']['recipients'])

            if 'message' in entry:
                message = entry['message']
            else:
                if len(collection['messages']) > 0:
                    message = random.choice(collection['messages'])
                else:
                    message = random.choice(self.collections['chat']['default']['messages'])

            if 'attachments' in entry:
                attachments = entry['attachments']
            else:
                if len(collection['attachments']) > 0:
                    attachments = random.choice(collection['attachments'])
                else:
                    attachments = random.choice(self.collections['chat']['default']['attachments'])

            actions.append(
                {'type': 'chat',
                 'application': entry['application'],
                 'recipient': recipient,
                 'message': message,
                 'attachments': attachments})

        return actions

    def _generate_action_printer(self, entry):
        """
        Generates printer action(s) by combining the specified parameters with randomized (default) values.
        :param entry:
        :return: List of actions.
        """
        actions = []

        if 'collection' in entry:
            if entry['collection'] in self.collections['printer']:
                collection = self.collections['printer'][entry['collection']]
            else:
                collection = self.collections['printer']['default']
        else:
            collection = self.collections['printer']['default']

        for _ in range(0, entry['amount']):
            if 'file' in entry:
                document = entry['file']
            else:
                if len(collection) > 0:
                    document = random.choice(collection)
                else:
                    document = random.choice(self.collections['printer']['default'])

            actions.append({'type': 'printer',
                            'application': entry['application'],
                            'file': document})

        return actions

    def _generate_action_smb(self, entry):
        """
        Generates SMB action(s) by combining the specified parameters with randomized (default) values.
        :param entry:
        :return: List of actions.
        """
        actions = []

        if 'collection' in entry:
            if entry['collection'] in self.collections['smb']:
                collection = self.collections['smb'][entry['collection']]
            else:
                collection = self.collections['smb']['default']
        else:
            collection = self.collections['smb']['default']

        for _ in range(0, entry['amount']):
            if 'files' in entry:
                files = entry['files']
            else:
                if len(collection) > 0:
                    files = random.choice(collection)
                else:
                    files = random.choice(self.collections['smb']['default'])

            actions.append({'type': 'smb',
                            'application': entry['application'],
                            'files': files})

        return actions

    def _load_collections(self):
        """
        Loads the default and user defined collections of parameters for actions (e.g. lists of URLs).
        """
        # Load custom collections if specified.
        for key, collection in self.config['collections'].items():
            if collection['type'] == 'http':
                if 'urls' in collection:
                    with open(collection['urls'], 'r') as f:
                        self.collections['http'][key] = f.read().splitlines()
                else:
                    self.collections['http'][key] = []

            elif collection['type'] == 'mail':
                self.collections['mail'][key] = {}

                if 'recipients' in collection:
                    with open(collection['recipients'], 'r') as f:
                        self.collections['mail'][key]['recipients'] = f.read().splitlines()
                else:
                    self.collections['mail'][key]['recipients'] = []

                if 'subjects' in collection:
                    with open(collection['subjects'], 'r') as f:
                        self.collections['mail'][key]['subjects'] = f.read().splitlines()
                else:
                    self.collections['mail'][key]['subjects'] = []

                if 'messages' in collection:
                    with open(collection['messages'], 'r') as f:
                        self.collections['mail'][key]['messages'] = f.read().splitlines()
                else:
                    self.collections['mail'][key]['messages'] = []

                if 'attachments' in collection:
                    with open(collection['attachments'], 'r') as f:
                        self.collections['mail'][key]['attachments'] = f.read().splitlines()
                else:
                    self.collections['mail'][key]['attachments'] = []

            elif collection['type'] == 'chat':
                self.collections['chat'][key] = {}

                if 'recipients' in collection:
                    with open(collection['recipients'], 'r') as f:
                        self.collections['chat'][key]['recipients'] = f.read().splitlines()
                else:
                    self.collections['chat'][key]['recipients'] = []

                if 'messages' in collection:
                    with open(collection['messages'], 'r') as f:
                        self.collections['chat'][key]['messages'] = f.read().splitlines()
                else:
                    self.collections['chat'][key]['messages'] = []

                if 'attachments' in collection:
                    with open(collection['attachments'], 'r') as f:
                        self.collections['chat'][key]['attachments'] = f.read().splitlines()
                else:
                    self.collections['chat'][key]['attachments'] = []

            elif collection['type'] == 'printer':
                self.collections['printer'][key] = {}

                if 'files' in collection:
                    with open(collection['files'], 'r') as f:
                        self.collections['printer'][key] = f.read().splitlines()
                else:
                    self.collections['printer'][key] = []

            elif collection['type'] == 'smb':
                self.collections['smb'][key] = {}

                if 'files' in collection:
                    with open(collection['files'], 'r') as f:
                        self.collections['smb'][key] = f.read().splitlines()
                else:
                    self.collections['printer'][key] = []
            elif collection['type'] == 'malware':
                self.collections['malware'][key] = {}
                if 'commands' in collection:
                    with open(collection['commands'], 'r') as f:
                        self.collections['malware'][key]['commands'] = f.read().splitlines()
                if 'email' in collection:
                    self.collections['malware'][key]['email'] = collection['email']

        # Load default fallback collections for http.
        with open('./generator/http_default_urls.txt', 'r') as f:
            self.collections['http']['default'] = f.read().splitlines()

        # Load default fallback collections for mails.
        with open('./generator/mail_default_recipients.txt', 'r') as f:
            self.collections['mail']['default']['recipients'] = f.read().splitlines()

        with open('./generator/mail_default_subjects.txt', 'r') as f:
            self.collections['mail']['default']['subjects'] = f.read().splitlines()

        with open('./generator/mail_default_messages.txt', 'r') as f:
            self.collections['mail']['default']['messages'] = f.read().splitlines()

        with open('./generator/general_default_attachments.txt', 'r') as f:
            self.collections['mail']['default']['attachments'] = f.read().splitlines()

        # Load default fallback collections for chat.
        with open('./generator/chat_default_recipients.txt', 'r') as f:
            self.collections['chat']['default']['recipients'] = f.read().splitlines()

        with open('./generator/chat_default_messages.txt', 'r') as f:
            self.collections['chat']['default']['messages'] = f.read().splitlines()

        with open('./generator/general_default_attachments.txt', 'r') as f:
            self.collections['chat']['default']['attachments'] = f.read().splitlines()

        # Load default fallback collections for printer.
        with open('./generator/printer_default_documents.txt', 'r') as f:
            self.collections['printer']['default'] = f.read().splitlines()

        # Load default fallback collections for SMB.
        with open('./generator/general_default_attachments.txt', 'r') as f:
            self.collections['smb']['default'] = f.read().splitlines()

    def _setup_applications(self):
        """
        Setups needed settings (and objects) for the applications to run later on.
        """
        if 'host_nfs_path' in self.config['settings'] and 'guest_nfs_path' in self.config['settings']:
            self.settings['nfs'] = NFSSettings(host_vm_nfs_path=self.config['settings']['host_nfs_path'],
                                               guest_vm_nfs_path=self.config['settings']['guest_nfs_path'])

        self._setup_printer()

    def _setup_printer(self):
        """
        Create network printer required by the config file.
        """

        # TODO remove obsolete code
        if self.config['applications'] is None:
            return

        printersetup = self.guest.application("windowsPrinter", {})

        for key, application in self.config['applications'].items():
            if application['type'] == 'printer':
                printersetup.setup_windows_network_printer(application['hostname'])
              #  self.guest.shellExec(
               #     'rundll32 printui.dll,PrintUIEntry /if /b IPPTool-Printer /m "Generic / Text Only" /r "{}"'.format(
                #        application['hostname']))
               # time.sleep(3)
               # self.guest.shellExec('rundll32 printui.dll,PrintUIEntry /y /n IPPTool-Printer')
               # time.sleep(3)
               # self.guest.shellExec(
                #    'REG ADD "HKCU\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Windows" /t REG_DWORD /v LegacyDefaultPrinterMode /d 1 /f')
                #time.sleep(5)
                self._logger.info('[~] Created new printer %s.', key)

    def _get_browser(self):
        """
        Start a instance of the Firefox browser if none is running yet and return the object. Is used to make that
        there is only one instance at the time.
        """
        # Create a new Firefox instance if there is none exists yet.
        if not self.browser:
            self.browser = self.guest.application("webBrowserFirefox", {'webBrowser': "firefox"})

            # Wait for Firefox to start.
            while self.browser.is_busy is True:
                self._logger.debug("[~] Firefox is starting. Waiting.")
                time.sleep(1)

        # Return the browser.
        return self.browser

    def _shutdown_browser(self):
        """
        Close the Firefox instance within the virtual machine.
        """
        if self.browser:
            self.browser.close()
