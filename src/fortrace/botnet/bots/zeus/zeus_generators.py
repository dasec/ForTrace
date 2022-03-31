# package for generating zeus specific data packets

from __future__ import absolute_import
import hashlib
import struct
import shlex
import fortrace.utility.rc4 as rc4
from six.moves import range

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


class ZeusPacketGenerator(object):
    """ This class generates zeus specific messages.

        A message consists of a message header and one or more segments containing segment specific data.
        Look at _build_segment_header and _build_message_header for details.
        In addition a message is encoded via the RC4 cypher without a seed or IV making communication vulnerable to
        sequence analysis.
    """

    def __init__(self):
        self.segments = list()

    # system info

    def add_machine_id_info(self, machine_id):
        """ Add the machine id segment.
            First information of POST.

        :type machine_id: str
        :param machine_id: a string representing the machine id
        """
        b = bytearray(machine_id)
        header = ZeusPacketGenerator._build_segment_header(0x00002711, b)
        b = header + b
        self.segments.append(b)

    def add_botnet_identifier_info(self, botnet_name):
        """ Add the botnet id segment.
            Second information of POST.

        :type botnet_name: str
        :param botnet_name: a string representing the machine id
        """
        b = bytearray(botnet_name)
        header = ZeusPacketGenerator._build_segment_header(0x00002712, b)
        b = header + b
        self.segments.append(b)

    def add_version_info(self, version_major, version_minor, version_sub_minor, version_sub_sub_minor):
        """ Add the zeus version information segment.
            Third segment of POST.
            Each parameter must fit a byte.

        :type version_sub_sub_minor: int
        :type version_sub_minor: int
        :type version_minor: int
        :type version_major: int
        :param version_major: Zeus major version number, doesn't change no major changes or rewrite detected, it's 1
        :param version_minor: Zeus minor version number, means some code or protocol changes
        :param version_sub_minor: Zeus sub minor version number, usually some kind of bugfix
        :param version_sub_sub_minor: Zeus sub sub minor version number, usually a fix for AV detection
        """
        b = bytearray()
        b.append(version_sub_sub_minor)
        b.append(version_sub_minor)
        b.append(version_minor)
        b.append(version_major)
        header = ZeusPacketGenerator._build_segment_header(0x00002713, b)
        b = header + b
        self.segments.append(b)

    def add_system_time_info(self, unix_time):
        """ Add the system type information segment.
            Forth segment of POST.

        :type unix_time: int
        :param unix_time: the current system time since epoch
        """
        if isinstance(unix_time, int):
            raise ValueError("unix_time size too large, use 32bit data")
        b = bytearray()
        b += struct.pack("<I", unix_time)
        header = ZeusPacketGenerator._build_segment_header(0x00002719, b)
        b = header + b
        self.segments.append(b)

    def add_unknown_info(self, data=0x00000000):
        """ This is fifth segment.
            Assumed to be timezone-offset

        :type data: int
        :param data: data of segment
        """
        b = bytearray()
        b += struct.pack("<I", data)
        header = ZeusPacketGenerator._build_segment_header(0x0000271b, b)
        b = header + b
        self.segments.append(b)

    def add_unknown_info2(self, data=0x0007dd2f):
        """ This is sixth segment.
            Assumed to be the current runtime.

        :type data: int
        :param data: data of segment
        """
        b = bytearray()
        b += struct.pack("<I", data)
        header = ZeusPacketGenerator._build_segment_header(0x0000271a, b)
        b = header + b
        self.segments.append(b)

    def add_unknown_info3(self,
                          data="\x05\x00\x00\x00\x01\x00\x00\x00\x28\x0A\x00\x00\x02\x00\x00\x00\x00\x01\x01\x00"):
        """ This is the seventh segment.
            Assumed to be some sort of system information.

        :type data: str
        :param data:
        """
        b = bytearray(data)
        header = ZeusPacketGenerator._build_segment_header(0x0000271c, b)
        b = header + b
        self.segments.append(b)

    def add_os_language_info(self, language_code=0x0409):
        """ Adds the os language segment.
            This is the eight segment.

        :type language_code: int
        :param language_code: the language code/codepage, needs to be 16bit integer/short
        """
        b = bytearray()
        b += struct.pack("<H", language_code)
        header = ZeusPacketGenerator._build_segment_header(0x0000271d, b)
        b = header + b
        self.segments.append(b)

    def add_unknown_info4(self, data=0x00000065):
        """ This is ninth segment.
            No clue!

        :type data: int
        :param data: data of segment
        """
        b = bytearray()
        b += struct.pack("<I", data)
        header = ZeusPacketGenerator._build_segment_header(0x00002714, b)
        b = header + b
        self.segments.append(b)

    def add_unknown_info5(self, data=0x00000000):
        """ This is tenth segment.
            No clue!

        :type data: int
        :param data: data of segment
        """
        b = bytearray()
        b += struct.pack("<I", data)
        header = ZeusPacketGenerator._build_segment_header(0x00002715, b)
        b = header + b
        self.segments.append(b)

    def add_unknown_info6(self, data=0x0000):
        """ This is the eleventh segment.
            No clue!

        :type data: int
        :param data: needs to be 16bit integer/short
        """
        b = bytearray()
        b += struct.pack("<H", data)
        header = ZeusPacketGenerator._build_segment_header(0x00002716, b)
        b = header + b
        self.segments.append(b)

    # ip utility

    def add_ip_address_info(self, ip_address):
        """ Adds the ip address segment requested for ip.php.

        :type ip_address: int
        :param ip_address: ip address as an integer
        """
        b = bytearray()
        b += struct.pack("<H", ip_address)
        header = ZeusPacketGenerator._build_segment_header(0x00000002, b)  # todo: verify segment id code
        b = header + b
        self.segments.append(b)

    # information about criminal activity

    def add_shop_info(self, url, referer, account, password, credit_card_owner, credit_card_number,
                      credit_card_expire_date_month, credit_card_expire_date_year):
        """ Adds a segment with shopping information such as the costumers account and credit card information.
            Segment is constructed like html content, meaning CR-LF linebreaks.

        :type credit_card_expire_date_year: str
        :type credit_card_expire_date_month: str
        :type credit_card_number: str
        :type credit_card_owner: str
        :type password: str
        :type account: str
        :type referer: str
        :type url: str
        :param url: payment page (e.g. http://192.168.252.132/catalog/checkout_process.php)
        :param referer: referer to payment page (e.g. http://192.168.252.132/catalog/checkout_confirmation.php)
        :param account: account name or email address (e.g. user@email.com123456)
        :param password: password or hash? for account (e.g. 4408041234567893)
        :param credit_card_owner: owner of the credit card (e.g. Name)
        :param credit_card_number: credit cards number (e.g. 4408041234567893)
        :param credit_card_expire_date_month: date of expiry (month) (e.g. 01)
        :param credit_card_expire_date_year: date of expiry (year) (e.g. 10x=47y=3)
        """
        s = ""
        s += url
        s += "\r\n"
        s += "Referer:\r\n"
        s += referer
        s += "\r\n"
        s += "Keys: "
        s += account
        s += " "
        s += password
        s += " Data:\r\n"
        s += "cc_owner="
        s += credit_card_owner
        s += " cc_number_nh-dns="
        s += credit_card_number
        s += "\r\n"
        s += "cc_expires_month="
        s += credit_card_expire_date_month
        s += "\r\n"
        s += "cc_expires_year="
        s += credit_card_expire_date_year
        s += "\r\n"
        b = bytearray(s)
        header = ZeusPacketGenerator._build_segment_header(0x00002720, b)
        b = header + b
        self.segments.append(b)

    def add_ftp_info(self, user, password, host):
        """ Adds a segment with ftp credentials

        :type host: str
        :type password: str
        :type user: str
        :param user: a username
        :param password: a password
        :param host: a host or ip address
        """
        s = "ftp://" + user + ":" + password + "@" + host + "\r\n"
        b = bytearray(s)
        header = ZeusPacketGenerator._build_segment_header(0x00002721, b)  # todo: check segment id code
        b = header + b
        self.segments.append(b)

    def add_pop3_info(self, user, password, host):
        """ Adds a segment with ftp credentials

        :type host: str
        :type password: str
        :type user: str
        :param user: a username
        :param password: a password
        :param host: a host or ip address
        """
        s = user + ":" + password + "@" + host + "\r\n"
        b = bytearray(s)
        header = ZeusPacketGenerator._build_segment_header(0x00002722, b)  # todo: check segment id code
        b = header + b
        self.segments.append(b)

    # generic command

    def add_command_info(self, cmd_string,
                         unknown_sequence="\x2f\x3f\x9b\xab\x30\x3c\x13\x5c\x6e\x79\x8e\x4e\xaf\xb1\xbf\xe6"):
        """ Generate the command segment.
            The following commands are supported by Zeus, but any string may be inserted as command
            (source: https://blogs.mcafee.com/mcafee-labs/zeus-crimeware-toolkit/):
            reboot                       -> Reboot computer
            kos                          -> Destroy system files
            shutdown                     -> Shuts the computer down
            bc_add [service] [ip] [port] -> Add backconnect to server
            bc_del [service] [ip] [port] -> Remove backconnect
            block_url [url]              -> Disable access to url
            unblock_url [url]            -> Enable access to url
            block_fake [url]             -> Disable fake/inject
            unblock_fake [url]           -> Enable fake/inject
            rexec [url] [args]           -> Download and execute file
            rexeci [url] [args]          -> Download and execute file (interactive)
            lexec [url] [args]           -> Execute local file
            lexeci [url] [args]          -> Execute local file (interactive)
            addsf [file_mask...]         -> Add file masks for local search
            delsf [file_mask...]         -> Remove file masks from local search
            getfile [path]               -> Upload file or folder to server
            getcerts                     -> Upload certificates to server
            resetgrab                    -> Upload info from protected store to server
            upcfg [url]                  -> Update config file, url is optional
            rename_bot [name]            -> Sets a new bot name
            getmff                       -> Upload Flash files to server
            delmff                       -> Delete Flash files
            sethomepage [url]            -> Set IE homepage to url

        :type unknown_sequence: str
        :type cmd_string: str
        :param cmd_string: a string representing a bot command
        :param unknown_sequence: this is a 16 byte sequence of unknown purpose, might be a hash but tests show
                                 that it isn't a md5 sequence like in the message header.
        """
        b = bytearray()
        b += unknown_sequence
        b += cmd_string
        header = ZeusPacketGenerator._build_segment_header(0x00000001, b)
        b = header + b
        self.segments.append(b)

    # generator specific

    def generate_message(self, encryption_key=None):
        """ Generates a message for the zeus network.

        :type encryption_key: str | None
        :param encryption_key: encryption_key used to encrypt message
        :return: the message
        :rtype: bytearray
        """
        if len(self.segments) == 0:  # no data, no message
            return bytearray()
        b = bytearray()
        for x in self.segments:
            b += x
        header = ZeusPacketGenerator._build_message_header(b)
        b = header + b
        if encryption_key is not None:
            b = rc4.encrypt(str(b), encryption_key, salt_length=0)  # zeus uses no salt
            b = bytearray(b)
        return b

    def clear(self):
        self.segments = list()

    @staticmethod
    def _build_segment_header(segment_type, data):
        """ Build a segment header from data and segment type.
            Format: type(4),unknown(4),length(4),copy of length(4)
            Number in brackets means amount of bytes used by field.
            All integers are little-endian.

        :type data: bytes | bytearray
        :type segment_type: int
        :param segment_type: value of the message type, will be converted to little-endian
        :param data: a segments data
        :return: a segment header
        """
        b = bytearray()
        if isinstance(segment_type, int):
            raise ValueError("segment_type size too large")
        length = len(data)
        if isinstance(length, int):
            raise ValueError("message size too large")
        b += struct.pack("<I", segment_type)
        for x in range(4):
            b.append(0x00)
        b += struct.pack("<I", length)
        b += struct.pack("<I", length)
        assert len(b) == 16
        return b

    @staticmethod
    def _build_message_header(data):
        """ Build a message header from data.
            Format: length(4),unknown(8),md5 hash(16)
            Number in brackets means amount of bytes used by field.
            All integers are little-endian.

        :type data: bytes | bytearray
        :param data: a message's data
        :return: the message header
        """
        b = bytearray()
        length = len(data)
        if isinstance(length, int):
            raise ValueError("message size too large")
        m = hashlib.md5()
        m.update(data)
        digest = m.digest()
        b += struct.pack("<I", length + 28)  # length is content size + header site
        for x in range(8):
            b.append(0x00)
        b += digest
        assert len(b) == 28
        return b


