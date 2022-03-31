# This module contains a version of the zeus bot without cryptography
# Work-cycle of Zeus v1.2.x.x:
# CnC is already running
# Clients will try to download config file via http from CnC (config.bin)
# After that a client will try to download /ip.php to determine the external ip address
# Clients may post to /gate.php to upload stolen information


# import SocketServer
# import socket
from __future__ import absolute_import
import random
import re
import shlex
import threading
import time

import requests
# from fortrace.botnet.core.botmasterbase import BotMasterBase
from requests.exceptions import MissingSchema

from fortrace.botnet.core.cncserverbase import CnCServerBase
from fortrace.botnet.core.botbase import BotBase

from fortrace.botnet.bots.zeus.zeus_generators import ZeusPacketGenerator
from fortrace.botnet.bots.zeus.zeus_generators import ZeusMessage
from fortrace.botnet.bots.zeus.zeus_generators import ZeusConfigGenerator
from fortrace.utility import rc4

from fortrace.utility.rc4 import decrypt

import six.moves.SimpleHTTPServer
import six.moves.BaseHTTPServer
from six.moves.socketserver import ThreadingMixIn
import six.moves.http_client

import six.moves.cPickle

import netifaces  # needs 0.10+

from fortrace.botnet.net.ssdp import discover
from six.moves import range

# some email providers

email_providers = ['hotmail.com', 'gmx.de', 'web.de', 'junkmail.com', 'google.com', 'googlemail.de']
passwords = ['1234', 'password', 'god', '1111', '4321', 'PASSWORD', '14.10.1967', '01.05.1955', '06.03.1982']


# used for emulating the zeus http part
# original taken from http://code.activestate.com/recipes/336012-stoppable-http-server/
# modified to enable multiple threads and accepting POST requests


class StoppableHttpRequestHandler(six.moves.SimpleHTTPServer.SimpleHTTPRequestHandler):
    """http request handler with QUIT stopping the server"""

    def do_QUIT(self):
        """send 200 OK response, and set server.stop to True"""
        self.send_response(200)
        self.end_headers()
        self.server.stop = True

    def do_POST(self):
        """ emulate post request with get handler, we don't need the data

        """
        self.do_GET()

    def parse_request(self):
        """Parse a request (internal).

        The request should be stored in self.raw_requestline; the results
        are in self.command, self.path, self.request_version and
        self.http_request_headers.

        Return True for success, False for failure; on failure, an
        error is sent back.

        """
        self.command = None  # set in case of error on the first line
        self.request_version = version = self.default_request_version
        self.close_connection = 1
        requestline = self.raw_requestline
        # hack: quick and dirty fix for doubled request with bad data
        ok = 0
        if requestline.startswith("GET"):
            ok += 1
        if requestline.startswith("POST"):
            ok += 1
        if requestline.startswith("QUIT"):
            ok += 1
        if ok == 0:
            return False
        # hack ends here
        requestline = requestline.rstrip('\r\n')
        self.requestline = requestline
        words = requestline.split()
        if len(words) == 3:
            command, path, version = words
            if version[:5] != 'HTTP/':
                self.send_error(400, "Bad request version (%r)" % version)
                return False
            try:
                base_version_number = version.split('/', 1)[1]
                version_number = base_version_number.split(".")
                # RFC 2145 section 3.1 says there can be only one "." and
                #   - major and minor numbers MUST be treated as
                #      separate integers;
                #   - HTTP/2.4 is a lower version than HTTP/2.13, which in
                #      turn is lower than HTTP/12.3;
                #   - Leading zeros MUST be ignored by recipients.
                if len(version_number) != 2:
                    raise ValueError
                version_number = int(version_number[0]), int(version_number[1])
            except (ValueError, IndexError):
                self.send_error(400, "Bad request version (%r)" % version)
                return False
            if version_number >= (1, 1) and self.protocol_version >= "HTTP/1.1":
                self.close_connection = 0
            if version_number >= (2, 0):
                self.send_error(505,
                                "Invalid HTTP Version (%s)" % base_version_number)
                return False
        elif len(words) == 2:
            command, path = words
            self.close_connection = 1
            if command != 'GET':
                self.send_error(400,
                                "Bad HTTP/0.9 request type (%r)" % command)
                return False
        elif not words:
            return False
        else:
            self.send_error(400, "Bad request syntax (%r)" % requestline)
            return False
        self.command, self.path, self.request_version = command, path, version

        # Examine the http_request_headers and look for a Connection directive
        self.headers = self.MessageClass(self.rfile, 0)

        conntype = self.headers.get('Connection', "")
        if conntype.lower() == 'close':
            self.close_connection = 1
        elif conntype.lower() == 'keep-alive' and self.protocol_version >= "HTTP/1.1":
            self.close_connection = 0
        return True


handler = StoppableHttpRequestHandler
handler.server_version = "nginx"  # Tell clients that this is an nginx server
handler.sys_version = ""  # omit the version
handler.protocol_version = "HTTP/1.1"  # Set HTTP version to 1.1
handler.extensions_map['.php'] = 'text/html'  # add mime-type for php


class StoppableHttpServer(ThreadingMixIn, six.moves.BaseHTTPServer.HTTPServer):
    """http server that reacts to self.stop flag with multi-thread support"""

    def serve_forever(self, unused_parameter=0.5):
        """Handle one request at a time until stopped.
        :param unused_parameter: originally the polling parameter
        """
        self.stop = False
        while not self.stop:
            self.handle_request()


def stop_server(port):
    """send QUIT request to http server running on localhost:<port>
    :param port: port to send request to
    """
    conn = six.moves.http_client.HTTPConnection("localhost:%d" % port)
    conn.request("QUIT", "/")
    conn.getresponse()


# the actual implementation


class ZeusBot(BotBase):
    def __init__(self, use_ssdp=True):
        BotBase.__init__(self, True)
        self.http_timeout = 3.0
        self.http_user_agent = "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)"
        self.http_request_headers = {"User-Agent": self.http_user_agent, "Pragma": "no-cache"}
        self.use_ssdp = use_ssdp
        self.encryption_key = None
        self.bot_thread = None
        self.cnc_host = "127.0.0.1"
        self.url_config = "/config.bin"  # holds the bot's config on the CnC server
        self.url_compip = "/ip.php"  # used to determine a bot's external ip for nat scenarios
        self.url_server = "/gate.php"  # used for uploading information
        self.url_loader = "/bot.exe"  # used for downloading the bot binary
        self.bot_external_ip = 0
        self.machine_id = ""  # the name of the bot
        self.botnet_name = "default"  # the botnet's name or id
        self.timer_config = (60, 1)  # time in minutes to request a config file and retry time
        self.timer_logs = (1, 1)  # time in minutes to upload stolen credentials and retry time
        self.timer_stats = (20, 1)  # time in minutes to upload machine info and retry time
        self.v_major = 1  # determines the bot major version, has not changed
        self.v_minor = 2  # determines the bot minor version, changes indicate protocol changes and such
        self.v_sub_minor = 4  # specifies a bug-fix release
        self.v_sub_sub_minor = 2  # specifies a av vendor detection change
        self.result_data = ZeusPacketGenerator()

    def execute_orders_impl(self):
        pass

    def pull_orders_impl(self, src_host, src_port):
        pass

    def start(self, agent_ip='127.0.0.1', agent_port=10556):
        BotBase.start(self, agent_ip, agent_port)
        self.cnc_host = self.globals["cnc_host"]
        try:
            self.botnet_name = self.globals["botnet_name"]
        except KeyError:
            pass
        try:
            self.url_config = self.globals["url_config"]
        except KeyError:
            pass
        try:
            self.url_compip = self.globals["url_compip"]
        except KeyError:
            pass
        try:
            self.url_server = self.globals["url_server"]
        except KeyError:
            pass
        try:
            self.url_loader = self.globals["url_loader"]
        except KeyError:
            pass
        try:
            self.encryption_key = self.globals["encryption_key"]
        except KeyError:
            self.logger.warning("RC4 cypher is disabled, using plaintext communication!")
        self._generate_machine_id()
        self._generate_random_credentials()
        self.bot_thread = threading.Thread(target=self.worker_thread)
        self.bot_thread.run()
        self.logger.info("zeus bot init done")

    def stop(self):
        BotBase.stop(self)
        if self.bot_thread is not None:
            self.bot_thread.join()
            self.bot_thread = None

    def worker_thread(self):
        if self.use_ssdp:
            self.logger.info("sending ssdp requests")
            for _ in range(3):
                discover("upnp:rootdevice", 2, 1)  # send ssdp requests to look for routers
        self.logger.info("downloading config")
        res = self._http_get_config(self.cnc_host, self.url_config)  # get the bot config
        if not self.use_ssdp:
            res = self._http_get_external_ip(self.cnc_host, self.url_compip)  # or get external ip
        self.logger.info("posting machine info")
        res = self._http_post_machine_info(self.cnc_host, self.url_server)  # post machine info
        waited = 0
        self.logger.info("init done: entering main loop")
        while self.active:
            if waited % self.timer_config[0] == 0:
                self.logger.info("downloading config")
                res = self._http_get_config(self.cnc_host, self.url_config)
                c = res.content
                if self.encryption_key is not None:
                    c = decrypt(c, self.encryption_key, salt_length=0)
                self._interpret_config(c)
            if waited % self.timer_stats[0] == 0:
                self.logger.info("posting machine info")
                res = self._http_post_machine_info(self.cnc_host, self.url_server)
                c = res.content
                if len(res.content) != 0:
                    if self.encryption_key is not None:
                        c = decrypt(c, self.encryption_key, salt_length=0)
                    z = ZeusMessage(c)
                    for s in z.segments:
                        try:
                            cmd = s.extract_command()
                            self._evaluate_command(cmd)
                        except RuntimeError:
                            pass
            if waited % self.timer_logs[0] == 0:
                self.logger.info("posting result data")
                res = self._http_post_result_data(self.cnc_host, self.url_server)
                c = res.content
                if len(res.content) != 0:
                    if self.encryption_key is not None:
                        c = decrypt(c, self.encryption_key, salt_length=0)
                    z = ZeusMessage(c)
                    for s in z.segments:
                        try:
                            cmd = s.extract_command()
                            self._evaluate_command(cmd)
                        except RuntimeError:
                            pass
            time.sleep(60)
            waited += 1
            if waited == 60 * 60 * 24:  # if day has passed reset timer
                waited = 0

    def _evaluate_command(self, cmd):
        """ Evaluate a zeus command.

        :type cmd: str
        :param cmd: a received command string
        """
        self.logger.info("got command: %s", cmd)
        l = shlex.split(cmd)
        if cmd.startswith("rexec"):  # download and (not) execute file
            if len(l) > 1:
                try:
                    requests.get(l[1], headers=self.http_request_headers, timeout=self.http_timeout)
                except requests.Timeout:
                    pass
                except MissingSchema:
                    pass
            return
        if cmd.startswith("upcfg"):  # update config file with optional url
            if len(l) < 2:
                url = self.url_config
            else:
                url = l[1]
            try:
                r = requests.get(url, headers=self.http_request_headers, timeout=self.http_timeout)
                if r.status_code == 200:
                    if len(r.content) > 0:
                        self._interpret_config(r.content)
            except requests.Timeout:
                pass
            except MissingSchema:
                pass
            return
        if cmd.startswith("rename_bot"):  # rename the bots machine id
            if len(l) == 2:
                self.machine_id = l[1]
            return

    def _interpret_config(self, cfg):
        """

        :type cfg: str
        :param cfg:
        """
        z = ZeusConfigGenerator()
        try:
            z.load_from_string(cfg)
            n = z.static_config['botnet']
            if n[0]:
                self.botnet_name = n[1]
            else:
                self.botnet_name = "default"
            tc = z.static_config['timer_config']
            if tc[0]:
                self.timer_config = (tc[1], tc[2])
            else:
                self.timer_config = (60, 1)
            tl = z.static_config['timer_logs']
            if tl[0]:
                self.timer_logs = (tl[1], tl[2])
            else:
                self.timer_logs = (1, 1)
            ts = z.static_config['timer_stats']
            if ts[0]:
                self.timer_stats = (ts[1], ts[2])
            else:
                self.timer_stats = (20, 1)
            uc = z.static_config['url_config']
            if uc[0]:
                self.url_config = uc[1]
            else:
                self.url_config = "/config.bin"
            up = z.static_config['url_compip']
            if up[0]:
                self.url_compip = up[1]
            else:
                self.url_compip = "/ip.php"
            ec = z.static_config['encryption_key']
            if self.encryption_key is not None:  # only evaluate if encryption should be used, key should not change
                if ec[0]:
                    self.encryption_key = ec[1]
                else:
                    self.encryption_key = "secret key"
            ul = z.dynamic_config['url_loader']
            if ul[0]:
                self.url_loader = ul[1]
            else:
                self.url_loader = "/bot.exe"
            us = z.dynamic_config['url_server']
            if us[0]:
                self.url_server = us[1]
            else:
                self.url_server = "/gate.php"
        except RuntimeError:
            self.logger.error("failed to parse config")

    def _generate_machine_id(self):
        """ Generate machine id based on default adapters mac address.

        """
        mach_id = "machine_"
        try:
            gws = netifaces.gateways()  # get all gateways
            default = gws['default']  # get the default gw
            adapter = default[2][1]  # get the adapter identifier
            real_adapter = netifaces.ifaddresses(adapter)  # get the adapter
            link_info = real_adapter[netifaces.AF_LINK]
            mac = link_info[0]['addr']
            mac = re.sub('[:]', '', mac)
        except:
            mac = "unsup"
            self.logger.error("Getting mac of internet card is not supported, needs netifaces >= 0.10")
        self.machine_id = mach_id + mac

    def _generate_random_credentials(self):
        url = "http://example.com/catalog/checkout_process.php"
        referer = "http://example.com/catalog/checkout_confirmation.php"
        account = "user" + str(random.choice([i for i in range(10000)]))
        account += "@"
        account += random.choice(email_providers)
        password = random.choice(passwords)
        credit_card_owner = "user"
        credit_card_number = ""
        numbers = [random.choice([i for i in range(10)]) for _ in range(16)]
        for x in numbers:
            credit_card_number += str(x)
        credit_card_expire_month = "01"
        credit_card_expire_year = "10x=47y=3"
        self.result_data.add_shop_info(url, referer, account, password, credit_card_owner, credit_card_number,
                                       credit_card_expire_month, credit_card_expire_year)

    def _http_get_config(self, host, uri="/config.bin"):
        url = "http://" + host + uri
        results = None
        while True:
            try:
                results = requests.get(url, timeout=self.http_timeout, headers=self.http_request_headers)
                if results.status_code == 200:
                    break
            except requests.Timeout:
                pass
            self.logger.info("Failed getting config, sleeping...")
            time.sleep(self.timer_config[1] * 60)
        return results

    def _http_get_external_ip(self, host, uri="/ip.php"):
        url = "http://" + host + uri
        results = None
        while True:
            try:
                results = requests.get(url, timeout=self.http_timeout, headers=self.http_request_headers)
                if results.status_code == 200:
                    break
            except requests.Timeout:
                pass
            self.logger.info("Failed getting ip, sleeping...")
            time.sleep(self.timer_config[1] * 60)
        return results

    def _http_post_machine_info(self, host, uri="/gate.php"):
        z = ZeusPacketGenerator()
        z.add_machine_id_info(self.machine_id)
        z.add_botnet_identifier_info(self.botnet_name)
        z.add_version_info(self.v_major, self.v_minor, self.v_sub_minor, self.v_sub_sub_minor)
        z.add_system_time_info(int(time.time()))
        z.add_unknown_info(0x00000000)
        z.add_unknown_info2(0x0007dd2f)
        z.add_unknown_info3("\x05\x00\x00\x00\x01\x00\x00\x00\x28\x0A\x00\x00\x02\x00\x00\x00\x00\x01\x01\x00")
        z.add_os_language_info(0x0409)
        z.add_unknown_info4(0x00000065)
        z.add_unknown_info5(0x00000000)
        z.add_unknown_info6(0x0000)
        msg = z.generate_message(self.encryption_key)
        url = "http://" + host + uri
        results = None
        while True:
            try:
                results = requests.post(url, msg, timeout=self.http_timeout, headers=self.http_request_headers)
                if results.status_code == 200:
                    break
            except requests.Timeout:
                pass
            self.logger.info("Failed posting machine info, sleeping...")
            time.sleep(self.timer_stats[1] * 60)
        return results

    def _http_post_result_data(self, host, uri):
        msg = self.result_data.generate_message(self.encryption_key)
        url = "http://" + host + uri
        results = None
        while True:
            try:
                results = requests.post(url, msg, timeout=self.http_timeout, headers=self.http_request_headers)
                if results.status_code == 200:
                    break
            except requests.Timeout:
                pass
            self.logger.info("Failed posting results, sleeping...")
            time.sleep(self.timer_logs[1] * 60)
        return results