class ZeusConfigGenerator(object):
    def __init__(self):
        self.static_config = dict()
        self.dynamic_config = dict()
        self.advanced_config = list()
        self.web_filters = list()
        self.web_data_filters = list()
        self.web_fakes = list()
        self.tan_graber = list()
        self.dns_map = list()
        self.build_time = ";Build time: 14:15:23 10.04.2009 GMT"
        self.version = ";Version: 1.2.4.2"
        self.static_config['botnet'] = (True, 'btn1')
        self.static_config['timer_config'] = (False, "60", "1")
        self.static_config['timer_logs'] = (False, "1", "1")
        self.static_config['timer_stats'] = (False, "20", "1")
        self.static_config['url_config'] = (False, "http://localhost/config.bin")
        self.static_config['url_compip'] = (False, "http://localhost/ip.php", "1024")
        self.static_config['encryption_key'] = (False, "secret key")
        self.static_config['blacklist_languages'] = (True, "1049")
        self.dynamic_config['url_loader'] = (False, "http://localhost/bot.exe")
        self.dynamic_config['url_server'] = (False, "http://localhost/gate.php")
        self.dynamic_config['file_webinjects'] = (False, "webinjects.txt")

    def set_defaults(self):
        """ This sets values for some default entries.
            The first value of each config specifies if a line is commented out.
            Each value is separated by a single space.

        """
        self.build_time = ";Build time: 14:15:23 10.04.2009 GMT"
        self.version = ";Version: 1.2.4.2"
        self.static_config['botnet'] = (True, 'btn1')
        self.static_config['timer_config'] = (False, "60", "1")
        self.static_config['timer_logs'] = (False, "1", "1")
        self.static_config['timer_stats'] = (False, "20", "1")
        self.static_config['url_config'] = (False, "http://localhost/config.bin")
        self.static_config['url_compip'] = (False, "http://localhost/ip.php", "1024")
        self.static_config['encryption_key'] = (False, "secret key")
        self.static_config['blacklist_languages'] = (True, "1049")
        self.dynamic_config['url_loader'] = (False, "http://localhost/bot.exe")
        self.dynamic_config['url_server'] = (False, "http://localhost/gate.php")
        self.dynamic_config['file_webinjects'] = (False, "webinjects.txt")

    def clear(self):
        self.__init__()

    def generate_config(self):
        # version header
        """ Generate a plaintext config file for Zeus v1.2.
            Write the resulting data using binary mode to preserve Windows line endings.

        :rtype: str
        :return: a string representing the binary config file
        """
        c = self.build_time + "\r\n"
        c += self.version + "\r\n"
        c += "\r\n"
        # static config
        c += "entry \"StaticConfig\"\r\n"
        c += "\t"
        if self.static_config['botnet'][0]:
            c += ";"
        c += "botnet "
        c += "\"" + self.static_config['botnet'][1] + "\"\r\n"
        c += "\t"
        if self.static_config['timer_config'][0]:
            c += ";"
        c += "timer_config "
        c += self.static_config['timer_config'][1] + " " + self.static_config['timer_config'][2] + "\r\n"
        c += "\t"
        if self.static_config['timer_logs'][0]:
            c += ";"
        c += "timer_logs "
        c += self.static_config['timer_logs'][1] + " " + self.static_config['timer_logs'][2] + "\r\n"
        c += "\t"
        if self.static_config['timer_stats'][0]:
            c += ";"
        c += "timer_stats "
        c += self.static_config['timer_stats'][1] + " " + self.static_config['timer_stats'][2] + "\r\n"
        c += "\t"
        if self.static_config['url_config'][0]:
            c += ";"
        c += "url_config "
        c += "\"" + self.static_config['url_config'][1] + "\"\r\n"
        c += "\t"
        if self.static_config['url_compip'][0]:
            c += ";"
        c += "url_compip "
        c += "\"" + self.static_config['url_compip'][1] + "\" " + self.static_config['url_compip'][2] + "\r\n"
        c += "\t"
        if self.static_config['encryption_key'][0]:
            c += ";"
        c += "encryption_key "
        c += "\"" + self.static_config['encryption_key'][1] + "\"\r\n"
        c += "\t"
        if self.static_config['blacklist_languages'][0]:
            c += ";"
        c += "blacklist_languages "
        c += self.static_config['blacklist_languages'][1] + "\r\n"
        c += "end\r\n"
        c += "\r\n"
        # dynamic config
        c += "entry \"DynamicConfig\"\r\n"
        c += "\t"
        if self.dynamic_config['url_loader'][0]:
            c += ";"
        c += "url_loader "
        c += "\"" + self.dynamic_config['url_loader'][1] + "\"\r\n"
        c += "\t"
        if self.dynamic_config['url_server'][0]:
            c += ";"
        c += "url_server "
        c += "\"" + self.dynamic_config['url_server'][1] + "\"\r\n"
        c += "\t"
        if self.dynamic_config['file_webinjects'][0]:
            c += ";"
        c += "file_webinjects "
        c += "\"" + self.dynamic_config['file_webinjects'][1] + "\"\r\n"
        # advanced config
        c += "\tentry \"AdvancedConfigs\"\r\n"
        for x in self.advanced_config:
            c += "\t\t" + x + "\r\n"
        c += "\tend\r\n"
        c += "\r\n"
        # web filters
        c += "\tentry \"WebFilters\"\r\n"
        for x in self.web_filters:
            c += "\t\t" + x + "\r\n"
        c += "\tend\r\n"
        c += "\r\n"
        # web data filters
        c += "\tentry \"WebDataFilters\"\r\n"
        for x in self.web_data_filters:
            c += "\t\t" + x + "\r\n"
        c += "\tend\r\n"
        c += "\r\n"
        # web fakes
        c += "\tentry \"WebFakes\"\r\n"
        for x in self.web_fakes:
            c += "\t\t" + x + "\r\n"
        c += "\tend\r\n"
        c += "\r\n"
        # tan grabber
        c += "\tentry \"TANGrabber\"\r\n"
        for x in self.tan_graber:
            c += "\t\t" + x + "\r\n"
        c += "\tend\r\n"
        c += "\r\n"
        # dns map
        c += "\tentry \"DnsMap\"\r\n"
        for x in self.dns_map:
            c += "\t\t" + x + "\r\n"
        c += "\tend\r\n"
        c += "\r\n"
        c += "end"
        return c

    def generate_sample_config(self):
        """ This generates a sample configuration file based on the config presented by:
            Zeus: King of the Bots by Nicolas Falliere and Eric Chien published by Symantec Corporation 2010

        :rtype: str
        :return: a string representing the binary config file
        """
        self.clear()
        self.add_advanced_config_entry("http://advdomain/cfg1.bin", True)
        self.add_web_filter("!*.microsoft.com/*")
        self.add_web_filter("!http://*myspace.com*")
        self.add_web_filter("https://www.gruposantander.es/*")
        self.add_web_filter("!http://*odnoklassniki.ru/*")
        self.add_web_filter("!http://vkontakte.ru/*")
        self.add_web_filter("@*/login.osmp.ru/*")
        self.add_web_filter("@*/atl.osmp.ru/*")
        self.add_web_data_filter("http://mail.rambler.ru/*", "passw;login", True)
        self.add_web_fake("\"http://www.google.com\" \"http://www.yahoo.com\" \"GP\" \"\" \"\"", True)
        self.add_tan_grabber("\"https://banking.*.de/cgi/ueberweisung.cgi/*\" \"S3R1C6G\" \"*&tid=*\" \"*&betrag=*\"")
        self.add_tan_grabber("\"https://internetbanking.gad.de/banking/*\" \"S3C6\" \"*\" \"*\" \"KktNrTanEnz\"")
        self.add_tan_grabber("\"https://www.citibank.de/*/jba/mp#/SubmitRecap.do\" \"S3C6R2\" \"SYNC_TOKEN=*\" \"*\"")
        self.add_dns_map_entry("127.0.0.1", "microsoft.com", True)
        return self.generate_config()

    def add_advanced_config_entry(self, entry, comment=False):
        if comment:
            self.advanced_config.append(";\"" + entry + "\"")
        else:
            self.advanced_config.append("\"" + entry + "\"")

    def add_web_filter(self, filter_regex, comment=False):
        if comment:
            self.web_filters.append(";\"" + filter_regex + "\"")
        else:
            self.web_filters.append("\"" + filter_regex + "\"")

    def add_web_data_filter(self, url, data, comment=False):
        if comment:
            self.web_data_filters.append(";\"" + url + "\" \"" + data + "\"")
        else:
            self.web_data_filters.append("\"" + url + "\" \"" + data + "\"")

    def add_web_fake(self, fake_line, comment=False):
        if comment:
            self.web_fakes.append(";" + fake_line)
        else:
            self.web_fakes.append(fake_line)

    def add_tan_grabber(self, grabber_line, comment=False):
        if comment:
            self.tan_graber.append(";" + grabber_line)
        else:
            self.tan_graber.append(grabber_line)

    def add_dns_map_entry(self, ip, dns_name, comment=False):
        if comment:
            self.dns_map.append(";" + ip + " " + dns_name)
        else:
            self.dns_map.append(ip + " " + dns_name)

    def load_from_string(self, s):
        self.clear()
        f = StringIO(s)
        section = ""
        first_line = True
        while True:
            commented = False
            x = f.readline()
            if not x:
                break
            if first_line:
                if x.startswith(";Build"):
                    first_line = False
                else:
                    raise RuntimeError("Bad config!")
            x = x.strip()
            if x == "":  # nothing, skip line
                continue
            if x.startswith(";"):  # is this a comment
                commented = True
                x = x.lstrip(";")
            temp = shlex.split(x)
            l = list()
            for z in temp:
                l.append(z.strip("\""))
            key = l[0]
            t = (commented,) + tuple(l[1:])
            if section == "":
                if x.startswith("Build"):
                    self.build_time = ";" + x
                if x.startswith("Version"):
                    self.version = ";" + x
                if x.startswith("entry"):
                    section = x[7:-1]
                continue
            if section == "StaticConfig":
                if x == "end":
                    section = ""
                else:
                    self.static_config[key] = t
            if section == "DynamicConfig":
                if x == "end":
                    section = ""
                    continue
                if x.startswith("entry"):
                    section = x[7:-1]
                    continue
                else:
                    self.dynamic_config[key] = t
                continue
            if section == "AdvancedConfigs":
                if x == "end":
                    section = ""
                    continue
                if commented:
                    self.advanced_config.append(";" + x)
                else:
                    self.advanced_config.append(x)
                continue
            if section == "WebFilters":
                if x == "end":
                    section = ""
                    continue
                if commented:
                    self.web_filters.append(";" + x)
                else:
                    self.web_filters.append(x)
                continue
            if section == "WebDataFilters":
                if x == "end":
                    section = ""
                    continue
                if commented:
                    self.web_data_filters.append(";" + x)
                else:
                    self.web_data_filters.append(x)
                continue
            if section == "WebFakes":
                if x == "end":
                    section = ""
                    continue
                if commented:
                    self.web_fakes.append(";" + x)
                else:
                    self.web_fakes.append(x)
                continue
            if section == "TANGrabber":
                if x == "end":
                    section = ""
                    continue
                if commented:
                    self.tan_graber.append(";" + x)
                else:
                    self.tan_graber.append(x)
                continue
            if section == "DnsMap":
                if x == "end":
                    section = ""
                    continue
                if commented:
                    self.dns_map.append(";" + x)
                else:
                    self.dns_map.append(x)
                continue

    def load_from_file(self, filename):
        with open(filename) as f:
            self.load_from_string(f.read())


# for parsing zeus messages


class ZeusMessageHeader(object):
    """ Represents the header from a zeus message.

    """

    def __init__(self, data):
        """ The initializer.

        :type data: bytearray
        :param data:
        """
        self.raw = data
        self.length = data[:4]
        self.length = struct.unpack("<I", str(self.length))[0]
        self.unknown = data[4:12:]
        self.md5_hash = data[-16:]


class ZeusSegment(object):
    """ Represents the header and content of a zeus message segment.

    """

    def __init__(self, data):
        """ The initializer.

        :type data: bytearray
        :param data:
        """
        self.data_type = data[:4]
        self.data_type = struct.unpack("<I", str(self.data_type))[0]
        self.unknown = data[4:8:]
        self.length = data[8:12:]
        self.length = struct.unpack("<I", str(self.length))[0]
        self.length2 = data[12:16:]
        self.length2 = struct.unpack("<I", str(self.length2))[0]
        self.segment_length = 16 + self.length
        self.raw = data[:self.segment_length]
        self.content = data[16:self.length + 16]

    def extract_command(self):
        """ Extracts command data from segment.

        :raise RuntimeError: if segment is not of type 1 (command)
        :return: string containing the command
        :rtype: str
        """
        if self.data_type != 1:
            raise RuntimeError("Not a command segment!")
        else:
            return str(self.content[16:])


class ZeusMessage(object):
    """ Represents a message used by the zeus v1.2 containing header and segments.

        :type segments: list[ZeusSegment]

    """

    def __init__(self, data):
        """ The initializer.

        :type data: bytearray
        :param data:
        """
        self.raw = data
        self.header = ZeusMessageHeader(data[:28])
        self.segments = list()
        left = data[28:]
        while len(left):
            s = ZeusSegment(left)
            self.segments.append(s)
            left = left[s.segment_length:]