class ZeusCnC(CnCServerBase):
    def __init__(self):
        CnCServerBase.__init__(self, True)
        self.http_server = StoppableHttpServer(('', 80), handler, True)  # listen on port 80 for all
        self.http_thread = None

    @staticmethod
    def push_file_to_server(cnc_bot, filename, content, encryption_key=None):
        """ Push a file to cnc server with optional rc4 encryption.

        :type cnc_bot: fortrace.core.cncserverbase.CnCServerBaseDelegate
        :type filename: str
        :type content: str
        :type encryption_key: str | None
        :param cnc_bot: the cnc bot to receive the file
        :param filename: the filename or path on cnc bot's side
        :param content: a files content
        :param encryption_key: an optional encryption key for the rc4 cypher
        """
        c = content
        if encryption_key is not None:
            c = rc4.encrypt(c, encryption_key, salt_length=0)  # encrypt content via rc4
        cfg = {'filename': filename, 'content': c}
        cnc_bot.host_orders(six.moves.cPickle.dumps(cfg))  # upload a serialized dict

    def host_orders_impl(self, orders):
        """ Used to write new data to the server.

        :param orders: a dict containing filename and binary content
        """
        d = six.moves.cPickle.loads(orders)
        if isinstance(d, dict):
            if 'filename' in d:
                if 'content' in d:
                    try:
                        with open(d['filename'], 'wb') as f:
                            f.write(d['content'])
                    except IOError:
                        self.logger.warning("Error writing file file due to IOError, ignoring...")
                        return False, 'IOError'
                    except OSError:
                        self.logger.warning("Error writing file file due to OSError, ignoring...")
                        return False, 'OsError'
        else:
            self.logger.warning("Received data is not a dict, ignoring...")
            return False, 'Bad data'

    def push_orders_impl(self, host, port):
        pass

    def broadcast_orders_impl(self):
        pass

    def http_worker(self):
        self.logger.info("listening on http port...")
        self.http_server.serve_forever()
        self.logger.info("stopped listening on http port")

    def start(self, agent_ip='127.0.0.1', agent_port=10556):
        CnCServerBase.start(self, agent_ip, agent_port)
        self.http_thread = threading.Thread(target=self.http_worker)
        self.http_thread.start()

    def stop(self):
        CnCServerBase.stop(self)
        if self.http_thread is not None:
            stop_server(80)
            self.http_thread.join()
            self.http_thread = None
